"""
UBA Service.
Coordinates UBA Agent execution, DB persistence, user profiles, and canonical SecurityEvidence storage.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from hactm.storage.repositories.evidence_repo import EvidenceRepository
from hactm.storage.repositories.entity_repo import EntityRepository
from hactm.storage.repositories.uba_repo import UbaRepository
from hactm.ingestion.entity_resolution import resolve_entity
from hactm.uba.agent import UBAAgent
from hactm.uba.evaluation import evaluate_uba_agent, UbaEvaluationMetrics
from hactm.uba.loader import generate_synthetic_uba_dataset
from hactm.uba.normalization import normalize_uba_event
from hactm.services.model_registry import ModelRegistry


class UbaService:
    def __init__(self, db: Session, agent: Optional[UBAAgent] = None):
        self.db = db
        self.repo = UbaRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.entity_repo = EntityRepository(db)
        self.model_registry = ModelRegistry(db)
        self.agent = agent or UBAAgent()

    def process_raw_events(
        self, raw_events: List[Dict[str, Any]], dataset_name: str = "uba_stream"
    ) -> Dict[str, Any]:
        processed_events = []
        all_detections = []
        evidence_created = 0

        for raw in raw_events:
            ev = normalize_uba_event(raw)
            self.repo.insert_event(ev)
            processed_events.append(ev)

            dets = self.agent.detect(ev)

            # Persist updated user profile to DB
            prof = self.agent.profile_mgr.get_profile(ev.user_id)
            if prof:
                self.repo.save_profile(prof)

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

    def train_baseline(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trains user profile baselines from dataset and registers model."""
        res = self.process_raw_events(dataset)
        summary = {
            "users_profiled": len(self.agent.profile_mgr.user_profiles),
            "events_trained": res["events_processed"],
        }
        self.model_registry.register_model(
            model_id="uba_stat_v1",
            agent_id="uba-agent",
            algorithm="Robust Z-score + User Behavioral Profile",
            version=self.agent.version,
            evaluation_metrics=summary,
            status="ACTIVE",
        )
        return summary

    def evaluate(self, dataset: Optional[List[Dict[str, Any]]] = None) -> UbaEvaluationMetrics:
        if not dataset:
            dataset = generate_synthetic_uba_dataset(count=100)
        return evaluate_uba_agent(self.agent, dataset)
