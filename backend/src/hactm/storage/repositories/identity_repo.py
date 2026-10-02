"""
Repository for Identity & Authentication Events and Detections.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from hactm.identity.models import IdentityDetectionResult, IdentityEvent
from hactm.storage.models import IdentityDetectionModel, IdentityEventModel


class IdentityRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert_event(self, event: IdentityEvent) -> IdentityEventModel:
        existing = self.db.query(IdentityEventModel).filter(
            IdentityEventModel.authentication_event_id == event.authentication_event_id
        ).first()
        if existing:
            return existing

        model = IdentityEventModel(
            authentication_event_id=event.authentication_event_id,
            timestamp=event.timestamp,
            user_id=event.user_id,
            account_id=event.account_id,
            device_id=event.device_id,
            source_ip=event.source_ip,
            location=event.location,
            authentication_method=event.authentication_method,
            authentication_status=event.authentication_status,
            failure_reason=event.failure_reason,
            two_factor_used=event.two_factor_used,
            two_factor_result=event.two_factor_result,
            session_id=event.session_id,
            biometric_verification_result=event.biometric_verification_result,
            device_fingerprint=event.device_fingerprint,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def insert_detection(self, det: IdentityDetectionResult) -> IdentityDetectionModel:
        existing = self.db.query(IdentityDetectionModel).filter(IdentityDetectionModel.detection_id == det.detection_id).first()
        if existing:
            return existing

        model = IdentityDetectionModel(
            detection_id=det.detection_id,
            event_id=det.event_id,
            user_id=det.user_id,
            agent_id=det.agent_id,
            detector_type=det.detector_type,
            detector_id=det.detector_id,
            detector_version=det.detector_version,
            category=det.category,
            risk_score=det.risk_score,
            confidence=det.confidence,
            uncertainty=det.uncertainty,
            severity=str(det.severity),
            reason_codes=det.reason_codes,
            explanation=det.explanation,
            features_used=det.features_used,
            model_version=det.model_version,
            timestamp=det.timestamp,
            processing_time_ms=det.processing_time_ms,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def list_events(self, page: int = 1, limit: int = 50) -> Tuple[List[IdentityEventModel], int]:
        total = self.db.query(func.count(IdentityEventModel.authentication_event_id)).scalar()
        query = self.db.query(IdentityEventModel).order_by(IdentityEventModel.timestamp.desc())
        items = query.offset((page - 1) * limit).limit(limit).all()
        return items, total or 0

    def list_detections(self, page: int = 1, limit: int = 50, min_risk: Optional[float] = None) -> Tuple[List[IdentityDetectionModel], int]:
        query = self.db.query(IdentityDetectionModel)
        if min_risk is not None:
            query = query.filter(IdentityDetectionModel.risk_score >= min_risk)
        total = query.count()
        items = query.order_by(IdentityDetectionModel.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total
