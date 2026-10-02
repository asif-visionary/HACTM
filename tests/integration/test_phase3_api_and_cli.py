"""
Integration tests for Specialized Security Agents API endpoints, CLI, and ModelRegistry.
"""

import pytest
from fastapi.testclient import TestClient
from hactm.api.app import app
from hactm.storage.database import SessionLocal, init_db
from hactm.services.model_registry import ModelRegistry


@pytest.fixture
def client():
    init_db()
    return TestClient(app)


def test_agents_api_endpoints(client):
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    agent_ids = [a["agent_id"] for a in data]
    assert "network-security-agent" in agent_ids
    assert "phishing-intelligence-agent" in agent_ids
    assert "uba-agent" in agent_ids
    assert "identity-authentication-agent" in agent_ids
    assert "transaction-security-agent" in agent_ids

    # Detail & Health
    detail_res = client.get("/api/v1/agents/phishing-intelligence-agent")
    assert detail_res.status_code == 200
    assert detail_res.json()["agent_id"] == "phishing-intelligence-agent"

    health_res = client.get("/api/v1/agents/phishing-intelligence-agent/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "OPERATIONAL"


def test_domain_api_endpoints(client):
    # Phishing
    p_events = client.get("/api/v1/phishing/events")
    assert p_events.status_code == 200
    assert "items" in p_events.json()

    p_metrics = client.get("/api/v1/phishing/metrics")
    assert p_metrics.status_code == 200

    # UBA
    u_events = client.get("/api/v1/uba/events")
    assert u_events.status_code == 200

    u_profiles = client.get("/api/v1/uba/profiles")
    assert u_profiles.status_code == 200

    # Identity
    i_events = client.get("/api/v1/identity/events")
    assert i_events.status_code == 200

    # Transactions
    t_events = client.get("/api/v1/transactions/events")
    assert t_events.status_code == 200


def test_model_registry_lifecycle():
    init_db()
    db = SessionLocal()
    try:
        reg = ModelRegistry(db)
        model = reg.register_model(
            model_id="test_m1",
            agent_id="phishing-intelligence-agent",
            algorithm="TF-IDF + Logistic Regression",
            status="CANDIDATE",
        )
        assert model.status == "CANDIDATE"

        activated = reg.activate_model("test_m1")
        assert activated.status == "ACTIVE"

        active_retrieved = reg.get_active_model("phishing-intelligence-agent")
        assert active_retrieved.model_id == "test_m1"
    finally:
        db.close()
