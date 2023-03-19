
import hashlib
import datetime

from functools import partial
from http import HTTPStatus as Status
# noinspection PyPackageRequirements
from playwright.sync_api import sync_playwright, TimeoutError, Error as PlaywrightError

from scrapper.util.argutil import (
    validate_args,
    get_browser_args,
    get_parser_args,
    check_user_scrips,
)
from scrapper.cache import load_result, dump_result
from scrapper.settings import (
    IN_DOCKER,
    USER_DATA_DIR,
    USER_SCRIPTS,
    READABILITY_SCRIPT,
    PARSE_SCRIPT,
    STEALTH_SCRIPTS_DIR,
    SCREENSHOT_TYPE,
    SCREENSHOT_QUALITY,
)


def parse(request):
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

        # add stealth scripts for bypassing anti-scraping mechanisms
        if args.stealth:
            use_stealth_mode(page)

        # add Readability.js script
        page.add_init_script(path=READABILITY_SCRIPT)

        # block by resource types
        if args.resource:
            page.route('**/*', resource_blocker(whitelist=args.resource))

        try:
            # navigate to the given url
            page.goto(args.url, timeout=args.timeout, wait_until=args.wait_until)
            page_content = page.content()
        except TimeoutError:
            # special handling for timeout error
            return {'err': [f'TimeoutError: timeout {args.timeout}ms exceeded.']}, Status.BAD_REQUEST

        # waits for the given timeout in milliseconds
        if args.sleep:
            page.wait_for_timeout(args.sleep)

        # add user scripts for DOM manipulation
        if args.user_scripts:
            for script_name in args.user_scripts:
                page.add_script_tag(path=USER_SCRIPTS / script_name)

        # take screenshot if requested
        screenshot = get_screenshot(page) if args.screenshot else None

        # evaluating JavaScript: parse DOM and extract article content
        with open(PARSE_SCRIPT) as fd:
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


def get_screenshot(page):
    # First try to take a screenshot of the full scrollable page,
    # if it fails, take a screenshot of the currently visible viewport.
    f = partial(page.screenshot, type=SCREENSHOT_TYPE, quality=SCREENSHOT_QUALITY)
    try:
        # try to take a full page screenshot
        return f(full_page=True)
    except PlaywrightError as err:
        # if the page is too large, take a screenshot of the currently visible viewport
        if 'Cannot take screenshot larger than ' in err.message:
            return f(full_page=False)
        raise err


def use_stealth_mode(page):
    for script in STEALTH_SCRIPTS_DIR.glob('*.js'):
        page.add_init_script(path=script)


def resource_blocker(whitelist):  # list of resource types to allow
    def block(route):
        if route.request.resource_type in whitelist:
            route.continue_()
        else:
            route.abort()
    return block


NoneType = type(None)
ARTICLE_FIELDS = (
    # (name, types, condition)

    # author metadata
    ('byline', (NoneType, str), None),
    # HTML string of processed article content
    ('content', (NoneType, str), None),
    # content direction
    ('dir', (NoneType, str), None),
    # article description, or short excerpt from the content
    ('excerpt', (NoneType, str), None),
    # full HTML contents of the page
    ('fullContent', str, lambda args: args.full_content),
    # unique request ID
    ('id', str, None),
    # content language
    ('lang', (NoneType, str), None),
    # length of an article, in characters
    ('length', (NoneType, int), None),
    # date of extracted article
    ('parsed', str, None),
    # request parameters
    ('query', dict, None),
    # URL of the current result, the data here is always taken from cache
    ('resultUri', str, None),
    # URL of the screenshot of the page
    ('screenshotUri', str, lambda args: args.screenshot),
    # name of the site
    ('siteName', (NoneType, str), None),
    # text content of the article, with all the HTML tags removed
    ('textContent', (NoneType, str), None),
    # article title
    ('title', (NoneType, str), None),
)


def check_article_fields(article, args):
    for (name, types, condition) in ARTICLE_FIELDS:
        if condition is None or condition(args):
            assert name in article, f'Missing {name}'
            assert isinstance(article[name], types), f'Invalid {name}'
