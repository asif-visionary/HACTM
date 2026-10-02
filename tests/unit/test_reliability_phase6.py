"""
Unit tests for Reliability Processing, Uncertainty, Calibration, Quality, Drift, Conflicts, and Reputation.
"""

import pytest
from datetime import datetime, timezone

from hactm.reliability.models import ReliabilityConfig, ReliabilityStatus, DriftSeverity
from hactm.reliability.reliability_engine import ReliabilityEngine
from hactm.reliability.uncertainty_engine import UncertaintyEngine
from hactm.reliability.calibration_engine import CalibrationEngine
from hactm.reliability.quality_engine import EvidenceQualityEngine
from hactm.reliability.drift_engine import DriftEngine
from hactm.reliability.conflict_engine import ConflictEngine
from hactm.reliability.reputation_engine import ReputationEngine
from hactm.reliability.fusion_adapter import ReliabilityFusionAdapter


def test_reliability_engine_wilson_interval_and_metrics():
    engine = ReliabilityEngine()
    rec = engine.evaluate_reliability(
        agent_id="test-agent",
        true_positives=80,
        false_positives=10,
        true_negatives=90,
        false_negatives=20,
    )

    assert rec.sample_count == 200
    assert rec.precision == 0.8889
    assert rec.recall == 0.8000
    assert rec.reliability_score > 0.70
    assert rec.confidence_interval_lower < rec.reliability_score < rec.confidence_interval_upper
    assert rec.reliability_status == ReliabilityStatus.WELL_SUPPORTED


def test_reliability_engine_small_sample_protection():
    config = ReliabilityConfig(minimum_sample_threshold=10)
    engine = ReliabilityEngine(config)

    # 4 samples < 10 threshold
    rec = engine.evaluate_reliability(
        agent_id="small-sample-agent",
        true_positives=3,
        false_positives=1,
        true_negatives=0,
        false_negatives=0,
    )

    assert rec.reliability_status == ReliabilityStatus.INSUFFICIENT_DATA
    assert rec.reliability_score == 0.50
    assert rec.confidence_interval_lower == 0.10
    assert rec.confidence_interval_upper == 0.90


def test_reliability_model_version_inheritance():
    engine = ReliabilityEngine()
    prev_rec = engine.evaluate_reliability("agent-v1", 90, 10, 90, 10, model_version="1.0.0")

    # Disallow inheritance
    rec_v2_reset = engine.handle_model_version_change("agent-v1", prev_rec, new_version="2.0.0", allow_inheritance=False)
    assert rec_v2_reset.reliability_status == ReliabilityStatus.INSUFFICIENT_DATA
    assert rec_v2_reset.model_version == "2.0.0"

    # Allow inheritance with decay
    rec_v2_inherited = engine.handle_model_version_change("agent-v1", prev_rec, new_version="2.0.0", allow_inheritance=True)
    assert rec_v2_inherited.reliability_status == ReliabilityStatus.LIMITED_EVIDENCE
    assert rec_v2_inherited.reliability_score < prev_rec.reliability_score


def test_uncertainty_engine_and_disagreement():
    engine = UncertaintyEngine()
    unc = engine.calculate_evidence_uncertainty(
        evidence_id="ev-123",
        agent_id="net-agent",
        confidence=0.50,
        missing_fields=["source_ip"],
        disagreement_score=0.40,
    )

    assert 0.0 <= unc.uncertainty_score <= 1.0
    assert unc.uncertainty_score > 0.30

    dis = engine.analyze_detector_disagreement(
        event_id="ev-1",
        entity_id="usr-1",
        detections=[
            {"detector_id": "det-1", "risk_score": 0.90, "severity": "HIGH"},
            {"detector_id": "det-2", "risk_score": 0.10, "severity": "LOW"},
        ],
    )

    assert dis.detector_count == 2
    assert dis.categorical_disagreement is True
    assert dis.disagreement_score > 0.50


def test_calibration_engine_ece_and_scaling():
    engine = CalibrationEngine(num_bins=5)
    confidences = [0.95, 0.90, 0.85, 0.80, 0.75, 0.20, 0.15, 0.10, 0.05, 0.01]
    outcomes = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]

    record = engine.evaluate_calibration(
        agent_id="phish-agent",
        predicted_confidences=confidences,
        observed_outcomes=outcomes,
    )

    assert record.sample_count == 10
    assert 0.0 <= record.ece <= 1.0
    assert record.brier_score >= 0.0

    calibrated_val = engine.calibrate_confidence(0.90, method="temperature_scaling", temperature=1.5)
    assert 0.0 <= calibrated_val <= 1.0


def test_evidence_quality_engine():
    engine = EvidenceQualityEngine(fresh_seconds=300, stale_seconds=3600)
    ev_item = {
        "event_id": "ev-qual-1",
        "agent_id": "uba-agent",
        "entity_id": "usr-99",
        "event_type": "user_login",
        "timestamp": datetime.now(timezone.utc),
        "risk_score": 0.75,
        "confidence": 0.85,
        "severity": "MODERATE",
        "evidence": {"action": "login"},
    }

    q = engine.evaluate_quality(ev_item)
    assert q.quality_score > 0.80
    assert q.freshness_score == 1.0
    assert len(q.missing_fields) == 0


def test_drift_engine_psi_and_policy():
    engine = DriftEngine(psi_threshold=0.20)
    ref = [1.0, 1.2, 1.1, 1.0, 1.3, 1.1, 1.2, 1.0, 1.1, 1.2]
    cur = [5.0, 5.5, 6.0, 5.2, 5.8, 6.1, 5.5, 5.3, 5.9, 6.2]

    record = engine.monitor_drift(
        agent_id="network-agent",
        feature_or_signal="flow_rate",
        reference_values=ref,
        current_values=cur,
    )

    assert record.drift_score > 0.20
    assert record.drift_detected is True
    assert record.severity in [DriftSeverity.MODERATE, DriftSeverity.HIGH]


def test_conflict_engine():
    engine = ConflictEngine()

    # Missing evidence
    missing = engine.evaluate_missing_evidence(
        entity_id="usr-55",
        expected_agents=["network", "phishing", "identity"],
        present_agents=["network"],
    )
    assert len(missing) == 2
    assert missing[0].coverage_gap is True

    # Evidence conflict
    conflict = engine.diagnose_evidence_conflicts(
        entity_id="usr-55",
        evidence_items=[
            {"event_id": "e1", "risk_score": 0.95, "timestamp": datetime.now(timezone.utc)},
            {"event_id": "e2", "risk_score": 0.10, "timestamp": datetime.now(timezone.utc)},
        ],
    )
    assert conflict is not None
    assert conflict.disagreement_score > 0.35
    assert conflict.conflict_type == "RISK_DISAGREEMENT"


def test_reputation_engine():
    engine = ReputationEngine()
    rep = engine.calculate_reputation(
        agent_id="txn-agent",
        historical_precision=0.92,
        historical_recall=0.88,
        stability_score=0.95,
    )

    assert rep.reputation_score > 0.80
    assert rep.confidence_interval_lower < rep.reputation_score < rep.confidence_interval_upper


def test_reliability_fusion_adapter():
    adapter = ReliabilityFusionAdapter()
    ev = {"event_id": "e1", "risk_score": 0.80}

    weight, codes, breakdown = adapter.compute_reliability_aware_weight(
        evidence_item=ev,
        base_weight=1.0,
    )

    assert weight > 0.0
    assert "effective_weight" in breakdown
    assert len(codes) > 0
