"""
Integration tests for Zero-Trust Engine REST API endpoints (/api/v1/policies, /api/v1/zero-trust/*, /api/v1/micro-segmentation/*).
"""

import pytest
from fastapi.testclient import TestClient
from hactm.api.app import app

client = TestClient(app)


def test_get_policy_health():
    resp = client.get("/api/v1/policy-health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert "enforcement_mode" in data


def test_list_and_create_policy():
    resp = client.get("/api/v1/policies")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    payload = {
        "policy_id": "pol_custom_test",
        "name": "Custom Integration Test Policy",
        "priority": 450,
        "decision": "BLOCK",
        "conditions": {"min_risk": 0.90},
    }
    resp_create = client.post("/api/v1/policies", json=payload)
    assert resp_create.status_code == 200
    assert resp_create.json()["policy_id"] == "pol_custom_test"


def test_evaluate_zero_trust_decision():
    payload = {
        "subject_id": "usr_test_api",
        "resource_id": "res_db_prod",
        "action": "READ",
        "current_risk": 0.85,
        "uncertainty": 0.10,
        "security_zone": "USER_ZONE",
    }
    resp = client.post("/api/v1/zero-trust/decide", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "decision_id" in data
    assert data["decision"] in ["QUARANTINE", "BLOCK", "VERIFY"]


def test_micro_segmentation_endpoints():
    resp_segs = client.get("/api/v1/micro-segmentation/segments")
    assert resp_segs.status_code == 200
    assert isinstance(resp_segs.json(), list)

    resp_sim = client.post("/api/v1/micro-segmentation/simulate?subject_zone=USER_ZONE&target_zone=DATABASE_ZONE&action=READ")
    assert resp_sim.status_code == 200
    assert resp_sim.json()["decision"] == "BLOCK"


def test_verification_events_and_security_context():
    resp_2fa = client.post("/api/v1/verification/2fa/event", json={"subject_id": "usr_2fa_test", "verification_type": "2FA", "status": "SUCCESS"})
    assert resp_2fa.status_code == 200
    assert resp_2fa.json()["status"] == "SUCCESS"

    resp_ctx = client.get("/api/v1/security-context/usr_2fa_test")
    assert resp_ctx.status_code == 200
    assert "security_tags" in resp_ctx.json()
