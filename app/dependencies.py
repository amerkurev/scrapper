import contextlib
from typing import TypedDict

from fastapi import FastAPI
from playwright.async_api import async_playwright, Browser


class State(TypedDict):
    # https://playwright.dev/python/docs/api/class-browsertype
    browser: Browser


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_playwright() as playwright:
        firefox = playwright.firefox
        browser = await firefox.launch(headless=True)
        yield {'browser': browser}
