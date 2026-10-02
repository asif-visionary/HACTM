"""
Orchestration Candidate Scoring Engine.
Computes multi-dimensional selection score combining relevance, expected information gain,
reliability, uncertainty, temporal context, attack-chain candidates, diversity, redundancy, cost, and latency.
"""

from typing import Dict, List, Any, Optional, Tuple
from hactm.orchestration.models import (
    AgentRecord,
    AgentSelectionContext,
    SelectionScore,
    AgentSelectionConfig,
)
from hactm.orchestration.information_gain import InformationGainEstimator


class CandidateScoringEngine:
    """Multi-dimensional Agent Candidate Scoring Engine for Orchestration."""

    def __init__(self, config: Optional[AgentSelectionConfig] = None):
        self.config = config or AgentSelectionConfig()
        self.gain_estimator = InformationGainEstimator()

    def score_candidate(
        self,
        agent: AgentRecord,
        context: AgentSelectionContext,
        previous_selections: Optional[List[str]] = None,
    ) -> SelectionScore:
        """
        Calculates complete SelectionScore for a candidate agent given current context.
        """
        prev_calls = set(previous_selections or context.previous_agent_calls or [])
        reason_codes = []

        # 1. Contextual Relevance
        rel_score = 0.50
        event_type = (context.event_type or "").lower()
        if any(e.lower() in event_type or event_type in e.lower() for e in agent.supported_event_types):
            rel_score += 0.35
            reason_codes.append("DIRECT_EVENT_MATCH")

        if agent.domain.lower() in (d.lower() for d in context.missing_domains or []):
            rel_score += 0.25
            reason_codes.append("MISSING_DOMAIN_COVERAGE")

        relevance_score = max(0.0, min(1.0, round(rel_score, 4)))

        # 2. Expected Information Gain
        gain_obj = self.gain_estimator.estimate_expected_gain(agent, context)
        expected_gain = gain_obj.estimated_gain
        if expected_gain >= 0.30:
            reason_codes.append("HIGH_EXPECTED_GAIN")

        # 3. Reliability & Calibration (Reliability & Trust)
        reliability_score = agent.reliability_score
        if agent.calibration_status == "CALIBRATED":
            reason_codes.append("CALIBRATION_VALIDATED")
        elif agent.calibration_status == "CALIBRATION_REQUIRED":
            reliability_score *= 0.85

        # 4. Drift Penalty (Reliability & Trust)
        drift_penalty = 0.0
        if agent.drift_status == "DRIFT_OBSERVED":
            drift_penalty = 0.20
            reason_codes.append("DRIFT_PENALIZED")

        # 5. Temporal Relevance (Adaptive Memory & Graph)
        temporal_rel = 0.50
        temp_ctx = context.temporal_context or {}
        if temp_ctx.get("recent_event_count", 0) > 0 and agent.domain in temp_ctx.get("domains_in_window", []):
            temporal_rel = 0.85
            reason_codes.append("TEMPORAL_CONTEXT_MATCH")

        # 6. Attack-Chain Relevance (Adaptive Memory & Graph)
        chain_rel = 0.50
        for chain in context.attack_chain_candidates or []:
            for stage in chain.get("stages", []):
                if stage.get("domain", "").lower() == agent.domain.lower():
                    chain_rel = 0.90
                    reason_codes.append("ATTACK_CHAIN_STAGE_MATCH")
                    break

        # 7. Evidence Diversity & Redundancy Penalty
        diversity_score = 0.70
        redundancy_penalty = 0.0

        if agent.agent_id in prev_calls:
            redundancy_penalty = 0.60
            reason_codes.append("RECENT_CALL_REDUNDANCY_PENALTY")

        domain_call_count = sum(1 for call in prev_calls if call.startswith(agent.domain))
        if domain_call_count > 0:
            redundancy_penalty = max(redundancy_penalty, 0.40)
            reason_codes.append("SAME_DOMAIN_REDUNDANCY_PENALTY")

        # 8. Execution & Communication Cost Penalty
        cost_total = agent.computational_cost + agent.communication_cost
        cost_score = max(0.10, min(1.0, cost_total / 3.0))

        # 9. Latency Penalty vs Budget
        lat_budget = context.latency_budget_ms or 1000.0
        latency_score = max(0.10, min(1.0, agent.average_latency_ms / lat_budget))
        if agent.average_latency_ms > lat_budget:
            reason_codes.append("LATENCY_BUDGET_EXCEEDED_PENALTY")

        # Weighted Final Score Calculation
        w = self.config.weights
        w_rel = w.get("relevance", 0.25)
        w_gain = w.get("expected_information_gain", 0.25)
        w_trust = w.get("reliability", 0.15)
        w_temp = w.get("temporal_relevance", 0.10)
        w_chain = w.get("chain_relevance", 0.10)
        w_div = w.get("diversity", 0.05)
        w_red = w.get("redundancy_penalty", 0.10)
        w_cost = w.get("cost_penalty", 0.10)
        w_lat = w.get("latency_penalty", 0.10)

        raw_score = (
            w_rel * relevance_score
            + w_gain * expected_gain
            + w_trust * reliability_score
            + w_temp * temporal_rel
            + w_chain * chain_rel
            + w_div * diversity_score
            - w_red * redundancy_penalty
            - w_cost * (cost_score * 0.30)
            - w_lat * (latency_score * 0.30)
            - drift_penalty
        )

        final_score = max(0.05, min(0.99, round(raw_score, 4)))

        # Explanation sentence
        explanation = f"Selected candidate '{agent.agent_id}' with final score {final_score:.4f} (Relevance: {relevance_score:.2f}, Expected Gain: {expected_gain:.2f}, Reliability: {reliability_score:.2f}, Cost: {cost_total:.1f} units)."

        return SelectionScore(
            agent_id=agent.agent_id,
            relevance_score=relevance_score,
            reliability_score=round(reliability_score, 4),
            expected_gain=expected_gain,
            cost_score=round(cost_score, 4),
            latency_score=round(latency_score, 4),
            diversity_score=round(diversity_score, 4),
            redundancy_penalty=round(redundancy_penalty, 4),
            final_score=final_score,
            reason_codes=reason_codes,
            explanation=explanation,
        )

    def score_candidates(
        self,
        agents: List[AgentRecord],
        context: AgentSelectionContext,
        previous_selections: Optional[List[str]] = None,
    ) -> List[SelectionScore]:
        """
        Calculates SelectionScore for a list of candidate agents and returns sorted by final_score desc.
        """
        scores = [self.score_candidate(a, context, previous_selections=previous_selections) for a in agents]
        scores.sort(key=lambda s: s.final_score, reverse=True)
        return scores
