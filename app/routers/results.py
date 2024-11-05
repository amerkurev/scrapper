from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, status, Response
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from internal import cache
from settings import TEMPLATES_DIR, SCREENSHOT_TYPE
from version import revision


router = APIRouter(tags=['results'])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get('/view/{r_id}', response_class=HTMLResponse, include_in_schema=False)
async def result_html(
    request: Request,
    r_id: Annotated[str, Path(title='Result ID', description='Unique result ID')],
):
    data = cache.load_result(key=r_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Not found result with id: {r_id}'
        )

    context = {'request': request, 'data': data, 'revision': revision}
    return templates.TemplateResponse('view.html', context=context)


@router.get('/result/{r_id}', include_in_schema=False)
async def result_json(
    r_id: Annotated[str, Path(title='Result ID', description='Unique result ID')],
):
    data = cache.load_result(key=r_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Not found result with id: {r_id}'
        )
    return data


@router.get('/screenshot/{r_id}', response_class=FileResponse, include_in_schema=False)
async def result_screenshot(
    r_id: Annotated[str, Path(title='Result ID', description='Unique result ID')],
):
    screenshot = cache.load_screenshot(r_id)
    if not screenshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Not found screenshot with id: {r_id}'
        )
    return Response(content=screenshot, media_type=f'image/{SCREENSHOT_TYPE}')
