"""
Database Repository for Reliability Processing, Calibration, Uncertainty, Drift, and Reputation.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from hactm.storage.models import (
    AgentReliabilityModel,
    ReliabilityHistoryModel,
    CalibrationRecordModel,
    UncertaintyRecordModel,
    EvidenceQualityModel,
    DriftRecordModel,
    ConflictRecordModel,
    AgentReputationModel,
    ReliabilityEvaluationModel,
)


class ReliabilityRepository:
    """SQLAlchemy Repository for Reliability & Trust storage tables."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------
    # Agent & Detector Reliability Records
    # ------------------------------------------------------------
    def save_reliability_record(self, record: AgentReliabilityModel) -> AgentReliabilityModel:
        existing = self.db.query(AgentReliabilityModel).filter(
            AgentReliabilityModel.reliability_id == record.reliability_id
        ).first()
        if existing:
            for col in AgentReliabilityModel.__table__.columns.keys():
                setattr(existing, col, getattr(record, col))
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record

    def get_reliability_by_id(self, reliability_id: str) -> Optional[AgentReliabilityModel]:
        return self.db.query(AgentReliabilityModel).filter(
            AgentReliabilityModel.reliability_id == reliability_id
        ).first()

    def get_latest_reliability(
        self,
        agent_id: str,
        detector_id: Optional[str] = None,
        domain: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> Optional[AgentReliabilityModel]:
        query = self.db.query(AgentReliabilityModel).filter(AgentReliabilityModel.agent_id == agent_id)
        if detector_id:
            query = query.filter(AgentReliabilityModel.detector_id == detector_id)
        if domain:
            query = query.filter(AgentReliabilityModel.domain == domain)
        if model_version:
            query = query.filter(AgentReliabilityModel.model_version == model_version)
        
        return query.order_by(desc(AgentReliabilityModel.created_at)).first()

    def list_reliability_records(
        self,
        agent_id: Optional[str] = None,
        detector_id: Optional[str] = None,
        domain: Optional[str] = None,
        model_version: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AgentReliabilityModel], int]:
        query = self.db.query(AgentReliabilityModel)
        if agent_id:
            query = query.filter(AgentReliabilityModel.agent_id == agent_id)
        if detector_id:
            query = query.filter(AgentReliabilityModel.detector_id == detector_id)
        if domain:
            query = query.filter(AgentReliabilityModel.domain == domain)
        if model_version:
            query = query.filter(AgentReliabilityModel.model_version == model_version)
        if status:
            query = query.filter(AgentReliabilityModel.reliability_status == status)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(AgentReliabilityModel.created_at)).offset(offset).limit(page_size).all()
        return items, total

    # ------------------------------------------------------------
    # Reliability History Audit Trail
    # ------------------------------------------------------------
    def save_history_record(self, record: ReliabilityHistoryModel) -> ReliabilityHistoryModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_history_for_agent(
        self,
        agent_id: str,
        detector_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[ReliabilityHistoryModel], int]:
        query = self.db.query(ReliabilityHistoryModel).filter(ReliabilityHistoryModel.agent_id == agent_id)
        if detector_id:
            query = query.filter(ReliabilityHistoryModel.detector_id == detector_id)
        
        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(ReliabilityHistoryModel.timestamp)).offset(offset).limit(page_size).all()
        return items, total

    # ------------------------------------------------------------
    # Calibration Records
    # ------------------------------------------------------------
    def save_calibration_record(self, record: CalibrationRecordModel) -> CalibrationRecordModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_calibration_records(
        self,
        agent_id: Optional[str] = None,
        detector_id: Optional[str] = None,
        model_version: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[CalibrationRecordModel], int]:
        query = self.db.query(CalibrationRecordModel)
        if agent_id:
            query = query.filter(CalibrationRecordModel.agent_id == agent_id)
        if detector_id:
            query = query.filter(CalibrationRecordModel.detector_id == detector_id)
        if model_version:
            query = query.filter(CalibrationRecordModel.model_version == model_version)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(CalibrationRecordModel.created_at)).offset(offset).limit(page_size).all()
        return items, total

    # ------------------------------------------------------------
    # Uncertainty Records
    # ------------------------------------------------------------
    def save_uncertainty_record(self, record: UncertaintyRecordModel) -> UncertaintyRecordModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_uncertainty_records(
        self,
        agent_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[UncertaintyRecordModel], int]:
        query = self.db.query(UncertaintyRecordModel)
        if agent_id:
            query = query.filter(UncertaintyRecordModel.agent_id == agent_id)
        if evidence_id:
            query = query.filter(UncertaintyRecordModel.evidence_id == evidence_id)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(UncertaintyRecordModel.created_at)).offset(offset).limit(page_size).all()
        return items, total

    # ------------------------------------------------------------
    # Evidence Quality Records
    # ------------------------------------------------------------
    def save_evidence_quality(self, record: EvidenceQualityModel) -> EvidenceQualityModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_quality_records(
        self,
        evidence_id: Optional[str] = None,
        min_quality: Optional[float] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[EvidenceQualityModel], int]:
        query = self.db.query(EvidenceQualityModel)
        if evidence_id:
            query = query.filter(EvidenceQualityModel.evidence_id == evidence_id)
        if min_quality is not None:
            query = query.filter(EvidenceQualityModel.quality_score >= min_quality)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(EvidenceQualityModel.evaluated_at)).offset(offset).limit(page_size).all()
        return items, total

    # ------------------------------------------------------------
    # Drift Records
    # ------------------------------------------------------------
    def save_drift_record(self, record: DriftRecordModel) -> DriftRecordModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_drift_records(
        self,
        agent_id: Optional[str] = None,
        detector_id: Optional[str] = None,
        drift_detected: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[DriftRecordModel], int]:
        query = self.db.query(DriftRecordModel)
        if agent_id:
            query = query.filter(DriftRecordModel.agent_id == agent_id)
        if detector_id:
            query = query.filter(DriftRecordModel.detector_id == detector_id)
        if drift_detected is not None:
            val = "true" if drift_detected else "false"
            query = query.filter(DriftRecordModel.drift_detected == val)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(DriftRecordModel.created_at)).offset(offset).limit(page_size).all()
        return items, total

    # ------------------------------------------------------------
    # Conflict Records
    # ------------------------------------------------------------
    def save_conflict_record(self, record: ConflictRecordModel) -> ConflictRecordModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_conflict_records(
        self,
        entity_id: Optional[str] = None,
        conflict_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[ConflictRecordModel], int]:
        query = self.db.query(ConflictRecordModel)
        if entity_id:
            query = query.filter(ConflictRecordModel.entity_id == entity_id)
        if conflict_type:
            query = query.filter(ConflictRecordModel.conflict_type == conflict_type)
        if status:
            query = query.filter(ConflictRecordModel.resolution_status == status)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(ConflictRecordModel.created_at)).offset(offset).limit(page_size).all()
        return items, total

    # ------------------------------------------------------------
    # Agent Reputation Records
    # ------------------------------------------------------------
    def save_agent_reputation(self, record: AgentReputationModel) -> AgentReputationModel:
        existing = self.db.query(AgentReputationModel).filter(
            AgentReputationModel.agent_id == record.agent_id
        ).first()
        if existing:
            for col in AgentReputationModel.__table__.columns.keys():
                if col != "reputation_id":
                    setattr(existing, col, getattr(record, col))
            existing.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record

    def get_agent_reputation(self, agent_id: str) -> Optional[AgentReputationModel]:
        return self.db.query(AgentReputationModel).filter(
            AgentReputationModel.agent_id == agent_id
        ).first()

    def list_agent_reputations(self) -> List[AgentReputationModel]:
        return self.db.query(AgentReputationModel).order_by(desc(AgentReputationModel.reputation_score)).all()

    # ------------------------------------------------------------
    # Reliability Evaluation Records
    # ------------------------------------------------------------
    def save_evaluation_record(self, record: ReliabilityEvaluationModel) -> ReliabilityEvaluationModel:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_evaluations(
        self,
        evaluation_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[ReliabilityEvaluationModel], int]:
        query = self.db.query(ReliabilityEvaluationModel)
        if evaluation_type:
            query = query.filter(ReliabilityEvaluationModel.evaluation_type == evaluation_type)
        if agent_id:
            query = query.filter(ReliabilityEvaluationModel.agent_id == agent_id)

        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(desc(ReliabilityEvaluationModel.created_at)).offset(offset).limit(page_size).all()
        return items, total
