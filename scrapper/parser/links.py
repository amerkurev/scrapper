
# noinspection PyPackageRequirements
from playwright.sync_api import sync_playwright

from scrapper.settings import PARSER_SCRIPTS_DIR
from scrapper.parser import new_context, close_context, page_processing
from scrapper.parser import ParserError


def parse(request, args):
    with sync_playwright() as playwright:
        context = new_context(playwright, args)
        page = context.new_page()
        page_content, screenshot = page_processing(page, args=args, init_scripts=[])

        # evaluating JavaScript: parse DOM and extract links of articles
        parser_args = {}
        with open(PARSER_SCRIPTS_DIR / 'links.js') as fd:
            links = page.evaluate(fd.read() % parser_args)
        close_context(context)

    # parser error: links are not extracted, result has 'err' field
    if 'err' in links:
        raise ParserError(links)

    return {}
