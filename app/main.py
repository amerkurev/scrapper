
import os
import sys
import json
import hashlib
import datetime

from http import HTTPStatus as Status
from pathlib import Path

from flask import Flask, request, render_template, send_file, send_from_directory
from playwright.sync_api import sync_playwright, TimeoutError, Error as PlaywrightError


IN_DOCKER = os.environ.get('IN_DOCKER')
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_HOME = Path(os.environ.get('APP_HOME', BASE_DIR / 'app'))
STATIC_DIR = Path(os.environ.get('STATIC_DIR', BASE_DIR / 'static'))
USER_DATA_DIR = Path(os.environ.get('USER_DATA_DIR', BASE_DIR / 'user_data_dir'))
USER_SCRIPTS = Path(os.environ.get('USER_SCRIPTS', BASE_DIR / 'user_scripts'))
READABILITY_SCRIPT = APP_HOME / 'scripts' / 'Readability.js'
STEALTH_SCRIPTS_DIR = APP_HOME / 'scripts' / 'stealth'
SCREENSHOT_TYPE = 'jpeg'  # png, jpeg
SCREENSHOT_QUALITY = 80  # 0-100


sys.path.append(str(APP_HOME))
from argutil import (
    validate_args,
    default_args,
    get_browser_args,
    get_parser_args,
    check_user_scrips,
    check_article_fields,
)
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


def playwright_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PlaywrightError as err:
            message = err.message.splitlines()[0]
            return {'err': [f'Playwright: {message}']}, Status.BAD_REQUEST
    return wrapper


@app.route('/parse', methods=['GET'])
@playwright_error
def parse():
    args, err = validate_args(args=request.args)
    check_user_scrips(args=args, user_scripts_dir=USER_SCRIPTS, err=err)
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
        browser_args = get_browser_args(args)
        if args.incognito:
            # create a new incognito browser context
            browser = playwright.firefox.launch(headless=True)
            context = browser.new_context(**browser_args)
        else:
            # create a persistent browser context
            context = playwright.firefox.launch_persistent_context(
                headless=True,
                user_data_dir=USER_DATA_DIR,
                **browser_args,
            )

        page = context.new_page()

        if args.stealth:
            use_stealth_mode(page)

        try:
            page.add_init_script(path=READABILITY_SCRIPT)
            page.goto(args.url, timeout=args.timeout, wait_until=args.wait_until)
            page_content = page.content()
        except TimeoutError:
            return {'err': [f'TimeoutError: timeout {args.timeout}ms exceeded.']}, Status.BAD_REQUEST

        # waits for the given timeout in milliseconds
        if args.sleep:
            page.wait_for_timeout(args.sleep)

        # add user scripts for DOM manipulation
        if args.user_scripts:
            for script_name in args.user_scripts:
                page.add_script_tag(path=USER_SCRIPTS / script_name)

        # take screenshot if requested
        screenshot = None
        if args.screenshot:
            screenshot = page.screenshot(full_page=True, type=SCREENSHOT_TYPE, quality=SCREENSHOT_QUALITY)

        # evaluating JavaScript: parse DOM and extract article content
        with open(APP_HOME / 'scripts' / 'parse.js') as fd:
            article = page.evaluate(fd.read() % get_parser_args(args))

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

        # self-check for development
        if not IN_DOCKER:
            check_article_fields(article, args=args)

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


def use_stealth_mode(page):
    for script in STEALTH_SCRIPTS_DIR.glob('*.js'):
        page.add_init_script(path=script)
