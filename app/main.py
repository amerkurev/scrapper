
import os
import sys
import json
import hashlib
import datetime

from http import HTTPStatus as Status
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, request, render_template, send_from_directory
from playwright.sync_api import sync_playwright


IN_DOCKER = os.environ.get('IN_DOCKER')
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_HOME = Path(os.environ.get('APP_HOME', BASE_DIR / 'app'))
STATIC_DIR = Path(os.environ.get('STATIC_DIR', BASE_DIR / 'static'))
USER_DATA_DIR = Path(os.environ.get('USER_DATA_DIR', BASE_DIR / 'user_data_dir'))

sys.path.append(str(APP_HOME))
from argutil import validate_args
from htmlutil import improve_content


with open(APP_HOME / 'scripts' / 'load_script.js', mode='r') as fd:
    LOAD_SCRIPT_JS = fd.read()

with open(APP_HOME / 'scripts' / 'parse_article.js', mode='r') as fd:
    PARSE_ARTICLE_JS = fd.read()


app = Flask(__name__, static_folder=STATIC_DIR)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/view/<string:id>', methods=['GET'])
def result_html(id):
    data = load_result(id)
    if data:
        data['content'] = improve_content(data)
        return render_template('view.html', data=data)
    return 'Not found', Status.NOT_FOUND


@app.route('/result/<string:id>', methods=['GET'])
def result_json(id):
    data = load_result(id)
    return data if data else 'Not found', Status.NOT_FOUND


@app.route('/parse', methods=['GET'])
def parse():
    args, err = validate_args(args=request.args)
    if err:
        return {'err': err}, Status.BAD_REQUEST

    _id = hashlib.sha1(request.full_path.encode()).hexdigest()  # unique request id

    # get cache data if exists
    if args.no_cache is False:
        data = load_result(_id)
        if data:
            return data

    with sync_playwright() as playwright:
        # https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch
        browser = playwright.firefox.launch(headless=True)

        # https://playwright.dev/python/docs/api/class-browser#browser-new-context
        viewport = {'width': args.viewport_width, 'height': args.viewport_height}
        context = browser.new_context(viewport=viewport, bypass_csp=True)
        page = context.new_page()
        page.goto(args.url)
        page_content = page.content()

        # Waits for the given timeout in milliseconds
        page.wait_for_timeout(args.wait_for_timeout)

        p = urlparse(request.base_url)
        scheme = p.scheme
        host = p.netloc
        readability_path = '/static/libs/readability/Readability.js'
        readability_src = f'{scheme}://{host}{readability_path}'

        # Evaluating JavaScript
        page.evaluate(LOAD_SCRIPT_JS % {'src': readability_src})
        parser_args = {
            'maxElemsToParse': args.max_elems_to_parse,
            'nbTopCandidates': args.nb_top_candidates,
            'charThreshold': args.char_threshold,
        }
        article = page.evaluate(PARSE_ARTICLE_JS % parser_args)

        # release resources
        context.close()
        browser.close()

    status_code = Status.INTERNAL_SERVER_ERROR if 'err' in article else Status.OK

    # Save result to disk
    if status_code == Status.OK:
        article['id'] = _id
        article['url'] = args.url
        article['parsed'] = datetime.datetime.utcnow().isoformat()  # ISO 8601 format
        article['resultUri'] = f'{scheme}://{host}/result/{_id}'

        if args.full_content:
            article['fullContent'] = page_content
        # result_html and result_json always get data from cache!
        dump_result(article, filename=_id)

    return article, status_code


@app.route('/favicon.ico')
def favicon():
    # https://flask.palletsprojects.com/en/1.1.x/patterns/favicon/
    d = STATIC_DIR / 'icons'
    return send_from_directory(d, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def dump_result(data, filename):
    path = USER_DATA_DIR / filename[:2]
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    with open(path / filename, mode='w') as f:
        json.dump(data, f, ensure_ascii=True)


def load_result(filename):
    path = USER_DATA_DIR / filename[:2] / filename
    if not path.exists():
        return None
    with open(path, mode='r') as f:
        data = json.load(f)
    return data
