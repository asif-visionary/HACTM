"""
Transaction Service.
Coordinates TransactionSecurityAgent execution, DB persistence, and canonical SecurityEvidence storage.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from hactm.storage.repositories.evidence_repo import EvidenceRepository
from hactm.storage.repositories.entity_repo import EntityRepository
from hactm.storage.repositories.transaction_repo import TransactionRepository
from hactm.ingestion.entity_resolution import resolve_entity
from hactm.transaction.agent import TransactionSecurityAgent
from hactm.transaction.evaluation import evaluate_transaction_agent, TransactionEvaluationMetrics
from hactm.transaction.loader import generate_synthetic_transaction_dataset
from hactm.transaction.normalization import normalize_transaction_event
from hactm.services.model_registry import ModelRegistry


class TransactionService:
    def __init__(self, db: Session, agent: Optional[TransactionSecurityAgent] = None):
        self.db = db
        self.repo = TransactionRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.entity_repo = EntityRepository(db)
        self.model_registry = ModelRegistry(db)
        self.agent = agent or TransactionSecurityAgent()

    def process_raw_events(
        self, raw_events: List[Dict[str, Any]], dataset_name: str = "transaction_stream"
    ) -> Dict[str, Any]:
        processed_events = []
        all_detections = []
        evidence_created = 0

        for raw in raw_events:
            ev = normalize_transaction_event(raw)
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

    def train_baseline(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        res = self.process_raw_events(dataset)
        summary = {
            "accounts_profiled": len(self.agent.baseline_mgr.account_history),
            "transactions_trained": res["events_processed"],
        }
        self.model_registry.register_model(
            model_id="tx_anom_v1",
            agent_id="transaction-security-agent",
            algorithm="Robust Z-score + Account Transaction Baseline",
            version=self.agent.version,
            evaluation_metrics=summary,
            status="ACTIVE",
        )
        return summary

    def evaluate(self, dataset: Optional[List[Dict[str, Any]]] = None) -> TransactionEvaluationMetrics:
        if not dataset:
            dataset = generate_synthetic_transaction_dataset(count=100)
        return evaluate_transaction_agent(self.agent, dataset)
