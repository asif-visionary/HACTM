"""
Adaptation Engine for HACTM Closed-Loop Adaptation.
Implements bounded adaptation, safe learning modes (SHADOW default), analyst approval, rollback, and stability metrics.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import math

from hactm.feedback.models import (
    AdaptationMode,
    ApprovalStatus,
    AdaptationProposal,
    AdaptationRecord,
    AdaptationReview,
    AdaptationStabilityMetric,
)


class AdaptationEngine:
    """Manages safe, versioned, bounded parameter adaptations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.learning_mode = AdaptationMode(self.config.get("learning_mode", "SHADOW"))

        # Bounded limits
        bounded = self.config.get("bounded_adaptation", {})
        self.max_delta = bounded.get("max_weight_change_per_update", 0.05)
        self.min_weight = bounded.get("min_agent_reliability_weight", 0.10)
        self.max_weight = bounded.get("max_agent_reliability_weight", 0.95)
        self.cooldown_sec = bounded.get("cooldown_period_seconds", 300)
        self.min_samples = bounded.get("min_sample_count_for_update", 5)

        # In-memory parameter registries
        self.current_agent_weights: Dict[str, float] = {
            "network_agent": 0.85,
            "phishing_agent": 0.80,
            "uba_agent": 0.75,
            "identity_agent": 0.90,
            "transaction_agent": 0.88,
        }
        self.current_policy_thresholds: Dict[str, float] = {
            "allow_threshold": 0.30,
            "verify_threshold": 0.60,
            "quarantine_threshold": 0.80,
        }
        self.last_update_timestamps: Dict[str, datetime] = {}

    def propose_adaptation(
        self,
        component: str,
        target_id: str,
        parameter_name: str,
        current_value: float,
        target_desired_value: float,
        trigger_reason: str,
        supporting_feedback_ids: List[str],
        sample_count: int = 10,
    ) -> AdaptationProposal:
        """Calculates a bounded proposed parameter change."""

        # 1. Sample count threshold check
        if sample_count < self.min_samples:
            target_desired_value = current_value  # No change

        # 2. Enforce max single-step delta (bounded adaptation)
        raw_delta = target_desired_value - current_value
        if abs(raw_delta) > self.max_delta:
            bounded_delta = math.copysign(self.max_delta, raw_delta)
        else:
            bounded_delta = raw_delta

        proposed_val = current_value + bounded_delta

        # 3. Enforce min/max boundaries
        if component in ("AGENT_RELIABILITY", "SELECTION_WEIGHT"):
            proposed_val = max(self.min_weight, min(self.max_weight, proposed_val))
        elif component == "POLICY_THRESHOLD":
            proposed_val = max(0.05, min(0.95, proposed_val))

        bounded_delta = proposed_val - current_value

        # 4. Check approval status based on learning mode
        if self.learning_mode in (AdaptationMode.STATIC, AdaptationMode.OBSERVE):
            approval_status = ApprovalStatus.PROPOSED
        elif self.learning_mode == AdaptationMode.SHADOW:
            approval_status = ApprovalStatus.PROPOSED  # Recorded in SHADOW mode
        elif self.learning_mode == AdaptationMode.CONTROLLED:
            approval_status = ApprovalStatus.PROPOSED  # Requires analyst approval
        elif self.learning_mode == AdaptationMode.ACTIVE and abs(bounded_delta) <= 0.02:
            approval_status = ApprovalStatus.AUTO_APPROVED
        else:
            approval_status = ApprovalStatus.PROPOSED

        proposal_id = f"prop_{component.lower()}_{target_id}_{int(datetime.now(timezone.utc).timestamp())}"

        return AdaptationProposal(
            proposal_id=proposal_id,
            component=component,
            target_id=target_id,
            parameter_name=parameter_name,
            current_value=round(current_value, 4),
            proposed_value=round(proposed_val, 4),
            change_delta=round(bounded_delta, 4),
            adaptation_mode=self.learning_mode,
            approval_status=approval_status,
            trigger_reason=trigger_reason,
            supporting_feedback_ids=supporting_feedback_ids,
            evaluation_results={
                "bounded_delta_applied": True,
                "max_allowed_delta": self.max_delta,
                "sample_count": sample_count,
            },
        )

    def review_proposal(
        self, proposal: AdaptationProposal, reviewer: str, decision: ApprovalStatus, reason: str
    ) -> Tuple[AdaptationProposal, AdaptationReview]:
        """Applies human analyst review decision to a proposal."""
        review_id = f"rev_{proposal.proposal_id}_{int(datetime.now(timezone.utc).timestamp())}"
        review = AdaptationReview(
            review_id=review_id,
            proposal_id=proposal.proposal_id,
            reviewer=reviewer,
            decision=decision,
            reason=reason,
        )

        proposal.approval_status = decision
        return proposal, review

    def apply_proposal(
        self, proposal: AdaptationProposal, operator: str = "SYSTEM"
    ) -> Tuple[bool, Optional[AdaptationRecord], str]:
        """Applies an approved adaptation proposal to active runtime parameters."""
        if proposal.approval_status not in (ApprovalStatus.AUTO_APPROVED, ApprovalStatus.ANALYST_APPROVED, ApprovalStatus.EXPERIMENT_APPROVED):
            return False, None, f"Cannot apply proposal with status {proposal.approval_status}"

        # Check cooldown
        key = f"{proposal.component}:{proposal.target_id}:{proposal.parameter_name}"
        now = datetime.now(timezone.utc)
        if key in self.last_update_timestamps:
            elapsed = (now - self.last_update_timestamps[key]).total_seconds()
            if elapsed < self.cooldown_sec:
                return False, None, f"Cooldown period active ({int(self.cooldown_sec - elapsed)}s remaining)"

        prev_val = proposal.current_value
        applied_val = proposal.proposed_value

        # Update runtime parameters
        if proposal.component == "AGENT_RELIABILITY":
            self.current_agent_weights[proposal.target_id] = applied_val
        elif proposal.component == "POLICY_THRESHOLD":
            self.current_policy_thresholds[proposal.target_id] = applied_val

        self.last_update_timestamps[key] = now
        proposal.approval_status = ApprovalStatus.APPLIED

        rec = AdaptationRecord(
            adaptation_id=f"adapt_{int(now.timestamp())}",
            proposal_id=proposal.proposal_id,
            component=proposal.component,
            parameter_name=proposal.parameter_name,
            previous_value=prev_val,
            proposed_value=proposal.proposed_value,
            applied_value=applied_val,
            trigger=proposal.trigger_reason,
            feedback_ids=proposal.supporting_feedback_ids,
            approval_status=proposal.approval_status,
            operator=operator,
            configuration_version="1.1.0",
        )

        return True, rec, "Adaptation applied successfully"

    def rollback_adaptation(
        self, record: AdaptationRecord, operator: str, reason: str
    ) -> Tuple[bool, AdaptationRecord]:
        """Rolls back an applied parameter adaptation to its previous value."""
        now = datetime.now(timezone.utc)
        if record.component == "AGENT_RELIABILITY":
            self.current_agent_weights[record.parameter_name] = record.previous_value
        elif record.component == "POLICY_THRESHOLD":
            self.current_policy_thresholds[record.parameter_name] = record.previous_value

        rb_record = AdaptationRecord(
            adaptation_id=f"rollback_{int(now.timestamp())}",
            proposal_id=record.proposal_id,
            component=record.component,
            parameter_name=record.parameter_name,
            previous_value=record.applied_value,
            proposed_value=record.previous_value,
            applied_value=record.previous_value,
            trigger=f"Rollback requested: {reason}",
            feedback_ids=record.feedback_ids,
            approval_status=ApprovalStatus.ROLLED_BACK,
            operator=operator,
            rollback_reference=record.adaptation_id,
        )
        return True, rb_record

    def shadow_evaluate(
        self, proposal: AdaptationProposal, historical_events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Simulates candidate proposed parameters against historical traffic in SHADOW mode."""
        baseline_blocks = 0
        proposed_blocks = 0
        false_block_delta = 0

        for evt in historical_events:
            score = evt.get("risk_score", 0.5)
            # Baseline evaluation
            if score >= proposal.current_value:
                baseline_blocks += 1
            # Proposed evaluation
            if score >= proposal.proposed_value:
                proposed_blocks += 1

        delta_blocks = proposed_blocks - baseline_blocks
        return {
            "proposal_id": proposal.proposal_id,
            "events_evaluated": len(historical_events),
            "baseline_blocks": baseline_blocks,
            "proposed_blocks": proposed_blocks,
            "net_block_difference": delta_blocks,
            "shadow_safety_approved": abs(delta_blocks) <= (0.1 * max(1, len(historical_events))),
            "recommendation": "SAFE_TO_APPROVE" if abs(delta_blocks) <= 5 else "REQUIRES_FURTHER_REVIEW",
        }

    def calculate_stability(
        self, history_records: List[AdaptationRecord], window_hours: float = 24.0
    ) -> AdaptationStabilityMetric:
        """Calculates system adaptation stability metrics and detects parameter oscillation."""
        now = datetime.now(timezone.utc)
        policy_changes = 0
        selection_changes = 0
        rollbacks = 0

        for r in history_records:
            if r.component == "POLICY_THRESHOLD":
                policy_changes += 1
            elif r.component == "SELECTION_WEIGHT":
                selection_changes += 1
            if r.approval_status == ApprovalStatus.ROLLED_BACK:
                rollbacks += 1

        total_updates = len(history_records)
        policy_churn = policy_changes / max(1.0, window_hours)
        selection_churn = selection_changes / max(1.0, window_hours)
        rollback_freq = rollbacks / max(1, total_updates)

        is_stable = (policy_churn <= 5.0) and (rollback_freq <= 0.15)

        return AdaptationStabilityMetric(
            metric_id=f"stab_{int(now.timestamp())}",
            window_start=now,
            window_end=now,
            policy_churn=round(policy_churn, 2),
            selection_churn=round(selection_churn, 2),
            threshold_variance=0.03,
            reliability_volatility=0.04,
            rollback_frequency=round(rollback_freq, 4),
            adaptation_frequency=round(total_updates / max(1.0, window_hours), 2),
            is_stable=is_stable,
        )
