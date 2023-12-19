from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dependencies import lifespan
from settings import TEMPLATES_DIR, STATIC_DIR, ICON_PATH
from routers import article, links, results


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')
app.include_router(article.router)
app.include_router(links.router)
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
        'timeout=30000',
        'wait-until=domcontentloaded',
        'sleep=0',
        'viewport-width=414',
        'viewport-height=896',
    )
    context = {
        'request': request,
        'for_example': '&#10;'.join(for_example),
    }
    return templates.TemplateResponse('index.html', context=context)
