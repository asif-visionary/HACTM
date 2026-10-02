"""
Unit tests for data normalization and validation rules.
"""

from datetime import datetime, timezone
import pytest

from hactm.core.constants import SeverityLevel
from hactm.core.errors import HACTMValidationError
from hactm.ingestion.normalization import (
    normalize_domain,
    normalize_email,
    normalize_ip,
    normalize_null_value,
    normalize_record,
    normalize_timestamp,
    normalize_url,
)
from hactm.ingestion.validation import validate_and_build_evidence


def test_normalization_null_values():
    assert normalize_null_value(None) is None
    assert normalize_null_value("") is None
    assert normalize_null_value("   ") is None
    assert normalize_null_value("null") is None
    assert normalize_null_value("NULL") is None
    assert normalize_null_value("None") is None
    assert normalize_null_value("N/A") is None
    assert normalize_null_value("-") is None
    assert normalize_null_value("valid_string") == "valid_string"
    assert normalize_null_value(42) == 42


def test_timestamp_normalization():
    # ISO string with UTC Z
    ts1 = normalize_timestamp("2026-10-01T12:00:00Z")
    assert ts1.tzinfo == timezone.utc
    assert ts1.hour == 12

    # ISO string with timezone offset (+05:30) converts to UTC
    ts2 = normalize_timestamp("2026-10-01T15:30:00+05:30")
    assert ts2.tzinfo == timezone.utc
    assert ts2.hour == 10  # 15:30 - 5:30 = 10:00 UTC

    # Epoch seconds
    ts3 = normalize_timestamp(1700000000)
    assert ts3.tzinfo == timezone.utc

    # Invalid timestamp
    with pytest.raises(ValueError):
        normalize_timestamp("NOT_A_TIMESTAMP")

    with pytest.raises(ValueError):
        normalize_timestamp(None)


def test_ip_normalization():
    # Valid IPv4
    c_ip, v = normalize_ip("  192.168.1.1  ")
    assert c_ip == "192.168.1.1"
    assert v == "IPv4"

    # Valid IPv6
    c_ip6, v6 = normalize_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
    assert v6 == "IPv6"
    assert "2001:db8:85a3::8a2e:370:7334" in c_ip6 or "2001:0db8" in c_ip6

    # Invalid IP preserves cleaned string without blowing up
    inv_ip, inv_v = normalize_ip("999.999.999.999")
    assert inv_ip == "999.999.999.999"
    assert inv_v is None


def test_domain_and_email_normalization_no_speculative_correction():
    # Typo domain must NOT be changed to gmail.com
    assert normalize_domain("  GMIAL.COM  ") == "gmial.com"
    assert normalize_email("  User.Test@GMIAL.COM  ") == "user.test@gmial.com"

    # URL normalization
    norm_url = normalize_url("HTTP://Example.COM:8080/Path/To/Resource?query=1")
    assert "http://example.com" in norm_url


def test_valid_evidence_validation():
    raw = {
        "event_id": "EVT-TEST-001",
        "agent_id": "AGENT-01",
        "entity_id": "IP:192.168.1.1",
        "event_type": "NETWORK",
        "timestamp": "2026-10-01T12:00:00Z",
        "risk_score": 0.85,
        "confidence": 0.95,
        "uncertainty": 0.05,
        "evidence": {"bytes": 1000},
        "security_tags": "tag1, tag2",
    }
    ev = validate_and_build_evidence(raw)
    assert ev.event_id == "EVT-TEST-001"
    assert ev.risk_score == 0.85
    assert ev.severity == SeverityLevel.CRITICAL
    assert ev.security_tags == ["tag1", "tag2"]


def test_validation_missing_event_id():
    raw = {
        "event_id": "",
        "agent_id": "AGENT-01",
        "event_type": "NETWORK",
        "timestamp": "2026-10-01T12:00:00Z",
        "risk_score": 0.5,
    }
    with pytest.raises(HACTMValidationError, match="event_id"):
        validate_and_build_evidence(raw)


def test_validation_risk_score_bounds():
    base = {
        "event_id": "EVT-RISK-BOUNDS",
        "agent_id": "AGENT-01",
        "event_type": "NETWORK",
        "timestamp": "2026-10-01T12:00:00Z",
        "confidence": 0.9,
        "uncertainty": 0.1,
    }

    # risk < 0.0
    with pytest.raises(HACTMValidationError, match="risk_score"):
        validate_and_build_evidence({**base, "risk_score": -0.01})

    # risk > 1.0
    with pytest.raises(HACTMValidationError, match="risk_score"):
        validate_and_build_evidence({**base, "risk_score": 1.01})


def test_validation_confidence_and_uncertainty_bounds():
    base = {
        "event_id": "EVT-CONF-BOUNDS",
        "agent_id": "AGENT-01",
        "event_type": "NETWORK",
        "timestamp": "2026-10-01T12:00:00Z",
        "risk_score": 0.5,
    }

    # confidence < 0
    with pytest.raises(HACTMValidationError, match="confidence"):
        validate_and_build_evidence({**base, "confidence": -0.1, "uncertainty": 0.1})

    # confidence > 1
    with pytest.raises(HACTMValidationError, match="confidence"):
        validate_and_build_evidence({**base, "confidence": 1.1, "uncertainty": 0.1})

    # uncertainty < 0
    with pytest.raises(HACTMValidationError, match="uncertainty"):
        validate_and_build_evidence({**base, "confidence": 0.9, "uncertainty": -0.05})

    # uncertainty > 1
    with pytest.raises(HACTMValidationError, match="uncertainty"):
        validate_and_build_evidence({**base, "confidence": 0.9, "uncertainty": 1.2})


def test_unicode_and_long_fields():
    raw = {
        "event_id": "EVT-UNICODE-999",
        "agent_id": "AGENT-AUTH-✓",
        "entity_id": "USER:инженер_иван",
        "event_type": "AUTHENTICATION",
        "timestamp": "2026-10-01T12:00:00Z",
        "risk_score": 0.35,
        "confidence": 0.9,
        "uncertainty": 0.1,
        "evidence": {
            "comment": "Тестовый вход с кириллицей и спецсимволами 🔐" * 5,
            "very_long_field": "A" * 5000,
        },
    }
    ev = validate_and_build_evidence(raw)
    assert ev.event_id == "EVT-UNICODE-999"
    assert "🔐" in ev.evidence["comment"]
