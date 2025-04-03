import asyncio
import datetime
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.requests import Request
from pydantic import BaseModel
from playwright.async_api import Browser

from settings import REVISION, BROWSER_CONTEXT_LIMIT


router = APIRouter(tags=['misc'])


class PingData(BaseModel):
    browserType: Annotated[str, Query(description='the browser type (chromium, firefox or webkit)')]
    browserVersion: Annotated[str, Query(description='the browser version')]
    browserContextLimit: Annotated[int, Query(description='the maximum number of browser contexts (aka tabs)')]
    browserContextUsed: Annotated[int, Query(description='the number of all open browser contexts')]
    availableSlots: Annotated[int, Query(description='the number of available browser contexts')]
    isConnected: Annotated[bool, Query(description='indicates that the browser is connected')]
    now: Annotated[datetime.datetime, Query(description='UTC time now')]
    revision: Annotated[str, Query(description='the scrapper revision')]


@router.get('/ping', summary='Ping the Scrapper', response_model=PingData)
async def ping(request: Request) -> dict:
    """
    The ping endpoint checks if the Scrapper is running, both from Docker and externally.
    """
    browser: Browser = request.state.browser
    semaphore: asyncio.Semaphore = request.state.semaphore

    now = datetime.datetime.now(datetime.timezone.utc)

    return {
        'browserType': browser.browser_type.name,
        'browserVersion': browser.version,
        'browserContextLimit': BROWSER_CONTEXT_LIMIT,
        'browserContextUsed': len(browser.contexts),
        'availableSlots': semaphore._value,
        'isConnected': browser.is_connected(),
        'now': now,
        'revision': REVISION,
    }
