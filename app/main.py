
import os
import json
import uuid
import datetime

from http import HTTPStatus as Status
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, request, render_template
from playwright.sync_api import sync_playwright
from .validator import validate_args


IN_DOCKER = os.environ.get('IN_DOCKER')
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_HOME = Path(os.environ.get('APP_HOME', BASE_DIR / 'app'))
STATIC_DIR = Path(os.environ.get('STATIC_DIR', BASE_DIR / 'static'))
USER_DATA_DIR = Path(os.environ.get('USER_DATA_DIR', BASE_DIR / 'user_data_dir'))


with open(APP_HOME / 'scripts' / 'load_script.js', mode='r') as fd:
    LOAD_SCRIPT_JS = fd.read()

with open(APP_HOME / 'scripts' / 'parse_article.js', mode='r') as fd:
    PARSE_ARTICLE_JS = fd.read()


app = Flask(__name__, static_folder=STATIC_DIR)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/view/<uuid:random_uuid>', methods=['GET'])
def result_html(random_uuid):
    data = load_result(str(random_uuid))
    if data:
        data['articleTagExists'] = '</article>' in data['content']
        return render_template('view.html', data=data)
    return 'Not found', Status.OK


@app.route('/result/<uuid:random_uuid>', methods=['GET'])
def result_json(random_uuid):
    data = load_result(str(random_uuid))
    return data if data else 'Not found', Status.OK


@app.route('/parse', methods=['GET'])
def parse():
    err = validate_args(args=request.args)
    if err:
        return {'err': err}, Status.BAD_REQUEST

    url = request.args.get('url')

    with sync_playwright() as playwright:
        # https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch
        browser = playwright.firefox.launch(headless=True)

        # https://playwright.dev/python/docs/api/class-browser#browser-new-context
        context = browser.new_context(viewport={'width': 414, 'height': 896}, bypass_csp=True)
        page = context.new_page()
        page.goto(url)

        # Waits for the given timeout in milliseconds
        page.wait_for_timeout(1000)

        p = urlparse(request.base_url)
        scheme = p.scheme
        host = p.netloc
        readability_path = '/static/libs/readability/Readability.js'
        readability_src = f'{scheme}://{host}{readability_path}'

        # Evaluating JavaScript
        page.evaluate(LOAD_SCRIPT_JS % {'src': readability_src})
        article = page.evaluate(PARSE_ARTICLE_JS)

        context.close()
        browser.close()

    status_code = Status.INTERNAL_SERVER_ERROR if 'err' in article else Status.OK

    # Save result to disk
    if status_code == Status.OK:
        random_uuid = str(uuid.uuid4())
        article['id'] = random_uuid
        article['url'] = url
        article['parsed'] = datetime.datetime.utcnow().isoformat()  # ISO 8601 format
        article['resultUri'] = f'{scheme}://{host}/result/{random_uuid}'
        dump_result(article, name=random_uuid)

    return article, status_code


def dump_result(data, name):
    path = USER_DATA_DIR / name[:2]
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    with open(path / name, mode='w') as f:
        json.dump(data, f, ensure_ascii=True)


def load_result(name):
    path = USER_DATA_DIR / name[:2] / name
    if not path.exists():
        return None
    with open(path, mode='r') as f:
        data = json.load(f)
    return data
