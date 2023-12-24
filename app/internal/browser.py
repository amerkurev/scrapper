import contextlib
from collections.abc import Sequence

from playwright.async_api import Browser, BrowserContext, Page, Route
from playwright.async_api import Error as PlaywrightError
from routers.query_params import CommonQueryParams, BrowserQueryParams, ProxyQueryParams

from settings import (
    USER_DATA_DIR,
    USER_SCRIPTS,
    STEALTH_SCRIPTS_DIR,
    SCREENSHOT_TYPE,
    SCREENSHOT_QUALITY,
)


@contextlib.asynccontextmanager
async def new_context(
    browser: Browser,
    params: BrowserQueryParams,
    proxy: ProxyQueryParams,
) -> BrowserContext:
    # https://playwright.dev/python/docs/api/class-browser#browser-new-context
    browser_args = {
        'bypass_csp': True,
        'viewport': {
            'width': params.viewport_width,
            'height': params.viewport_height,
        },
        'screen': {
            'width': params.screen_width,
            'height': params.screen_height,
        },
        'ignore_https_errors': params.ignore_https_errors,
        'user_agent': params.user_agent,
        'locale': params.locale,
        'timezone_id': params.timezone,
        'http_credentials': params.http_credentials,
        'extra_http_headers': params.extra_http_headers,
    }
    # proxy settings:
    if proxy.proxy_server:
        browser_args['proxy'] = {
            'server': proxy.proxy_server,
        }
        if proxy.proxy_username:
            browser_args['proxy']['username'] = proxy.proxy_username
        if proxy.proxy_password:
            browser_args['proxy']['password'] = proxy.proxy_password
        if proxy.proxy_bypass:
            browser_args['proxy']['bypass'] = proxy.proxy_bypass

    if params.incognito:
        # create a new incognito browser context
        # (more efficient way, because it doesn't create a new browser instance)
        context = await browser.new_context(**browser_args)
    else:
        # create a persistent browser context
        # (less efficient way, because it creates a new browser instance)
        context = await browser.browser_type.launch_persistent_context(
            headless=True,
            user_data_dir=USER_DATA_DIR,
            **browser_args,
        )
    try:
        yield context
    finally:
        # context should always be closed at the end
        await context.close()


async def page_processing(
    page: Page,
    url: str,
    params: CommonQueryParams,
    browser_params: BrowserQueryParams,
    init_scripts: Sequence[str] = None,
):
    # add stealth scripts for bypassing anti-scraping mechanisms
    if params.stealth:
        await use_stealth_mode(page)

    # add extra init scripts
    if init_scripts:
        for path in init_scripts:
            await page.add_init_script(path=path)

    # block by resource types
    if browser_params.resource:
        handler = resource_blocker(whitelist=browser_params.resource)
        await page.route('**/*', handler)

    # navigate to the given url
    # noinspection PyTypeChecker
    await page.goto(url, timeout=browser_params.timeout, wait_until=browser_params.wait_until)

    # wait for the given timeout in milliseconds and scroll down the page
    n = 10
    if browser_params.sleep:
        for _ in range(n):
            # scroll down the page by 1/n of the given scroll_down value
            if browser_params.scroll_down:
                await page.mouse.wheel(0, browser_params.scroll_down / n)
            # sleep for 1/n of the given sleep value
            await page.wait_for_timeout(browser_params.sleep / n)

        # scroll to the top of the page for the screenshot to be in the correct position
        if browser_params.scroll_down:
            await page.mouse.wheel(0, 0)

    # add user scripts for DOM manipulation
    if params.user_scripts:
        for script in params.user_scripts:
            await page.add_script_tag(path=USER_SCRIPTS / script)

    # wait for the given timeout in milliseconds after user scripts were injected.
    if params.user_scripts_timeout:
        await page.wait_for_timeout(params.user_scripts_timeout)


def resource_blocker(whitelist: Sequence[str]):  # list of resource types to allow
    async def block(route: Route):
        if route.request.resource_type in whitelist:
            await route.continue_()
        else:
            await route.abort()
    return block


async def use_stealth_mode(page: Page):
    for script in STEALTH_SCRIPTS_DIR.glob('*.js'):
        await page.add_init_script(path=script)


async def get_screenshot(page: Page):
    # First try to take a screenshot of the full scrollable page,
    # if it fails, take a screenshot of the currently visible viewport.
    kwargs = dict(type=SCREENSHOT_TYPE, quality=SCREENSHOT_QUALITY)
    try:
        # try to take a full page screenshot
        return await page.screenshot(full_page=True, **kwargs)
    except PlaywrightError as err:
        # if the page is too large, take a screenshot of the currently visible viewport
        if 'Cannot take screenshot larger than ' in err.message:
            return await page.screenshot(full_page=False, **kwargs)
        raise err
