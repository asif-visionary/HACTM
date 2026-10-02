"""
Phishing Intelligence Service.
Coordinates Phishing Intelligence Agent execution, DB persistence, and canonical SecurityEvidence storage.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

from hactm.phishing.agent import PhishingIntelligenceAgent
from hactm.phishing.evaluation import evaluate_phishing_agent, PhishingEvaluationMetrics
from hactm.phishing.loader import generate_synthetic_phishing_dataset
from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.phishing.normalization import normalize_email_event
from hactm.storage.repositories.evidence_repo import EvidenceRepository
from hactm.storage.repositories.entity_repo import EntityRepository
from hactm.storage.repositories.phishing_repo import PhishingRepository
from hactm.ingestion.entity_resolution import resolve_entity
from hactm.services.model_registry import ModelRegistry


class PhishingService:
    def __init__(self, db: Session, agent: Optional[PhishingIntelligenceAgent] = None):
        self.db = db
        self.repo = PhishingRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.entity_repo = EntityRepository(db)
        self.model_registry = ModelRegistry(db)
        self.agent = agent or PhishingIntelligenceAgent()

    def process_raw_events(
        self, raw_events: List[Dict[str, Any]], dataset_name: str = "phishing_stream"
    ) -> Dict[str, Any]:
        """Ingests raw email events, executes detection, and stores events, detections, and canonical SecurityEvidence."""
        processed_events = []
        all_detections = []
        evidence_created = 0

        for raw in raw_events:
            ev = normalize_email_event(raw)
            self.repo.insert_event(ev)
            processed_events.append(ev)

            dets = self.agent.detect(ev)
            for d in dets:
                self.repo.insert_detection(d)
                all_detections.append(d)

                # Convert & persist canonical SecurityEvidence
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

    def train_nlp_model(self, dataset: List[Dict[str, Any]], model_id: str = "phish_tfidf_v1") -> Dict[str, Any]:
        """Trains baseline NLP classifier and registers in ModelRegistry."""
        texts = [f"{item.get('subject', '')} {item.get('body', '')}" for item in dataset]
        labels = [1 if item.get("dataset_label") in {"phishing", "spear_phishing", "bec"} else 0 for item in dataset]

        summary = self.agent.nlp_detector.train(texts, labels)

        entry = self.model_registry.register_model(
            model_id=model_id,
            agent_id="phishing-intelligence-agent",
            algorithm="TF-IDF + Logistic Regression",
            version=self.agent.version,
            dataset="synthetic_phishing",
            feature_schema={"max_features": 5000, "ngram_range": [1, 2]},
            evaluation_metrics=summary,
            status="ACTIVE",
        )
        return summary

    def evaluate(self, dataset: Optional[List[Dict[str, Any]]] = None) -> PhishingEvaluationMetrics:
        """Evaluates agent performance."""
        if not dataset:
            dataset = generate_synthetic_phishing_dataset(count=100)
        return evaluate_phishing_agent(self.agent, dataset)
