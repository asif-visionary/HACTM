"""
FeedbackRepository: Database access layer for Closed-Loop Feedback, Adaptation, and Replay data.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from hactm.storage.models import (
    SecurityDecisionOutcomeModel,
    FeedbackEventModel,
    FeedbackValidationModel,
    FeedbackConflictModel,
    FeedbackRetractionModel,
    AdaptationProposalModel,
    AdaptationRecordModel,
    AdaptationReviewModel,
    PolicyEffectivenessRecordModel,
    AgentPerformanceUpdateModel,
    SelectionFeedbackModel,
    ModelVersionModel,
    ModelEvaluationModel,
    ModelPromotionModel,
    ModelRollbackModel,
    DriftResponseModel,
    DecisionReplayModel,
    CounterfactualRunModel,
    AdaptationStabilityModel,
    LearningDatasetVersionModel,
)


class FeedbackRepository:
    """Repository handling CRUD operations for Closed-Loop Adaptation database tables."""

    def __init__(self, db: Session):
        self.db = db

    # --- Outcomes ---
    def create_outcome(self, outcome_data: Dict[str, Any]) -> SecurityDecisionOutcomeModel:
        obj = SecurityDecisionOutcomeModel(**outcome_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_outcome(self, outcome_id: str) -> Optional[SecurityDecisionOutcomeModel]:
        return self.db.query(SecurityDecisionOutcomeModel).filter_by(outcome_id=outcome_id).first()

    def get_outcome_by_decision(self, decision_id: str) -> Optional[SecurityDecisionOutcomeModel]:
        return self.db.query(SecurityDecisionOutcomeModel).filter_by(decision_id=decision_id).first()

    def list_outcomes(self, limit: int = 100, status: Optional[str] = None) -> List[SecurityDecisionOutcomeModel]:
        query = self.db.query(SecurityDecisionOutcomeModel)
        if status:
            query = query.filter(SecurityDecisionOutcomeModel.validation_status == status)
        return query.order_by(SecurityDecisionOutcomeModel.created_at.desc()).limit(limit).all()

    def update_outcome_status(
        self, outcome_id: str, status: str, analyst_id: Optional[str] = None
    ) -> Optional[SecurityDecisionOutcomeModel]:
        outcome = self.get_outcome(outcome_id)
        if outcome:
            outcome.validation_status = status
            if analyst_id:
                outcome.analyst_id = analyst_id
            outcome.validated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(outcome)
        return outcome

    # --- Feedback Events ---
    def create_feedback_event(self, feedback_data: Dict[str, Any]) -> FeedbackEventModel:
        obj = FeedbackEventModel(**feedback_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_feedback_event(self, feedback_id: str) -> Optional[FeedbackEventModel]:
        return self.db.query(FeedbackEventModel).filter_by(feedback_id=feedback_id).first()

    def list_feedback_events(
        self, limit: int = 100, source_type: Optional[str] = None, validation_status: Optional[str] = None
    ) -> List[FeedbackEventModel]:
        query = self.db.query(FeedbackEventModel)
        if source_type:
            query = query.filter(FeedbackEventModel.source_type == source_type)
        if validation_status:
            query = query.filter(FeedbackEventModel.validation_status == validation_status)
        return query.order_by(FeedbackEventModel.timestamp.desc()).limit(limit).all()

    # --- Feedback Validations & Retractions ---
    def add_validation(self, validation_data: Dict[str, Any]) -> FeedbackValidationModel:
        obj = FeedbackValidationModel(**validation_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def record_retraction(self, retraction_data: Dict[str, Any]) -> FeedbackRetractionModel:
        obj = FeedbackRetractionModel(**retraction_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # --- Adaptation Proposals & Records ---
    def create_adaptation_proposal(self, proposal_data: Dict[str, Any]) -> AdaptationProposalModel:
        obj = AdaptationProposalModel(**proposal_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_adaptation_proposal(self, proposal_id: str) -> Optional[AdaptationProposalModel]:
        return self.db.query(AdaptationProposalModel).filter_by(proposal_id=proposal_id).first()

    def list_adaptation_proposals(
        self, status: Optional[str] = None, limit: int = 50
    ) -> List[AdaptationProposalModel]:
        query = self.db.query(AdaptationProposalModel)
        if status:
            query = query.filter(AdaptationProposalModel.approval_status == status)
        return query.order_by(AdaptationProposalModel.created_at.desc()).limit(limit).all()

    def update_proposal_status(self, proposal_id: str, status: str) -> Optional[AdaptationProposalModel]:
        proposal = self.get_adaptation_proposal(proposal_id)
        if proposal:
            proposal.approval_status = status
            self.db.commit()
            self.db.refresh(proposal)
        return proposal

    def record_adaptation(self, adaptation_data: Dict[str, Any]) -> AdaptationRecordModel:
        obj = AdaptationRecordModel(**adaptation_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_adaptation_history(self, limit: int = 100) -> List[AdaptationRecordModel]:
        return self.db.query(AdaptationRecordModel).order_by(AdaptationRecordModel.applied_at.desc()).limit(limit).all()

    # --- Policy Effectiveness ---
    def record_policy_effectiveness(self, record_data: Dict[str, Any]) -> PolicyEffectivenessRecordModel:
        obj = PolicyEffectivenessRecordModel(**record_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_policy_effectiveness(self, limit: int = 50) -> List[PolicyEffectivenessRecordModel]:
        return self.db.query(PolicyEffectivenessRecordModel).order_by(PolicyEffectivenessRecordModel.created_at.desc()).limit(limit).all()

    # --- Model Registry ---
    def create_model_version(self, model_data: Dict[str, Any]) -> ModelVersionModel:
        obj = ModelVersionModel(**model_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_champion_model(self, model_id: str) -> Optional[ModelVersionModel]:
        return self.db.query(ModelVersionModel).filter_by(model_id=model_id, is_champion=1).first()

    def list_challengers(self, model_id: str) -> List[ModelVersionModel]:
        return self.db.query(ModelVersionModel).filter_by(model_id=model_id, is_champion=0).all()

    def promote_model_version(self, model_id: str, version_id: str, operator: str, reason: str) -> bool:
        champion = self.get_champion_model(model_id)
        candidate = self.db.query(ModelVersionModel).filter_by(version_id=version_id).first()
        if not candidate:
            return False

        if champion:
            champion.is_champion = 0
            champion.status = "RETIRED"
            champion.retired_at = datetime.now(timezone.utc)

        candidate.is_champion = 1
        candidate.status = "ACTIVE"
        candidate.approved_at = datetime.now(timezone.utc)

        promo = ModelPromotionModel(
            promotion_id=f"promo_{int(datetime.now(timezone.utc).timestamp())}",
            model_id=model_id,
            promoted_version_id=version_id,
            demoted_version_id=champion.version_id if champion else None,
            promoted_by=operator,
            reason=reason,
        )
        self.db.add(promo)
        self.db.commit()
        return True

    # --- Decision Replay & Counterfactual Runs ---
    def record_decision_replay(self, replay_data: Dict[str, Any]) -> DecisionReplayModel:
        obj = DecisionReplayModel(**replay_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def record_counterfactual_run(self, cf_data: Dict[str, Any]) -> CounterfactualRunModel:
        obj = CounterfactualRunModel(**cf_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # --- Stability Metrics ---
    def record_stability_metric(self, metric_data: Dict[str, Any]) -> AdaptationStabilityModel:
        obj = AdaptationStabilityModel(**metric_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_latest_stability(self) -> Optional[AdaptationStabilityModel]:
        return self.db.query(AdaptationStabilityModel).order_by(AdaptationStabilityModel.created_at.desc()).first()
