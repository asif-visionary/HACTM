"""
Unit tests for Network Security Evidence Generation, Risk Scoring, and Agent Coordination.
Covers Sections 28, 31, 32, 33, 34, 35, 36, 37, 67, 68 of Network Security Agent.
"""

from datetime import datetime, timezone
import pytest

from hactm.core.constants import SeverityLevel
from hactm.network.models import DetectorType, NetworkDetectionResult, NetworkEvent
from hactm.network.evidence_adapter import detection_to_security_evidence, calculate_risk_and_confidence
from hactm.network.agent import NetworkSecurityAgent


def test_calculate_risk_and_confidence():
    # Signature match (high confidence, low uncertainty)
    risk_sig, conf_sig, unc_sig = calculate_risk_and_confidence(
        detector_type=DetectorType.SIGNATURE,
        severity=SeverityLevel.HIGH,
        raw_anomaly_score=None
    )
    assert 0.70 <= risk_sig <= 0.95
    assert conf_sig >= 0.85
    assert unc_sig <= 0.15
    assert abs((conf_sig + unc_sig) - 1.0) < 1e-4

    # Heuristic detection (medium confidence)
    risk_heu, conf_heu, unc_heu = calculate_risk_and_confidence(
        detector_type=DetectorType.HEURISTIC,
        severity=SeverityLevel.MEDIUM,
        raw_anomaly_score=None
    )
    assert 0.40 <= risk_heu <= 0.75
    assert conf_heu <= conf_sig
    assert unc_heu >= unc_sig

    # Anomaly detector (score-driven)
    risk_anom, conf_anom, unc_anom = calculate_risk_and_confidence(
        detector_type=DetectorType.ANOMALY,
        severity=SeverityLevel.LOW,
        raw_anomaly_score=0.92
    )
    assert risk_anom >= 0.75


def test_detection_to_security_evidence():
    det = NetworkDetectionResult(
        detection_id="NET-DET-001",
        event_id="EVT-001",
        detector_type=DetectorType.SIGNATURE,
        detector_id="SIG_TELNET_EXPOSURE",
        detector_version="1.0.0",
        category="cleartext_telnet",
        risk_score=0.85,
        confidence=0.90,
        uncertainty=0.10,
        severity=SeverityLevel.HIGH,
        reason_codes=["TELNET_PORT_23"],
        explanation="Telnet protocol detected on port 23",
        features_used={"dst_port": 23, "protocol": "TCP"},
        timestamp=datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc),
        src_ip="192.168.1.15",
        dst_ip="10.0.0.5"
    )

    ev = detection_to_security_evidence(det, dataset_name="unit_test")

    assert ev.entity_id in ["192.168.1.15", "IP:192.168.1.15"]
    assert ev.agent_id == "network-security-agent"
    assert ev.event_type in ["NETWORK", "network_anomaly"]
    assert ev.risk_score == 0.85
    assert ev.confidence == 0.90
    assert ev.uncertainty == 0.10
    assert ev.severity == SeverityLevel.HIGH

    # Check evidence structure
    raw = ev.evidence
    assert raw["detector_type"] == "SIGNATURE"
    assert raw["detector_id"] == "SIG_TELNET_EXPOSURE"
    assert raw["dst_ip"] == "10.0.0.5"
    assert raw["explanation"] == "Telnet protocol detected on port 23"


def test_agent_health_and_processing():
    agent = NetworkSecurityAgent()
    agent.initialize()

    health_before = agent.health()
    assert health_before["status"] == "OPERATIONAL"
    assert health_before["events_processed"] == 0

    evt = NetworkEvent(
        event_id="EVT-AGENT-TEST",
        timestamp=datetime.now(timezone.utc),
        src_ip="192.168.1.55",
        dst_ip="10.0.0.1",
        src_port=44444,
        dst_port=23,
        protocol="TCP"
    )

    detections = agent.process_event(evt)
    assert len(detections) >= 1

    health_after = agent.health()
    assert health_after["events_processed"] == 1
    assert health_after["detections_generated"] >= 1
    assert health_after["average_latency_ms"] >= 0.0
