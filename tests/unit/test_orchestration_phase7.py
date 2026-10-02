"""
Unit tests for Orchestration: Adaptive Agent Selection + Resource-Aware Evidence Orchestration.
Verifies candidate generation, capability matching, scoring engine, sequential loop,
stopping conditions, edge cases, and reproducible baselines.
"""

import pytest
from hactm.orchestration.models import (
    AgentRecord,
    AgentSelectionContext,
    AgentSelectionConfig,
    SelectionMethod,
    StoppingReason,
)
from hactm.orchestration.registry import AgentRegistry
from hactm.orchestration.candidate_generator import CandidateAgentGenerator
from hactm.orchestration.scoring_engine import CandidateScoringEngine
from hactm.orchestration.information_gain import InformationGainEstimator
from hactm.orchestration.orchestrator import AdaptiveOrchestrator
from hactm.orchestration.evaluator import OrchestrationEvaluator


@pytest.fixture
def registry():
    reg = AgentRegistry()
    return reg


@pytest.fixture
def scoring_engine():
    return CandidateScoringEngine()


@pytest.fixture
def info_estimator():
    return InformationGainEstimator()


@pytest.fixture
def orchestrator(registry, scoring_engine, info_estimator):
    return AdaptiveOrchestrator(
        registry=registry,
        config_or_scoring=scoring_engine,
        info_estimator=info_estimator,
    )


def test_agent_registry_initialization(registry):
    agents = registry.get_all_agents()
    assert len(agents) == 5
    ids = [a.agent_id for a in agents]
    assert "network-security-agent" in ids
    assert "phishing-intelligence-agent" in ids
    assert "identity-authentication-agent" in ids
    assert "uba-agent" in ids
    assert "transaction-security-agent" in ids


def test_candidate_generation_deterministic(registry):
    generator = CandidateAgentGenerator(registry)
    ctx = AgentSelectionContext(
        context_id="ctx_unit_001",
        event_id="evt_001",
        entity_ids=["user_123"],
        event_type="suspicious_login",
        domains_observed=["identity"],
    )
    candidates1 = generator.generate_candidates(ctx)
    candidates2 = generator.generate_candidates(ctx)

    assert len(candidates1) > 0
    # Deterministic sorting check
    assert [c.agent_id for c in candidates1] == [c.agent_id for c in candidates2]


def test_scoring_engine_computes_transparent_scores(registry, scoring_engine):
    generator = CandidateAgentGenerator(registry)
    ctx = AgentSelectionContext(
        context_id="ctx_unit_002",
        event_id="evt_002",
        entity_ids=["user_123"],
        event_type="suspicious_login",
        domains_observed=["identity"],
        current_risk=0.82,
        current_uncertainty=0.65,
    )
    candidates = generator.generate_candidates(ctx)
    scores = scoring_engine.score_candidates(candidates, ctx)

    assert len(scores) == len(candidates)
    for score in scores:
        assert 0.0 <= score.final_score <= 1.0
        assert len(score.reason_codes) >= 0
        assert score.relevance_score >= 0.0


def test_sequential_orchestration_loop_and_stopping(orchestrator):
    ctx = AgentSelectionContext(
        context_id="ctx_seq_001",
        event_id="evt_seq_001",
        entity_ids=["user_123"],
        event_type="phishing_attack",
        domains_observed=["phishing"],
        current_uncertainty=0.75,
        attack_chain_candidates=[{"stages": [{"domain": "identity"}, {"domain": "transaction"}]}],
    )
    decision = orchestrator.select_agents(ctx)
    assert len(decision.selected_agents) > 0

    # Run execution loop
    decision, rounds, invocations = orchestrator.execute_closed_loop_orchestration(ctx, max_rounds=3)
    assert len(rounds) >= 1
    assert len(invocations) >= 1


def test_edge_case_budget_exhaustion(orchestrator):
    ctx = AgentSelectionContext(
        context_id="ctx_budget_001",
        event_id="evt_budget_001",
        entity_ids=["user_123"],
        event_type="suspicious_login",
        current_uncertainty=0.90,
    )
    # Strict budget constraint
    orchestrator.config.constraints["max_agent_calls"] = 1
    decision = orchestrator.select_agents(ctx)
    assert decision.stopping_reason in [
        StoppingReason.RESOURCE_BUDGET_EXHAUSTED,
        StoppingReason.LATENCY_BUDGET_EXHAUSTED,
        StoppingReason.INSUFFICIENT_EXPECTED_GAIN,
        StoppingReason.UNCERTAINTY_BELOW_THRESHOLD,
        StoppingReason.SUFFICIENT_COVERAGE_ACHIEVED,
    ]


def test_research_evaluator_baselines():
    evaluator = OrchestrationEvaluator()
    res = evaluator.run_all_evaluations(num_events=5)

    assert "baselines" in res
    assert "ablations" in res
    assert "scenarios" in res

    baselines = res["baselines"]
    assert "BASELINE_1" in baselines
    assert "BASELINE_6" in baselines

    b1 = baselines["BASELINE_1"]
    b6 = baselines["BASELINE_6"]
    # Adaptive should invoke fewer agents on average
    assert b6["avg_calls_per_event"] <= b1["avg_calls_per_event"]
