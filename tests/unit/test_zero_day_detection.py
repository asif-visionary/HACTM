"""
Unit tests for HACTM Zero-Day Detection Subsystem and Research Evaluation Framework.
"""

import pytest
import numpy as np
from hactm.network.detectors.zero_day import (
    DNNDetector,
    CNNDetector,
    BayesianUncertaintyDetector,
    ZeroDayCandidateScoreCalculator,
    AgentDisagreementTracker,
    ZeroDayEscalationPolicy
)
from hactm.research.zero_day import (
    LeakageGuard,
    DatasetCompatibilityChecker,
    TemporalZeroDayEvaluator,
    AttackFamilyHoldoutEvaluator,
    CalibrationEngine,
    FixedFPREvaluator,
    ResourceProfiler
)


def test_dnn_detector_adapters():
    detector = DNNDetector(input_dim=5)
    X = [[0.1, 0.2, 0.3, 0.4, 0.5], [0.9, 0.8, 0.7, 0.6, 0.5]]
    y = [0, 1]
    
    detector.fit(X, y, epochs=2)
    scores = detector.predict_score(X)
    assert len(scores) == 2
    assert all(0.0 <= s <= 1.0 for s in scores)

    uncertainties = detector.predict_uncertainty(X)
    assert len(uncertainties) == 2
    assert all(0.0 <= u <= 1.0 for u in uncertainties)

    results = detector.detect_unknown(X)
    assert len(results) == 2
    assert hasattr(results[0], "zero_day_indicator")
    assert hasattr(results[0], "anomaly_score")
    assert hasattr(results[0], "confidence")


def test_cnn_detector_adapter():
    detector = CNNDetector(input_dim=8)
    X = [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]]
    scores = detector.predict_score(X)
    assert len(scores) == 1
    assert 0.0 <= scores[0] <= 1.0

    results = detector.detect_unknown(X)
    assert len(results) == 1
    assert results[0].model == "HACTM-CNN-Detector-v1"


def test_bayesian_detector_adapter():
    detector = BayesianUncertaintyDetector(input_dim=4)
    X_train = [[0.1, 0.1, 0.1, 0.1], [0.2, 0.2, 0.2, 0.2]]
    detector.fit(X_train)

    X_test = [[0.15, 0.15, 0.15, 0.15], [5.0, 5.0, 5.0, 5.0]]
    results = detector.detect_unknown(X_test)
    assert len(results) == 2
    # Out-of-distribution sample should yield higher anomaly and uncertainty
    assert results[1].anomaly_score > results[0].anomaly_score


def test_agent_disagreement_tracker():
    agent_scores = [
        {"agent_id": "network", "score": 0.88, "confidence": 0.90},
        {"agent_id": "uba", "score": 0.21, "confidence": 0.70},
        {"agent_id": "identity", "score": 0.74, "confidence": 0.85}
    ]
    res = AgentDisagreementTracker.calculate(agent_scores)
    assert res.agent_count == 3
    assert res.max_min_difference == round(0.88 - 0.21, 4)
    assert res.variance > 0.0


def test_zero_day_candidate_score_and_escalation():
    calc = ZeroDayCandidateScoreCalculator()
    cand = calc.calculate(
        event_id="evt-test-1",
        anomaly_score=0.90,
        uncertainty=0.40,
        novelty_indicator=0.35,
        temporal_deviation=0.30,
        contextual_deviation=0.25,
        agent_disagreement=0.40
    )
    assert 0.0 <= cand.candidate_score <= 1.0
    
    escalation = ZeroDayEscalationPolicy.evaluate_escalation(
        candidate_result=cand,
        known_class_confidence=0.20,
        entity_criticality=0.80
    )
    assert escalation["action"] in ["QUARANTINE", "BLOCK", "RESTRICT", "2FA", "VERIFY", "MONITOR", "ALLOW"]
    assert escalation["escalation_triggered"] is True


def test_leakage_guard():
    X_train = [[1.0, 2.0], [3.0, 4.0]]
    X_test = [[1.0, 2.0], [5.0, 6.0]]  # Duplicate row overlap!
    
    res = LeakageGuard.audit_splits(X_train=X_train, X_test=X_test)
    assert res.duplicate_overlap is True
    assert res.status == "FAIL"


def test_dataset_compatibility():
    res = DatasetCompatibilityChecker.check_compatibility("CIC-IDS2017", "UNSW-NB15")
    assert hasattr(res, "is_compatible")
    assert res.status in ["COMPATIBLE", "NOT_COMPARABLE"]


test_temporal_split_data = (
    [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 5.0], [5.0, 6.0]],
    [0, 0, 1, 0, 1],
    [100.0, 200.0, 300.0, 400.0, 500.0]
)


def test_temporal_evaluator():
    X, y, ts = test_temporal_split_data
    X_tr, y_tr, ts_tr, X_v, y_v, ts_v, X_te, y_te, ts_te, manifest = TemporalZeroDayEvaluator.split_by_time(
        X, y, ts, train_ratio=0.40, val_ratio=0.40
    )
    assert len(X_tr) == 2
    assert len(X_v) == 2
    assert len(X_te) == 1
    assert manifest.temporal_leakage_detected is False


def test_calibration_engine():
    y_true = [0, 0, 1, 1, 0, 1]
    y_prob = [0.1, 0.2, 0.8, 0.9, 0.3, 0.7]
    res = CalibrationEngine.compute_ece_and_brier(y_true, y_prob)
    assert 0.0 <= res.ece <= 1.0
    assert 0.0 <= res.brier_score <= 1.0


def test_fixed_fpr_evaluator():
    y_true = [0, 0, 0, 1, 1]
    scores = [0.1, 0.2, 0.3, 0.8, 0.9]
    res = FixedFPREvaluator.evaluate(y_true, scores, target_fpr_levels=[0.05])
    assert len(res.operating_points) == 1
    assert res.auroc >= 0.50


def test_resource_profiler():
    latencies = [1.0, 2.0, 3.0, 4.0, 5.0]
    res = ResourceProfiler.measure_throughput_and_latencies(latencies, total_duration_sec=0.10)
    assert res.inference_latency_ms == 3.0
    assert res.throughput_events_per_sec == 50.0
