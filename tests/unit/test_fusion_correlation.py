"""
Unit Tests for Evidence Fusion Cross-Domain Evidence Correlator.
"""

from datetime import datetime, timedelta, timezone
from hactm.fusion.correlator import CrossDomainEvidenceCorrelator
from hactm.fusion.models import CorrelationType


def test_entity_correlation_matches():
    correlator = CrossDomainEvidenceCorrelator()
    evidence_list = [
        {"event_id": "E1", "entity_id": "USER-100", "domain": "phishing"},
        {"event_id": "E2", "entity_id": "USER-100", "domain": "identity"},
        {"event_id": "E3", "entity_id": "USER-999", "domain": "transaction"},
    ]
    correlated, related, corr_type = correlator.correlate_entities("USER-100", evidence_list)
    assert len(correlated) == 2
    assert corr_type == CorrelationType.ENTITY_MATCH


def test_temporal_correlation_window():
    correlator = CrossDomainEvidenceCorrelator(default_window_seconds=1800)
    now = datetime.now(timezone.utc)
    evidence_list = [
        {"event_id": "E1", "timestamp": now.isoformat()},
        {"event_id": "E2", "timestamp": (now - timedelta(minutes=15)).isoformat()},
        {"event_id": "E3", "timestamp": (now - timedelta(hours=2)).isoformat()},
    ]
    correlated, max_delta = correlator.correlate_temporal(evidence_list, reference_time=now)
    assert len(correlated) == 2
    assert max_delta <= 1800.0


def test_cross_domain_pattern_detection():
    correlator = CrossDomainEvidenceCorrelator()
    evidence_list = [
        {"domain": "phishing"},
        {"domain": "identity"},
        {"domain": "transaction"},
    ]
    patterns = correlator.detect_cross_domain_patterns(evidence_list)
    assert len(patterns) == 1
    assert patterns[0]["pattern_id"] == "PHISH_AUTH_TX"
    assert patterns[0]["classification"] == "MULTI_DOMAIN_SECURITY_PATTERN"
