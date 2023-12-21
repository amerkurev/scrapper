from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_get_favicon():
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/vnd.microsoft.icon'


def test_index_html():
    response = client.get('/')
    assert response.status_code == 200
    assert 'https://example.com/article.html' in response.text
    assert 'apiEndpoint = "/api/article"' in response.text

    response = client.get('/links')
    assert response.status_code == 200
    assert 'https://example.com/news.html' in response.text
    assert 'apiEndpoint = "/api/links"' in response.text
