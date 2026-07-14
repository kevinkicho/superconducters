import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from superconductors.api import create_app
from superconductors.config import Settings


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    data = tmp_path / "data"
    data.mkdir()
    (data / "superconductor_database.json").write_text(
        json.dumps(
            [
                {"name": "H3S", "Tc": 203, "pressure": 155, "source": "literature"},
                {"name": "MgB2", "Tc": 39, "pressure": 0, "source": "literature"},
                {
                    "name": "Lu-N-H",
                    "Tc": 294,
                    "pressure": 1,
                    "source": "literature",
                    "doi": "10.1038/s41586-023-05742-0",
                },
            ]
        ),
        encoding="utf-8",
    )
    return Settings(
        data_dir=data,
        output_dir=tmp_path / "state",
        api_key="test-key",
        admin_username="admin",
        admin_password="secret",
    )


@pytest.fixture
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings))


@pytest.fixture
def headers() -> dict[str, str]:
    return {"X-API-Key": "test-key"}


def test_candidates_have_stable_ids_and_tc_alias(client, headers):
    first = client.get("/candidates", headers=headers)
    second = client.get("/candidates", headers=headers)

    assert first.status_code == 200
    assert first.json() == second.json()
    assert first.json()[0]["tc"] == first.json()[0]["temperature"]
    assert first.json()[0]["evidence_type"] == "unclassified"
    assert len(first.json()[0]["id"]) == 36
    assert all(candidate["formula"] != "Lu-N-H" for candidate in first.json())
    quarantined = client.get("/candidates?include_quarantined=true", headers=headers).json()
    assert any(candidate["verification_status"] == "retracted" for candidate in quarantined)


def test_candidate_filters_validate_range(client, headers):
    response = client.get("/candidates?min_tc=100&max_tc=300", headers=headers)
    assert [candidate["formula"] for candidate in response.json()] == ["H3S"]
    assert client.get("/candidates?min_tc=300&max_tc=100", headers=headers).status_code == 422
    paged = client.get("/candidates?offset=1&limit=1", headers=headers)
    assert [candidate["formula"] for candidate in paged.json()] == ["MgB2"]
    assert client.get("/candidates?limit=501", headers=headers).status_code == 422


def test_created_candidate_persists_across_app_recreation(settings, headers):
    first_client = TestClient(create_app(settings))
    created = first_client.post(
        "/candidates",
        json={"formula": "LaH10", "tc": 250, "pressure": 170},
        headers=headers,
    )
    assert created.status_code == 201
    candidate_id = created.json()["id"]

    second_client = TestClient(create_app(settings))
    records = second_client.get("/candidates", headers=headers).json()
    assert any(record["id"] == candidate_id for record in records)


def test_candidate_validation_and_duplicate_detection(client, headers):
    assert (
        client.post("/candidates", json={"formula": "not valid!"}, headers=headers).status_code
        == 422
    )
    payload = {"formula": "LaH10", "temperature": 250, "pressure": 170}
    assert client.post("/candidates", json=payload, headers=headers).status_code == 201
    assert client.post("/candidates", json=payload, headers=headers).status_code == 409


def test_submission_is_persistent_and_accepts_typed_params(settings, headers):
    client = TestClient(create_app(settings))
    candidate_id = client.get("/candidates", headers=headers).json()[0]["id"]
    response = client.post(
        "/submit",
        json={
            "candidate_id": candidate_id,
            "synthesis_params": {"pressure_gpa": 155, "temperature_k": 300},
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["candidate_id"] == candidate_id
    assert response.json()["id"] == 1
    assert response.json()["created_at"]

    recreated = TestClient(create_app(settings))
    stored = recreated.get("/submissions", headers=headers)
    assert stored.status_code == 200
    assert stored.json()[0]["candidate_id"] == candidate_id
    next_response = recreated.post("/submit", json={"candidate_id": candidate_id}, headers=headers)
    assert next_response.json()["id"] == 2
    assert recreated.get("/submissions?limit=501", headers=headers).status_code == 422


def test_legacy_numeric_submission_id_remains_supported(client, headers):
    assert client.post("/submit", json={"candidate_id": 1}, headers=headers).status_code == 200
    assert client.post("/submit", json={"candidate_id": "bad"}, headers=headers).status_code == 422
    assert (
        client.post(
            "/submit",
            json={"candidate_id": 1, "synthesis_params": {"unexpected": 1}},
            headers=headers,
        ).status_code
        == 422
    )


def test_prediction_errors_are_not_reported_as_zero_kelvin(client, headers):
    response = client.get("/predict-tc?compound=not-a-formula!", headers=headers)
    assert response.status_code == 422
    assert client.get("/predict-tc?compound=H3S", headers=headers).status_code == 200

    batch = client.post("/batch_predict", json={"formulas": ["H3S", "LaH10"]}, headers=headers)
    assert batch.status_code == 200
    assert len(batch.json()["predictions"]) == 2
    assert client.post("/batch_predict", json={"formulas": []}, headers=headers).json() == {
        "predictions": []
    }


def test_batch_size_is_limited(client, headers):
    response = client.post("/batch_predict", json={"formulas": ["H3S"] * 101}, headers=headers)
    assert response.status_code == 422


def test_login_uses_body_and_returns_expiring_token(client):
    schema = client.get("/openapi.json").json()["paths"]["/login"]["post"]
    assert "requestBody" in schema
    assert not schema.get("parameters")

    response = client.post("/login", json={"username": "admin", "password": "secret"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert "api_key" not in response.json()
    assert client.get("/candidates", headers={"X-API-Key": token}).status_code == 200
    assert client.post("/login", json={"username": "admin", "password": "bad"}).status_code == 401


def test_login_is_rate_limited(client):
    for _ in range(5):
        client.post("/login", json={"username": "admin", "password": "bad"})
    response = client.post("/login", json={"username": "admin", "password": "bad"})
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"


def test_successful_logins_do_not_consume_failure_budget(client):
    for _ in range(6):
        response = client.post("/login", json={"username": "admin", "password": "secret"})
        assert response.status_code == 200


def test_authentication_and_readiness(client, headers, settings):
    assert client.get("/candidates", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/health").json() == {"status": "ok"}
    ready = client.get("/ready", headers={"X-Request-ID": "review-request"})
    assert ready.json() == {"status": "ready"}
    assert ready.headers["X-Request-ID"] == "review-request"

    settings.database_path.write_text("{}", encoding="utf-8")
    response = client.get("/ready")
    assert response.status_code == 503
    assert "Candidate storage" in response.json()["detail"]


def test_unconfigured_authentication_returns_503(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "superconductor_database.json").write_text("[]", encoding="utf-8")
    client = TestClient(create_app(Settings(data_dir=data, output_dir=tmp_path / "state")))

    assert client.get("/candidates").status_code == 503
    assert client.post("/login", json={"username": "a", "password": "b"}).status_code == 503


def test_compatibility_module_exposes_application():
    from app import app

    assert app.title == "Superconductivity Pipeline API"
