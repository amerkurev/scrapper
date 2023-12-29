from enum import Enum
from email.errors import MessageParseError
from email.parser import Parser as HeaderParser
from typing import Any, Annotated
from urllib.parse import urlparse

from fastapi import Query
from fastapi.exceptions import RequestValidationError

from settings import USER_SCRIPTS_DIR


class WaitUntilEnum(str, Enum):
    load = 'load'
    domcontentloaded = 'domcontentloaded'
    networkidle = 'networkidle'
    commit = 'commit'


def query_parsing_error(field: str, msg: str, value: Any) -> RequestValidationError:
    obj = {
        'type': f'{field}_parsing',
        'loc': ('query', field),
        'msg': msg,
        'input': value,
    }
    return RequestValidationError([obj])


class CommonQueryParams:
    """Common scraper settings"""
    def __init__(
        self,
        cache: Annotated[
            bool,
            Query(
                description='All results of the parsing process will be cached in the `user_data` directory.<br>'
                            'Cache can be disabled by setting the cache option to false. In this case, the page will be fetched and parsed every time.<br>'
                            'Cache is enabled by default.<br><br>',
            ),
        ] = True,
        full_content: Annotated[
            bool,
            Query(
                alias='full-content',
                description='If this option is set to true, the result will have the full HTML contents of the page (`fullContent` field in the result).<br><br>',
            ),
        ] = False,
        stealth: Annotated[
            bool,
            Query(
                description='Stealth mode allows you to bypass anti-scraping techniques. It is disabled by default.<br>'
                            'Mostly taken from [https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth/evasions](https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth/evasions)<br><br>',
            ),
        ] = False,
        screenshot: Annotated[
            bool,
            Query(
                description='If this option is set to true, the result will have the link to the screenshot of the page (`screenshot` field in the result).<br>'
                            'Important implementation details: Initially, Scrapper attempts to take a screenshot of the entire scrollable page.<br>'
                            'If it fails because the image is too large, it will only capture the currently visible viewport.<br><br>',
            ),
        ] = False,
        user_scripts: Annotated[
            str | None,
            Query(
                alias='user-scripts',
                description='To use your JavaScript scripts on a webpage, put your script files into the `user_scripts` directory. '
                            'Then, list the scripts you need in the `user-scripts` parameter, separating them with commas. '
                            'These scripts will run after the page loads but before the article parser starts. '
                            'This means you can use these scripts to do things like remove ad blocks or automatically click the cookie acceptance button. '
                            'Keep in mind, script names cannot include commas, as they are used for separation.<br>For example, you might pass `remove-ads.js, click-cookie-accept-button.js`.<br><br>'
                            'If you plan to run asynchronous long-running scripts, check `user-scripts-timeout` parameter.'
            ),
        ] = None,
        user_scripts_timeout: Annotated[
            int,
            Query(
                alias='user-scripts-timeout',
                description='Waits for the given timeout in milliseconds after injecting users scripts.<br>'
                            'For example if you want to navigate through page to specific content, set a longer period (higher value).<br>'
                            'The default value is 0, which means no sleep.<br><br>',
                ge=0,
            ),
        ] = 0,
    ):
        self.cache = cache
        self.full_content = full_content
        self.stealth = stealth
        self.screenshot = screenshot
        self.user_scripts = None
        self.user_scripts_timeout = user_scripts_timeout

        if user_scripts:
            user_scripts = list(filter(None, map(str.strip, user_scripts.split(','))))
            if user_scripts:
                # check if all files exist
                for script in user_scripts:
                    if not (USER_SCRIPTS_DIR / script).exists():
                        raise query_parsing_error('user_scripts', 'User script not found', script)
                self.user_scripts = user_scripts


class BrowserQueryParams:
    """Browser settings"""
    def __init__(
        self,
        incognito: Annotated[
            bool,
            Query(
                description="Allows creating `incognito` browser contexts. Incognito browser contexts don't write any browsing data to disk.<br><br>",
            ),
        ] = True,
        timeout: Annotated[
            int,
            Query(
                description='Maximum operation time to navigate to the page in milliseconds; defaults to 60000 (60 seconds).<br>'
                            'Pass 0 to disable the timeout.<br><br>',
                ge=0,
            ),
        ] = 60000,
        wait_until: Annotated[
            WaitUntilEnum,
            Query(
                alias='wait-until',
                description='When to consider navigation succeeded, defaults to `domcontentloaded`. Events can be either:<br>'
                            '`load` - consider operation to be finished when the `load` event is fired.<br>'
                            '`domcontentloaded` - consider operation to be finished when the DOMContentLoaded event is fired.<br>'
                            '`networkidle` -  consider operation to be finished when there are no network connections for at least 500 ms.<br>'
                            '`commit` - consider operation to be finished when network response is received and the document started loading.<br>'
                            'See for details: [https://playwright.dev/python/docs/navigations](https://playwright.dev/python/docs/navigations#navigation-lifecycle)<br><br>',

            ),
        ] = WaitUntilEnum.domcontentloaded,
        sleep: Annotated[
            int,
            Query(
                description='Waits for the given timeout in milliseconds before parsing the article, and after the page has loaded.<br>'
                            'In many cases, a sleep timeout is not necessary. However, for some websites, it can be quite useful.<br>'
                            'Other waiting mechanisms, such as waiting for selector visibility, are not currently supported.<br>'
                            'The default value is 0, which means no sleep.<br><br>',
                ge=0,
            ),
        ] = 0,
        resource: Annotated[
            str | None,
            Query(
                description='List of resource types allowed to be loaded on the page.<br>'
                            'All other resources will not be allowed, and their network requests will be aborted.<br>'
                            'The following resource types are supported:<br>'
                            '`document`<br>'
                            '`stylesheet`<br>'
                            '`image`<br>'
                            '`media`<br>'
                            '`font`<br>'
                            '`script`<br>'
                            '`texttrack`<br>'
                            '`xhr`<br>'
                            '`fetch`<br>'
                            '`eventsource`<br>'
                            '`websocket`<br>'
                            '`manifest`<br>'
                            '`other`<br><br>'
                            'By default, all resource types are allowed.',
            ),
        ] = None,
        viewport_width: Annotated[
            int,
            Query(
                alias='viewport-width',
                description='The viewport width in pixels. The default value is 414 (iPhone 11 Viewport).<br><br>',
                ge=1,
            ),
        ] = 414,
        viewport_height: Annotated[
            int,
            Query(
                alias='viewport-height',
                description='The viewport height in pixels. The default value is 896 (iPhone 11 Viewport).<br><br>',
                ge=1,
            ),
        ] = 896,
        screen_width: Annotated[
            int,
            Query(
                alias='screen-width',
                description='Emulates consistent window screen size available inside web page via window.screen. Is only used when the viewport is set.<br>'
                            'The page width in pixels. Defaults to 828 (iPhone 11 Resolution).<br><br>',
                ge=1,
            ),
        ] = 828,
        screen_height: Annotated[
            int,
            Query(
                alias='screen-height',
                description='Emulates consistent window screen size available inside web page via window.screen. Is only used when the viewport is set.<br>'
                            'The page height in pixels. Defaults to 1792 (iPhone 11 Resolution).<br><br>',
                ge=1,
            ),
        ] = 1792,
        scroll_down: Annotated[
            int,
            Query(
                alias='scroll-down',
                description='Scroll down the page by a specified number of pixels.<br>'
                            'This is particularly useful when dealing with lazy-loading pages (pages that are loaded only as you scroll down).<br>'
                            'This parameter is used in conjunction with the `sleep` parameter.<br>'
                            "Make sure to set a positive value for the `sleep` parameter, otherwise, the scroll function won't work.<br><br>",
                ge=0,
            ),
        ] = 0,
        ignore_https_errors: Annotated[
            bool,
            Query(
                alias='ignore-https-errors',
                description='Whether to ignore HTTPS errors when sending network requests.<br>'
                            'The default setting is to ignore HTTPS errors.<br><br>',
            ),
        ] = True,
        user_agent: Annotated[
            str | None,
            Query(
                alias='user-agent',
                description='Specify user agent to emulate.<br>'
                            'By default, Playwright uses a user agent that matches the browser version.',
            ),
        ] = None,
        locale: Annotated[
            str | None,
            Query(
                description='Specify user locale, for example en-GB, de-DE, etc.<br>'
                            'Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting rules.',
            ),
        ] = None,
        timezone: Annotated[
            str | None,
            Query(
                description="Changes the timezone of the context. See ICU's metaZones.txt for a list of supported timezone IDs.",
            ),
        ] = None,
        http_credentials: Annotated[
            str | None,
            Query(
                alias='http-credentials',
                description='Credentials for HTTP authentication (string containing username and password separated by a colon, e.g. `username:password`).',
            ),
        ] = None,
        extra_http_headers: Annotated[
            list | None,
            Query(
                alias='extra-http-headers',
                description='Contains additional HTTP headers to be sent with every request. Example: `X-API-Key:123456;X-Auth-Token:abcdef`.',
            ),
        ] = None,
    ):
        self.incognito = incognito
        self.timeout = timeout
        self.wait_until = wait_until
        self.sleep = sleep
        self.resource = None
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll_down = scroll_down
        self.ignore_https_errors = ignore_https_errors
        self.user_agent = user_agent
        self.locale = locale
        self.timezone = timezone
        self.http_credentials = None
        self.extra_http_headers = None

        if resource:
            resource = list(filter(None, map(str.strip, resource.split(','))))
            if resource:
                self.resource = resource

        if http_credentials:
            fake_url = f'http://{http_credentials}@localhost'
            try:
                p = urlparse(fake_url)
                self.http_credentials = {
                    'username': p.username or '',  # expected only string, not None
                    'password': p.password or '',  # same
                }
            except ValueError:
                raise query_parsing_error('http_credentials', 'Invalid HTTP credentials', http_credentials)

        if extra_http_headers:
            try:
                headers = HeaderParser().parsestr('\r\n'.join(extra_http_headers))
                self.extra_http_headers = dict(headers)
                # check if headers were parsed correctly
                if not self.extra_http_headers:
                    raise MessageParseError()
            except MessageParseError:
                raise query_parsing_error('extra_http_headers', 'Invalid HTTP header', extra_http_headers)


class ProxyQueryParams:
    """Network proxy settings"""
    def __init__(
        self,
        proxy_server: Annotated[
            str | None,
            Query(
                alias='proxy-server',
                description='Proxy to be used for all requests.<br>'
                            'HTTP and SOCKS proxies are supported, for example http://myproxy.com:3128 or socks5://myproxy.com:3128.<br>'
                            'Short form myproxy.com:3128 is considered an HTTP proxy.',
            ),
        ] = None,
        proxy_bypass: Annotated[
            str | None,
            Query(
                alias='proxy-bypass',
                description='Optional comma-separated domains to bypass proxy, for example `.com, chromium.org, .domain.com`.',
            ),
        ] = None,
        proxy_username: Annotated[
            str | None,
            Query(
                alias='proxy-username',
                description='Optional username to use if HTTP proxy requires authentication.',
            ),
        ] = None,
        proxy_password: Annotated[
            str | None,
            Query(
                alias='proxy-password',
                description='Optional password to use if HTTP proxy requires authentication.',
            ),
        ] = None,
    ):
        self.proxy_server = proxy_server
        self.proxy_bypass = proxy_bypass
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password


class ReadabilityQueryParams:
    """Readability settings"""
    def __init__(
        self,
        max_elems_to_parse: Annotated[
            int,
            Query(
                alias='max-elems-to-parse',
                description='The maximum number of elements to parse. The default value is 0, which means no limit.<br><br>',
                ge=0,
            ),
        ] = 0,
        nb_top_candidates: Annotated[
            int,
            Query(
                alias='nb-top-candidates',
                description='The number of top candidates to consider when analysing how tight the competition is among candidates.<br>'
                            'The default value is 5.<br><br>',
                ge=1,
            ),
        ] = 5,
        char_threshold: Annotated[
            int,
            Query(
                alias='char-threshold',
                description='The number of chars an article must have in order to return a result.<br>'
                            'The default value is 500.<br><br>',
                ge=1,
            ),
        ] = 500,
    ):
        self.max_elems_to_parse = max_elems_to_parse
        self.nb_top_candidates = nb_top_candidates
        self.char_threshold = char_threshold


class LinkParserQueryParams:
    """Link parser settings"""
    def __init__(
        self,
        text_len_threshold: Annotated[
            int,
            Query(
                alias='text-len-threshold',
                description='The median (middle value) of the link text length in characters. The default value is 40 characters.<br>'
                            'Hyperlinks must adhere to this criterion to be included in the results.<br>'
                            'However, this criterion is not a strict threshold value, and some links may ignore it.<br><br>',
                ge=0,
            ),
        ] = 40,
        words_threshold: Annotated[
            int,
            Query(
                alias='words-threshold',
                description='The median (middle value) of the number of words in the link text. The default value is 3 words.<br>'
                            'Hyperlinks must adhere to this criterion to be included in the results.<br>'
                            'However, this criterion is not a strict threshold value, and some links may ignore it.<br><br>',
                ge=0,
            ),
        ] = 3,
    ):
        self.text_len_threshold = text_len_threshold
        self.words_threshold = words_threshold
