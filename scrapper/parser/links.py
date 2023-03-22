
import hashlib
import tldextract
import unicodedata

from statistics import median
from operator import itemgetter

# noinspection PyPackageRequirements
from playwright.sync_api import sync_playwright

from scrapper.settings import PARSER_SCRIPTS_DIR
from scrapper.parser import new_context, close_context, page_processing
from scrapper.parser import ParserError


def parse(request, args):
    with sync_playwright() as playwright:
        context = new_context(playwright, args)
        page = context.new_page()
        page_processing(page, args=args, init_scripts=[])

        # evaluating JavaScript: parse DOM and extract links of articles
        parser_args = {}
        with open(PARSER_SCRIPTS_DIR / 'links.js') as fd:
            links = page.evaluate(fd.read() % parser_args)
        close_context(context)

    # parser error: links are not extracted, result has 'err' field
    if 'err' in links:
        raise ParserError(links)

    # filter links by domain
    domain = tldextract.extract(args.url).domain
    links = [x for x in links if allowed_domain(x['href'], domain)]

    # split text of link to words
    for link in links:
        # remove newlines from text
        link['text'] = unicodedata.normalize('NFKD', link['text'])  # remove \xa0
        s = ' '.join(link['text'].splitlines())
        link['words'] = list(filter(None, s.split()))

    # transform links to dict where key is 'cssSel' field and value is list of links for this selector
    links_dict = {}
    for link in links:
        key = make_key(link)
        if key not in links_dict:
            links_dict[key] = []
        links_dict[key].append(link)

    # get stat for groups of links and filter groups with median length of text and words more than 40 and 3
    filtered_links = []
    stats = {}
    for key, group in links_dict.items():
        stat = get_stat(group)
        stats[key] = stat
        if stat['text']['median_len'] > 40 and stat['words']['median_len'] > 3:
            filtered_links.extend(links_dict[key])

    import pprint
    pprint.pprint(links)

    # sort filtered links by 'pos' field. pos is position of link in DOM
    filtered_links.sort(key=itemgetter('pos'))
    return [x['text'] for x in filtered_links]


def make_key(link):
    # Make key from 'CSS selector', 'color', 'font', 'parent padding', 'parent margin' and 'parent background color' properties
    props = link['cssSel'], link['color'], link['font'], link['parentPadding'], link['parentMargin'], link['parentBgColor']
    s = '|'.join(props)
    return hashlib.sha1(s.encode()).hexdigest()[:7]  # because 7 chars is enough for uniqueness


def get_stat(links):
    # Get stat for group of links
    return {
        'count': len(links),
        'text': {
            'median_len': median([len(x['text']) for x in links]),
        },
        'words': {
            'median_len': median([len(x['words']) for x in links]),
        },
        'sample': links[0]['text'],
    }


def allowed_domain(href, domain):
    # Check if href is from the same domain
    if href.startswith('http'):
        # absolute link
        return tldextract.extract(href).domain == domain
    return True  # relative link
