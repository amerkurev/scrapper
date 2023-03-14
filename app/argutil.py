
import re
import validators


# Camel case to snake case
pattern = re.compile(r'(?<!^)(?=[A-Z])')


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


def is_present(name, value):
    return value is not None, ''


OPTIONS = (
    # (name, (check_1, check_2, check_3), default_value)

    # # # Custom scraper settings:

    # Page URL. The page should contain the text of the article that needs to be extracted.
    ('url', (is_url,), None),
    # All results of the parsing process will be cached in the user_data_dir directory.
    # If this option is present, the cached result will be ignored and the page will be fetched and parsed again.
    ('noCache', (is_present,), False),
    # If the option is present, the result will have the full HTML contents of the page, including the doctype.
    ('fullContent', (is_present,), False),

    # # # Playwright settings:

    # Launches browser that uses persistent storage located at user_data_dir.
    # User Data Directory stores browser session data like cookies and local storage.
    ('persistentContext', (is_present,), False),
    # Maximum operation time to navigate to the page in milliseconds; defaults to 30000 (30 seconds). Pass 0 to disable the timeout.
    ('timeout', (is_number, gte(0)), 30000),
    # Waits for the given timeout in milliseconds before parsing the article, and after the page has loaded.
    # In many cases, a sleep timeout is not necessary. However, for some websites, it can be quite useful.
    # Other waiting mechanisms, such as network events or waiting for selector visibility, are not currently supported.
    # The default value is 300 milliseconds.
    ('sleep', (is_number, gte(0)), 300),
    # The viewport width in pixels. The default value is 414 (iPhone 11 Viewport).
    ('viewportWidth', (is_number, gt(0)), 414),
    # The viewport height in pixels. The default value is 896 (iPhone 11 Viewport).
    ('viewportHeight', (is_number, gt(0)), 896),
    # Emulates consistent window screen size available inside web page via window.screen. Is only used when the viewport is set.
    # The page width in pixels. Defaults to 828 (iPhone 11 Resolution).
    ('screenWidth', (is_number, gt(0)), 828),
    # The page height in pixels. Defaults to 1792 (iPhone 11 Resolution).
    ('screenHeight', (is_number, gt(0)), 1792),
    # Whether to ignore HTTPS errors when sending network requests. Defaults to not ignore.
    ('ignoreHttpsErrors', (is_present,), False),
    # Specific user agent. Example: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36
    ('userAgent', (), None),

    # # # Readability settings:

    # The maximum number of elements to parse. The default value is 0, which means no limit.
    ('maxElemsToParse', (is_number, gte(0)), 0),

    # The number of top candidates to consider when analysing how tight the competition is among candidates.
    # The default value is 5.
    ('nbTopCandidates', (is_number, gt(0)), 5),

    # The number of characters an article must have in order to return a result.
    # The default value is 500.
    ('charThreshold', (is_number, gt(0)), 500),
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
        setattr(opt, pattern.sub('_', name).lower(), value)

    return opt, errs
