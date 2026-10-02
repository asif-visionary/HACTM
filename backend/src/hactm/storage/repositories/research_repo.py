"""
Repository for persisting Research Validation Validation & Publication artifacts.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from hactm.storage.models import (
    ResearchValidationRunModel,
    StatisticalResultModel,
    SensitivityRunModel,
    RobustnessRunModel,
    HypothesisResultModel,
    ResearchClaimModel,
    ReproducibilityRunModel,
    ResearchAuditResultModel,
    PublicationArtifactModel,
)


class ResearchRepository:
    """Handles CRUD database operations for research validation runs, statistical results, claims, and publication packages."""

    def __init__(self, db: Session):
        self.db = db

    def save_validation_run(self, run_data: Dict[str, Any]) -> ResearchValidationRunModel:
        model = ResearchValidationRunModel(**run_data)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get_validation_run(self, validation_id: str) -> Optional[ResearchValidationRunModel]:
        return self.db.query(ResearchValidationRunModel).filter(
            ResearchValidationRunModel.validation_id == validation_id
        ).first()

    def list_validation_runs(self, experiment_id: Optional[str] = None, limit: int = 50) -> List[ResearchValidationRunModel]:
        query = self.db.query(ResearchValidationRunModel)
        if experiment_id:
            query = query.filter(ResearchValidationRunModel.experiment_id == experiment_id)
        return query.order_by(ResearchValidationRunModel.created_at.desc()).limit(limit).all()

    def save_statistical_result(self, stat_data: Dict[str, Any]) -> StatisticalResultModel:
        model = StatisticalResultModel(**stat_data)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def list_statistical_results(self, experiment_id: Optional[str] = None) -> List[StatisticalResultModel]:
        query = self.db.query(StatisticalResultModel)
        if experiment_id:
            query = query.filter(StatisticalResultModel.experiment_id == experiment_id)
        return query.order_by(StatisticalResultModel.created_at.desc()).all()

    def save_sensitivity_runs(self, items: List[Dict[str, Any]]) -> List[SensitivityRunModel]:
        models = [SensitivityRunModel(**item) for item in items]
        self.db.add_all(models)
        self.db.commit()
        return models

    def list_sensitivity_runs(self, experiment_id: Optional[str] = None) -> List[SensitivityRunModel]:
        query = self.db.query(SensitivityRunModel)
        if experiment_id:
            query = query.filter(SensitivityRunModel.experiment_id == experiment_id)
        return query.order_by(SensitivityRunModel.created_at.desc()).all()

    def save_robustness_runs(self, items: List[Dict[str, Any]]) -> List[RobustnessRunModel]:
        models = [RobustnessRunModel(**item) for item in items]
        self.db.add_all(models)
        self.db.commit()
        return models

    def list_robustness_runs(self, experiment_id: Optional[str] = None) -> List[RobustnessRunModel]:
        query = self.db.query(RobustnessRunModel)
        if experiment_id:
            query = query.filter(RobustnessRunModel.experiment_id == experiment_id)
        return query.order_by(RobustnessRunModel.created_at.desc()).all()

    def save_hypothesis_results(self, items: List[Dict[str, Any]]) -> List[HypothesisResultModel]:
        for item in items:
            self.db.merge(HypothesisResultModel(**item))
        self.db.commit()
        return self.list_hypothesis_results()

    def list_hypothesis_results(self) -> List[HypothesisResultModel]:
        return self.db.query(HypothesisResultModel).order_by(HypothesisResultModel.hypothesis_id.asc()).all()

    def save_research_claims(self, claims: List[Dict[str, Any]]) -> List[ResearchClaimModel]:
        for claim in claims:
            self.db.merge(ResearchClaimModel(**claim))
        self.db.commit()
        return self.list_research_claims()

    def list_research_claims(self) -> List[ResearchClaimModel]:
        return self.db.query(ResearchClaimModel).order_by(ResearchClaimModel.claim_id.asc()).all()

    def save_publication_artifact(self, artifact_data: Dict[str, Any]) -> PublicationArtifactModel:
        model = PublicationArtifactModel(**artifact_data)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def list_publication_artifacts(self) -> List[PublicationArtifactModel]:
        return self.db.query(PublicationArtifactModel).order_by(PublicationArtifactModel.created_at.desc()).all()
