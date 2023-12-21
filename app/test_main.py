from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_get_favicon():
    response = client.get('/favicon.ico')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/vnd.microsoft.icon'
