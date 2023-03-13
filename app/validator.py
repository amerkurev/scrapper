
import argname
import validators


class Options:
    def __init__(self):
        # # # Custom scraper settings:
        self.url = None
        self.no_cache = False
        self.full_content = False
        # # # Playwright settings:
        self.viewport_width = 414
        self.viewport_height = 896
        self.wait_for_timeout = 300
        # # # Readability settings:
        self.max_elems_to_parse = 0
        self.nb_top_candidates = 5
        self.char_threshold = 500


def check_number(value, name, err):
    try:
        value = int(value)
    except ValueError:
        err.append(f'{name} must be a number')
        return None
    if value < 0:
        err.append(f'{name} must be greater or equal to 0')
        return None
    return value


def validate_args(args):
    err = []
    opt = Options()

    url = args.get(argname.URL)
    if not url:
        err.append('Page URL is required')
        return None, err  # critical error, no need to continue

    if not validators.url(url):
        err.append('Page URL is invalid')
        return None, err  # critical error, no need to continue

    opt.url = url
    opt.no_cache = argname.NO_CACHE in args
    opt.full_content = argname.FULL_CONTENT in args

    opt.viewport_width = check_number(
        value=args.get(argname.VIEWPORT_WIDTH, opt.viewport_width),
        name=argname.VIEWPORT_WIDTH,
        err=err,
    )

    opt.viewport_height = check_number(
        value=args.get(argname.VIEWPORT_HEIGHT, opt.viewport_height),
        name=argname.VIEWPORT_HEIGHT,
        err=err,
    )

    opt.wait_for_timeout = check_number(
        value=args.get(argname.WAIT_FOR_TIMEOUT, opt.wait_for_timeout),
        name=argname.WAIT_FOR_TIMEOUT,
        err=err,
    )

    opt.max_elems_to_parse = check_number(
        value=args.get(argname.MAX_ELEMS_TO_PARSE, opt.max_elems_to_parse),
        name=argname.MAX_ELEMS_TO_PARSE,
        err=err,
    )

    opt.nb_top_candidates = check_number(
        value=args.get(argname.NB_TOP_CANDIDATES, opt.nb_top_candidates),
        name=argname.NB_TOP_CANDIDATES,
        err=err,
    )

    opt.char_threshold = check_number(
        value=args.get(argname.CHAR_THRESHOLD, opt.char_threshold),
        name=argname.CHAR_THRESHOLD,
        err=err,
    )
    return opt, err
