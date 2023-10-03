# noinspection PyPackageRequirements
from playwright.sync_api import sync_playwright, Error

from scrapper.core import (
    new_context,
    close_context,
    page_processing,
)
from scrapper.settings import PARSER_SCRIPTS_DIR


def scrape(request, args, _id):
    with sync_playwright() as playwright:
        context = new_context(playwright, args)
        page = context.new_page()

        page_content = ""
        try:
            setattr(args, "wait_until", "networkidle")
            setattr(args, "url", "view-source:" + args.url)
            page_processing(page, args=args)
            with open(PARSER_SCRIPTS_DIR / 'raw.js') as fd:
                page_content = page.evaluate(fd.read())
        except Error as error:
            print(error)

        close_context(context)

    return page_content
