
from functools import partial
# noinspection PyPackageRequirements
from playwright.sync_api import Error as PlaywrightError

from scrapper.util.argutil import get_browser_args
from scrapper.settings import (
    USER_DATA_DIR,
    USER_SCRIPTS,
    STEALTH_SCRIPTS_DIR,
    SCREENSHOT_TYPE,
    SCREENSHOT_QUALITY,
)


def new_context(playwright, args):
    # https://playwright.dev/python/docs/api/class-browsertype
    browser_args = get_browser_args(args)
    if args.incognito:
        # create a new incognito browser context
        browser = playwright.firefox.launch(headless=args.headless)
        context = browser.new_context(**browser_args)
    else:
        # create a persistent browser context
        context = playwright.firefox.launch_persistent_context(
            headless=args.headless,
            user_data_dir=USER_DATA_DIR,
            **browser_args,
        )
    return context


def close_context(context):
    # if it was launched as a persistent context null gets returned.
    browser = context.browser
    context.close()
    if browser:
        browser.close()


def page_processing(page, args, init_scripts=None):
    # add stealth scripts for bypassing anti-scraping mechanisms
    if args.stealth:
        use_stealth_mode(page)

    # add extra init scripts
    if init_scripts:
        for path in init_scripts:
            page.add_init_script(path=path)

    # block by resource types
    if args.resource:
        page.route('**/*', resource_blocker(whitelist=args.resource))

    # navigate to the given url
    page.goto(args.url, timeout=args.timeout, wait_until=args.wait_until)

    # waits for the given timeout in milliseconds
    if args.sleep:
        page.wait_for_timeout(args.sleep)

    # add user scripts for DOM manipulation
    if args.user_scripts:
        for script_name in args.user_scripts:
            page.add_script_tag(path=USER_SCRIPTS / script_name)


def resource_blocker(whitelist):  # list of resource types to allow
    def block(route):
        if route.request.resource_type in whitelist:
            route.continue_()
        else:
            route.abort()
    return block


def use_stealth_mode(page):
    for script in STEALTH_SCRIPTS_DIR.glob('*.js'):
        page.add_init_script(path=script)


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


class ParserError(Exception):

    def __init__(self, err):
        super().__init__('Parser error')
        self.err = err
