from collections.abc import MutableMapping
from urllib.parse import parse_qs

from bs4 import BeautifulSoup
from starlette.datastructures import URL


TITLE_MAX_DISTANCE = 350
ACCEPTABLE_LINK_TEXT_LEN = 40


def improve_content(title: str, content: str) -> str:
    tree = BeautifulSoup(content, 'html.parser')

    # 1. remove all p and div tags that contain one word or less (or only digits),
    # and not contain any images (or headers)
    for el in tree.find_all(['p', 'div']):
        # skip if the element has any images, headers, code blocks, lists, tables, forms, etc.
        if el.find([
            'img',
            'picture',
            'svg',
            'canvas',
            'video',
            'audio',
            'iframe',
            'embed',
            'object',
            'param',
            'source',
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'pre',
            'code',
            'blockquote',
            'dl',
            'ol',
            'ul',
            'table',
            'form',
        ]):
            continue
        text = el.get_text(strip=True)
        # remove the element if it contains one word or less (or only digits)
        words = text.split()
        if len(words) <= 1 or (''.join(words)).isnumeric():
            el.decompose()

    # 2. move the first tag h1 (or h2) to the top of the tree
    title_distance = 0

    for el in tree.find_all(string=True):
        if el.parent.name in ('h1', 'h2', 'h3'):
            text = el.parent.get_text(strip=True)
            # stop if the header is similar to the title
            min_len = min(len(text), len(title))
            # remove all non-alphabetic characters and convert to lowercase
            # noinspection PyTypeChecker
            str1 = ''.join(filter(str.isalpha, text[:min_len])).lower()
            # noinspection PyTypeChecker
            str2 = ''.join(filter(str.isalpha, title[:min_len])).lower()
            if str1 and str2 and levenshtein_similarity(str1, str2) > 0.9:
                title = text
                el.parent.decompose()  # 'real' move will be below, at 3.1 or 3.2
                break

        # stop if distance is too big
        title_distance += len(el.text)
        if title_distance > TITLE_MAX_DISTANCE:
            # will be used article['title'] as title
            break

    # 3.1 check if article tag already exists, and then insert the title into it
    for el in tree.find_all():
        if el.name == 'article':
            el.insert(0, BeautifulSoup(f'<h1>{title}</h1>', 'html.parser'))
            return str(tree)

    # 3.2 if not, create a new article tag and insert the title into it
    content = str(tree)
    return f'<article><h1>{title}</h1>{content}</article>'


def improve_link(link: MutableMapping) -> MutableMapping:
    lines = link['text'].splitlines()
    text = ''
    # find the longest line
    for line in lines:
        if len(line) > len(text):
            text = line
        # stop if the line is long enough
        if len(text) > ACCEPTABLE_LINK_TEXT_LEN:
            break

    link['text'] = text
    return link


def social_meta_tags(full_page_content: str) -> dict:
    og = {}  # open graph
    twitter = {}
    tree = BeautifulSoup(full_page_content, 'html.parser')
    for el in tree.find_all('meta'):
        attrs = el.attrs
        # open Graph protocol
        if 'property' in attrs and attrs['property'].startswith('og:'):
            key = attrs['property'][3:]  # len('og:') == 3
            if key and 'content' in attrs:
                og[key] = attrs['content']

        # twitter protocol
        if 'name' in attrs and attrs['name'].startswith('twitter:'):
            key = attrs['name'][8:]  # len('twitter:') == 8
            if key and 'content' in attrs:
                twitter[key] = attrs['content']

    res = {key: props for key, props in (('og', og), ('twitter', twitter)) if props}
    return res


def levenshtein_similarity(str1: str, str2: str) -> float:
    # create a matrix to hold the distances
    d = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]

    # initialize the first row and column of the matrix
    for i in range(len(str1) + 1):
        d[i][0] = i
    for j in range(len(str2) + 1):
        d[0][j] = j

    # fill in the rest of the matrix
    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            if str1[i - 1] == str2[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]) + 1

    # return normalized distance
    return 1 - d[-1][-1] / max(len(str1), len(str2))


def improve_text_content(text: str) -> str:
    s = '\n'.join(filter(None, map(str.strip, text.splitlines())))
    return s


def split_url(url: URL) -> tuple[str, str, dict]:
    """
    Split URL into parts. Return host_url, full_path, query_dict.
    :param url: Starlette URL object
    :return:
        host_url - just the host with scheme
        full_path - just the path with query
        query_dict - query params as a dict
    """
    # just the host with scheme
    host_url = URL(scheme=url.scheme, netloc=url.netloc)

    # just the path with query
    full_path = URL(path=url.path, query=url.query)

    # query params as a dict
    query_dict = parse_qs(qs=url.query, keep_blank_values=True)
    return host_url, full_path, query_dict
