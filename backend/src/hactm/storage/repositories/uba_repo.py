"""
Repository for User Behavior Analytics Events, Detections, and Profiles.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session

from hactm.storage.models import UbaDetectionModel, UbaEventModel, UbaProfileModel
from hactm.uba.models import UbaDetectionResult, UbaEvent, UserProfile


class UbaRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert_event(self, event: UbaEvent) -> UbaEventModel:
        existing = self.db.query(UbaEventModel).filter(UbaEventModel.event_id == event.event_id).first()
        if existing:
            return existing

        model = UbaEventModel(
            event_id=event.event_id,
            user_id=event.user_id,
            timestamp=event.timestamp,
            session_id=event.session_id,
            device_id=event.device_id,
            source_ip=event.source_ip,
            action=event.action,
            resource=event.resource,
            resource_type=event.resource_type,
            file_name=event.file_name,
            file_size=event.file_size,
            application=event.application,
            authentication_status=event.authentication_status,
            privilege_level=event.privilege_level,
            location=event.location,
            bytes_transferred=event.bytes_transferred,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def insert_detection(self, det: UbaDetectionResult) -> UbaDetectionModel:
        existing = self.db.query(UbaDetectionModel).filter(UbaDetectionModel.detection_id == det.detection_id).first()
        if existing:
            return existing

        model = UbaDetectionModel(
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

    def save_profile(self, profile: UserProfile) -> UbaProfileModel:
        existing = self.db.query(UbaProfileModel).filter(UbaProfileModel.user_id == profile.user_id).first()
        if existing:
            existing.peer_group = profile.peer_group
            existing.last_seen = profile.last_seen
            existing.event_count = profile.event_count
            existing.normal_login_hours = profile.normal_login_hours
            existing.known_devices = profile.known_devices
            existing.known_ips = profile.known_ips
            existing.known_applications = profile.known_applications
            existing.typical_resources = profile.typical_resources
            existing.avg_bytes_transferred = profile.avg_bytes_transferred
            existing.max_bytes_transferred = profile.max_bytes_transferred
            self.db.commit()
            self.db.refresh(existing)
            return existing

        model = UbaProfileModel(
            user_id=profile.user_id,
            peer_group=profile.peer_group,
            first_seen=profile.first_seen,
            last_seen=profile.last_seen,
            event_count=profile.event_count,
            normal_login_hours=profile.normal_login_hours,
            known_devices=profile.known_devices,
            known_ips=profile.known_ips,
            known_applications=profile.known_applications,
            typical_resources=profile.typical_resources,
            avg_bytes_transferred=profile.avg_bytes_transferred,
            max_bytes_transferred=profile.max_bytes_transferred,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def list_events(self, page: int = 1, limit: int = 50) -> Tuple[List[UbaEventModel], int]:
        total = self.db.query(func.count(UbaEventModel.event_id)).scalar()
        query = self.db.query(UbaEventModel).order_by(UbaEventModel.timestamp.desc())
        items = query.offset((page - 1) * limit).limit(limit).all()
        return items, total or 0

    def list_detections(self, page: int = 1, limit: int = 50, min_risk: Optional[float] = None) -> Tuple[List[UbaDetectionModel], int]:
        query = self.db.query(UbaDetectionModel)
        if min_risk is not None:
            query = query.filter(UbaDetectionModel.risk_score >= min_risk)
        total = query.count()
        items = query.order_by(UbaDetectionModel.timestamp.desc()).offset((page - 1) * limit).limit(limit).all()
        return items, total

    def list_profiles(self) -> List[UbaProfileModel]:
        return self.db.query(UbaProfileModel).all()
