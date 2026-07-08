import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fastapi.testclient import TestClient
from scripts.api import app

client = TestClient(app)


def test_get_candidates():
    """Test GET /candidates returns list of candidates."""
    response = client.get("/candidates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "name" in data[0] or "formula" in data[0]


def test_get_candidates_with_filters():
    """Test GET /candidates with query parameters."""
    response = client.get("/candidates?min_tc=100&max_tc=300")
    assert response.status_code == 200
    data = response.json()
    for candidate in data:
        tc = candidate.get("Tc", candidate.get("predicted_tc", 0))
        assert 100 <= tc <= 300


def test_submit_candidate_success():
    """Test POST /submit with valid candidate data."""
    payload = {
        "name": "TestCandidate",
        "composition": "H3S",
        "pressure": 155,
        "predicted_tc": 203.0
    }
    response = client.post("/submit", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "experiment_id" in result or "status" in result


def test_submit_candidate_missing_fields():
    """Test POST /submit with missing required fields returns 422."""
    payload = {"name": "Incomplete"}
    response = client.post("/submit", json=payload)
    assert response.status_code == 422


def test_submit_candidate_invalid_data():
    """Test POST /submit with invalid data types returns 422."""
    payload = {"name": "Bad", "pressure": "high"}
    response = client.post("/submit", json=payload)
    assert response.status_code == 422


def test_batch_predict_success():
    """Test POST /batch_predict with valid JSON data."""
    payload = {
        "candidates": [
            {"composition": "H3S", "pressure": 155},
            {"composition": "LaH10", "pressure": 170}
        ]
    }
    response = client.post("/batch_predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for item in data:
        assert "predicted_tc" in item or "Tc" in item


def test_batch_predict_empty_list():
    """Test POST /batch_predict with empty list returns 200 and empty list."""
    payload = {"candidates": []}
    response = client.post("/batch_predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_batch_predict_invalid_input():
    """Test POST /batch_predict with missing candidates field returns 422."""
    payload = {}
    response = client.post("/batch_predict", json=payload)
    assert response.status_code == 422


def test_health_check():
    """Test GET /health returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
