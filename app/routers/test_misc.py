from fastapi.testclient import TestClient

from main import app


def test_ping():
    """
    For Docker healthcheck
    """
    with TestClient(app) as client:
        response = client.get('/ping')
        assert response.status_code == 200
