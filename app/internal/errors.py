from typing import Any

from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError


class ArticleParsingError(HTTPException):
    def __init__(self, url: str, msg: str):
        obj = {
            'type': 'article_parsing',
            'loc': ('readability.js',),
            'msg': msg,
            'input': url,
        }
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=[obj])


class LinksParsingError(HTTPException):
    def __init__(self, url: str, msg: str):
        obj = {
            'type': 'links_parsing',
            'loc': ('links.js',),
            'msg': msg,
            'input': url,
        }
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=[obj])


class QueryParsingError(RequestValidationError):
    def __init__(self, field: str, msg: str, value: Any):
        obj = {
            'type': f'{field}_parsing',
            'loc': ('query', field),
            'msg': msg,
            'input': value,
        }
        super().__init__([obj])
