"""
Unit tests and edge-case test matrix for IdentityAuthenticationAgent.
Section 94 Test Matrix:
- normal login
- repeated failed logins (credential abuse)
- successful login after multiple failures (account takeover candidate)
- 2FA failure / timeout / bypass
- impossible travel candidate (Haversine calculation)
- missing location / non-geocoded location
"""

import pytest
from hactm.identity.agent import IdentityAuthenticationAgent


@pytest.fixture
def agent():
    return IdentityAuthenticationAgent()


def test_credential_abuse_brute_force(agent):
    acc = "target_user_01"
    # Execute 6 failed logins rapidly
    for i in range(6):
        dets = agent.process_event({
            "authentication_event_id": f"fail_{i}",
            "user_id": acc,
            "timestamp": "2026-10-02T10:00:00Z",
            "authentication_status": "FAILED",
            "failure_reason": "INVALID_PASSWORD",
        })

    # The 6th failure should trigger CREDENTIAL_ABUSE_INDICATORS
    assert len(dets) > 0
    cats = [d.category for d in dets]
    assert "CREDENTIAL_ABUSE_INDICATORS" in cats


def test_account_takeover_indicators(agent):
    acc = "target_user_02"
    # 3 failures
    for i in range(3):
        agent.process_event({
            "authentication_event_id": f"fail_ato_{i}",
            "user_id": acc,
            "timestamp": "2026-10-02T10:00:00Z",
            "authentication_status": "FAILED",
        })

    # Successful login from NEW device
    success_event = {
        "authentication_event_id": "ato_success",
        "user_id": acc,
        "timestamp": "2026-10-02T10:01:00Z",
        "device_id": "NEW-ATTACKER-DEVICE",
        "source_ip": "198.51.100.99",
        "authentication_status": "SUCCESS",
    }
    dets = agent.process_event(success_event)
    cats = [d.category for d in dets]
    assert "ACCOUNT_TAKEOVER_INDICATORS" in cats


def test_impossible_travel(agent):
    acc = "traveler_01"
    # Login in San Francisco (37.77, -122.41)
    agent.process_event({
        "authentication_event_id": "login_sf",
        "user_id": acc,
        "timestamp": "2026-10-02T10:00:00Z",
        "location": {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco"},
        "authentication_status": "SUCCESS",
    })

    # Login 15 minutes later in London (51.50, -0.12) -> ~8700 km apart!
    dets = agent.process_event({
        "authentication_event_id": "login_london",
        "user_id": acc,
        "timestamp": "2026-10-02T10:15:00Z",
        "location": {"lat": 51.5074, "lon": -0.1278, "city": "London"},
        "authentication_status": "SUCCESS",
    })

    cats = [d.category for d in dets]
    assert "POSSIBLE_IMPOSSIBLE_TRAVEL" in cats


def test_mfa_anomalies(agent):
    dets = agent.process_event({
        "authentication_event_id": "mfa_fail_01",
        "user_id": "user_mfa",
        "timestamp": "2026-10-02T10:00:00Z",
        "authentication_status": "SUCCESS",
        "two_factor_used": "KEY",
        "two_factor_result": "TIMEOUT",
    })
    cats = [d.category for d in dets]
    assert "MFA_AUTHENTICATION_ANOMALY" in cats
