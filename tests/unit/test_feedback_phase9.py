"""
Unit tests for Closed-Loop Adaptation Closed-Loop Feedback & Continuous Adaptation.
"""

import pytest
from datetime import datetime, timezone

from hactm.feedback.models import (
    SecurityDecisionOutcome,
    FeedbackEvent,
    ObservedOutcome,
    ValidationStatus,
    FeedbackSourceType,
    FeedbackType,
    FeedbackTrustLevel,
    AdaptationProposal,
    AdaptationMode,
    ApprovalStatus,
    DecisionReplayRequest,
    CounterfactualRequest,
)
from hactm.feedback.validation import FeedbackValidator
from hactm.feedback.router import FeedbackRouter
from hactm.feedback.adaptation_engine import AdaptationEngine
from hactm.feedback.replay_engine import DecisionReplayEngine, CounterfactualEngine, RootCauseAnalyzer
from hactm.feedback.model_registry import ModelRegistry, ControlledRetrainingPipeline
from hactm.feedback.evaluator import FeedbackEvaluator


def test_feedback_trust_level_assignment():
    validator = FeedbackValidator()
    assert validator.determine_trust_level(FeedbackSourceType.GROUND_TRUTH_DATASET) == FeedbackTrustLevel.GROUND_TRUTH
    assert validator.determine_trust_level(FeedbackSourceType.CONTROLLED_EXPERIMENT) == FeedbackTrustLevel.CONTROLLED_EXPERIMENT
    assert validator.determine_trust_level(FeedbackSourceType.ANALYST_VALIDATION) == FeedbackTrustLevel.ANALYST_CONFIRMED
    assert validator.determine_trust_level(FeedbackSourceType.SUCCESSFUL_2FA) == FeedbackTrustLevel.MULTI_SOURCE_VALIDATED


def test_feedback_quality_calculation():
    validator = FeedbackValidator()
    quality = validator.calculate_quality(
        source_type=FeedbackSourceType.ANALYST_VALIDATION,
        validation_status=ValidationStatus.ANALYST_CONFIRMED,
        evidence_count=3,
        delay_seconds=3600.0,
    )
    assert quality.feedback_quality_score > 0.70
    assert validator.is_usable_feedback(quality, FeedbackTrustLevel.ANALYST_CONFIRMED)


def test_feedback_conflict_detection():
    validator = FeedbackValidator()
    fb1 = FeedbackEvent(
        feedback_id="fb1", source_type=FeedbackSourceType.ANALYST_VALIDATION, source_id="a1",
        event_type=FeedbackType.ANALYST_FEEDBACK, details={"observed_outcome": "ATTACK_CONFIRMED"}
    )
    fb2 = FeedbackEvent(
        feedback_id="fb2", source_type=FeedbackSourceType.ANALYST_VALIDATION, source_id="a2",
        event_type=FeedbackType.ANALYST_FEEDBACK, details={"observed_outcome": "FALSE_ALARM"}
    )
    has_conflict, notes = validator.detect_conflict([fb1, fb2])
    assert has_conflict
    assert "Conflicting observed outcomes" in notes


def test_feedback_router():
    router = FeedbackRouter()
    fb = FeedbackEvent(
        feedback_id="fb_test_1",
        source_type=FeedbackSourceType.ANALYST_VALIDATION,
        source_id="analyst_smith",
        event_type=FeedbackType.DETECTION_FEEDBACK,
        decision_id="dec_999",
        agent_ids=["network_agent"],
        evidence_ids=["ev_101", "ev_102"],
        validation_status=ValidationStatus.ANALYST_CONFIRMED,
        details={"observed_outcome": "ATTACK_CONFIRMED"},
    )
    ctx = {"expected_info_gain": 0.65}
    res = router.route_feedback(fb, ctx)
    assert res["usable"]
    assert "RELIABILITY" in res["subsystems_updated"]
    assert "SELECTION_STATS" in res["subsystems_updated"]


def test_bounded_adaptation_engine():
    engine = AdaptationEngine({"learning_mode": "SHADOW"})
    prop = engine.propose_adaptation(
        component="AGENT_RELIABILITY",
        target_id="network_agent",
        parameter_name="network_agent",
        current_value=0.80,
        target_desired_value=0.95,  # Raw delta +0.15 exceeds max_delta +0.05
        trigger_reason="Test bounded adaptation",
        supporting_feedback_ids=["fb_1"],
        sample_count=10,
    )
    # Check that change delta was bounded to max_delta (0.05)
    assert prop.change_delta == 0.05
    assert prop.proposed_value == 0.85
    assert prop.approval_status == ApprovalStatus.PROPOSED


def test_analyst_review_and_rollback():
    engine = AdaptationEngine({"learning_mode": "CONTROLLED"})
    prop = engine.propose_adaptation(
        component="POLICY_THRESHOLD",
        target_id="verify_threshold",
        parameter_name="verify_threshold",
        current_value=0.60,
        target_desired_value=0.64,
        trigger_reason="Reduce false step-ups",
        supporting_feedback_ids=["fb_2"],
        sample_count=10,
    )
    updated_prop, review = engine.review_proposal(prop, "analyst_1", ApprovalStatus.ANALYST_APPROVED, "Approved")
    assert updated_prop.approval_status == ApprovalStatus.ANALYST_APPROVED

    applied, record, msg = engine.apply_proposal(updated_prop, "analyst_1")
    assert applied
    assert engine.current_policy_thresholds["verify_threshold"] == 0.64

    # Rollback
    rolled_back, rb_rec = engine.rollback_adaptation(record, "analyst_1", "Unexpected friction")
    assert rolled_back
    assert engine.current_policy_thresholds["verify_threshold"] == 0.60


def test_model_registry_champion_challenger():
    registry = ModelRegistry()
    champ = registry.get_champion_model("network_model")
    assert champ is not None

    challenger = registry.register_candidate(
        model_id="network_model",
        agent_id="network_agent",
        version="2.0.0",
        metrics={"f1": 0.95, "precision": 0.96, "recall": 0.94, "fpr": 0.02, "ece": 0.02},
    )

    evaluation = registry.evaluate_champion_vs_challenger(champ.version_id, challenger.version_id)
    assert evaluation.recommendation == "PROMOTE"

    promoted, msg = registry.promote_challenger("network_model", challenger.version_id, "admin", "Approved")
    assert promoted
    assert registry.registry[challenger.version_id].is_champion


def test_decision_replay_and_counterfactuals():
    replay_eng = DecisionReplayEngine()
    req = DecisionReplayRequest(target_decision_id="dec_101")
    hist = {"decision": "ALLOW", "risk_score": 0.25}
    res = replay_eng.replay_decision(req, hist)
    assert res.matches_original

    cf_eng = CounterfactualEngine()
    cf_req = CounterfactualRequest(
        scenario_name="NO_RELIABILITY_WEIGHTING",
        decision_ids=["dec_101"],
        disable_reliability_weighting=True,
    )
    cf_res = cf_eng.run_counterfactual(cf_req, [hist])
    assert cf_res.scenario_name == "NO_RELIABILITY_WEIGHTING"


def test_evaluator_baselines_and_ablations():
    evaluator = FeedbackEvaluator()
    baselines = evaluator.run_baselines_comparison([])
    assert "BASELINE_F_FULL_HACTM_CLOSED_LOOP" in baselines["baselines"]

    ablations = evaluator.run_ablations_study([])
    assert "A12_FULL_CLOSED_LOOP" in ablations["ablations"]
