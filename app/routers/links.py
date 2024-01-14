import asyncio
import datetime
import hashlib

from collections import defaultdict
from operator import itemgetter
from statistics import median

from typing import Annotated, Mapping, Sequence

import tldextract

from fastapi import APIRouter, Query, Depends
from fastapi.requests import Request
from pydantic import BaseModel
from playwright.async_api import Browser

from settings import PARSER_SCRIPTS_DIR
from internal import cache
from internal.browser import (
    new_context,
    page_processing,
    get_screenshot,
)
from internal.util import htmlutil, split_url
from internal.errors import LinksParsingError
from .query_params import (
    URLParam,
    CommonQueryParams,
    BrowserQueryParams,
    ProxyQueryParams,
    LinkParserQueryParams,
)


router = APIRouter(prefix='/api/links', tags=['links'])


class Links(BaseModel):
    id: Annotated[str, Query(description='unique result ID')]
    url: Annotated[str, Query(description='page URL after redirects, may not match the query URL')]
    domain: Annotated[str, Query(description="page's registered domain")]
    date: Annotated[str, Query(description='date of extracted article in ISO 8601 format')]
    query: Annotated[dict, Query(description='request parameters')]
    meta: Annotated[dict, Query(description='social meta tags (open graph, twitter)')]
    resultUri: Annotated[str, Query(description='URL of the current result, the data here is always taken from cache')]
    fullContent: Annotated[str | None, Query(description='full HTML contents of the page')] = None
    screenshotUri: Annotated[str | None, Query(description='URL of the screenshot of the page')] = None
    title: Annotated[str | None, Query(description="page's title")] = None
    links: Annotated[list[dict], Query(description='list of links')]


@router.get('', summary='Parse news links from the given URL', response_model=Links)
async def parser_links(
    request: Request,
    url: Annotated[URLParam, Depends()],
    common_params: Annotated[CommonQueryParams, Depends()],
    browser_params: Annotated[BrowserQueryParams, Depends()],
    proxy_params: Annotated[ProxyQueryParams, Depends()],
    link_parser_params: Annotated[LinkParserQueryParams, Depends()],
) -> dict:
    """
    Parse news links from the given URL.<br><br>
    The page from the URL should contain hyperlinks to news articles. For example, this could be the main page of a website.
    """
    # split URL into parts: host with scheme, path with query, query params as a dict
    host_url, full_path, query_dict = split_url(request.url)

    # get cache data if exists
    r_id = cache.make_key(full_path)  # unique result ID
    if common_params.cache:
        data = cache.load_result(key=r_id)
        if data:
            return data

    browser: Browser = request.state.browser
    semaphore: asyncio.Semaphore = request.state.semaphore

    # create a new browser context
    async with semaphore:
        async with new_context(browser, browser_params, proxy_params) as context:
            page = await context.new_page()
            await page_processing(
                page=page,
                url=url.url,
                params=common_params,
                browser_params=browser_params,
            )
            page_content = await page.content()
            screenshot = await get_screenshot(page) if common_params.screenshot else None
            page_url = page.url
            title = await page.title()

            # evaluating JavaScript: parse DOM and extract links of articles
            parser_args = {}
            with open(PARSER_SCRIPTS_DIR / 'links.js', encoding='utf-8') as f:
                links = await page.evaluate(f.read() % parser_args)

    # parser error: links are not extracted, result has 'err' field
    if 'err' in links:
        raise LinksParsingError(page_url, links['err'])  # pragma: no cover

    # filter links by domain
    domain = tldextract.extract(url.url).domain
    links = [x for x in links if allowed_domain(x['href'], domain)]

    links_dict = group_links(links)

    # get stat for groups of links and filter groups with
    # median length of text and words more than 40 and 3
    links = []
    for _, group in links_dict.items():
        stat = get_stat(
            group,
            text_len_threshold=link_parser_params.text_len_threshold,
            words_threshold=link_parser_params.words_threshold,
        )
        if stat['approved']:
            links.extend(group)

    # sort links by 'pos' field, to show links in the same order as they are on the page
    # ('pos' is position of link in DOM)
    links.sort(key=itemgetter('pos'))
    links = list(map(htmlutil.improve_link, map(link_fields, links)))

    # set common fields
    r = {
        'id': r_id,
        'url': page_url,
        'domain': tldextract.extract(page_url).registered_domain,
        'date': datetime.datetime.utcnow().isoformat(),  # ISO 8601 format
        'resultUri': f'{host_url}/result/{r_id}',
        'query': query_dict,
        'links': links,
        'title': title,
        'meta': htmlutil.social_meta_tags(page_content),
    }

    if common_params.full_content:
        r['fullContent'] = page_content
    if common_params.screenshot:
        r['screenshotUri'] = f'{host_url}/screenshot/{r_id}'

    # save result to disk
    cache.dump_result(r, key=r_id, screenshot=screenshot)
    return r


def allowed_domain(href: str, domain: str) -> bool:
    # check if the link is from the same domain
    if href.startswith('http'):
        # absolute link
        return tldextract.extract(href).domain == domain
    return True  # relative link


def group_links(links: Sequence[Mapping]) -> dict:
    # group links by 'CSS selector', 'color', 'font', 'parent padding', 'parent margin' and 'parent background color' properties
    links_dict = defaultdict(list)
    for link in links:
        links_dict[make_key(link)].append(link)
    return links_dict


def make_key(link: Mapping) -> str:
    # make key from 'CSS selector', 'color', 'font', 'parent padding', 'parent margin' and 'parent background color' properties
    props = link['cssSel'], link['color'], link['font'], link['parentPadding'], link['parentMargin'], link['parentBgColor']
    s = '|'.join(props)
    return hashlib.sha1(s.encode()).hexdigest()[:7]  # because 7 chars is enough for uniqueness


def get_stat(links: Sequence[Mapping], text_len_threshold: int, words_threshold: int) -> dict:
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


def link_fields(link: Mapping) -> dict:
    return {
        'url': link['url'],
        'text': link['text'],
    }
