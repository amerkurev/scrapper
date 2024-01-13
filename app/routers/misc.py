import datetime
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.requests import Request
from pydantic import BaseModel
from playwright.async_api import Browser

from version import revision


router = APIRouter(tags=['misc'])


class PingData(BaseModel):
    browserType: Annotated[str, Query(description='the browser type (chromium, firefox or webkit)')]
    browserVersion: Annotated[str, Query(description='the browser version')]
    contexts: Annotated[int, Query(description='number of active browser contexts')]
    isConnected: Annotated[bool, Query(description='indicates that the browser is connected')]
    now: Annotated[datetime.datetime, Query(description='UTC time now')]
    revision: Annotated[str, Query(description='the scrapper revision')]


@router.get('/ping', summary='Ping the Scrapper', response_model=PingData)
async def ping(request: Request) -> dict:
    """
    The ping endpoint checks if the Scrapper is running, both from Docker and externally.
    """
    browser: Browser = request.state.browser
    return {
        'browserType': browser.browser_type.name,
        'browserVersion': browser.version,
        'contexts': len(browser.contexts),
        'isConnected': browser.is_connected(),
        'now': datetime.datetime.utcnow(),
        'revision': revision,
    }
