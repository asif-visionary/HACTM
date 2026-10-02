"""
Evidence Service for HACTM.
Business logic layer for Security Evidence query, retrieval, and KPI metrics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from hactm.core.constants import EntityType
from hactm.core.errors import DuplicateError, NotFoundError
from hactm.core.models import SecurityEvidence
from hactm.ingestion.entity_resolution import resolve_entity
from hactm.storage.models import SecurityEvidenceModel
from hactm.storage.repositories.entity_repo import EntityRepository
from hactm.storage.repositories.evidence_repo import EvidenceRepository
from hactm.storage.repositories.ingestion_repo import IngestionRepository


class EvidenceService:
    def __init__(self, db: Session):
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.entity_repo = EntityRepository(db)
        self.ingestion_repo = IngestionRepository(db)

    def get_by_event_id(self, event_id: str) -> SecurityEvidenceModel:
        evidence = self.evidence_repo.get_by_event_id(event_id)
        if not evidence:
            raise NotFoundError(f"Security evidence with event_id '{event_id}' not found")
        return evidence

    def create_evidence(self, evidence: SecurityEvidence) -> SecurityEvidenceModel:
        if self.evidence_repo.exists(evidence.event_id):
            raise DuplicateError(f"Security evidence with event_id '{evidence.event_id}' already exists")

        # Resolve entity
        ent_id, ent_type, canon_name, attrs = resolve_entity({
            "entity_id": evidence.entity_id,
            "event_id": evidence.event_id
        })
        self.entity_repo.upsert_entity(
            entity_id=ent_id,
            entity_type=ent_type,
            canonical_name=canon_name,
            attributes=attrs,
            seen_at=evidence.timestamp
        )

        model = self.evidence_repo.insert_evidence_and_event(evidence)
        self.db.commit()
        self.db.refresh(model)
        return model

    def list_evidence(
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
        return self.evidence_repo.query_evidence(
            search=search,
            event_type=event_type,
            entity_id=entity_id,
            agent_id=agent_id,
            source=source,
            dataset=dataset,
            severity=severity,
            min_risk=min_risk,
            max_risk=max_risk,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size,
        )

    def get_overview_metrics(self) -> Dict[str, Any]:
        """
        Returns accurate metrics computed directly from database storage.
        No fabricated or static numbers!
        """
        total_events = self.evidence_repo.count_total()
        total_entities = self.entity_repo.count_total()
        high_risk_count = self.evidence_repo.count_high_risk(threshold=0.6)
        ingestion_health = self.ingestion_repo.calculate_health_percentage()
        risk_distribution = self.evidence_repo.get_risk_distribution()

        return {
            "total_events": total_events,
            "total_entities": total_entities,
            "high_risk_events": high_risk_count,
            "ingestion_health_pct": ingestion_health,
            "risk_distribution": risk_distribution,
        }

    def get_timeline(self, limit: int = 15) -> List[SecurityEvidenceModel]:
        return self.evidence_repo.get_timeline(limit=limit)
