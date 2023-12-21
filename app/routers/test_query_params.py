from fastapi.testclient import TestClient

from main import app


def test_various_query_params():
    api_url = '/api/article'

    with TestClient(app) as client:
        # test stealth mode and page scroll down
        url = 'https://en.wikipedia.org/wiki/Web_scraping'
        params = {
            'url': url,
            'full-content': True,
            'stealth': True,
            'cache': False,
            'sleep': 1000,  # 1 second
            'scroll-down': 500,  # 500 pixels
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # test persistent context (incognito=no)
        url = 'https://en.wikipedia.org/wiki/Data_scraping'
        params = {
            'url': url,
            'incognito': False,
            'resource': 'document,stylesheet,fetch',
            'cache': False,
            'extra-http-headers': 'Accept-Language:da, en-gb, en',
            'user-scripts-timeout': 1000,  # 1 second
            'http-credentials': 'username:password',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # test proxy params
        params = {
            'url': url,
            'user-scripts-timeout': 1000,  # 1 second
            'http-credentials': 'username',
            'proxy_server': 'http://myproxyserver.com',
            'proxy_username': 'user',
            'proxy_password': 'pass',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 200

        # test user scripts
        params = {
            'url': url,
            'user-scripts': 'jquery-3.5.1.min.js,my-script.js',
        }
        response = client.get(api_url, params=params)
        assert response.status_code == 422
        assert response.json() == {
            'detail': [{
                'input': 'jquery-3.5.1.min.js',
                'loc': ['query', 'user_scripts'],
                'msg': 'User script not found',
                'type': 'user_scripts_parsing',
            }]
        }
