
import os

from http import HTTPStatus as Status
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, request, send_file
from playwright.sync_api import sync_playwright


IN_DOCKER = os.environ.get('IN_DOCKER')
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_HOME = Path(os.environ.get('APP_HOME', BASE_DIR / 'app'))
STATIC_DIR = os.environ.get('STATIC_DIR', BASE_DIR / 'static')
READABILITY_PATH = '/static/libs/readability/Readability.js'
READABILITY_READERABLE_PATH = '/static/libs/readability/Readability-readerable.js'


with open(APP_HOME / 'load_script.js', mode='r') as fd:
    LOAD_SCRIPT_JS = fd.read()

with open(APP_HOME / 'parse_article.js', mode='r') as fd:
    PARSE_ARTICLE_JS = fd.read()


app = Flask(__name__, static_folder=STATIC_DIR)


@app.route('/', methods=['GET'])
def index():
    return send_file('index.html')


@app.route('/parse', methods=['GET'])
def parse():
    url = request.args.get('url')
    # TODO: if it's not URL, return 400!

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
        netloc = p.netloc
        readability_src = f'{scheme}://{netloc}{READABILITY_PATH}'
        readability_readerable_src = f'{scheme}://{netloc}{READABILITY_READERABLE_PATH}'

        # Evaluating JavaScript
        page.evaluate(LOAD_SCRIPT_JS % {'src': readability_src})
        page.evaluate(LOAD_SCRIPT_JS % {'src': readability_readerable_src})
        article = page.evaluate(PARSE_ARTICLE_JS)

        context.close()
        browser.close()

    status_code = Status.INTERNAL_SERVER_ERROR if 'err' in article else Status.OK
    return article, status_code
