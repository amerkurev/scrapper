
import os
import sys
import json
import hashlib
import datetime

from http import HTTPStatus as Status
from pathlib import Path

from flask import Flask, request, render_template, send_file, send_from_directory
from playwright.sync_api import sync_playwright


IN_DOCKER = os.environ.get('IN_DOCKER')
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_HOME = Path(os.environ.get('APP_HOME', BASE_DIR / 'app'))
STATIC_DIR = Path(os.environ.get('STATIC_DIR', BASE_DIR / 'static'))
USER_DATA_DIR = Path(os.environ.get('USER_DATA_DIR', BASE_DIR / 'user_data_dir'))
READABILITY_SCRIPT = APP_HOME / 'scripts' / 'Readability.js'
STEALTH_SCRIPTS_DIR = APP_HOME / 'scripts' / 'stealth'
SCREENSHOT_TYPE = 'jpeg'  # png, jpeg
SCREENSHOT_QUALITY = 80  # 0-100


sys.path.append(str(APP_HOME))
from argutil import validate_args, default_args
from htmlutil import improve_content


app = Flask(__name__, static_folder=STATIC_DIR)


@app.route('/', methods=['GET'])
def index():
    args = list(default_args())
    placeholder = '&#10;'.join((f'{x[0]}={x[1]}' for x in args[:10]))  # max 10 args
    placeholder = placeholder.replace('=True', '=yes').replace('=False', '=no')
    return render_template('index.html', context={'placeholder': placeholder})


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


@app.route('/screenshot/<string:id>', methods=['GET'])
def result_screenshot(id):
    return send_file(screenshot_location(id), mimetype=f'image/{SCREENSHOT_TYPE}')


@app.route('/parse', methods=['GET'])
def parse():
    args, err = validate_args(args=request.args)
    if err:
        return {'err': err}, Status.BAD_REQUEST

    _id = hashlib.sha1(request.full_path.encode()).hexdigest()  # unique request id

    # get cache data if exists
    if args.cache is True:
        data = load_result(_id)
        if data:
            return data

    with sync_playwright() as playwright:
        # https://playwright.dev/python/docs/api/class-browsertype
        browser_args = {
            'bypass_csp': True,
            'viewport': {
                'width': args.viewport_width,
                'height': args.viewport_height,
            },
            'screen':  {
                'width': args.screen_width,
                'height': args.screen_height,
            },
            'ignore_https_errors': args.ignore_https_errors,
            'user_agent': args.user_agent,
            'locale': args.locale,
            'timezone_id': args.timezone,
            'http_credentials': args.http_credentials,
            'extra_http_headers': args.extra_http_headers,
        }
        # proxy settings:
        if args.proxy_server:
            browser_args['proxy'] = {
                'server': args.proxy_server,
                'bypass': args.proxy_bypass,
                'username': args.proxy_username,
                'password': args.proxy_password,
            }

        # create a new browser context
        if args.incognito:
            browser = playwright.firefox.launch(headless=True)
            context = browser.new_context(**browser_args)  # create a new incognito browser context
        else:
            context = playwright.firefox.launch_persistent_context(
                headless=True,
                user_data_dir=USER_DATA_DIR,
                **browser_args,
            )

        # https://playwright.dev/python/docs/api/class-page
        page = context.new_page()
        if args.stealth:
            for script in STEALTH_SCRIPTS_DIR.glob('*.js'):
                page.add_init_script(path=script)

        page.add_init_script(path=READABILITY_SCRIPT)
        page.goto(args.url, timeout=args.timeout)
        page_content = page.content()

        # waits for the given timeout in milliseconds
        page.wait_for_timeout(args.sleep)

        # take screenshot if requested
        screenshot = None
        if args.screenshot:
            screenshot = page.screenshot(full_page=True, type=SCREENSHOT_TYPE, quality=SCREENSHOT_QUALITY)

        # evaluating JavaScript: parse DOM and extract article content
        parser_args = {
            'maxElemsToParse': args.max_elems_to_parse,
            'nbTopCandidates': args.nb_top_candidates,
            'charThreshold': args.char_threshold,
        }
        with open(APP_HOME / 'scripts' / 'parse.js') as fd:
            article = page.evaluate(fd.read() % parser_args)

        # if it was launched as a persistent context null gets returned.
        browser = context.browser
        context.close()
        if browser:
            browser.close()

    status_code = Status.INTERNAL_SERVER_ERROR if 'err' in article else Status.OK

    # save result to disk
    if status_code == Status.OK:
        article['id'] = _id
        article['parsed'] = datetime.datetime.utcnow().isoformat()  # ISO 8601 format
        article['resultUri'] = f'{request.host_url}result/{_id}'
        article['query'] = request.args.to_dict(flat=True)

        if args.full_content:
            article['fullContent'] = page_content
        if args.screenshot:
            article['screenshotUri'] = f'{request.host_url}screenshot/{_id}'

        dump_result(article, filename=_id, screenshot=screenshot)

    return article, status_code


@app.route('/favicon.ico')
def favicon():
    # https://flask.palletsprojects.com/en/1.1.x/patterns/favicon/
    d = STATIC_DIR / 'icons'
    return send_from_directory(d, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def dump_result(data, filename, screenshot=None):
    path = json_location(filename)

    # create dir if not exists
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

    # save result as json
    with open(path, mode='w') as f:
        json.dump(data, f, ensure_ascii=True)

    # save screenshot
    if screenshot:
        with open(screenshot_location(filename), mode='wb') as f:
            f.write(screenshot)


def load_result(filename):
    path = json_location(filename)
    if not path.exists():
        return None
    with open(path, mode='r') as f:
        return json.load(f)


def json_location(filename):
    return USER_DATA_DIR / '_res' / filename[:2] / filename


def screenshot_location(filename):
    return str(json_location(filename)) + '.' + SCREENSHOT_TYPE
