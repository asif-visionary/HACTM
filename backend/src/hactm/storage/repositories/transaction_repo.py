"""
Repository for Transaction Security Events and Detections.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from hactm.storage.models import TransactionDetectionModel, TransactionEventModel
from hactm.transaction.models import TransactionDetectionResult, TransactionEvent


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert_event(self, event: TransactionEvent) -> TransactionEventModel:
        existing = self.db.query(TransactionEventModel).filter(
            TransactionEventModel.transaction_id == event.transaction_id
        ).first()
        if existing:
            return existing

        model = TransactionEventModel(
            transaction_id=event.transaction_id,
            timestamp=event.timestamp,
            account_id=event.account_id,
            user_id=event.user_id,
            device_id=event.device_id,
            amount=event.amount,
            currency=event.currency,
            merchant_id=event.merchant_id,
            merchant_category=event.merchant_category,
            recipient_id=event.recipient_id,
            source_account=event.source_account,
            destination_account=event.destination_account,
            transaction_type=event.transaction_type,
            channel=event.channel,
            location=event.location,
            status=event.status,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def insert_detection(self, det: TransactionDetectionResult) -> TransactionDetectionModel:
        existing = self.db.query(TransactionDetectionModel).filter(TransactionDetectionModel.detection_id == det.detection_id).first()
        if existing:
            return existing

        model = TransactionDetectionModel(
            detection_id=det.detection_id,
            event_id=det.event_id,
            account_id=det.account_id,
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

    def list_events(self, page: int = 1, limit: int = 50) -> Tuple[List[TransactionEventModel], int]:
        total = self.db.query(func.count(TransactionEventModel.transaction_id)).scalar()
        query = self.db.query(TransactionEventModel).order_by(TransactionEventModel.timestamp.desc())
        items = query.offset((page - 1) * limit).limit(limit).all()
        return items, total or 0

    def list_detections(self, page: int = 1, limit: int = 50, min_risk: Optional[float] = None) -> Tuple[List[TransactionDetectionModel], int]:
        query = self.db.query(TransactionDetectionModel)
        if min_risk is not None:
            query = query.filter(TransactionDetectionModel.risk_score >= min_risk)
        total = query.count()
        items = query.order_by(TransactionDetectionModel.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total
