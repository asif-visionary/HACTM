"""
Unit tests for Zero-Trust Engine: Zero-Trust Policy Decision, Dynamic Security Context,
Micro-Segmentation, Step-Up Verification, and Policy Precedence.
"""

import pytest
from hactm.zerotrust.models import (
    ZeroTrustDecisionContext,
    PolicyDecision,
    EnforcementMode,
    SubjectType,
    ResourceType,
    ActionType,
    SecurityZoneName,
    AuthenticationAssuranceLevel,
)
from hactm.zerotrust.policy_engine import ZeroTrustPolicyEngine
from hactm.zerotrust.tags_and_groups import SecurityTagManager
from hactm.zerotrust.micro_segmentation import MicroSegmentationEngine
from hactm.zerotrust.simulator import ZeroTrustPolicySimulator
from hactm.zerotrust.evaluator import ZeroTrustEvaluator


@pytest.fixture
def policy_engine():
    return ZeroTrustPolicyEngine(enforcement_mode=EnforcementMode.DRY_RUN)


@pytest.fixture
def tag_manager():
    return SecurityTagManager()


@pytest.fixture
def micro_engine():
    return MicroSegmentationEngine()


def test_zero_trust_policy_engine_allow_decision(policy_engine):
    ctx = ZeroTrustDecisionContext(
        context_id="ctx_u1",
        subject_id="user_normal",
        resource_id="app_portal",
        requested_action=ActionType.READ,
        current_risk=0.15,
        uncertainty=0.05,
    )
    record = policy_engine.evaluate_decision(ctx)

    assert record.decision == PolicyDecision.ALLOW
    assert record.cyber_risk_score == 0.15
    assert record.enforcement_mode == EnforcementMode.DRY_RUN
    assert record.enforcement_status == "DRY_RUN_LOGGED"


def test_high_risk_quarantine_policy(policy_engine):
    ctx = ZeroTrustDecisionContext(
        context_id="ctx_u2",
        subject_id="user_compromised",
        resource_id="app_portal",
        requested_action=ActionType.WRITE,
        current_risk=0.85,
        uncertainty=0.10,
    )
    record = policy_engine.evaluate_decision(ctx)

    assert record.decision == PolicyDecision.QUARANTINE
    assert "COMPROMISED" in record.security_tags
    assert "group_high_risk_users" in record.security_groups


def test_step_up_2fa_verification_policy(policy_engine):
    ctx = ZeroTrustDecisionContext(
        context_id="ctx_u3",
        subject_id="user_tx",
        resource_id="service_payments",
        requested_action=ActionType.TRANSFER,
        current_risk=0.55,
        two_factor_state="NOT_REQUIRED",
    )
    record = policy_engine.evaluate_decision(ctx)

    assert record.decision == PolicyDecision.VERIFY

    # Simulate successful 2FA step-up
    ctx.two_factor_state = "VERIFIED"
    record_satisfied = policy_engine.evaluate_decision(ctx)
    assert record_satisfied.decision == PolicyDecision.ALLOW


def test_micro_segmentation_east_west_control(micro_engine):
    dec, reason = micro_engine.evaluate_micro_segment(
        subject_zone=SecurityZoneName.USER_ZONE,
        target_zone=SecurityZoneName.DATABASE_ZONE,
        subject_groups=["group_normal"],
        requested_action=ActionType.READ,
        assurance=AuthenticationAssuranceLevel.AAL1,
    )

    assert dec == PolicyDecision.BLOCK
    assert "Direct User-Zone to Database-Zone" in reason


def test_blast_radius_reduction_calculation(micro_engine):
    metrics = micro_engine.calculate_blast_radius_reduction(total_assets=100)
    assert metrics["dynamic_segmented_reachable"] == 12
    assert metrics["blast_radius_reduction_percent"] == 88.0


def test_policy_simulator(policy_engine):
    sim = ZeroTrustPolicySimulator(policy_engine)
    res = sim.simulate_decision(
        subject_id="usr_sim",
        resource_id="app_financial",
        action="TRANSFER",
        current_risk=0.65,
    )

    assert "decision_record" in res
    assert "simulated_enforcement" in res
    assert res["decision_record"]["decision"] == "VERIFY"


def test_zero_trust_research_evaluator():
    evaluator = ZeroTrustEvaluator()
    res = evaluator.run_all_evaluations(num_events=5)

    assert "baselines" in res
    assert "ablations" in res
    assert "scenarios" in res
    assert "BASELINE_D" in res["baselines"]
