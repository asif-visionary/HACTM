"""
Integration tests for Research Validation Validation & Publication Endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from hactm.api.app import app

client = TestClient(app)


def test_get_validation_summary():
    response = client.get("/api/v1/research/validation")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "VALID"


def test_post_validate_result():
    payload = {
        "experiment_id": "EXP-001",
        "run_id": "run-01",
        "dataset_id": "cic_ids_2017",
        "dataset_version": "v1.0",
        "config_hash": "cfg-hash-123",
        "model_versions": {"net": "2.1"},
        "code_version": "1.0.0",
        "timestamp": "2026-10-02T10:00:00Z",
        "random_seed": 42,
        "environment_id": "env-01",
        "metrics": {"precision": 0.962, "recall": 0.931, "f1": 0.946, "fpr": 0.024},
    }
    response = client.post("/api/v1/research/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "VALID"


def test_get_statistics():
    response = client.get("/api/v1/research/statistics?experiment_id=EXP-001")
    assert response.status_code == 200
    data = response.json()
    assert "descriptive_stats" in data
    assert "confidence_intervals" in data


def test_get_sensitivity():
    response = client.get("/api/v1/research/sensitivity?experiment_id=EXP-001")
    assert response.status_code == 200
    data = response.json()
    assert "sensitivity_items" in data


def test_get_robustness():
    response = client.get("/api/v1/research/robustness?experiment_id=EXP-001")
    assert response.status_code == 200
    data = response.json()
    assert "robustness_items" in data


def test_get_hypotheses():
    response = client.get("/api/v1/research/hypotheses")
    assert response.status_code == 200
    data = response.json()
    assert len(data["hypotheses"]) == 9


def test_post_validate_claims():
    payload = {"claims": ["Adaptive orchestration reduces unnecessary agent calls."]}
    response = client.post("/api/v1/research/claims/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["validated_claims"][0]["status"] == "DIRECTLY_SUPPORTED"


def test_get_reproducibility():
    response = client.get("/api/v1/research/reproducibility?experiment_id=EXP-001")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REPRODUCED"


def test_get_audit():
    response = client.get("/api/v1/research/audit")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SECURITY_PASS"


def test_get_publication_readiness():
    response = client.get("/api/v1/research/publication")
    assert response.status_code == 200
    data = response.json()
    assert len(data["dimensions"]) == 10


def test_post_generate_publication():
    payload = {"title": "Test Title", "include_latex": True}
    response = client.post("/api/v1/research/publication/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "package_id" in data


def test_get_traceability():
    response = client.get("/api/v1/research/traceability")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10


def test_get_completion():
    response = client.get("/api/v1/research/completion")
    assert response.status_code == 200
    data = response.json()
    assert data["project_status"] == "FULLY_COMPLETED"
