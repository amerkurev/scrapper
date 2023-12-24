import contextlib
import os
from typing import TypedDict

from fastapi import FastAPI
from playwright.async_api import async_playwright, Browser

from settings import USER_SCRIPTS


class State(TypedDict):
    # https://playwright.dev/python/docs/api/class-browsertype
    browser: Browser


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(USER_SCRIPTS, exist_ok=True)
    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch(headless=True)
        yield {'browser': browser}
