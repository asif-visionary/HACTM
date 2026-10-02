"""
Unit Tests for Evidence Fusion Evidence Quality Evaluator.
"""

from datetime import datetime, timedelta, timezone
from hactm.fusion.quality_evaluator import EvidenceQualityEvaluator


def test_quality_evaluator_fresh_evidence():
    evaluator = EvidenceQualityEvaluator(fresh_seconds=300)
    now = datetime.now(timezone.utc)
    evidence = {
        "event_id": "EV-QUAL-1",
        "agent_id": "phishing-intelligence-agent",
        "entity_id": "USER-101",
        "event_type": "SUSPICIOUS_EMAIL",
        "timestamp": now.isoformat(),
        "risk_score": 0.80,
        "confidence": 0.90,
        "uncertainty": 0.10,
        "severity": "HIGH",
        "source": "phishing_loader",
        "dataset": "enron",
        "model_version": "v1.0.0",
        "detector_version": "v1.0.0",
    }
    assessment = evaluator.evaluate(evidence, current_time=now)
    assert assessment.completeness_score > 0.8
    assert assessment.provenance_score > 0.8
    assert assessment.freshness_score == 1.0
    assert assessment.quality_score > 0.80


def test_quality_evaluator_stale_evidence():
    evaluator = EvidenceQualityEvaluator(fresh_seconds=300, stale_seconds=3600)
    now = datetime.now(timezone.utc)
    stale_time = now - timedelta(hours=5)
    evidence = {
        "event_id": "EV-QUAL-2",
        "agent_id": "uba-agent",
        "entity_id": "USER-102",
        "event_type": "ANOMALOUS_ACCESS",
        "timestamp": stale_time.isoformat(),
        "risk_score": 0.70,
        "severity": "MEDIUM",
    }
    assessment = evaluator.evaluate(evidence, current_time=now)
    assert assessment.freshness_score == 0.20
    assert assessment.quality_score < assessment.completeness_score
