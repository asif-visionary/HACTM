"""
Evidence & Event Repository for HACTM.
Handles database access for SecurityEvidenceModel and EventModel.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_, select, func, and_
from sqlalchemy.orm import Session

from hactm.storage.models import EventModel, SecurityEvidenceModel, EntityModel
from hactm.core.models import SecurityEvidence


class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_event_id(self, event_id: str) -> Optional[SecurityEvidenceModel]:
        return self.db.query(SecurityEvidenceModel).filter(SecurityEvidenceModel.event_id == event_id).first()

    def exists(self, event_id: str) -> bool:
        stmt = select(func.count(SecurityEvidenceModel.event_id)).filter(SecurityEvidenceModel.event_id == event_id)
        return bool(self.db.execute(stmt).scalar_one() > 0)

    def insert_evidence_and_event(self, evidence: SecurityEvidence) -> SecurityEvidenceModel:
        """
        Persists both SecurityEvidence and corresponding summary Event.
        """
        # Save SecurityEvidence record
        evidence_model = SecurityEvidenceModel(
            event_id=evidence.event_id,
            agent_id=evidence.agent_id,
            entity_id=evidence.entity_id,
            event_type=evidence.event_type,
            timestamp=evidence.timestamp,
            risk_score=evidence.risk_score,
            confidence=evidence.confidence,
            uncertainty=evidence.uncertainty,
            severity=evidence.severity.value if hasattr(evidence.severity, "value") else str(evidence.severity),
            evidence=evidence.evidence,
            source=evidence.source,
            source_type=evidence.source_type,
            dataset=evidence.dataset,
            dataset_name=evidence.dataset_name,
            dataset_version=evidence.dataset_version,
            schema_version=evidence.schema_version,
            preprocessing_version=evidence.preprocessing_version,
            source_record_id=evidence.source_record_id,
            ingestion_run_id=evidence.ingestion_run_id,
            security_tags=evidence.security_tags,
            security_group=evidence.security_group,
            security_zone=evidence.security_zone,
            created_at=evidence.created_at,
            updated_at=evidence.updated_at,
            calibrated_probability=evidence.calibrated_probability,
            agent_reliability=evidence.agent_reliability,
            evidence_quality=evidence.evidence_quality,
            recommended_action=evidence.recommended_action,
        )
        self.db.add(evidence_model)

        # Save Event record
        event_model = EventModel(
            event_id=evidence.event_id,
            entity_id=evidence.entity_id,
            event_type=evidence.event_type,
            timestamp=evidence.timestamp,
            source=evidence.source,
            risk_score=evidence.risk_score,
            severity=evidence.severity.value if hasattr(evidence.severity, "value") else str(evidence.severity),
            raw_data=evidence.evidence,
            created_at=evidence.created_at,
        )
        self.db.add(event_model)

        return evidence_model

    def query_evidence(
        self,
        search: Optional[str] = None,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        source: Optional[str] = None,
        dataset: Optional[str] = None,
        severity: Optional[str] = None,
        min_risk: Optional[float] = None,
        max_risk: Optional[float] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[SecurityEvidenceModel], int]:
        """
        Queries evidence records with server-side filters and pagination.
        """
        stmt = select(SecurityEvidenceModel)
        filters = []

        if event_type:
            filters.append(SecurityEvidenceModel.event_type == event_type.upper())
        if entity_id:
            filters.append(SecurityEvidenceModel.entity_id == entity_id)
        if agent_id:
            filters.append(SecurityEvidenceModel.agent_id == agent_id)
        if source:
            filters.append(SecurityEvidenceModel.source == source)
        if dataset:
            filters.append(SecurityEvidenceModel.dataset == dataset)
        if severity:
            filters.append(SecurityEvidenceModel.severity == severity.upper())
        if min_risk is not None:
            filters.append(SecurityEvidenceModel.risk_score >= min_risk)
        if max_risk is not None:
            filters.append(SecurityEvidenceModel.risk_score <= max_risk)
        if start_time is not None:
            filters.append(SecurityEvidenceModel.timestamp >= start_time)
        if end_time is not None:
            filters.append(SecurityEvidenceModel.timestamp <= end_time)

        if search:
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    SecurityEvidenceModel.event_id.ilike(pattern),
                    SecurityEvidenceModel.entity_id.ilike(pattern),
                    SecurityEvidenceModel.agent_id.ilike(pattern),
                    SecurityEvidenceModel.event_type.ilike(pattern),
                    SecurityEvidenceModel.source.ilike(pattern),
                )
            )

        if filters:
            stmt = stmt.filter(and_(*filters))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        # Order and paginate
        offset = (page - 1) * page_size
        stmt = stmt.order_by(SecurityEvidenceModel.timestamp.desc()).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())

        return items, total

    def count_total(self) -> int:
        return self.db.query(func.count(SecurityEvidenceModel.event_id)).scalar() or 0

    def count_high_risk(self, threshold: float = 0.6) -> int:
        return self.db.query(func.count(SecurityEvidenceModel.event_id)).filter(
            SecurityEvidenceModel.risk_score >= threshold
        ).scalar() or 0

    def get_risk_distribution(self) -> Dict[str, int]:
        """
        Computes observed cyber risk distribution across standard severity tiers.
        """
        results = (
            self.db.query(SecurityEvidenceModel.severity, func.count(SecurityEvidenceModel.event_id))
            .group_by(SecurityEvidenceModel.severity)
            .all()
        )
        dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for sev, count in results:
            if sev in dist:
                dist[sev] = count
        return dist

    def get_timeline(self, limit: int = 15) -> List[SecurityEvidenceModel]:
        """
        Retrieves recent evidence ordered chronologically for the Evidence Timeline.
        """
        stmt = (
            select(SecurityEvidenceModel)
            .order_by(SecurityEvidenceModel.timestamp.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_entity(self, entity_id: str, limit: int = 20) -> List[SecurityEvidenceModel]:
        stmt = (
            select(SecurityEvidenceModel)
            .filter(SecurityEvidenceModel.entity_id == entity_id)
            .order_by(SecurityEvidenceModel.timestamp.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
