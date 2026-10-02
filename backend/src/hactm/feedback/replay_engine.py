"""
Decision Replay & Counterfactual Simulation Engine for HACTM Closed-Loop Adaptation.
Reconstructs historical decisions and evaluates counterfactual scenarios safely.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from hactm.feedback.models import (
    DecisionReplayRequest,
    DecisionReplayResult,
    CounterfactualRequest,
    CounterfactualResult,
    FalsePositiveAnalysis,
    FalseNegativeAnalysis,
    RootCauseCandidate,
    ValidationStatus,
)


class DecisionReplayEngine:
    """Reconstructs historical security decisions without mutating past state."""

    def __init__(self, db_session: Optional[Any] = None):
        self.db = db_session

    def replay_decision(
        self, request: DecisionReplayRequest, historical_record: Dict[str, Any]
    ) -> DecisionReplayResult:
        """Reconstructs what HACTM would decide given historical or overridden state."""
        replay_id = f"replay_{request.target_decision_id}_{int(datetime.now(timezone.utc).timestamp())}"
        replayed_at = request.replayed_at_time or datetime.now(timezone.utc)

        original_decision = historical_record.get("decision", "ALLOW")
        risk_score = historical_record.get("risk_score", 0.35)

        # Apply overrides if provided
        weights = request.override_reliability_weights or historical_record.get("reliability_weights", {})
        if request.override_reliability_weights:
            # Re-weight risk score
            weighted_risk = sum(score * weights.get(agent, 0.8) for agent, score in historical_record.get("agent_scores", {}).items())
            weighted_risk = weighted_risk / max(1.0, len(historical_record.get("agent_scores", {})))
        else:
            weighted_risk = risk_score

        # Determine replayed decision
        allow_thresh = 0.30
        verify_thresh = 0.60
        quarantine_thresh = 0.80

        if weighted_risk < allow_thresh:
            replayed_decision = "ALLOW"
        elif weighted_risk < verify_thresh:
            replayed_decision = "STEP_UP_2FA"
        elif weighted_risk < quarantine_thresh:
            replayed_decision = "QUARANTINE"
        else:
            replayed_decision = "BLOCK"

        matches = (original_decision == replayed_decision)

        differences = {}
        if not matches:
            differences = {
                "original_decision": original_decision,
                "replayed_decision": replayed_decision,
                "original_risk_score": risk_score,
                "replayed_risk_score": round(weighted_risk, 4),
                "reason_for_difference": "Reliability weight override or threshold parameter shift",
            }

        return DecisionReplayResult(
            replay_id=replay_id,
            target_decision_id=request.target_decision_id,
            replayed_at_time=replayed_at,
            original_decision=original_decision,
            replayed_decision=replayed_decision,
            matches_original=matches,
            differences=differences,
            reconstruction_metadata={
                "policy_version": request.override_policy_version or "1.0.0",
                "model_version": request.override_model_version or "1.0.0",
                "simulated_only": True,
            },
        )


class CounterfactualEngine:
    """Simulates counterfactual security policy scenarios across historical datasets."""

    def run_counterfactual(
        self, request: CounterfactualRequest, historical_decisions: List[Dict[str, Any]]
    ) -> CounterfactualResult:
        """Executes counterfactual simulation across selected decisions."""
        run_id = f"cf_{request.scenario_name.lower()}_{int(datetime.now(timezone.utc).timestamp())}"

        orig_allow, orig_verify, orig_block = 0, 0, 0
        sim_allow, sim_verify, sim_block = 0, 0, 0

        for d in historical_decisions:
            orig = d.get("decision", "ALLOW")
            if orig == "ALLOW":
                orig_allow += 1
            elif orig in ("STEP_UP_2FA", "VERIFY"):
                orig_verify += 1
            else:
                orig_block += 1

            # Simulate counterfactual modification
            risk = d.get("risk_score", 0.4)
            if request.disable_reliability_weighting:
                risk = risk * 1.15  # Unweighted score drift
            if request.static_agent_selection:
                risk = risk * 0.90  # Missed specialized agent evidence

            if risk < 0.30:
                sim_allow += 1
            elif risk < 0.65:
                sim_verify += 1
            else:
                sim_block += 1

        return CounterfactualResult(
            run_id=run_id,
            scenario_name=request.scenario_name,
            decision_ids=request.decision_ids,
            parameters_modified={
                "disable_reliability_weighting": request.disable_reliability_weighting,
                "static_agent_selection": request.static_agent_selection,
                "disable_temporal_memory": request.disable_temporal_memory,
                "static_segmentation": request.static_segmentation,
            },
            original_outcomes_summary={
                "ALLOW": orig_allow,
                "VERIFY": orig_verify,
                "BLOCK": orig_block,
                "total": len(historical_decisions),
            },
            simulated_outcomes_summary={
                "ALLOW": sim_allow,
                "VERIFY": sim_verify,
                "BLOCK": sim_block,
                "total": len(historical_decisions),
            },
            impact_analysis={
                "decision_change_rate": round(abs(sim_block - orig_block) / max(1, len(historical_decisions)), 4),
                "security_impact": "Simulated security posture change",
                "friction_impact": f"{sim_verify - orig_verify} net change in 2FA step-up verifications",
                "disclaimer": "Simulated counterfactual evaluation only; historical state remains unmodified",
            },
        )


class RootCauseAnalyzer:
    """Analyzes validated false positives and false negatives to generate RootCauseCandidates."""

    def analyze_false_positive(self, fp_data: Dict[str, Any]) -> FalsePositiveAnalysis:
        factors = []
        if fp_data.get("uncertainty", 0) > 0.4:
            factors.append("HIGH_MODEL_UNCERTAINTY")
        if fp_data.get("evidence_quality", 1.0) < 0.6:
            factors.append("LOW_EVIDENCE_QUALITY")
        if not factors:
            factors.append("INCORRECT_POLICY_THRESHOLD")

        return FalsePositiveAnalysis(
            event_id=fp_data.get("event_id", "fp_1"),
            agent_id=fp_data.get("agent_id", "network_agent"),
            decision_id=fp_data.get("decision_id", "dec_1"),
            predicted_state="ATTACK",
            validated_state="FALSE_ALARM",
            likely_contributing_factors=factors,
            evidence_quality=fp_data.get("evidence_quality", 0.55),
            uncertainty=fp_data.get("uncertainty", 0.45),
            calibration=fp_data.get("calibration", 0.12),
            context=fp_data.get("context", {}),
            remediation_candidate="ADJUST_VERIFY_THRESHOLD",
        )

    def analyze_false_negative(self, fn_data: Dict[str, Any]) -> FalseNegativeAnalysis:
        return FalseNegativeAnalysis(
            event_id=fn_data.get("event_id", "fn_1"),
            missed_agent=fn_data.get("missed_agent", "phishing_agent"),
            attack_category=fn_data.get("attack_category", "PHISHING"),
            available_evidence=fn_data.get("available_evidence", ["ev_1"]),
            missing_evidence=fn_data.get("missing_evidence", ["ev_2"]),
            policy_state="ALLOW",
            model_version="1.0.0",
            drift_state="LOW_DRIFT",
            contributing_factors=["AGENT_NOT_SELECTED", "INSUFFICIENT_EVIDENCE"],
            remediation_candidate="ENABLE_SEQUENTIAL_EVIDENCE_ACQUISITION",
        )

    def generate_root_cause_candidate(self, incident_id: str, analysis: Any) -> RootCauseCandidate:
        return RootCauseCandidate(
            candidate_id=f"rca_{incident_id}_{int(datetime.now(timezone.utc).timestamp())}",
            incident_id=incident_id,
            category="DETECTOR_DISAGREEMENT" if hasattr(analysis, "missed_agent") else "POLICY_THRESHOLD_STRICTNESS",
            affected_component=getattr(analysis, "missed_agent", getattr(analysis, "agent_id", "policy_engine")),
            evidence_ids=getattr(analysis, "available_evidence", ["ev_sample"]),
            confidence=0.82,
            validation_status=ValidationStatus.PENDING,
            remediation_candidate=getattr(analysis, "remediation_candidate", "REVIEW_CONFIGURATION"),
        )
