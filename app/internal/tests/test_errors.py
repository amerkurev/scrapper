from fastapi.exceptions import HTTPException, RequestValidationError

from internal.errors import ArticleParsingError, LinksParsingError, QueryParsingError


def test_errors():
    page_url = 'https://example.com'
    msg = "The page doesn't contain any articles."
    err = ArticleParsingError(page_url, msg)
    assert isinstance(err, HTTPException)
    assert err.status_code == 400
    assert err.detail == [
        {
            'type': 'article_parsing',
            'loc': ('readability.js',),
            'msg': "The page doesn't contain any articles.",
            'input': page_url,
        }
    ]

    msg = "The page doesn't contain any links."
    err = LinksParsingError(page_url, msg)
    assert isinstance(err, HTTPException)
    assert err.status_code == 400
    assert err.detail == [
        {
            'type': 'links_parsing',
            'loc': ('links.js',),
            'msg': "The page doesn't contain any links.",
            'input': page_url,
        }
    ]

    field = 'url'
    msg = 'Invalid URL'
    value = 'example.com'
    err = QueryParsingError(field, msg, value)
    assert isinstance(err, RequestValidationError)
    assert err.errors() == [
        {
            'type': f'{field}_parsing',
            'loc': ('query', field),
            'msg': msg,
            'input': value,
        }
    ]

    field = 'http_credentials'
    msg = 'Invalid HTTP credentials'
    value = {'username': 'user', 'password': 'pass'}
    err = QueryParsingError(field, msg, value)
    assert isinstance(err, RequestValidationError)
    assert err.errors() == [
        {
            'type': f'{field}_parsing',
            'loc': ('query', field),
            'msg': msg,
            'input': value,
        }
    ]
