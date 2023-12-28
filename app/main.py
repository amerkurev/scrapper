from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from playwright.async_api import Error as PlaywrightError

from dependencies import lifespan
from settings import TEMPLATES_DIR, STATIC_DIR, ICON_PATH
from routers import article, links, misc, results
from version import revision

# at startup
print('revision:', revision)


app = FastAPI(
    title='Scrapper',
    summary='Web scraper with a simple REST API living in Docker and using a Headless browser and Readability.js for parsing.',
    contact={
        'name': 'GitHub',
        'url': 'https://github.com/amerkurev/scrapper',
    },
    license_info={
        'name': 'Apache-2.0 license',
        'url': 'https://github.com/amerkurev/scrapper/blob/master/LICENSE',
    },
    description=f'revision: {revision}',
    lifespan=lifespan,
)
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')
app.include_router(article.router)
app.include_router(links.router)
app.include_router(misc.router)
app.include_router(results.router)
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get('/favicon.ico', response_class=FileResponse, include_in_schema=False)
async def favicon():
    return FileResponse(ICON_PATH, media_type='image/vnd.microsoft.icon')


@app.get('/', response_class=HTMLResponse, include_in_schema=False)
@app.get('/links', response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    for_example = (
        'cache=yes',
        'full-content=no',
        'stealth=no',
        'screenshot=no',
        'incognito=yes',
        'timeout=60000',
        'wait-until=domcontentloaded',
        'sleep=0',
        'viewport-width=414',
        'viewport-height=896',
    )
    context = {
        'request': request,
        'revision': revision,
        'for_example': '&#10;'.join(for_example),
    }
    return templates.TemplateResponse('index.html', context=context)


@app.exception_handler(PlaywrightError)
async def playwright_exception_handler(_, err):
    content = f'PlaywrightError: {err}'
    return PlainTextResponse(content, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
