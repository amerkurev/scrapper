from fastapi.testclient import TestClient

from main import app
from settings import USER_SCRIPTS_DIR


def test_various_query_params():
    api_url = '/api/article'

    with TestClient(app) as client:
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
            'detail': [
                {
                    'input': ['Accept-Language'],
                    'loc': ['query', 'extra_http_headers'],
                    'msg': 'Invalid HTTP header',
                    'type': 'extra_http_headers_parsing',
                }
            ]
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
        assert 'PlaywrightError: Page.goto: net::ERR_TUNNEL_CONNECTION_FAILED at ' in response.text

        # test user scripts
        with open(USER_SCRIPTS_DIR / 'my-script.js', mode='w', encoding='utf-8') as f:
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
            'detail': [
                {
                    'input': 'not-exists.js',
                    'loc': ['query', 'user_scripts'],
                    'msg': 'User script not found',
                    'type': 'user_scripts_parsing',
                }
            ]
        }

        # test huge page with taking screenshot
        params = {
            'url': 'https://en.wikipedia.org/wiki/African_humid_period',
            'cache': False,
            'screenshot': True,
            'device': 'Desktop Firefox',  # to raise (Page.screenshot): Cannot take screenshot larger than 32767
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # test viewport and screen settings
        url = 'https://en.wikipedia.org/wiki/World_Wide_Web'
        params = {
            'url': url,
            'cache': False,
            'viewport-width': 390,
            'viewport-height': 844,
            'screen-width': 1170,
            'screen-height': 2532,
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) ',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # test wrong device name
        params = {
            'url': url,
            'device': 'not-exists',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 422
        assert response.json() == {
            'detail': [
                {
                    'input': 'not-exists',
                    'loc': ['query', 'device'],
                    'msg': 'Device not found',
                    'type': 'device_parsing',
                }
            ]
        }
