import ssl
import logging
from pathlib import Path

from fastapi import FastAPI, status
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from playwright.async_api import Error as PlaywrightError

from server.state import lifespan
from internal.logger import setup_logger
from router import site, article, links, any_page, misc, results

import settings


app = FastAPI(
    title='Scrapper',
    summary='Web scraper with a simple REST API living in Docker and using a Headless browser and Readability.js for parsing.',
    contact={
        'name': 'GitHub',
        'url': 'https://github.com/amerkurev/scrapper',
    },
    license_info={
        'name': 'MIT license',
        'url': 'https://github.com/amerkurev/scrapper/blob/master/LICENSE',
    },
    version=settings.REVISION,
    lifespan=lifespan,
)
app.mount('/static', StaticFiles(directory=settings.STATIC_DIR), name='static')

# router lists
app.include_router(site.router)
app.include_router(article.router)
app.include_router(links.router)
app.include_router(any_page.router)
app.include_router(misc.router)
app.include_router(results.router)


@app.exception_handler(PlaywrightError)
async def playwright_exception_handler(_, err):
    content = f'PlaywrightError: {err}'
    return PlainTextResponse(content, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def main():
    logger = setup_logger()
    logger.info(f'Revision: {settings.REVISION}')

    if settings.LOG_LEVEL == logging.DEBUG:
        logger.debug(settings.to_string())

    kwargs = {
        'host': settings.HOST,
        'port': settings.PORT,
        'workers': settings.WORKERS,
        'reload': settings.DEBUG,
        'log_level': settings.LOG_LEVEL,
        'access_log': settings.DEBUG,
        'server_header': False,
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None,  # TODO: add settings.SSL_CA_CERTS
        'ssl_ciphers': settings.SSL_CIPHERS,
        'proxy_headers': True,
        'forwarded_allow_ips': '*',
    }

    # enable SSL if key and cert files are provided
    if settings.SSL_KEYFILE and settings.SSL_CERTFILE:
        if Path(settings.SSL_KEYFILE).is_file() and Path(settings.SSL_CERTFILE).is_file():
            kwargs.update({
                'ssl_keyfile': settings.SSL_KEYFILE,
                'ssl_certfile': settings.SSL_CERTFILE,
            })
            if settings.SSL_KEYFILE_PASSWORD:
                kwargs['ssl_keyfile_password'] = settings.SSL_KEYFILE_PASSWORD

    import uvicorn

    uvicorn.run('main:app', **kwargs)


if __name__ == '__main__':
    main()  # pragma: no cover
