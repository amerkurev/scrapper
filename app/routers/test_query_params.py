from fastapi.testclient import TestClient

from main import app
from settings import USER_SCRIPTS_DIR


def test_various_query_params():
    api_url = '/api/article'

    with TestClient(app) as client:
        # test stealth mode and page scroll down
        url = 'https://en.wikipedia.org/wiki/Web_scraping'
        params = {
            'url': url,
            'cache': False,
            'full-content': True,
            'stealth': True,
            'sleep': 1000,  # 1 second
            'scroll-down': 500,  # 500 pixels
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # test persistent context (incognito=no)
        url = 'https://en.wikipedia.org/wiki/Data_scraping'
        params = {
            'url': url,
            'cache': False,
            'incognito': False,
            'resource': 'document,stylesheet,fetch',
            'extra-http-headers': [
                'Accept-Language:da, en-gb, en',
                'Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3;',
                'Accept: text/html;q=0.9,text/plain',
            ],
            'user-scripts-timeout': 1000,  # 1 second
            'http-credentials': 'username:password',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # wrong http header
        params = {
            'url': url,
            'extra-http-headers': 'Accept-Language',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 422
        assert response.json() == {
            'detail': [{
                'input': ['Accept-Language'],
                'loc': ['query', 'extra_http_headers'],
                'msg': 'Invalid HTTP header',
                'type': 'extra_http_headers_parsing',
            }]
        }

        # test fake proxy
        params = {
            'url': url,
            'user-scripts-timeout': 1000,  # 1 second
            'http-credentials': 'username',
            'proxy-server': 'http://myproxyserver.com',
            'proxy-username': 'user',
            'proxy-password': 'pass',
            'proxy-bypass': 'localhost',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 500
        assert response.text == 'PlaywrightError: NS_ERROR_UNKNOWN_PROXY_HOST'

        # test user scripts
        with open(USER_SCRIPTS_DIR / 'my-script.js', 'w') as f:
            f.write('console.log("Hello world!");')

        url = 'https://en.wikipedia.org/wiki/World_Wide_Web'
        params = {
            'url': url,
            'cache': False,
            'user-scripts': 'my-script.js',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # test user script that not exists
        params = {
            'url': url,
            'user-scripts': 'not-exists.js',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 422
        assert response.json() == {
            'detail': [{
                'input': 'not-exists.js',
                'loc': ['query', 'user_scripts'],
                'msg': 'User script not found',
                'type': 'user_scripts_parsing',
            }]
        }

        # test huge page with taking screenshot
        params = {
            'url': 'https://en.wikipedia.org/wiki/African_humid_period',
            'cache': False,
            'screenshot': True,
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200
