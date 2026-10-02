"""
Unit tests for BaseSecurityAgent interface and SecurityDetectionResult contracts.
"""

import pytest
from hactm.core.agent_base import BaseSecurityAgent, SecurityDetectionResult
from hactm.phishing.agent import PhishingIntelligenceAgent
from hactm.uba.agent import UBAAgent
from hactm.identity.agent import IdentityAuthenticationAgent
from hactm.transaction.agent import TransactionSecurityAgent


def test_agent_interface_inheritance():
    """Verifies all Specialized Security Agents specialized agents inherit from BaseSecurityAgent."""
    agents = [
        PhishingIntelligenceAgent(),
        UBAAgent(),
        IdentityAuthenticationAgent(),
        TransactionSecurityAgent(),
    ]

    for ag in agents:
        assert isinstance(ag, BaseSecurityAgent)

        # Mandatory lifecycle methods
        health = ag.health()
        assert isinstance(health, dict)
        assert "agent_id" in health
        assert "status" in health
        assert "events_processed" in health
        assert "detections_generated" in health

        ag.shutdown()


def test_security_detection_result_risk_semantics():
    """Verifies Cyber Risk Score semantics: 0.0 to 1.0, bounded confidence and baseline uncertainty."""
    res = SecurityDetectionResult(
        detection_id="det_test_01",
        event_id="ev_01",
        agent_id="test-agent",
        detector_type="HEURISTIC",
        detector_id="test-detector",
        category="TEST_ANOMALY",
        risk_score=1.5,  # Out of bounds -> should clamp to 1.0
        confidence=0.90,
        uncertainty=0.10,
        severity="HIGH",
        explanation="Test explanation",
        features_used={"feat": 1},
    )

    assert res.risk_score == 1.0
    assert res.confidence == 0.90
    assert res.uncertainty == 0.10

    d_dict = res.to_dict()
    assert d_dict["risk_score"] == 1.0
    assert d_dict["agent_id"] == "test-agent"
