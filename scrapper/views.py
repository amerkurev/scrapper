
from http import HTTPStatus as Status
from flask import request, render_template, send_file, send_from_directory
# noinspection PyPackageRequirements
from playwright.sync_api import Error as PlaywrightError

from scrapper import app
from scrapper.settings import STATIC_DIR, SCREENSHOT_TYPE
from scrapper.cache import load_result, screenshot_location
from scrapper.util.argutil import default_args
from scrapper.util.htmlutil import improve_content
from scrapper.parsers.article import parse as parse_article


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
    try:
        return parse_article(request=request)
    except PlaywrightError as err:
        message = err.message.splitlines()[0]
        return {'err': [f'Playwright: {message}']}, Status.BAD_REQUEST


@app.route('/favicon.ico')
def favicon():
    # https://flask.palletsprojects.com/en/1.1.x/patterns/favicon/
    d = STATIC_DIR / 'icons'
    return send_from_directory(d, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def startup():
    pass
