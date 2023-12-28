from fastapi.testclient import TestClient

from main import app


def test_ping():
    with TestClient(app) as client:
        response = client.get('/ping')
        assert response.status_code == 200


def test_docs():
    with TestClient(app) as client:
        response = client.get('/docs')
        assert response.status_code == 200
