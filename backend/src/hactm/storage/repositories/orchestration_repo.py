"""
Database Repository for Orchestration Agent Registry, Selection Decisions, Candidates, and Invocations.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from hactm.storage.models import (
    AgentRegistryModel,
    AgentCapabilityModel,
    AgentSelectionContextModel,
    AgentSelectionDecisionModel,
    AgentSelectionCandidateModel,
    AgentInvocationModel,
    SelectionRoundModel,
    InformationGainEstimateModel,
    AgentCostProfileModel,
    OrchestrationMetricsModel,
    SelectionHistoryModel,
)


class OrchestrationRepository:
    """SQLAlchemy Repository for Orchestration Engine Tables."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------
    # Agent Registry & Capabilities
    # ------------------------------------------------------------
    def save_agent_registry(self, record: AgentRegistryModel) -> AgentRegistryModel:
        existing = self.db.query(AgentRegistryModel).filter(
            AgentRegistryModel.agent_id == record.agent_id
        ).first()
        if existing:
            for col in AgentRegistryModel.__table__.columns.keys():
                setattr(existing, col, getattr(record, col))
            existing.last_updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record

    def get_registered_agent(self, agent_id: str) -> Optional[AgentRegistryModel]:
        return self.db.query(AgentRegistryModel).filter(
            AgentRegistryModel.agent_id == agent_id
        ).first()

    def list_registered_agents(
        self,
        domain: Optional[str] = None,
        availability_status: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[AgentRegistryModel]:
        query = self.db.query(AgentRegistryModel)
        if domain:
            query = query.filter(AgentRegistryModel.domain == domain)
        if availability_status:
            query = query.filter(AgentRegistryModel.availability_status == availability_status)
        if enabled_only:
            query = query.filter(AgentRegistryModel.enabled == "true")

        return query.order_by(AgentRegistryModel.agent_id).all()

    # ------------------------------------------------------------
    # Selection Context
    # ------------------------------------------------------------
    def save_selection_context(self, record: AgentSelectionContextModel) -> AgentSelectionContextModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_selection_context(self, context_id: str) -> Optional[AgentSelectionContextModel]:
        return self.db.query(AgentSelectionContextModel).filter(
            AgentSelectionContextModel.context_id == context_id
        ).first()

    # ------------------------------------------------------------
    # Selection Decisions & Candidates
    # ------------------------------------------------------------
    def save_selection_decision(self, record: AgentSelectionDecisionModel) -> AgentSelectionDecisionModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_selection_decision(self, decision_id: str) -> Optional[AgentSelectionDecisionModel]:
        return self.db.query(AgentSelectionDecisionModel).filter(
            AgentSelectionDecisionModel.decision_id == decision_id
        ).first()

    def list_selection_decisions(
        self,
        context_id: Optional[str] = None,
        selection_method: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AgentSelectionDecisionModel], int]:
        query = self.db.query(AgentSelectionDecisionModel)
        if context_id:
            query = query.filter(AgentSelectionDecisionModel.context_id == context_id)
        if selection_method:
            query = query.filter(AgentSelectionDecisionModel.selection_method == selection_method)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(AgentSelectionDecisionModel.created_at)).offset(offset).limit(page_size).all()
        return items, total

    def save_candidate_scores(self, candidates: List[AgentSelectionCandidateModel]):
        self.db.add_all(candidates)
        self.db.commit()

    def get_candidates_for_decision(self, decision_id: str) -> List[AgentSelectionCandidateModel]:
        return self.db.query(AgentSelectionCandidateModel).filter(
            AgentSelectionCandidateModel.decision_id == decision_id
        ).order_by(desc(AgentSelectionCandidateModel.final_score)).all()

    # ------------------------------------------------------------
    # Agent Invocations & Selection Rounds
    # ------------------------------------------------------------
    def save_agent_invocation(self, record: AgentInvocationModel) -> AgentInvocationModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_agent_invocations(
        self,
        context_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AgentInvocationModel], int]:
        query = self.db.query(AgentInvocationModel)
        if context_id:
            query = query.filter(AgentInvocationModel.context_id == context_id)
        if agent_id:
            query = query.filter(AgentInvocationModel.agent_id == agent_id)
        if status:
            query = query.filter(AgentInvocationModel.invocation_status == status)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(AgentInvocationModel.created_at)).offset(offset).limit(page_size).all()
        return items, total

    def save_selection_round(self, record: SelectionRoundModel) -> SelectionRoundModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_rounds_for_context(self, context_id: str) -> List[SelectionRoundModel]:
        return self.db.query(SelectionRoundModel).filter(
            SelectionRoundModel.context_id == context_id
        ).order_by(asc(SelectionRoundModel.round_number)).all()

    # ------------------------------------------------------------
    # Information Gain Estimates & Cost Profiles
    # ------------------------------------------------------------
    def save_gain_estimate(self, record: InformationGainEstimateModel) -> InformationGainEstimateModel:
        existing = self.db.query(InformationGainEstimateModel).filter(
            InformationGainEstimateModel.agent_id == record.agent_id,
            InformationGainEstimateModel.event_type == record.event_type,
        ).first()

        if existing:
            existing.average_uncertainty_reduction = record.average_uncertainty_reduction
            existing.median_uncertainty_reduction = record.median_uncertainty_reduction
            existing.sample_count += 1
            existing.last_updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record

    def get_gain_estimate(self, agent_id: str, event_type: str) -> Optional[InformationGainEstimateModel]:
        return self.db.query(InformationGainEstimateModel).filter(
            InformationGainEstimateModel.agent_id == agent_id,
            InformationGainEstimateModel.event_type == event_type,
        ).first()

    def save_cost_profile(self, record: AgentCostProfileModel) -> AgentCostProfileModel:
        existing = self.db.query(AgentCostProfileModel).filter(
            AgentCostProfileModel.agent_id == record.agent_id
        ).first()

        if existing:
            for col in AgentCostProfileModel.__table__.columns.keys():
                setattr(existing, col, getattr(record, col))
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record

    def get_cost_profile(self, agent_id: str) -> Optional[AgentCostProfileModel]:
        return self.db.query(AgentCostProfileModel).filter(
            AgentCostProfileModel.agent_id == agent_id
        ).first()

    # ------------------------------------------------------------
    # History & Metrics
    # ------------------------------------------------------------
    def save_selection_history(self, record: SelectionHistoryModel) -> SelectionHistoryModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_selection_history(self, page: int = 1, page_size: int = 50) -> Tuple[List[SelectionHistoryModel], int]:
        query = self.db.query(SelectionHistoryModel)
        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(SelectionHistoryModel.timestamp)).offset(offset).limit(page_size).all()
        return items, total
