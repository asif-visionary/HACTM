"""
Zero-Trust Engine Interactive Policy and Enforcement Simulator.
Allows researchers and SOC analysts to simulate zero-trust policy decisions,
2FA step-up challenges, analyst overrides, and micro-segmentation path evaluations without real infrastructure mutations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from hactm.zerotrust.models import (
    ZeroTrustDecisionContext,
    PolicyDecisionRecord,
    EnforcementAction,
    VerificationEvent,
    PolicyOverride,
    EnforcementMode,
    PolicyDecision,
    ActionType,
    ResourceType,
    SubjectType,
    SecurityZoneName,
)
from hactm.zerotrust.policy_engine import ZeroTrustPolicyEngine


class ZeroTrustPolicySimulator:
    """Interactive Policy & Enforcement Research Simulator for Zero-Trust Engine."""

    def __init__(self, engine: Optional[ZeroTrustPolicyEngine] = None):
        self.engine = engine or ZeroTrustPolicyEngine(enforcement_mode=EnforcementMode.SIMULATION)

    def simulate_decision(
        self,
        subject_id: str,
        resource_id: str,
        action: str = "READ",
        current_risk: float = 0.50,
        uncertainty: float = 0.20,
        two_factor_state: str = "NOT_REQUIRED",
        security_zone: str = "USER_ZONE",
    ) -> Dict[str, Any]:
        """
        Simulates a zero-trust policy decision for input scenario parameters.
        """
        ctx = ZeroTrustDecisionContext(
            context_id=f"ctx_sim_{int(datetime.now(timezone.utc).timestamp())}",
            subject_id=subject_id,
            subject_type=SubjectType.USER,
            resource_id=resource_id,
            resource_type=ResourceType.APPLICATION,
            requested_action=ActionType(action) if action in ActionType.__members__ else ActionType.READ,
            current_risk=current_risk,
            uncertainty=uncertainty,
            security_zone=SecurityZoneName(security_zone) if security_zone in SecurityZoneName.__members__ else SecurityZoneName.USER_ZONE,
            two_factor_state=two_factor_state,
        )

        record = self.engine.evaluate_decision(ctx)

        sim_action = EnforcementAction(
            action_id=f"act_sim_{record.decision_id}",
            decision_id=record.decision_id,
            action_type=record.decision.value,
            target=resource_id,
            mode=EnforcementMode.SIMULATION,
            status="SIMULATION_PASSED",
            reason=record.explanation,
        )

        return {
            "context": ctx.model_dump(),
            "decision_record": record.model_dump(),
            "simulated_enforcement": sim_action.model_dump(),
        }

    def simulate_analyst_override(
        self,
        decision_id: str,
        analyst_id: str,
        override_type: str,  # ALLOW_OVERRIDE, DENY_OVERRIDE, REQUIRE_REVIEW
        previous_decision: str,
        new_decision: str,
        reason: str,
    ) -> PolicyOverride:
        """
        Simulates explicit analyst override with mandatory audit trail.
        """
        return PolicyOverride(
            override_id=f"ovr_{int(datetime.now(timezone.utc).timestamp())}",
            decision_id=decision_id,
            analyst_id=analyst_id,
            override_type=override_type,
            previous_decision=previous_decision,
            new_decision=new_decision,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
        )
