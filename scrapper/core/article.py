
import datetime
import tldextract

# noinspection PyPackageRequirements
from playwright.sync_api import sync_playwright

from scrapper.cache import dump_result
from scrapper.settings import IN_DOCKER, READABILITY_SCRIPT, PARSER_SCRIPTS_DIR
from scrapper.core import (
    new_context,
    close_context,
    page_processing,
    get_screenshot,
    ParserError,
    check_fields,
)


def scrape(request, args, _id):
    with sync_playwright() as playwright:
        context = new_context(playwright, args)
        page = context.new_page()
        page_processing(page, args=args, init_scripts=[READABILITY_SCRIPT])
        page_content = page.content()
        screenshot = get_screenshot(page) if args.screenshot else None
        url = page.url

        # evaluating JavaScript: parse DOM and extract article content
        parser_args = {
            # Readability options:
            'maxElemsToParse': args.max_elems_to_parse,
            'nbTopCandidates': args.nb_top_candidates,
            'charThreshold': args.char_threshold,
        }
        with open(PARSER_SCRIPTS_DIR / 'article.js') as fd:
            article = page.evaluate(fd.read() % parser_args)
        close_context(context)

    if article is None:
        raise ParserError({'err': ["The page doesn't contain any articles."]})

    # parser error: article is not extracted, result has 'err' field
    if 'err' in article:
        raise ParserError(article)

    # set common fields
    article['id'] = _id
    article['url'] = url
    article['date'] = datetime.datetime.utcnow().isoformat()  # ISO 8601 format
    article['resultUri'] = f'{request.host_url}result/{_id}'
    article['query'] = request.args.to_dict(flat=True)

    if args.full_content:
        article['fullContent'] = page_content
    if args.screenshot:
        article['screenshotUri'] = f'{request.host_url}screenshot/{_id}'

    if article['siteName'] is None:
        # extract site name from the URL if it's not set by the parser
        article['siteName'] = tldextract.extract(url).registered_domain

    # save result to disk
    dump_result(article, filename=_id, screenshot=screenshot)

    # self-check for development
    if not IN_DOCKER:
        check_fields(article, args=args, fields=ARTICLE_FIELDS)
    return article


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
    # unique request ID
    ('id', str, None),
    # page URL after redirects, may not match the query URL
    ('url', str, None),
    # content language
    ('lang', (NoneType, str), None),
    # length of an article, in characters
    ('length', (NoneType, int), None),
    # date of extracted article in ISO 8601 format
    ('date', str, None),
    # request parameters
    ('query', dict, None),
    # URL of the current result, the data here is always taken from cache
    ('resultUri', str, None),
    # full HTML contents of the page
    ('fullContent', str, lambda args: args.full_content),
    # URL of the screenshot of the page
    ('screenshotUri', str, lambda args: args.screenshot),
    # name of the site
    ('siteName', (NoneType, str), None),
    # text content of the article, with all the HTML tags removed
    ('textContent', (NoneType, str), None),
    # article title
    ('title', (NoneType, str), None),
)
