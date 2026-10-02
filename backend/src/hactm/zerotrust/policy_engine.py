"""
Zero-Trust Engine Declarative Zero-Trust Policy Engine.
Evaluates context against declarative policies, resolves policy conflicts via priority precedence
(BLOCK > QUARANTINE > VERIFY > MONITOR > ALLOW), enforces AAL step-up requirements,
and operates safely under DRY_RUN, SIMULATION, or CONTROLLED_ENFORCEMENT modes.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

from hactm.zerotrust.models import (
    ZeroTrustDecisionContext,
    Policy,
    PolicyDecision,
    PolicyDecisionRecord,
    EnforcementMode,
    AuthenticationAssuranceLevel,
    SecurityZoneName,
    ActionType,
)
from hactm.zerotrust.tags_and_groups import SecurityTagManager
from hactm.zerotrust.micro_segmentation import MicroSegmentationEngine


class ZeroTrustPolicyEngine:
    """Core Context-Aware Zero-Trust Policy Decision Engine for HACTM Zero-Trust Engine."""

    def __init__(
        self,
        enforcement_mode: EnforcementMode = EnforcementMode.DRY_RUN,
        engine_version: str = "1.0.0",
    ):
        self.enforcement_mode = enforcement_mode
        self.engine_version = engine_version
        self.tag_manager = SecurityTagManager()
        self.micro_segment_engine = MicroSegmentationEngine()
        self._policies: Dict[str, Policy] = {}
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        now = datetime.now(timezone.utc)

        # Policy 1: Critical Risk Quarantine Policy
        p1 = Policy(
            policy_id="pol_critical_risk_quarantine",
            name="Critical Risk Compromise Quarantine",
            description="Quarantines entities with Cyber Risk Score >= 0.80 or COMPROMISED tag",
            priority="500",
            enabled=True,
            scope="GLOBAL",
            conditions={"min_risk": 0.80, "required_tags": ["COMPROMISED"]},
            decision=PolicyDecision.QUARANTINE,
            actions=["QUARANTINE", "NOTIFY_SOC"],
            created_at=now,
        )

        # Policy 2: High Uncertainty Step-up Verification
        p2 = Policy(
            policy_id="pol_high_uncertainty_verify",
            name="High Uncertainty Step-Up Verification",
            description="Triggers 2FA verification when uncertainty is above 0.70 for sensitive resources",
            priority="400",
            enabled=True,
            scope="GLOBAL",
            conditions={"min_uncertainty": 0.70, "min_risk": 0.40},
            decision=PolicyDecision.VERIFY,
            required_assurance=AuthenticationAssuranceLevel.AAL2,
            actions=["REQUIRE_2FA"],
            created_at=now,
        )

        # Policy 3: Elevated Risk Sensitive Transaction Policy
        p3 = Policy(
            policy_id="pol_transaction_stepup",
            name="Elevated Risk Financial Transaction Verification",
            description="Requires step-up 2FA for TRANSFER or TRANSACT actions when risk >= 0.50",
            priority="350",
            enabled=True,
            scope="TRANSACTION",
            conditions={"actions": ["TRANSFER", "TRANSACT"], "min_risk": 0.50},
            decision=PolicyDecision.VERIFY,
            required_assurance=AuthenticationAssuranceLevel.AAL2,
            actions=["REQUIRE_2FA"],
            created_at=now,
        )

        # Policy 4: Database Admin Protection Policy
        p4 = Policy(
            policy_id="pol_database_admin_protection",
            name="Database Zone Admin Protection",
            description="Requires AAL3 + LOW risk for administrative operations on Database Zone",
            priority="300",
            enabled=True,
            scope="DATABASE",
            conditions={"zone": "DATABASE_ZONE", "actions": ["ADMINISTER", "EXECUTE"]},
            decision=PolicyDecision.VERIFY,
            required_assurance=AuthenticationAssuranceLevel.AAL3,
            actions=["REQUIRE_2FA", "REQUIRE_BIOMETRIC"],
            created_at=now,
        )

        # Policy 5: Normal Low-Risk Allow Policy
        p5 = Policy(
            policy_id="pol_low_risk_allow",
            name="Low Risk Standard Access Allow",
            description="Allows standard access for authenticated users with low risk (< 0.30)",
            priority="100",
            enabled=True,
            scope="GLOBAL",
            conditions={"max_risk": 0.30},
            decision=PolicyDecision.ALLOW,
            required_assurance=AuthenticationAssuranceLevel.AAL1,
            actions=["ALLOW"],
            created_at=now,
        )

        for p in [p1, p2, p3, p4, p5]:
            self._policies[p.policy_id] = p

    def evaluate_decision(self, context: ZeroTrustDecisionContext) -> PolicyDecisionRecord:
        """
        Evaluates dynamic security context against declarative policies, micro-segmentation, and AAL requirements.
        Returns auditable PolicyDecisionRecord.
        """
        now = datetime.now(timezone.utc)
        dec_id = f"dec-{uuid.uuid4().hex[:12]}"
        reasons: List[str] = []
        applicable_policies: List[Policy] = []
        candidate_decisions: List[Tuple[PolicyDecision, int, str]] = []  # (decision, priority, policy_id)

        # 1. Derive Dynamic Security Tags & Groups
        derived_tags = self.tag_manager.derive_security_tags(
            entity_id=context.subject_id,
            current_risk=context.current_risk,
            identity_state=context.identity_state,
        )
        tag_names = [t.tag for t in derived_tags]
        security_groups = self.tag_manager.evaluate_security_groups(derived_tags, context.current_risk)

        # 2. Evaluate Logical Micro-Segmentation
        micro_dec, micro_reason = self.micro_segment_engine.evaluate_micro_segment(
            subject_zone=context.security_zone,
            target_zone=SecurityZoneName.APPLICATION_ZONE,  # Target resource zone
            subject_groups=security_groups,
            requested_action=context.requested_action,
            assurance=context.subject_type == "ADMIN" and AuthenticationAssuranceLevel.AAL2 or AuthenticationAssuranceLevel.AAL1,
            is_compromised="COMPROMISED" in tag_names,
        )

        candidate_decisions.append((micro_dec, 250, "micro_segmentation_rule"))
        reasons.append(micro_reason)

        # 3. Evaluate Declarative Policies
        for policy in self._policies.values():
            if not policy.enabled:
                continue

            cond = policy.conditions
            match = True

            if "min_risk" in cond and context.current_risk < cond["min_risk"]:
                match = False
            if "max_risk" in cond and context.current_risk > cond["max_risk"]:
                match = False
            if "min_uncertainty" in cond and context.uncertainty < cond["min_uncertainty"]:
                match = False
            if "required_tags" in cond and not any(t in tag_names for t in cond["required_tags"]):
                match = False
            if "actions" in cond and context.requested_action.value not in cond["actions"]:
                match = False

            if match:
                applicable_policies.append(policy)
                prio = int(policy.priority) if isinstance(policy.priority, (int, str)) and str(policy.priority).isdigit() else 100
                candidate_decisions.append((policy.decision, prio, policy.policy_id))
                reasons.append(f"Matched declarative policy '{policy.name}' ({policy.policy_id}).")

        # 4. Resolve Conflicts using Precedence: BLOCK > QUARANTINE > VERIFY > MONITOR > ALLOW
        precedence_map = {
            PolicyDecision.BLOCK: 50,
            PolicyDecision.QUARANTINE: 40,
            PolicyDecision.VERIFY: 30,
            PolicyDecision.MONITOR: 20,
            PolicyDecision.ALLOW: 10,
        }

        winning_decision = PolicyDecision.ALLOW
        highest_weight = -1

        for dec, prio, pol_id in candidate_decisions:
            weight = precedence_map[dec] * 1000 + prio
            if weight > highest_weight:
                highest_weight = weight
                winning_decision = dec

        # 5. Check Assurance Requirements for VERIFY decision
        if winning_decision == PolicyDecision.VERIFY:
            if context.two_factor_state == "VERIFIED":
                winning_decision = PolicyDecision.ALLOW
                reasons.append("Step-up 2FA verification successfully satisfied; granting ALLOW.")
            else:
                reasons.append("Step-up 2FA verification required before authorization.")

        # 6. Safety Boundary Enforcement Mode
        enforcement_status = "SIMULATED"
        if self.enforcement_mode == EnforcementMode.DRY_RUN:
            enforcement_status = "DRY_RUN_LOGGED"
            reasons.append("Safety Boundary Active: Executed in DRY_RUN mode. No real infrastructure mutation.")
        elif self.enforcement_mode == EnforcementMode.SIMULATION:
            enforcement_status = "SIMULATION_PASSED"
        elif self.enforcement_mode == EnforcementMode.CONTROLLED_ENFORCEMENT:
            enforcement_status = "ENFORCED"

        explanation = (
            f"Zero-Trust Decision for Subject '{context.subject_id}' on Resource '{context.resource_id}' "
            f"Action '{context.requested_action.value}': Final Decision = {winning_decision.value} "
            f"(Cyber Risk: {context.current_risk:.2f}, Uncertainty: {context.uncertainty:.2f}, Enforcement: {self.enforcement_mode.value})."
        )

        return PolicyDecisionRecord(
            decision_id=dec_id,
            subject_id=context.subject_id,
            resource_id=context.resource_id,
            requested_action=context.requested_action,
            decision=winning_decision,
            cyber_risk_score=context.current_risk,
            confidence=round(1.0 - context.uncertainty, 4),
            uncertainty=context.uncertainty,
            evidence_ids=[],
            applicable_policy_ids=[p.policy_id for p in applicable_policies],
            policy_versions={p.policy_id: p.version for p in applicable_policies},
            security_tags=tag_names,
            security_groups=security_groups,
            security_zone=context.security_zone,
            authentication_assurance=AuthenticationAssuranceLevel.AAL1,
            enforcement_mode=self.enforcement_mode,
            enforcement_status=enforcement_status,
            explanation=explanation,
            reasons=reasons,
            timestamp=now,
            engine_version=self.engine_version,
        )
