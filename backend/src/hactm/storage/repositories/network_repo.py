"""
Repository for Network Security Agent Network Events, Detections, Models, and Feedback.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from hactm.core.constants import SeverityLevel
from hactm.network.models import (
    AnalystLabel,
    DetectorType,
    NetworkDetectionResult,
    NetworkEvent,
    NetworkModelMetadata,
)
from hactm.storage.models import (
    DetectionFeedbackModel,
    NetworkDetectionModel,
    NetworkEventModel,
    NetworkModelDbModel,
)


class NetworkRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert_event(self, event: NetworkEvent) -> NetworkEventModel:
        model = NetworkEventModel(
            event_id=event.event_id,
            timestamp=event.timestamp,
            src_ip=event.src_ip,
            dst_ip=event.dst_ip,
            src_port=event.src_port,
            dst_port=event.dst_port,
            protocol=event.protocol,
            duration=event.duration,
            flow_bytes=event.flow_bytes,
            flow_packets=event.flow_packets,
            forward_bytes=event.forward_bytes,
            backward_bytes=event.backward_bytes,
            forward_packets=event.forward_packets,
            backward_packets=event.backward_packets,
            tcp_flags=event.tcp_flags,
            connection_state=event.connection_state,
            flow_rate=event.flow_rate,
            packet_rate=event.packet_rate,
            dataset=event.dataset,
            src_ip_classification=event.src_ip_classification.value if event.src_ip_classification else None,
            dst_ip_classification=event.dst_ip_classification.value if event.dst_ip_classification else None,
            label=event.label,
        )
        self.db.add(model)
        return model

    def bulk_insert_events(self, events: List[NetworkEvent]) -> int:
        count = 0
        for ev in events:
            # Check existence
            exists = self.db.query(NetworkEventModel.event_id).filter(NetworkEventModel.event_id == ev.event_id).first()
            if not exists:
                self.insert_event(ev)
                count += 1
        self.db.commit()
        return count

    def insert_detection(self, det: NetworkDetectionResult) -> NetworkDetectionModel:
        # Check duplicate detection_id
        existing = self.db.query(NetworkDetectionModel).filter(NetworkDetectionModel.detection_id == det.detection_id).first()
        if existing:
            return existing

        model = NetworkDetectionModel(
            detection_id=det.detection_id,
            event_id=det.event_id,
            detector_type=det.detector_type.value,
            detector_id=det.detector_id,
            detector_version=det.detector_version,
            category=det.category,
            risk_score=det.risk_score,
            confidence=det.confidence,
            uncertainty=det.uncertainty,
            severity=det.severity.value if hasattr(det.severity, "value") else str(det.severity),
            reason_codes=det.reason_codes,
            explanation=det.explanation,
            features_used=det.features_used,
            model_version=det.model_version,
            signature_id=det.signature_id,
            processing_time_ms=det.processing_time_ms,
            src_ip=det.src_ip,
            dst_ip=det.dst_ip,
            timestamp=det.timestamp,
        )
        self.db.add(model)
        return model

    def bulk_insert_detections(self, detections: List[NetworkDetectionResult]) -> int:
        count = 0
        for d in detections:
            existing = self.db.query(NetworkDetectionModel.detection_id).filter(
                NetworkDetectionModel.detection_id == d.detection_id
            ).first()
            if not existing:
                self.insert_detection(d)
                count += 1
        self.db.commit()
        return count

    def query_events(
        self,
        src_ip: Optional[str] = None,
        dst_ip: Optional[str] = None,
        protocol: Optional[str] = None,
        dst_port: Optional[int] = None,
        dataset: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[NetworkEventModel], int]:
        stmt = select(NetworkEventModel)
        filters = []
        if src_ip:
            filters.append(NetworkEventModel.src_ip.ilike(f"%{src_ip.strip()}%"))
        if dst_ip:
            filters.append(NetworkEventModel.dst_ip.ilike(f"%{dst_ip.strip()}%"))
        if protocol:
            filters.append(NetworkEventModel.protocol == protocol.upper())
        if dst_port is not None:
            filters.append(NetworkEventModel.dst_port == dst_port)
        if dataset:
            filters.append(NetworkEventModel.dataset == dataset)

        if filters:
            stmt = stmt.filter(and_(*filters))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        offset = (page - 1) * page_size
        stmt = stmt.order_by(NetworkEventModel.timestamp.desc()).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def query_detections(
        self,
        detector_type: Optional[str] = None,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        min_risk: Optional[float] = None,
        max_risk: Optional[float] = None,
        src_ip: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[NetworkDetectionModel], int]:
        stmt = select(NetworkDetectionModel)
        filters = []
        if detector_type:
            filters.append(NetworkDetectionModel.detector_type == detector_type.upper())
        if category:
            filters.append(NetworkDetectionModel.category.ilike(f"%{category.strip()}%"))
        if severity:
            filters.append(NetworkDetectionModel.severity == severity.upper())
        if min_risk is not None:
            filters.append(NetworkDetectionModel.risk_score >= min_risk)
        if max_risk is not None:
            filters.append(NetworkDetectionModel.risk_score <= max_risk)
        if src_ip:
            filters.append(NetworkDetectionModel.src_ip.ilike(f"%{src_ip.strip()}%"))

        if filters:
            stmt = stmt.filter(and_(*filters))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        offset = (page - 1) * page_size
        stmt = stmt.order_by(NetworkDetectionModel.timestamp.desc()).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def get_detection_by_id(self, detection_id: str) -> Optional[NetworkDetectionModel]:
        return self.db.query(NetworkDetectionModel).filter(NetworkDetectionModel.detection_id == detection_id).first()

    def get_network_metrics(self) -> Dict[str, Any]:
        """Calculates live non-fabricated metrics for Network Security Dashboard."""
        total_events = self.db.query(func.count(NetworkEventModel.event_id)).scalar() or 0
        total_detections = self.db.query(func.count(NetworkDetectionModel.detection_id)).scalar() or 0
        high_risk_detections = (
            self.db.query(func.count(NetworkDetectionModel.detection_id))
            .filter(NetworkDetectionModel.risk_score >= 0.60)
            .scalar()
            or 0
        )

        # Category breakdown
        cat_counts = (
            self.db.query(NetworkDetectionModel.category, func.count(NetworkDetectionModel.detection_id))
            .group_by(NetworkDetectionModel.category)
            .all()
        )
        categories = {cat: count for cat, count in cat_counts}

        # Detector type breakdown
        type_counts = (
            self.db.query(NetworkDetectionModel.detector_type, func.count(NetworkDetectionModel.detection_id))
            .group_by(NetworkDetectionModel.detector_type)
            .all()
        )
        detector_types = {t: count for t, count in type_counts}

        # Risk breakdown
        low_risk = self.db.query(func.count(NetworkDetectionModel.detection_id)).filter(NetworkDetectionModel.risk_score < 0.40).scalar() or 0
        med_risk = self.db.query(func.count(NetworkDetectionModel.detection_id)).filter(NetworkDetectionModel.risk_score >= 0.40, NetworkDetectionModel.risk_score < 0.70).scalar() or 0
        high_risk = self.db.query(func.count(NetworkDetectionModel.detection_id)).filter(NetworkDetectionModel.risk_score >= 0.70, NetworkDetectionModel.risk_score < 0.90).scalar() or 0
        crit_risk = self.db.query(func.count(NetworkDetectionModel.detection_id)).filter(NetworkDetectionModel.risk_score >= 0.90).scalar() or 0

        # Detection rate
        det_rate = round((total_detections / total_events) * 100.0, 2) if total_events > 0 else 0.0

        return {
            "total_network_events": total_events,
            "total_events": total_events,
            "total_detections": total_detections,
            "high_risk_detections": high_risk_detections,
            "detection_rate_pct": det_rate,
            "detection_rate": (total_detections / total_events) if total_events > 0 else 0.0,
            "categories": categories,
            "category_distribution": categories,
            "detector_types": detector_types,
            "detector_distribution": detector_types,
            "risk_distribution": {
                "low": low_risk,
                "medium": med_risk,
                "high": high_risk,
                "critical": crit_risk,
            },
        }

    def upsert_model(self, meta: NetworkModelMetadata) -> NetworkModelDbModel:
        model = self.db.query(NetworkModelDbModel).filter(NetworkModelDbModel.model_id == meta.model_id).first()
        if not model:
            model = NetworkModelDbModel(
                model_id=meta.model_id,
                model_version=meta.model_version,
                algorithm=meta.algorithm,
                parameters=meta.parameters,
                feature_schema_version=meta.feature_schema_version,
                features=meta.features,
                training_dataset=meta.training_dataset,
                training_timestamp=meta.training_timestamp,
                training_samples=meta.training_samples,
                artifact_path=meta.artifact_path,
                random_seed=meta.random_seed,
                status=meta.status,
                evaluation_summary=meta.evaluation_summary,
            )
            self.db.add(model)
        else:
            model.model_version = meta.model_version
            model.parameters = meta.parameters
            model.training_samples = meta.training_samples
            model.artifact_path = meta.artifact_path
            model.status = meta.status
            model.evaluation_summary = meta.evaluation_summary
        self.db.commit()
        self.db.refresh(model)
        return model

    def list_models(self) -> List[NetworkModelDbModel]:
        return self.db.query(NetworkModelDbModel).order_by(NetworkModelDbModel.training_timestamp.desc()).all()

    def set_active_model(self, model_id: str) -> bool:
        # Atomic activation: retire old active, set candidate to active
        target = self.db.query(NetworkModelDbModel).filter(NetworkModelDbModel.model_id == model_id).first()
        if not target:
            return False
        # Set all others to CANDIDATE or RETIRED
        self.db.query(NetworkModelDbModel).filter(NetworkModelDbModel.status == "ACTIVE").update({"status": "RETIRED"})
        target.status = "ACTIVE"
        self.db.commit()
        return True

    def add_feedback(self, detection_id: str, label: AnalystLabel, note: Optional[str]) -> DetectionFeedbackModel:
        fb = DetectionFeedbackModel(
            detection_id=detection_id,
            label=label.value if hasattr(label, "value") else str(label),
            analyst_note=note,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(fb)
        self.db.commit()
        self.db.refresh(fb)
        return fb
