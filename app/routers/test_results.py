from fastapi.testclient import TestClient

from main import app


def test_get_article():
    api_url = '/api/article'
    url = 'https://en.wikipedia.org/wiki/Web_crawler'
    _get_result(api_url, url)


def test_get_links():
    api_url = '/api/links'
    url = 'https://en.wikinews.org/wiki/Main_Page'
    _get_result(api_url, url)


def _get_result(api_url: str, url: str):
    with TestClient(app) as client:
        # empty url
        response = client.get(api_url)
        assert response.status_code == 422
        assert response.json() == {
            'detail': [{
                'input': None,
                'loc': ['query', 'url'],
                'msg': 'Field required',
                'type': 'missing',
                'url': 'https://errors.pydantic.dev/2.5/v/missing'
            }]
        }

        # invalid url
        response = client.get(f'{api_url}?url=//example.com')
        assert response.status_code == 422
        assert response.json() == {
            'detail': [{
                'input': '//example.com',
                'loc': ['query', 'url'],
                'msg': 'Invalid URL',
                'type': 'url_parsing',
            }]
        }

        # at this time cache is empty, and data is fetched from the web
        params = {'url': url, 'cache': True, 'full-content': True, 'screenshot': True}
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # but now cache is not empty, and data is fetched from the cache
        response = client.get(api_url, params=params)
        assert response.status_code == 200
        data = response.json()

        # get the screenshot
        response = client.get(data['screenshotUri'])
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/jpeg'

        # get result from cache
        response = client.get(data['resultUri'])
        assert response.status_code == 200
        assert response.json() == data

        # get html result view
        response = client.get(f'/view/{data["id"]}')
        assert response.status_code == 200
        assert '<!doctype html>' in response.text

        # not found error
        response = client.get('/screenshot/0000')
        assert response.status_code == 404

        response = client.get('/result/0000')
        assert response.status_code == 404

        response = client.get('/view/0000')
        assert response.status_code == 404
