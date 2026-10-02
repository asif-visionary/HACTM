"""
Orchestration Engine Service.
Orchestrates agent registries, candidate generation, candidate scoring,
closed-loop agent selection decisions, invocations, and empirical research evaluation.
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from hactm.storage.repositories.orchestration_repo import OrchestrationRepository
from hactm.storage.models import (
    AgentRegistryModel,
    AgentSelectionContextModel,
    AgentSelectionDecisionModel,
    AgentSelectionCandidateModel,
    AgentInvocationModel,
    SelectionRoundModel,
    SelectionHistoryModel,
)
from hactm.orchestration.models import (
    AgentSelectionContext,
    AgentSelectionConfig,
    SelectionMethod,
    OrchestrationStrategy,
)
from hactm.orchestration.registry import AgentRegistry
from hactm.orchestration.orchestrator import AdaptiveOrchestrator
from hactm.orchestration.evaluator import OrchestrationEvaluator


from hactm.storage.database import SessionLocal, get_db

class OrchestrationService:
    """Service orchestrator for Orchestration Adaptive Evidence Orchestration."""

    def __init__(self, db: Optional[Session] = None, config: Optional[AgentSelectionConfig] = None):
        self.db = db if db is not None else SessionLocal()
        self.repo = OrchestrationRepository(self.db)
        self.config = config or AgentSelectionConfig()
        self.registry = AgentRegistry()

        # Sync registry with database records if present
        db_agents = self.repo.list_registered_agents(enabled_only=False)
        if not db_agents:
            # Seed database with initial registry
            for a in self.registry.get_all_agents(enabled_only=False):
                db_model = AgentRegistryModel(
                    agent_id=a.agent_id,
                    agent_name=a.agent_name,
                    domain=a.domain,
                    capabilities=a.capabilities,
                    supported_event_types=a.supported_event_types,
                    supported_entity_types=a.supported_entity_types,
                    supported_attack_categories=a.supported_attack_categories,
                    reliability_score=a.reliability_score,
                    reliability_lower_bound=a.reliability_lower_bound,
                    reliability_upper_bound=a.reliability_upper_bound,
                    uncertainty_profile=a.uncertainty_profile,
                    average_latency_ms=a.average_latency_ms,
                    p95_latency_ms=a.p95_latency_ms,
                    computational_cost=a.computational_cost,
                    communication_cost=a.communication_cost,
                    availability_status=a.availability_status.value if hasattr(a.availability_status, "value") else str(a.availability_status),
                    current_model_version=a.current_model_version,
                    drift_status=a.drift_status,
                    calibration_status=a.calibration_status,
                    enabled="true" if a.enabled else "false",
                )
                self.repo.save_agent_registry(db_model)

        self.orchestrator = AdaptiveOrchestrator(self.registry, self.config)
        self.evaluator = OrchestrationEvaluator()

    def get_health(self) -> Dict[str, Any]:
        agents = self.repo.list_registered_agents()
        decisions, total_decisions = self.repo.list_selection_decisions(page_size=1)
        invocations, total_invocations = self.repo.list_agent_invocations(page_size=1)

        return {
            "status": "HEALTHY",
            "phase": "ORCHESTRATION_ADAPTIVE_EVIDENCE_ORCHESTRATION",
            "registered_agents_count": len(agents),
            "decisions_count": total_decisions,
            "invocations_count": total_invocations,
            "strategy": self.config.strategy.value if hasattr(self.config.strategy, "value") else str(self.config.strategy),
            "method": self.config.method.value if hasattr(self.config.method, "value") else str(self.config.method),
            "version": self.config.version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def list_agents(self, domain: Optional[str] = None, availability_status: Optional[str] = None, enabled_only: bool = True) -> List[Dict[str, Any]]:
        agents = self.repo.list_registered_agents(domain=domain, availability_status=availability_status)
        if not agents:
            # Fallback to in-memory registry
            mem_agents = self.registry.get_all_agents(enabled_only=enabled_only)
            if domain:
                mem_agents = [a for a in mem_agents if a.domain.lower() == domain.lower()]
            return [a.model_dump() for a in mem_agents]
        return [self._model_to_dict(a) for a in agents]

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        agent = self.repo.get_registered_agent(agent_id)
        if not agent:
            mem_a = self.registry.get_agent(agent_id)
            return mem_a.model_dump() if mem_a else None
        return self._model_to_dict(agent)

    def get_candidates(self, context: AgentSelectionContext) -> List[Dict[str, Any]]:
        records = self.orchestrator.candidate_generator.generate_candidates(context)
        return [r.model_dump() for r in records]

    def select_agents(
        self,
        context: AgentSelectionContext,
        config: Optional[AgentSelectionConfig] = None,
    ) -> Dict[str, Any]:
        orchestrator = self.orchestrator
        if config:
            orchestrator = AdaptiveOrchestrator(self.registry, config)
        decision = orchestrator.select_agents(context)
        return decision.model_dump()

    def list_metrics(self) -> Dict[str, Any]:
        return self.get_metrics()

    def get_metrics(self) -> Dict[str, Any]:
        agents = self.repo.list_registered_agents()
        decisions, total_dec = self.repo.list_selection_decisions()
        invs, total_inv = self.repo.list_agent_invocations()
        return {
            "total_agents": len(agents),
            "total_decisions": total_dec,
            "total_invocations": total_inv,
            "avg_invocations_per_decision": round(total_inv / max(1, total_dec), 2),
        }

    def select_agents_for_context(
        self,
        event_type: str,
        entity_ids: Optional[List[str]] = None,
        current_risk: float = 0.0,
        current_uncertainty: float = 1.0,
        missing_domains: Optional[List[str]] = None,
        latency_budget_ms: float = 1000.0,
        selection_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes dynamic agent selection decision for incoming context payload.
        Saves Context, Decision, Candidates, and History in database.
        """
        now = datetime.now(timezone.utc)
        ctx_id = f"ctx-{uuid.uuid4().hex[:12]}"

        ctx_pyd = AgentSelectionContext(
            context_id=ctx_id,
            event_id=f"ev-{uuid.uuid4().hex[:8]}",
            entity_ids=entity_ids or ["usr-001"],
            event_type=event_type,
            domains_observed=[],
            current_risk=current_risk,
            current_uncertainty=current_uncertainty,
            missing_domains=missing_domains or [],
            latency_budget_ms=latency_budget_ms,
            timestamp=now,
        )

        # Save Context Model
        ctx_db = AgentSelectionContextModel(
            context_id=ctx_pyd.context_id,
            event_id=ctx_pyd.event_id,
            entity_ids=ctx_pyd.entity_ids,
            event_type=ctx_pyd.event_type,
            domains_observed=ctx_pyd.domains_observed,
            current_risk=ctx_pyd.current_risk,
            current_uncertainty=ctx_pyd.current_uncertainty,
            evidence_count=ctx_pyd.evidence_count,
            evidence_quality=ctx_pyd.evidence_quality,
            missing_domains=ctx_pyd.missing_domains,
            latency_budget_ms=ctx_pyd.latency_budget_ms,
            created_at=now,
        )
        self.repo.save_selection_context(ctx_db)

        # Execute Decision via Orchestrator
        method_enum = SelectionMethod(selection_method) if selection_method else self.config.method
        decision_pyd = self.orchestrator.select_agents(ctx_pyd, method=method_enum)

        # Save Decision Model
        dec_db = AgentSelectionDecisionModel(
            decision_id=decision_pyd.decision_id,
            context_id=decision_pyd.context_id,
            candidate_agents=decision_pyd.candidate_agents,
            selected_agents=decision_pyd.selected_agents,
            selection_method=decision_pyd.selection_method.value if hasattr(decision_pyd.selection_method, "value") else str(decision_pyd.selection_method),
            selection_scores=decision_pyd.selection_scores,
            expected_total_gain=decision_pyd.expected_total_gain,
            expected_total_cost=decision_pyd.expected_total_cost,
            expected_latency=decision_pyd.expected_latency,
            stopping_reason=decision_pyd.stopping_reason.value if hasattr(decision_pyd.stopping_reason, "value") else str(decision_pyd.stopping_reason),
            configuration_version=decision_pyd.configuration_version,
            created_at=now,
        )
        saved_dec = self.repo.save_selection_decision(dec_db)

        # Save Candidate Score Breakdown
        candidate_models = []
        for cand in decision_pyd.candidate_details:
            candidate_models.append(
                AgentSelectionCandidateModel(
                    decision_id=decision_pyd.decision_id,
                    agent_id=cand.agent_id,
                    relevance_score=cand.relevance_score,
                    reliability_score=cand.reliability_score,
                    expected_gain=cand.expected_gain,
                    cost_score=cand.cost_score,
                    latency_score=cand.latency_score,
                    diversity_score=cand.diversity_score,
                    redundancy_penalty=cand.redundancy_penalty,
                    final_score=cand.final_score,
                    selected="true" if cand.agent_id in decision_pyd.selected_agents else "false",
                )
            )
        self.repo.save_candidate_scores(candidate_models)

        res_dict = self._model_to_dict(saved_dec)
        res_dict["candidate_details"] = [c.model_dump() for c in decision_pyd.candidate_details]
        return res_dict

    def execute_closed_loop_acquisition(
        self,
        event_type: str,
        entity_ids: Optional[List[str]] = None,
        max_rounds: int = 3,
    ) -> Dict[str, Any]:
        """
        Executes full closed-loop evidence acquisition across multiple selection rounds.
        """
        now = datetime.now(timezone.utc)
        ctx_id = f"ctx-{uuid.uuid4().hex[:12]}"
        ctx_pyd = AgentSelectionContext(
            context_id=ctx_id,
            event_id=f"ev-{uuid.uuid4().hex[:8]}",
            entity_ids=entity_ids or ["usr-001"],
            event_type=event_type,
            current_risk=0.45,
            current_uncertainty=0.85,
            missing_domains=["identity", "transaction"],
            latency_budget_ms=1000.0,
            timestamp=now,
        )

        decision_pyd, rounds, invocations = self.orchestrator.execute_closed_loop_orchestration(ctx_pyd, max_rounds=max_rounds)

        # Persist Invocation Records
        for inv in invocations:
            inv_db = AgentInvocationModel(
                invocation_id=inv.invocation_id,
                context_id=inv.context_id,
                agent_id=inv.agent_id,
                selection_round=inv.selection_round,
                selection_score=inv.selection_score,
                expected_gain=inv.expected_gain,
                actual_gain=inv.actual_gain,
                uncertainty_before=inv.uncertainty_before,
                uncertainty_after=inv.uncertainty_after,
                risk_before=inv.risk_before,
                risk_after=inv.risk_after,
                actual_cost=inv.actual_cost,
                actual_latency=inv.actual_latency,
                invocation_status=inv.invocation_status,
                created_at=inv.created_at,
            )
            self.repo.save_agent_invocation(inv_db)

        # Persist Rounds
        for rnd in rounds:
            rnd_db = SelectionRoundModel(
                round_id=rnd.round_id,
                context_id=rnd.context_id,
                round_number=rnd.round_number,
                selected_agent=rnd.selected_agent,
                selection_score=rnd.selection_score,
                expected_gain=rnd.expected_gain,
                actual_gain=rnd.actual_gain,
                cost=rnd.cost,
                latency=rnd.latency,
                resulting_uncertainty=rnd.resulting_uncertainty,
                resulting_risk=rnd.resulting_risk,
                created_at=rnd.created_at,
            )
            self.repo.save_selection_round(rnd_db)

        return {
            "context_id": ctx_id,
            "decision": decision_pyd.model_dump(),
            "rounds": [r.model_dump() for r in rounds],
            "invocations": [i.model_dump() for i in invocations],
        }

    def list_decisions(self, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_selection_decisions(page=page, page_size=page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        decision = self.repo.get_selection_decision(decision_id)
        if not decision:
            return None
        res = self._model_to_dict(decision)
        cands = self.repo.get_candidates_for_decision(decision_id)
        res["candidate_details"] = [self._model_to_dict(c) for c in cands]
        return res

    def list_invocations(self, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_agent_invocations(page=page, page_size=page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def list_history(self, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_selection_history(page=page, page_size=page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def run_research_evaluation(self, num_events: int = 10) -> Dict[str, Any]:
        return self.evaluator.run_all_evaluations(num_events=num_events)

    def _model_to_dict(self, model_inst: Any) -> Dict[str, Any]:
        if not model_inst:
            return {}
        res = {}
        for col in model_inst.__table__.columns.keys():
            val = getattr(model_inst, col)
            if isinstance(val, datetime):
                res[col] = val.isoformat()
            else:
                res[col] = val
        return res
