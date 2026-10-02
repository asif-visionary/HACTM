"""
Integration Tests for Evidence Fusion API Endpoints and CLI Commands.
"""

from fastapi.testclient import TestClient
from hactm.api.app import app

client = TestClient(app)


def test_fusion_results_endpoint():
    res = client.get("/api/v1/fusion/results")
    assert res.status_code == 200
    body = res.json()
    assert "data" in body
    assert "pagination" in body
    assert "total" in body["pagination"]


def test_fusion_run_and_query():
    run_res = client.post("/api/v1/fusion/run", json={"entity_id": "USER-103", "window_seconds": 1800.0})
    assert run_res.status_code == 200
    data = run_res.json()["data"]
    assert data["status"] == "SUCCESS"
    fusion_id = data["fusion"]["fusion_id"]

    get_res = client.get(f"/api/v1/fusion/results/{fusion_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["fusion_id"] == fusion_id


def test_fusion_evaluate_endpoint():
    res = client.post("/api/v1/fusion/evaluate")
    assert res.status_code == 200
    body = res.json()["data"]
    assert "hypotheses_validation" in body


def test_fusion_conflicts_and_coverage():
    conf_res = client.get("/api/v1/fusion/conflicts")
    assert conf_res.status_code == 200

    cov_res = client.get("/api/v1/fusion/coverage")
    assert cov_res.status_code == 200
    assert "expected_domains" in cov_res.json()["data"]


def test_entity_risk_endpoint():
    res = client.get("/api/v1/risk/entities/USER-103")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "current_risk_score" in data
    assert "history" in data
