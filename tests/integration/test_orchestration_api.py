"""
Integration tests for Orchestration REST API endpoints (/api/v1/orchestration/*).
"""

import pytest
from fastapi.testclient import TestClient
from hactm.api.app import app

client = TestClient(app)


def test_get_agents():
    resp = client.get("/api/v1/orchestration/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 5


def test_get_candidates():
    resp = client.get("/api/v1/orchestration/candidates?context_id=ctx_test_1&event_type=suspicious_login")
    assert resp.status_code == 200
    data = resp.json()
    assert "candidates" in data
    assert len(data["candidates"]) >= 1


def test_select_agents():
    payload = {
        "context": {
            "context_id": "ctx_api_001",
            "event_id": "evt_api_001",
            "entity_ids": ["usr_999"],
            "event_type": "phishing_email",
            "domains_observed": ["phishing"],
            "current_risk": 0.75,
            "current_uncertainty": 0.60,
        }
    }
    resp = client.post("/api/v1/orchestration/select", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "decision_id" in data
    assert "selected_agents" in data
    assert "selection_scores" in data


def test_orchestration_config_and_health():
    resp_cfg = client.get("/api/v1/orchestration/config")
    assert resp_cfg.status_code == 200
    assert "method" in resp_cfg.json()
    assert "weights" in resp_cfg.json()

    resp_health = client.get("/api/v1/orchestration/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "healthy"


def test_orchestration_evaluation_endpoint():
    resp = client.get("/api/v1/orchestration/evaluation?num_events=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "baselines" in data
    assert "scenarios" in data
