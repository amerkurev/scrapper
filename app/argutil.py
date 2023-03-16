
import validators
from operator import methodcaller


TRUE_VALUES = ('true', '1', 'yes', 'on', 'y')
FALSE_VALUES = ('false', '0', 'no', 'off', 'n')


def is_url(name, val):
    err = ''
    if not validators.url(val):
        err = f'{name} is invalid'
    return val, err


def is_number(name, val):
    err = ''
    try:
        val = int(val)
    except ValueError:
        err = f'{name} must be a positive natural number'
    return val, err


def gte(min_value):
    def f(name, val):
        err = ''
        if val < min_value:
            err = f'{name} must be greater than or equal to {min_value}'
        return val, err
    return f


def gt(min_value):
    def f(name, val):
        err = ''
        if val <= min_value:
            err = f'{name} must be greater than {min_value}'
        return val, err
    return f


def lte(max_value):
    def f(name, val):
        err = ''
        if val > max_value:
            err = f'{name} must be less than or equal to {max_value}'
        return val, err
    return f


def lt(max_value):
    def f(name, val):
        err = ''
        if val >= max_value:
            err = f'{name} must be less than {max_value}'
        return val, err
    return f


def is_bool(name, value):
    if value in TRUE_VALUES:
        return True, ''
    if value in FALSE_VALUES:
        return False, ''
    return value, f'{name} must be a boolean value: true, 1, yes, on, y, false, 0, no, off, n'


def is_credentials(name, val):
    err = ''
    parts = val.split(':')
    if len(parts) == 1:
        return {'username': parts[0], 'password': ''}, err
    if len(parts) == 2:
        return {'username': parts[0], 'password': parts[1]}, err
    err = f'{name} must be in the format username:password'
    return val, err


def is_list(name, val):
    err = ''
    return list(filter(None, map(methodcaller('strip'), val.split(',')))), err


def is_dict(name, val):
    err = ''
    r = {}
    parts = val.split(';')
    for part in parts:
        if ':' not in part:
            err = f'{name} must be in the format key:value;key:value'
            return val, err
        key, v = part.split(':', 1)  # maxsplit=1
        r[key] = v
    return r, err


def is_enum(choices):
    def f(name, val):
        err = ''
        if val not in choices:
            err = f'{name} must be one of {choices}'
        return val, err
    return f


OPTIONS = (
    # (name, (check_1, check_2, check_3), default_value)

    # # # Custom scraper settings:

    # Page URL. The page should contain the text of the article that needs to be extracted.
    ('url', (is_url,), None),
    # All results of the parsing process will be cached in the user_data_dir directory.
    # Cache can be disabled by setting the cache option to false. In this case, the page will be fetched and parsed every time.
    # Cache is enabled by default.
    ('cache', (is_bool,), True),
    # If this option is set to true, the result will have the full HTML contents of the page (fullContent field in the result).
    ('full-content', (is_bool,), False),
    # Stealth mode allows you to bypass anti-scraping techniques. It is disabled by default.
    # Mostly taken from https://github.com/berstend/puppeteer-extra/tree/master/packages/puppeteer-extra-plugin-stealth/evasions
    ('stealth', (is_bool,), False),
    # If this option is set to true, the result will have the link to the screenshot of the page (screenshot field in the result).
    ('screenshot', (is_bool,), False),
    # To use your JavaScript scripts on the page, add script files to the "user_scripts" directory,
    # and list the required ones (separated by commas) in the "user-scripts" parameter. These scripts will execute after the page loads
    # but before the article parser runs. This allows you to help parse the article in a variety of ways,
    # such as removing markup, ad blocks, or anything else. For example: user-scripts=remove_ads.js, click_cookie_accept_button.js
    ('user-scripts', (is_list,), None),

    # # # Playwright settings:

    # Allows creating "incognito" browser contexts. "Incognito" browser contexts don't write any browsing data to disk.
    ('incognito', (is_bool,), True),
    # Maximum operation time to navigate to the page in milliseconds; defaults to 30000 (30 seconds). Pass 0 to disable the timeout.
    ('timeout', (is_number, gte(0)), 30000),
    # When to consider navigation succeeded, defaults to "domcontentloaded". Events can be either:
    # - load - consider operation to be finished when the "load" event is fired.
    # - domcontentloaded - consider operation to be finished when the DOMContentLoaded event is fired.
    # - networkidle -  consider operation to be finished when there are no network connections for at least 500 ms.
    # - commit - consider operation to be finished when network response is received and the document started loading.
    ('wait_until', (is_enum(('domcontentloaded', 'load', 'networkidle', 'commit')),), 'domcontentloaded'),
    # Waits for the given timeout in milliseconds before parsing the article, and after the page has loaded.
    # In many cases, a sleep timeout is not necessary. However, for some websites, it can be quite useful.
    # Other waiting mechanisms, such as network events or waiting for selector visibility, are not currently supported.
    # The default value is 300 milliseconds.
    ('sleep', (is_number, gte(0)), 300),
    # The viewport width in pixels. The default value is 414 (iPhone 11 Viewport).
    ('viewport-width', (is_number, gt(0)), 414),
    # The viewport height in pixels. The default value is 896 (iPhone 11 Viewport).
    ('viewport-height', (is_number, gt(0)), 896),
    # Emulates consistent window screen size available inside web page via window.screen. Is only used when the viewport is set.
    # The page width in pixels. Defaults to 828 (iPhone 11 Resolution).
    ('screen-width', (is_number, gt(0)), 828),
    # The page height in pixels. Defaults to 1792 (iPhone 11 Resolution).
    ('screen-height', (is_number, gt(0)), 1792),
    # Whether to ignore HTTPS errors when sending network requests. Defaults to not ignore.
    ('ignore-https-errors', (is_bool,), False),
    # Specific user agent.
    ('user-agent', (), None),
    # Specify user locale, for example en-GB, de-DE, etc.
    # Locale will affect navigator.language value, Accept-Language request header value as well as number and date formatting rules.
    ('locale', (), None),
    # Changes the timezone of the context. See ICU's metaZones.txt for a list of supported timezone IDs.
    ('timezone', (), None),
    # Credentials for HTTP authentication (string containing username and password separated by a colon, e.g. "username:password").
    ('http-credentials', (is_credentials,), None),
    # Contains additional HTTP headers to be sent with every request. Example: "X-API-Key:123456;X-Auth-Token:abcdef".
    ('extra-http-headers', (is_dict,), None),

    # # # Network proxy settings:

    # Proxy to be used for all requests. HTTP and SOCKS proxies are supported, for example http://myproxy.com:3128 or socks5://myproxy.com:3128.
    # Short form myproxy.com:3128 is considered an HTTP proxy.
    ('proxy-server', (), None),
    # Optional comma-separated domains to bypass proxy, for example ".com, chromium.org, .domain.com".
    ('proxy-bypass', (), ''),
    # Optional username to use if HTTP proxy requires authentication.
    ('proxy-username', (), ''),
    # Optional password to use if HTTP proxy requires authentication.
    ('proxy-password', (), ''),

    # # # Readability settings:

    # The maximum number of elements to parse. The default value is 0, which means no limit.
    ('max-elems-to-parse', (is_number, gte(0)), 0),
    # The number of top candidates to consider when analysing how tight the competition is among candidates.
    # The default value is 5.
    ('nb-top-candidates', (is_number, gt(0)), 5),
    # The number of characters an article must have in order to return a result.
    # The default value is 500.
    ('char-threshold', (is_number, gt(0)), 500),
)

REQUIRED = ('url',)


class Options(object):
    pass


def validate_args(args):
    errs = []
    opt = Options()

    for x in OPTIONS:
        name, checks, default_value = x
        value = args.get(name)

        if value is None:  # value is not provided
            value = default_value  # skip all checks for default values
            if name in REQUIRED:
                errs.append(f'{name} is required')
        else:
            for check in checks:
                value, err = check(name, value)
                if err:
                    errs.append(err)
                    break

        # Camel case to snake case
        setattr(opt, name.replace('-', '_'), value)

    return opt, errs


def check_user_scrips(args, user_scripts_dir, err):
    if not args.user_scripts:
        return

    for script_name in args.user_scripts:
        if not (user_scripts_dir / script_name).exists():
            err.append(f'User script "{script_name}" not found')


def default_args():
    return ((x[0], x[2]) for x in OPTIONS if x[2] is not None)


def get_browser_args(args):
    browser_args = {
        'bypass_csp': True,
        'viewport': {
            'width': args.viewport_width,
            'height': args.viewport_height,
        },
        'screen': {
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
    return browser_args


def get_parser_args(args):
    parser_args = {
        'maxElemsToParse': args.max_elems_to_parse,
        'nbTopCandidates': args.nb_top_candidates,
        'charThreshold': args.char_threshold,
    }
    return parser_args
