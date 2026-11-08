"""
Unit tests for HACTM Workspace Real-Time Events, SSE Broadcasting,
Trust Passports, and Demo Incident Workflow.
Tests domain logic and broadcaster directly without loopback socket dependencies.
"""

import pytest
from hactm.services.workspace_event_broadcaster import broadcaster
from hactm.api.routers.trust_passport import (
    _build_passport,
    list_trust_passports,
    get_trust_passport,
    ISOLATED_AGENTS,
)
from hactm.api.routers.workspace_events import (
    AgentIsolationRequest,
    ToolValidationRequest,
    IncidentDemoRequest,
    toggle_agent_isolation,
    validate_tool_request,
    simulate_incident_workflow,
)


@pytest.fixture(autouse=True)
def reset_state():
    broadcaster.clear()
    ISOLATED_AGENTS.clear()
    yield
    broadcaster.clear()
    ISOLATED_AGENTS.clear()


def test_broadcaster_publish_and_retrieve():
    assert len(broadcaster.get_recent_events()) == 0

    event = broadcaster.publish_event(
        event_type="agent_status",
        agent_id="phishing-intelligence-agent",
        status="ANALYSING",
        message="Analysing suspicious email headers",
        incident_id="INC-TEST-001",
    )
    assert event["event_type"] == "agent_status"
    assert event["agent_id"] == "phishing-intelligence-agent"
    assert event["status"] == "ANALYSING"
    assert event["incident_id"] == "INC-TEST-001"
    assert "timestamp" in event
    assert "event_id" in event

    recent = broadcaster.get_recent_events(limit=10)
    assert len(recent) == 1
    assert recent[0]["event_id"] == event["event_id"]


def test_trust_passport_generation(db_session):
    passports = list_trust_passports(db=db_session)
    assert len(passports) >= 6
    agent_ids = [p.agent_id for p in passports]

    assert "global-orchestrator" in agent_ids
    assert "network-security-agent" in agent_ids
    assert "phishing-intelligence-agent" in agent_ids
    assert "uba-agent" in agent_ids
    assert "identity-authentication-agent" in agent_ids
    assert "transaction-security-agent" in agent_ids

    phish = next(p for p in passports if p.agent_id == "phishing-intelligence-agent")
    assert phish.department == "Phishing Intelligence"
    assert phish.reliability_score is not None
    assert phish.reliability_score > 0.0
    assert len(phish.tool_permissions) > 0
    assert phish.is_isolated is False


def test_agent_isolation_and_governance(db_session):
    # 1. Isolate agent
    req_isolate = AgentIsolationRequest(
        agent_id="network-security-agent",
        action="ISOLATE",
        reason="Simulated policy violation: unauthorized network scan detected",
        operator_role="SECURITY_OPERATOR",
    )
    res = toggle_agent_isolation(req_isolate, db=db_session)
    assert res["is_isolated"] is True
    assert res["agent_id"] == "network-security-agent"

    # 2. Check passport reflects ISOLATED state
    passport = get_trust_passport("network-security-agent", db=db_session)
    assert passport.is_isolated is True
    assert passport.current_status == "ISOLATED"
    assert "unauthorized network scan" in passport.isolation_reason

    # 3. Check event was published
    events = broadcaster.get_recent_events()
    iso_event = next((e for e in events if e["event_type"] == "agent_isolated"), None)
    assert iso_event is not None
    assert iso_event["agent_id"] == "network-security-agent"
    assert iso_event["status"] == "ISOLATED"

    # 4. Reinstate agent
    req_reinstate = AgentIsolationRequest(
        agent_id="network-security-agent",
        action="REINSTATE",
        reason="Operator verified no lateral movement occurred",
        operator_role="ADMIN",
    )
    res_re = toggle_agent_isolation(req_reinstate, db=db_session)
    assert res_re["is_isolated"] is False

    passport_re = get_trust_passport("network-security-agent", db=db_session)
    assert passport_re.is_isolated is False


def test_simulate_incident_end_to_end_workflow(db_session):
    demo_req = IncidentDemoRequest(
        scenario="PHISHING_CREDENTIAL_HARVESTING",
        sender="alert@fake-login-update.ru",
        subject="URGENT: Verify Your Credentials Immediately",
        target_user="cfo@enterprise.internal",
        suspicious_url="https://fake-login-update.ru/token",
        attachment_name="UrgentNotice.pdf.exe",
    )

    result = simulate_incident_workflow(demo_req, db=db_session)
    assert result["status"] == "INCIDENT_SIMULATED"
    assert "incident_id" in result
    assert "work_order_id" in result
    assert "approval_request_id" in result
    assert result["risk_score"] > 0.0

    # Verify event stream received all workflow milestones
    events = broadcaster.get_recent_events(limit=50)
    event_types = [e["event_type"] for e in events]

    assert "incident_created" in event_types
    assert "task_assigned" in event_types
    assert "task_started" in event_types
    assert "evidence_generated" in event_types
    assert "agent_message" in event_types
    assert "risk_updated" in event_types
    assert "approval_requested" in event_types

    # Verify agent messages
    messages = [e for e in events if e["event_type"] == "agent_message"]
    assert len(messages) >= 2
    assert any(m["agent_id"] == "phishing-intelligence-agent" for m in messages)
    assert any(m["agent_id"] == "threat-intelligence-agent" for m in messages)
