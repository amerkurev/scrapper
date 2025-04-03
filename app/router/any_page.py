import asyncio
import datetime
from typing import Annotated

import tldextract

from fastapi import APIRouter, Query, Depends
from fastapi.requests import Request
from pydantic import BaseModel
from playwright.async_api import Browser

from internal import util, cache
from internal.browser import (
    new_context,
    page_processing,
    get_screenshot,
)
from .query_params import (
    URLParam,
    CommonQueryParams,
    BrowserQueryParams,
    ProxyQueryParams,
)
from server.auth import AuthRequired


router = APIRouter(prefix='/api/page', tags=['page'])


class AnyPage(BaseModel):
    id: Annotated[str, Query(description='unique result ID')]
    url: Annotated[str, Query(description='page URL after redirects, may not match the query URL')]
    domain: Annotated[str, Query(description="page's registered domain")]
    date: Annotated[str, Query(description='date of fetched page in ISO 8601 format')]
    query: Annotated[dict, Query(description='request parameters')]
    meta: Annotated[dict, Query(description='social meta tags (open graph, twitter)')]
    resultUri: Annotated[str, Query(description='URL of the current result, the data here is always taken from cache')]
    fullContent: Annotated[str | None, Query(description='full HTML contents of the page')] = None
    screenshotUri: Annotated[str | None, Query(description='URL of the screenshot of the page')] = None
    title: Annotated[str | None, Query(description='page title')] = None


@router.get('', summary='Get any page from the given URL', response_model=AnyPage)
async def get_any_page(
    request: Request,
    url: Annotated[URLParam, Depends()],
    params: Annotated[CommonQueryParams, Depends()],
    browser_params: Annotated[BrowserQueryParams, Depends()],
    proxy_params: Annotated[ProxyQueryParams, Depends()],
    _: AuthRequired,
) -> dict:
    """
    Get any page from the given URL.<br><br>
    Page is fetched using Playwright, but no additional processing is done.
    """
    # split URL into parts: host with scheme, path with query, query params as a dict
    host_url, full_path, query_dict = util.split_url(request.url)

    # get cache data if exists
    r_id = cache.make_key(full_path)  # unique result ID
    if params.cache:
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
                params=params,
                browser_params=browser_params,
            )
            page_content = await page.content()
            screenshot = await get_screenshot(page) if params.screenshot else None
            page_url = page.url
            title = await page.title()

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()  # ISO 8601 format
    domain = tldextract.extract(page_url).registered_domain

    r = {
        'id': r_id,
        'url': page_url,
        'domain': domain,
        'date': now,
        'resultUri': f'{host_url}/result/{r_id}',
        'query': query_dict,
        'title': title,
        'meta': util.social_meta_tags(page_content),
    }

    if params.full_content:
        r['fullContent'] = page_content
    if params.screenshot:
        r['screenshotUri'] = f'{host_url}/screenshot/{r_id}'

    # save result to disk
    cache.dump_result(r, key=r_id, screenshot=screenshot)
    return r
