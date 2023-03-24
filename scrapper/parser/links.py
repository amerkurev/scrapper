
import hashlib
import datetime
import tldextract

from statistics import median
from operator import itemgetter

# noinspection PyPackageRequirements
from playwright.sync_api import sync_playwright

from scrapper.cache import dump_result
from scrapper.settings import IN_DOCKER, PARSER_SCRIPTS_DIR
from scrapper.parser import new_context, close_context, page_processing
from scrapper.util import check_fields
from scrapper.parser import ParserError


def parse(request, args, _id):
    with sync_playwright() as playwright:
        context = new_context(playwright, args)
        page = context.new_page()
        page_content, screenshot = page_processing(page, args=args, init_scripts=[])

        # evaluating JavaScript: parse DOM and extract links of articles
        parser_args = {}
        with open(PARSER_SCRIPTS_DIR / 'links.js') as fd:
            links = page.evaluate(fd.read() % parser_args)

        title = page.title()
        close_context(context)

    # parser error: links are not extracted, result has 'err' field
    if 'err' in links:
        raise ParserError(links)

    # filter links by domain
    domain = tldextract.extract(args.url).domain
    links = [x for x in links if allowed_domain(x['href'], domain)]

    links_dict = group_links(links)

    # get stat for groups of links and filter groups with
    # median length of text and words more than 40 and 3
    links = []
    for key, group in links_dict.items():
        stat = get_stat(
            group,
            text_len_threshold=args.text_len_threshold,
            words_threshold=args.words_threshold,
        )
        if stat['approved']:
            links.extend(group)

    # Sort links by 'pos' field, to show links in the same order as they are on the page
    # ('pos' is position of link in DOM)
    links.sort(key=itemgetter('pos'))
    links = list(map(link_to_json, links))

    # set common fields
    newsfeed = {
        'id': _id,
        'date': datetime.datetime.utcnow().isoformat(),
        'resultUri': f'{request.host_url}result/{_id}',
        'query': request.args.to_dict(flat=True),
        'links': links,
        'title': title,
    }

    if args.full_content:
        newsfeed['fullContent'] = page_content
    if args.screenshot:
        newsfeed['screenshotUri'] = f'{request.host_url}screenshot/{_id}'

    # save result to disk
    dump_result(newsfeed, filename=_id, screenshot=screenshot)

    # self-check for development
    if not IN_DOCKER:
        check_fields(newsfeed, args=args, fields=NEWSFEED_FIELDS)
    return newsfeed


def group_links(links):
    # Group links by 'CSS selector', 'color', 'font', 'parent padding', 'parent margin' and 'parent background color' properties
    links_dict = {}
    for link in links:
        key = make_key(link)
        if key not in links_dict:
            links_dict[key] = []
        links_dict[key].append(link)
    return links_dict


def make_key(link):
    # Make key from 'CSS selector', 'color', 'font', 'parent padding', 'parent margin' and 'parent background color' properties
    props = link['cssSel'], link['color'], link['font'], link['parentPadding'], link['parentMargin'], link['parentBgColor']
    s = '|'.join(props)
    return hashlib.sha1(s.encode()).hexdigest()[:7]  # because 7 chars is enough for uniqueness


def get_stat(links, text_len_threshold, words_threshold):
    # Get stat for group of links
    median_text_len = median([len(x['text']) for x in links])
    median_words_count = median([len(x['words']) for x in links])
    approved = median_text_len > text_len_threshold and median_words_count > words_threshold
    return {
        'count': len(links),
        'median_text_len': median_text_len,
        'median_words_count': median_words_count,
        'approved': approved,
    }


def allowed_domain(href, domain):
    # Check if href is from the same domain
    if href.startswith('http'):
        # absolute link
        return tldextract.extract(href).domain == domain
    return True  # relative link


def link_to_json(link):
    return {
        'url': link['url'],
        'text': link['text'],
    }


NoneType = type(None)
NEWSFEED_FIELDS = (
    # (name, types, condition)

    # unique request ID
    ('id', str, None),
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
    # list of links
    ('links', list, None),
    # the page's title
    ('title', (NoneType, str), None),
)
