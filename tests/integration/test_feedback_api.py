"""
Integration tests for Closed-Loop Adaptation API Endpoints.
"""

import pytest
import uuid
from fastapi.testclient import TestClient

from hactm.api.app import app
from hactm.storage.database import init_db

init_db()
client = TestClient(app)


def test_api_closed_loop_adaptation_health():
    response = client.get("/api/v1/closed_loop_adaptation/health")
    assert response.status_code == 200
    data = response.json()
    assert data["phase"] == "CLOSED_LOOP_ADAPTATION_CLOSED_LOOP_FEEDBACK"
    assert data["status"] == "HEALTHY"


def test_api_submit_and_list_feedback():
    uid = uuid.uuid4().hex[:8]
    payload = {
        "feedback_id": f"fb_api_{uid}",
        "source_type": "ANALYST_VALIDATION",
        "source_id": "analyst_jones",
        "event_type": "DETECTION_FEEDBACK",
        "decision_id": f"dec_{uid}",
        "agent_ids": ["phishing_agent"],
        "evidence_ids": ["ev_301"],
        "validation_status": "ANALYST_CONFIRMED",
        "details": {"observed_outcome": "PHISHING_CONFIRMED"},
    }
    response = client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["routing_result"]["usable"]

    # List feedback
    list_res = client.get("/api/v1/feedback")
    assert list_res.status_code == 200
    assert len(list_res.json()["feedback"]) >= 1


def test_api_outcomes_flow():
    uid = uuid.uuid4().hex[:8]
    payload = {
        "outcome_id": f"out_api_{uid}",
        "decision_id": f"dec_{uid}",
        "subject_id": "user_alice",
        "original_decision": "STEP_UP_2FA",
        "observed_outcome": "ACCESS_LEGITIMATE",
        "validation_status": "PENDING",
    }
    response = client.post("/api/v1/outcomes", json=payload)
    assert response.status_code == 200

    outcomes_res = client.get("/api/v1/outcomes")
    assert outcomes_res.status_code == 200
    assert len(outcomes_res.json()["outcomes"]) >= 1


def test_api_adaptation_proposals_and_approval():
    props_res = client.get("/api/v1/adaptation/proposals")
    assert props_res.status_code == 200
    props = props_res.json()["proposals"]

    if props:
        pid = props[0]["proposal_id"]
        app_res = client.post(f"/api/v1/adaptation/proposals/{pid}/approve?reviewer=analyst_1&reason=TestApprove")
        assert app_res.status_code == 200
        assert app_res.json()["success"]


def test_api_model_registry():
    champions = client.get("/api/v1/models/champion")
    assert champions.status_code == 200
    assert len(champions.json()["champions"]) >= 1

    challengers = client.get("/api/v1/models/challengers")
    assert challengers.status_code == 200


def test_api_decision_replay_and_counterfactual():
    uid = uuid.uuid4().hex[:8]
    replay_payload = {
        "target_decision_id": f"dec_{uid}",
    }
    replay_res = client.post("/api/v1/decision-replay/run", json=replay_payload)
    assert replay_res.status_code == 200
    assert "matches_original" in replay_res.json()

    cf_payload = {
        "scenario_name": "DISABLE_TEMPORAL_MEMORY",
        "decision_ids": [f"dec_{uid}"],
        "disable_temporal_memory": True,
    }
    cf_res = client.post("/api/v1/counterfactual/run", json=cf_payload)
    assert cf_res.status_code == 200
    assert "impact_analysis" in cf_res.json()


def test_api_eval_baselines():
    eval_res = client.post("/api/v1/eval/baselines")
    assert eval_res.status_code == 200
    data = eval_res.json()
    assert "baselines" in data
    assert "ablations" in data
    assert "evolving_threat_scenario" in data
