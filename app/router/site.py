from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

import settings
from server.auth import AuthRequired


router = APIRouter(tags=['common'])
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)


@router.get('/favicon.ico', response_class=FileResponse, include_in_schema=False)
async def favicon():
    return FileResponse(settings.ICON_PATH, media_type='image/vnd.microsoft.icon')


@router.get('/', response_class=HTMLResponse, include_in_schema=False)
@router.get('/links', response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request, _: AuthRequired):
    for_example = (
        'cache=yes',
        'full-content=no',
        'screenshot=no',
        'incognito=yes',
        'timeout=60000',
        'wait-until=domcontentloaded',
        'sleep=0',
        'device=Desktop Chrome',
    )
    context = {
        'request': request,
        'revision': settings.REVISION,
        'for_example': '&#10;'.join(for_example),
    }
    return templates.TemplateResponse(request=request, name='index.html', context=context)
