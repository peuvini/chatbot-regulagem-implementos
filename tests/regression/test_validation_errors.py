from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user


@pytest.fixture
def client():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1, role="user", is_active=True)
    app.dependency_overrides[get_db] = lambda: SimpleNamespace()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.mark.regression
def test_invalid_period_returns_typed_user_friendly_error(client):
    response = client.post(
        "/api/operation-planning/calculate",
        json={
            "area_ha": 20,
            "start_date": "2026-08-19",
            "end_date": "2026-08-18",
            "hours_per_day": 8,
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "VALIDATION_ERROR",
        "message": "Data final: A data final deve ser posterior à data inicial.",
        "fields": [
            {
                "field": "end_date",
                "message": "A data final deve ser posterior à data inicial.",
                "type": "value_error",
            }
        ],
    }


@pytest.mark.regression
def test_missing_fields_do_not_expose_raw_pydantic_messages(client):
    response = client.post("/api/operation-planning/calculate", json={})

    body = response.json()
    assert response.status_code == 422
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == "Revise os campos destacados e tente novamente."
    assert all("Value error" not in item["message"] for item in body["fields"])
