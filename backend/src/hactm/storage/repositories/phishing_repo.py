"""
Repository for Phishing Intelligence Events and Detections.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.storage.models import PhishingDetectionModel, PhishingEventModel


class PhishingRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert_event(self, event: PhishingEmailEvent) -> PhishingEventModel:
        existing = self.db.query(PhishingEventModel).filter(PhishingEventModel.message_id == event.message_id).first()
        if existing:
            return existing

        atts = [a.model_dump() if hasattr(a, "model_dump") else a for a in event.attachments]
        model = PhishingEventModel(
            message_id=event.message_id,
            timestamp=event.timestamp,
            sender=event.sender,
            recipient=event.recipient,
            subject=event.subject,
            body=event.body,
            headers=event.headers,
            urls=event.urls,
            attachments=atts,
            sender_domain=event.sender_domain,
            reply_to=event.reply_to,
            return_path=event.return_path,
            authentication_results=event.authentication_results,
            source_ip=event.source_ip,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def bulk_insert_events(self, events: List[PhishingEmailEvent]) -> int:
        count = 0
        for ev in events:
            ex = self.db.query(PhishingEventModel.message_id).filter(PhishingEventModel.message_id == ev.message_id).first()
            if not ex:
                self.insert_event(ev)
                count += 1
        return count

    def insert_detection(self, det: PhishingDetectionResult) -> PhishingDetectionModel:
        existing = self.db.query(PhishingDetectionModel).filter(PhishingDetectionModel.detection_id == det.detection_id).first()
        if existing:
            return existing

        model = PhishingDetectionModel(
            detection_id=det.detection_id,
            event_id=det.event_id,
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

    def list_events(self, page: int = 1, limit: int = 50) -> Tuple[List[PhishingEventModel], int]:
        total = self.db.query(func.count(PhishingEventModel.message_id)).scalar()
        query = self.db.query(PhishingEventModel).order_by(PhishingEventModel.timestamp.desc())
        items = query.offset((page - 1) * limit).limit(limit).all()
        return items, total or 0

    def list_detections(self, page: int = 1, limit: int = 50, min_risk: Optional[float] = None) -> Tuple[List[PhishingDetectionModel], int]:
        query = self.db.query(PhishingDetectionModel)
        if min_risk is not None:
            query = query.filter(PhishingDetectionModel.risk_score >= min_risk)
        total = query.count()
        items = query.order_by(PhishingDetectionModel.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total
