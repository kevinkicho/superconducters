import os
import sys

os.environ.setdefault("SUPERCONDUCTOR_API_KEY", "test")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_get_candidates():
    """Test GET /candidates returns list of candidates."""
    response = client.get("/candidates", headers={"X-API-Key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "formula" in data[0]


def test_get_candidates_with_filters():
    """Test GET /candidates with query parameters."""
    response = client.get("/candidates?min_tc=100&max_tc=300", headers={"X-API-Key": "test"})
    assert response.status_code == 200
    data = response.json()
    for candidate in data:
        tc = candidate.get("temperature", 0)
        assert 100 <= tc <= 300


def test_submit_candidate_success():
    """Test POST /submit with valid candidate data."""
    payload = {"candidate_id": 1}
    response = client.post("/submit", json=payload, headers={"X-API-Key": "test"})
    assert response.status_code == 200
    result = response.json()
    assert "status" in result


def test_submit_candidate_missing_fields():
    """Test POST /submit with missing required fields returns 422."""
    payload = {}
    response = client.post("/submit", json=payload, headers={"X-API-Key": "test"})
    assert response.status_code == 422


def test_submit_candidate_invalid_data():
    """Test POST /submit with invalid data types returns 422."""
    payload = {"candidate_id": "bad"}
    response = client.post("/submit", json=payload, headers={"X-API-Key": "test"})
    assert response.status_code == 422


def test_batch_predict_success():
    """Test POST /batch_predict with valid JSON data."""
    payload = {"formulas": ["H3S", "LaH10"]}
    response = client.post("/batch_predict", json=payload, headers={"X-API-Key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert isinstance(data["predictions"], list)
    assert len(data["predictions"]) == 2
    for item in data["predictions"]:
        assert "predicted_tc" in item


def test_batch_predict_empty_list():
    """Test POST /batch_predict with empty list returns 200 and empty list."""
    payload = {"formulas": []}
    response = client.post("/batch_predict", json=payload, headers={"X-API-Key": "test"})
    assert response.status_code == 200
    data = response.json()
    assert data == {"predictions": []}


def test_batch_predict_invalid_input():
    """Test POST /batch_predict with missing formulas field returns 422."""
    payload = {}
    response = client.post("/batch_predict", json=payload, headers={"X-API-Key": "test"})
    assert response.status_code == 422


def test_health_check():
    """Test GET /health returns 200."""
    response = client.get("/health", headers={"X-API-Key": "test"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_api_key_is_rejected():
    response = client.get("/candidates", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401
