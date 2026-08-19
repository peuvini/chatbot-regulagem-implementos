import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.mark.smoke
def test_health_endpoint_is_available():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.smoke
def test_openapi_exposes_core_routes():
    response = client.get("/openapi.json")

    paths = response.json()["paths"]
    assert "/api/chat" in paths
    assert "/api/operation-planning/calculate" in paths
    assert "/api/recommendations" in paths
