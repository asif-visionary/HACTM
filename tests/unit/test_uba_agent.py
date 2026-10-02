"""
Unit tests and edge-case test matrix for UBAAgent.
Section 93 Test Matrix:
- normal user activity
- new user insufficient baseline
- off-hours login
- rare resource access
- data movement anomaly (exfiltration indicator)
- privilege escalation indicator
- sparse history, service accounts
"""

import pytest
from hactm.uba.agent import UBAAgent


@pytest.fixture
def agent():
    return UBAAgent()


def test_new_user_insufficient_baseline(agent):
    raw = {
        "event_id": "uba_new_01",
        "user_id": "brand_new_employee",
        "timestamp": "2026-10-02T10:00:00Z",
        "action": "login",
    }
    dets = agent.process_event(raw)
    assert len(dets) == 1
    assert dets[0].category == "INSUFFICIENT_BASELINE"
    assert dets[0].is_insufficient_baseline is True
    assert dets[0].risk_score <= 0.10


def test_uba_anomaly_detection_after_baseline(agent):
    user = "emp_john"

    # Build baseline with 5 normal events
    for i in range(5):
        agent.process_event({
            "event_id": f"base_{i}",
            "user_id": user,
            "timestamp": f"2026-10-02T{10+i:02d}:00:00Z",
            "device_id": "LAPTOP-JOHN",
            "source_ip": "10.0.1.50",
            "action": "file_read",
            "resource": "/shared/reports/sales.xlsx",
            "bytes_transferred": 50000,
            "application": "Excel",
        })

    # Test Off-Hours Login Anomaly
    off_hours_event = {
        "event_id": "anom_off_hours",
        "user_id": user,
        "timestamp": "2026-10-02T03:30:00Z",
        "device_id": "LAPTOP-JOHN",
        "source_ip": "10.0.1.50",
        "action": "login",
        "application": "Excel",
    }
    dets = agent.process_event(off_hours_event)
    cats = [d.category for d in dets]
    assert "UNUSUAL_ACTIVITY_TIME" in cats

    # Test Potential Data Movement Anomaly
    data_exfil_event = {
        "event_id": "anom_exfil",
        "user_id": user,
        "timestamp": "2026-10-02T11:00:00Z",
        "device_id": "LAPTOP-JOHN",
        "source_ip": "10.0.1.50",
        "action": "file_download",
        "resource": "/db/export_all.sql",
        "bytes_transferred": 600_000_000,  # 600 MB
        "application": "CloudSync",
    }
    dets_exfil = agent.process_event(data_exfil_event)
    cats_exfil = [d.category for d in dets_exfil]
    assert "POTENTIAL_DATA_MOVEMENT_ANOMALY" in cats_exfil


def test_uba_edge_cases_matrix(agent):
    edge_cases = [
        {"event_id": "ec_01", "user_id": "usr_ec1"},  # sparse minimal fields
        {"event_id": "ec_02", "user_id": "usr_ec2", "action": "privilege_elevation", "privilege_level": "ADMIN"},
        {"event_id": "ec_03", "user_id": "service_account_db", "bytes_transferred": 0},
    ]
    for ec in edge_cases:
        dets = agent.process_event(ec)
        assert isinstance(dets, list)
