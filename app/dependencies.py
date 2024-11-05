import asyncio
import contextlib
# import os
from typing import TypedDict

from fastapi import FastAPI
from playwright.async_api import async_playwright, Browser

# from settings import USER_SCRIPTS_DIR, BROWSER_CONTEXT_LIMIT
from settings import BROWSER_CONTEXT_LIMIT

class State(TypedDict):
    # https://playwright.dev/python/docs/api/class-browsertype
    browser: Browser
    semaphore: asyncio.Semaphore


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    # os.makedirs(USER_SCRIPTS_DIR, exist_ok=True)
    semaphore = asyncio.Semaphore(BROWSER_CONTEXT_LIMIT)

    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch(headless=True)
        yield State(browser=browser, semaphore=semaphore)
