import asyncio
import contextlib
import os
from pathlib import Path
from typing import TypedDict

from fastapi import FastAPI
from playwright.async_api import async_playwright, Browser, BrowserType
import settings


class State(TypedDict):
    # https://playwright.dev/python/docs/api/class-browsertype
    browser: Browser
    semaphore: asyncio.Semaphore
    basic_auth_credentials: dict[str, str] | None  # username: bcrypt hash of password


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    creds = None

    # load basic auth credentials from htpasswd file if provided
    if settings.BASIC_HTPASSWD:
        path = Path(settings.BASIC_HTPASSWD)
        if path.is_file():
            with path.open('r') as fd:
                creds = dict(line.strip().split(':', 1) for line in fd)

    # browser set up
    os.makedirs(settings.USER_SCRIPTS_DIR, exist_ok=True)
    semaphore = asyncio.Semaphore(settings.BROWSER_CONTEXT_LIMIT)

    async with async_playwright() as playwright:
        browser_type: BrowserType = getattr(playwright, settings.BROWSER_TYPE.value)
        browser = await browser_type.launch(headless=True)
        yield State(
            basic_auth_credentials=creds,
            browser=browser,
            semaphore=semaphore,
        )
