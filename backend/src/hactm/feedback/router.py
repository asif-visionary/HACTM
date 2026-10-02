"""
FeedbackRouter: Central routing module for validated feedback in HACTM Closed-Loop Adaptation.
Routes feedback to Reliability, Calibration, Selection Statistics, Policy Effectiveness, Drift, and Memory.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from hactm.feedback.models import (
    FeedbackEvent,
    ValidationStatus,
    FeedbackTrustLevel,
    FeedbackQuality,
    PolicyEffectivenessRecord,
    DriftResponseAction,
)
from hactm.feedback.validation import FeedbackValidator


class FeedbackRouter:
    """Routes validated feedback events to target HACTM subsystems."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.validator = FeedbackValidator(self.config)

    def route_feedback(
        self, feedback: FeedbackEvent, decision_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Routes a single feedback event across all target subsystems."""

        # 1. Determine trust level & quality score
        trust_level = self.validator.determine_trust_level(feedback.source_type)
        delay_sec = max(0.0, (datetime.now(timezone.utc) - feedback.timestamp).total_seconds())

        quality = self.validator.calculate_quality(
            source_type=feedback.source_type,
            validation_status=feedback.validation_status,
            evidence_count=len(feedback.evidence_ids),
            delay_seconds=delay_sec,
        )

        feedback.trust_level = trust_level
        feedback.quality_score = quality.feedback_quality_score

        routing_results = {
            "feedback_id": feedback.feedback_id,
            "trust_level": trust_level.value,
            "quality_score": quality.feedback_quality_score,
            "usable": False,
            "subsystems_updated": [],
            "provenance": {
                "source_type": feedback.source_type.value,
                "source_id": feedback.source_id,
                "decision_id": feedback.decision_id,
                "timestamp": feedback.timestamp.isoformat(),
                "quality_dimensions": quality.model_dump(),
            },
        }

        # 2. Check usability threshold
        if not self.validator.is_usable_feedback(quality, trust_level):
            routing_results["reason"] = "Feedback quality or trust level below threshold for adaptation"
            return routing_results

        routing_results["usable"] = True

        # 3. Subsystem Routings
        # A. Reliability & Agent Performance
        if feedback.agent_ids:
            rel_update = self._route_to_reliability(feedback, decision_context)
            routing_results["subsystems_updated"].append("RELIABILITY")
            routing_results["reliability_update"] = rel_update

        # B. Agent Selection Statistics (Orchestration expected vs actual info gain)
        if feedback.decision_id and "expected_info_gain" in (decision_context or {}):
            sel_update = self._route_to_selection_stats(feedback, decision_context)
            routing_results["subsystems_updated"].append("SELECTION_STATS")
            routing_results["selection_update"] = sel_update

        # C. Policy Effectiveness Engine
        if feedback.policy_ids or feedback.event_type.value in ("POLICY_FEEDBACK", "VERIFICATION_FEEDBACK", "SEGMENTATION_FEEDBACK"):
            pol_update = self._route_to_policy_effectiveness(feedback, decision_context)
            routing_results["subsystems_updated"].append("POLICY_EFFECTIVENESS")
            routing_results["policy_update"] = pol_update

        # D. Concept Drift & Model Performance
        if feedback.event_type.value == "DRIFT_FEEDBACK" or feedback.details.get("drift_detected"):
            drift_update = self._route_to_drift_monitoring(feedback)
            routing_results["subsystems_updated"].append("DRIFT_MONITORING")
            routing_results["drift_response"] = drift_update

        # E. Adaptive Evidence Memory & Graph Provenance
        if feedback.evidence_ids:
            mem_update = self._route_to_memory_and_graph(feedback)
            routing_results["subsystems_updated"].append("EVIDENCE_MEMORY_GRAPH")
            routing_results["memory_update"] = mem_update

        return routing_results

    def _route_to_reliability(self, feedback: FeedbackEvent, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Routes feedback to update Reliability & Trust agent performance & reputation."""
        obs = feedback.details.get("observed_outcome", "")
        is_tp = feedback.validation_status in (ValidationStatus.VALIDATED_TRUE_POSITIVE, ValidationStatus.ANALYST_CONFIRMED, ValidationStatus.GROUND_TRUTH_CONFIRMED)
        is_fp = feedback.validation_status == ValidationStatus.VALIDATED_FALSE_POSITIVE
        is_fn = feedback.validation_status == ValidationStatus.VALIDATED_FALSE_NEGATIVE

        return {
            "agent_ids": feedback.agent_ids,
            "outcome": obs,
            "is_true_positive": is_tp,
            "is_false_positive": is_fp,
            "is_false_negative": is_fn,
            "weight_adj_recommendation": +0.02 if is_tp else (-0.03 if is_fp else 0.0),
        }

    def _route_to_selection_stats(self, feedback: FeedbackEvent, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compares Orchestration expected info gain vs actual info gain."""
        expected_gain = context.get("expected_info_gain", 0.5)
        # Compute actual info gain from validation result
        actual_gain = 0.9 if feedback.validation_status in (ValidationStatus.VALIDATED_TRUE_POSITIVE, ValidationStatus.GROUND_TRUTH_CONFIRMED) else 0.1
        error = abs(expected_gain - actual_gain)

        return {
            "decision_id": feedback.decision_id,
            "expected_gain": expected_gain,
            "actual_gain": actual_gain,
            "gain_prediction_error": round(error, 4),
        }

    def _route_to_policy_effectiveness(self, feedback: FeedbackEvent, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluates security policy effectiveness and false block friction."""
        is_false_block = feedback.validation_status == ValidationStatus.VALIDATED_FALSE_POSITIVE
        is_missed_attack = feedback.validation_status == ValidationStatus.VALIDATED_FALSE_NEGATIVE

        review_required = False
        if is_false_block or is_missed_attack:
            review_required = True

        return {
            "policy_ids": feedback.policy_ids or ["default_zero_trust"],
            "false_block": is_false_block,
            "missed_attack": is_missed_attack,
            "review_required": review_required,
            "signal": "POLICY_REVIEW_REQUIRED" if review_required else "POLICY_OK",
        }

    def _route_to_drift_monitoring(self, feedback: FeedbackEvent) -> Dict[str, Any]:
        """Generates drift response action based on drift severity."""
        drift_score = feedback.details.get("drift_score", 0.5)
        if drift_score > 0.75:
            action = DriftResponseAction.RETRAIN_CANDIDATE
        elif drift_score > 0.50:
            action = DriftResponseAction.RECALIBRATE
        else:
            action = DriftResponseAction.MONITOR

        return {
            "drift_score": drift_score,
            "recommended_action": action.value,
            "justification": f"Drift score {drift_score} triggered action {action.value}",
        }

    def _route_to_memory_and_graph(self, feedback: FeedbackEvent) -> Dict[str, Any]:
        """Creates importance revision candidates for Adaptive Memory & Graph evidence memory without mutating history."""
        is_critical = feedback.validation_status in (ValidationStatus.GROUND_TRUTH_CONFIRMED, ValidationStatus.ANALYST_CONFIRMED)
        return {
            "evidence_ids": feedback.evidence_ids,
            "importance_revision_candidate": True if is_critical else False,
            "validated_graph_relationship": True if is_critical else False,
            "immutable_past_preserved": True,
        }
