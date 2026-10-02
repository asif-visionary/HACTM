"""
Integration tests for Reliability Processing & Uncertainty endpoints and service flow.
"""

import pytest
from fastapi.testclient import TestClient
from hactm.api.app import app

client = TestClient(app)


def test_reliability_health_endpoint():
    res = client.get("/api/v1/reliability/health")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "HEALTHY"
    assert data["phase"] == "RELIABILITY_TRUST_RELIABILITY_UNCERTAINTY_LAYER"


def test_reliability_config_endpoint():
    res = client.get("/api/v1/reliability/config")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "metric_weights" in data
    assert data["minimum_sample_threshold"] == 10


def test_reliability_evaluation_flow():
    # Evaluate an agent
    eval_payload = {
        "agent_id": "test-net-agent",
        "true_positives": 50,
        "false_positives": 5,
        "true_negatives": 40,
        "false_negatives": 5,
        "detector_id": "sig-det-1",
        "domain": "network",
        "model_version": "1.0.0",
        "calibration_error": 0.04,
        "drift_score": 0.0,
        "dataset": "test_dataset_v1",
        "change_reason": "Integration test run",
    }

    eval_res = client.post("/api/v1/reliability/evaluate", json=eval_payload)
    assert eval_res.status_code == 200
    data = eval_res.json()["data"]
    assert data["agent_id"] == "test-net-agent"
    assert data["reliability_score"] > 0.70

    # Retrieve via GET /agents
    get_res = client.get("/api/v1/reliability/agents?agent_id=test-net-agent")
    assert get_res.status_code == 200
    items = get_res.json()["data"]
    assert len(items) >= 1

    # Retrieve history
    hist_res = client.get("/api/v1/reliability/history/test-net-agent")
    assert hist_res.status_code == 200
    h_items = hist_res.json()["data"]
    assert len(h_items) >= 1


def test_calibration_and_drift_endpoints():
    cal_payload = {
        "agent_id": "test-phish-agent",
        "predicted_confidences": [0.9, 0.8, 0.7, 0.2, 0.1],
        "observed_outcomes": [1, 1, 1, 0, 0],
    }
    cal_res = client.post("/api/v1/reliability/calibration/evaluate", json=cal_payload)
    assert cal_res.status_code == 200

    drift_payload = {
        "agent_id": "test-uba-agent",
        "feature_or_signal": "bytes_transferred",
        "reference_values": [10, 12, 11, 10, 13],
        "current_values": [50, 52, 55, 60, 58],
    }
    drift_res = client.post("/api/v1/reliability/drift/evaluate", json=drift_payload)
    assert drift_res.status_code == 200
    assert drift_res.json()["data"]["drift_detected"] in [True, "true"]


def test_research_evaluation_endpoint():
    eval_res = client.post("/api/v1/reliability/research/evaluate")
    assert eval_res.status_code == 200
    data = eval_res.json()["data"]
    assert "baselines" in data
    assert "ablations" in data
    assert "scenarios" in data
