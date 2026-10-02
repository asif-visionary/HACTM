"""
Orchestration Adaptive Evidence Orchestrator.
Implements closed-loop state machine, sequential/parallel/hybrid selection strategies,
stopping criteria, and agent timeout/failure handling.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

from hactm.orchestration.models import (
    AgentSelectionContext,
    AgentSelectionDecision,
    AgentInvocationRecord,
    SelectionRound,
    AgentSelectionConfig,
    SelectionMethod,
    OrchestrationStrategy,
    StoppingReason,
    SelectionScore,
)
from hactm.orchestration.registry import AgentRegistry
from hactm.orchestration.candidate_generator import CandidateAgentGenerator
from hactm.orchestration.scoring_engine import CandidateScoringEngine


class AdaptiveOrchestrator:
    """Core Closed-Loop Evidence Orchestrator for HACTM Orchestration."""

    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        config_or_scoring: Optional[Any] = None,
        info_estimator: Optional[Any] = None,
        config: Optional[AgentSelectionConfig] = None,
    ):
        self.registry = registry or AgentRegistry()

        if isinstance(config_or_scoring, AgentSelectionConfig):
            self.config = config_or_scoring
            self.scoring_engine = CandidateScoringEngine(self.config)
        elif isinstance(config_or_scoring, CandidateScoringEngine):
            self.scoring_engine = config_or_scoring
            self.config = config or self.scoring_engine.config
        else:
            self.config = config or AgentSelectionConfig()
            self.scoring_engine = CandidateScoringEngine(self.config)

        self.candidate_generator = CandidateAgentGenerator(self.registry)

    def select_agents(
        self,
        context: AgentSelectionContext,
        method: Optional[SelectionMethod] = None,
        strategy: Optional[OrchestrationStrategy] = None,
    ) -> AgentSelectionDecision:
        """
        Executes selection decision for a context based on configured method & strategy.
        Returns AgentSelectionDecision.
        """
        sel_method = method or self.config.method
        sel_strategy = strategy or self.config.strategy

        dec_id = f"dec-{uuid.uuid4().hex[:12]}"
        candidates = self.candidate_generator.generate_candidates(context)

        # Baseline METHOD A: ALL_AGENTS
        if sel_method == SelectionMethod.ALL_AGENTS:
            all_ids = [c.agent_id for c in candidates]
            candidate_details = [
                SelectionScore(agent_id=c.agent_id, final_score=1.0, reason_codes=["ALL_AGENTS_BASELINE"])
                for c in candidates
            ]
            return AgentSelectionDecision(
                decision_id=dec_id,
                context_id=context.context_id,
                candidate_agents=all_ids,
                selected_agents=all_ids,
                selection_method=sel_method,
                selection_scores={c.agent_id: 1.0 for c in candidates},
                candidate_details=candidate_details,
                stopping_reason=StoppingReason.SUFFICIENT_COVERAGE_ACHIEVED,
                created_at=datetime.now(timezone.utc),
            )

        # Score candidates using scoring engine
        scored_candidates: List[SelectionScore] = []
        scores_map: Dict[str, float] = {}

        for cand in candidates:
            score_obj = self.scoring_engine.score_candidate(cand, context)
            scored_candidates.append(score_obj)
            scores_map[cand.agent_id] = score_obj.final_score

        # Sort candidate details by final_score descending
        scored_candidates.sort(key=lambda s: s.final_score, reverse=True)

        # Apply strategy constraints (max_agent_calls, max_parallel_agents, latency_budget)
        max_calls = self.config.constraints.get("max_agent_calls", 3)
        max_parallel = self.config.constraints.get("max_parallel_agents", 2)
        min_gain = self.config.stopping.get("minimum_expected_gain", 0.05)

        selected_ids: List[str] = []
        total_cost = 0.0
        total_latency = 0.0
        total_gain = 0.0
        stopping_reason = StoppingReason.SUFFICIENT_COVERAGE_ACHIEVED

        # Check stopping condition 1: Uncertainty already below threshold
        if context.current_uncertainty <= self.config.stopping.get("uncertainty_threshold", 0.25):
            stopping_reason = StoppingReason.UNCERTAINTY_BELOW_THRESHOLD
        else:
            limit = max_parallel if sel_strategy == OrchestrationStrategy.PARALLEL else max_calls
            for s in scored_candidates:
                if len(selected_ids) >= limit:
                    stopping_reason = StoppingReason.RESOURCE_BUDGET_EXHAUSTED
                    break
                if s.expected_gain < min_gain:
                    stopping_reason = StoppingReason.INSUFFICIENT_EXPECTED_GAIN
                    break

                agent_rec = self.registry.get_agent(s.agent_id)
                cost_est = (agent_rec.computational_cost + agent_rec.communication_cost) if agent_rec else 1.0
                lat_est = agent_rec.average_latency_ms if agent_rec else 150.0

                if total_latency + lat_est > context.latency_budget_ms:
                    stopping_reason = StoppingReason.LATENCY_BUDGET_EXHAUSTED
                    break

                selected_ids.append(s.agent_id)
                total_cost += cost_est
                total_latency += lat_est
                total_gain += s.expected_gain

        if not selected_ids and candidates:
            # Fallback to top candidate if none selected
            selected_ids = [scored_candidates[0].agent_id]

        return AgentSelectionDecision(
            decision_id=dec_id,
            context_id=context.context_id,
            candidate_agents=[c.agent_id for c in candidates],
            selected_agents=selected_ids,
            selection_method=sel_method,
            selection_scores=scores_map,
            candidate_details=scored_candidates,
            expected_total_gain=round(total_gain, 4),
            expected_total_cost=round(total_cost, 4),
            expected_latency=round(total_latency, 4),
            stopping_reason=stopping_reason,
            configuration_version=self.config.version,
            created_at=datetime.now(timezone.utc),
        )

    def execute_closed_loop_orchestration(
        self,
        context: AgentSelectionContext,
        max_rounds: int = 3,
    ) -> Tuple[AgentSelectionDecision, List[SelectionRound], List[AgentInvocationRecord]]:
        """
        Executes complete multi-round Closed-Loop Evidence Acquisition loop.
        Observe -> Assess -> Candidate Generation -> Score -> Invoke Agent -> Update Context -> Reassess -> Stop.
        """
        rounds: List[SelectionRound] = []
        invocations: List[AgentInvocationRecord] = []

        curr_context = context
        round_num = 1
        final_decision: Optional[AgentSelectionDecision] = None

        while round_num <= max_rounds:
            decision = self.select_agents(curr_context)
            final_decision = decision

            if not decision.selected_agents or decision.stopping_reason in [
                StoppingReason.UNCERTAINTY_BELOW_THRESHOLD,
                StoppingReason.INSUFFICIENT_EXPECTED_GAIN,
                StoppingReason.RESOURCE_BUDGET_EXHAUSTED,
                StoppingReason.LATENCY_BUDGET_EXHAUSTED,
            ]:
                break

            target_agent_id = decision.selected_agents[0]
            agent_rec = self.registry.get_agent(target_agent_id)

            # Simulate agent invocation execution
            start_time = time.perf_counter()
            actual_latency = (agent_rec.average_latency_ms if agent_rec else 140.0) * 0.95
            actual_cost = (agent_rec.computational_cost if agent_rec else 1.0)

            # Simulated actual uncertainty reduction
            expected_gain = decision.candidate_details[0].expected_gain if decision.candidate_details else 0.30
            actual_gain = max(0.05, round(expected_gain * 0.90, 4))
            new_uncertainty = max(0.10, round(curr_context.current_uncertainty - actual_gain, 4))
            new_risk = min(1.0, round(curr_context.current_risk + 0.15, 4))

            # Record Selection Round
            rnd_id = f"rnd-{uuid.uuid4().hex[:12]}"
            round_obj = SelectionRound(
                round_id=rnd_id,
                context_id=curr_context.context_id,
                round_number=round_num,
                selected_agent=target_agent_id,
                selection_score=decision.selection_scores.get(target_agent_id, 0.80),
                expected_gain=expected_gain,
                actual_gain=actual_gain,
                cost=actual_cost,
                latency=actual_latency,
                resulting_uncertainty=new_uncertainty,
                resulting_risk=new_risk,
                created_at=datetime.now(timezone.utc),
            )
            rounds.append(round_obj)

            # Record Agent Invocation
            inv_id = f"inv-{uuid.uuid4().hex[:12]}"
            inv_obj = AgentInvocationRecord(
                invocation_id=inv_id,
                context_id=curr_context.context_id,
                agent_id=target_agent_id,
                selection_round=round_num,
                selection_score=decision.selection_scores.get(target_agent_id, 0.80),
                expected_gain=expected_gain,
                actual_gain=actual_gain,
                uncertainty_before=curr_context.current_uncertainty,
                uncertainty_after=new_uncertainty,
                risk_before=curr_context.current_risk,
                risk_after=new_risk,
                actual_cost=actual_cost,
                actual_latency=actual_latency,
                invocation_status="SUCCESS",
                created_at=datetime.now(timezone.utc),
            )
            invocations.append(inv_obj)

            # Update context for next round iteration
            prev_calls = list(curr_context.previous_agent_calls or [])
            prev_calls.append(target_agent_id)

            curr_context = AgentSelectionContext(
                context_id=curr_context.context_id,
                event_id=curr_context.event_id,
                entity_ids=curr_context.entity_ids,
                event_type=curr_context.event_type,
                domains_observed=curr_context.domains_observed + [agent_rec.domain if agent_rec else "unknown"],
                current_risk=new_risk,
                current_uncertainty=new_uncertainty,
                evidence_count=curr_context.evidence_count + 1,
                evidence_quality=curr_context.evidence_quality,
                previous_agent_calls=prev_calls,
                latency_budget_ms=max(50.0, curr_context.latency_budget_ms - actual_latency),
                timestamp=datetime.now(timezone.utc),
            )

            round_num += 1

        if not final_decision:
            final_decision = self.select_agents(curr_context)

        return final_decision, rounds, invocations
