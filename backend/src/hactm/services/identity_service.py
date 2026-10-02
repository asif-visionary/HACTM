"""
Identity Service.
Coordinates IdentityAuthenticationAgent execution, DB persistence, and canonical SecurityEvidence storage.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from hactm.identity.agent import IdentityAuthenticationAgent
from hactm.identity.evaluation import evaluate_identity_agent, IdentityEvaluationMetrics
from hactm.identity.loader import generate_synthetic_identity_dataset
from hactm.identity.normalization import normalize_identity_event
from hactm.storage.repositories.evidence_repo import EvidenceRepository
from hactm.storage.repositories.entity_repo import EntityRepository
from hactm.storage.repositories.identity_repo import IdentityRepository
from hactm.ingestion.entity_resolution import resolve_entity
from hactm.services.model_registry import ModelRegistry


class IdentityService:
    def __init__(self, db: Session, agent: Optional[IdentityAuthenticationAgent] = None):
        self.db = db
        self.repo = IdentityRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.entity_repo = EntityRepository(db)
        self.model_registry = ModelRegistry(db)
        self.agent = agent or IdentityAuthenticationAgent()

    def process_raw_events(
        self, raw_events: List[Dict[str, Any]], dataset_name: str = "identity_stream"
    ) -> Dict[str, Any]:
        processed_events = []
        all_detections = []
        evidence_created = 0

        for raw in raw_events:
            ev = normalize_identity_event(raw)
            self.repo.insert_event(ev)
            processed_events.append(ev)

            dets = self.agent.detect(ev)
            for d in dets:
                self.repo.insert_detection(d)
                all_detections.append(d)

                sec_ev = self.agent.generate_evidence(d, dataset_name=dataset_name)
                if not self.evidence_repo.exists(sec_ev.event_id):
                    ent_id, ent_type, canon_name, attrs = resolve_entity({"entity_id": sec_ev.entity_id})
                    self.entity_repo.upsert_entity(
                        entity_id=ent_id,
                        entity_type=ent_type,
                        canonical_name=canon_name,
                        attributes=attrs,
                        seen_at=sec_ev.timestamp,
                    )
                    self.evidence_repo.insert_evidence_and_event(sec_ev)
                    evidence_created += 1

        self.db.commit()
        return {
            "events_processed": len(processed_events),
            "detections_generated": len(all_detections),
            "security_evidence_created": evidence_created,
        }

    def evaluate(self, dataset: Optional[List[Dict[str, Any]]] = None) -> IdentityEvaluationMetrics:
        if not dataset:
            dataset = generate_synthetic_identity_dataset(count=100)
        return evaluate_identity_agent(self.agent, dataset)
