"""
Network Security Agent Service.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Business logic layer coordinating:
- Network Data Loading & Preprocessing
- Detection Execution across Signature, Heuristic, and Anomaly Engines
- Model Training & Atomic Activation
- Performance & Classification Evaluation
- Canonical Foundation SecurityEvidence & Network Storage Persistence
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from hactm.core.constants import IngestionPolicy
from hactm.core.errors import NotFoundError, HACTMValidationError
from hactm.core.logging import logger
from hactm.network.agent import NetworkSecurityAgent
from hactm.network.evaluation import evaluate_detections
from hactm.network.loader import NetworkDataLoader
from hactm.network.models import (
    AnalystLabel,
    NetworkDetectionResult,
    NetworkEvaluationMetrics,
    NetworkEvent,
    NetworkModelMetadata,
)
from hactm.storage.models import (
    NetworkDetectionModel,
    NetworkEventModel,
    NetworkModelDbModel,
)
from hactm.storage.repositories.evidence_repo import EvidenceRepository
from hactm.storage.repositories.entity_repo import EntityRepository
from hactm.storage.repositories.network_repo import NetworkRepository
from hactm.ingestion.entity_resolution import resolve_entity


class NetworkService:
    def __init__(self, db: Session, agent: Optional[NetworkSecurityAgent] = None):
        self.db = db
        self.repo = NetworkRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.entity_repo = EntityRepository(db)
        self.loader = NetworkDataLoader()
        self.agent = agent or NetworkSecurityAgent()

    def ingest_network_file(
        self,
        file_path: Union[str, Path],
        dataset_name: Optional[str] = None,
        batch_size: int = 1000,
        run_detection: bool = True,
    ) -> Dict[str, Any]:
        """
        Loads network events, runs detection pipeline, and persists events, detections, and security evidence.
        """
        path = Path(file_path)
        if not path.exists():
            raise NotFoundError(f"Dataset file not found: {file_path}")

        total_events = 0
        total_detections = 0
        total_evidence_created = 0

        for batch in self.loader.load_from_file(
            file_path=path,
            dataset_name=dataset_name,
            batch_size=batch_size,
            policy=IngestionPolicy.QUARANTINE_INVALID,
        ):
            total_events += len(batch)
            self.repo.bulk_insert_events(batch)

            if run_detection:
                detections, evidence_records = self.agent.process_batch(
                    batch, dataset_name=dataset_name or path.stem
                )
                total_detections += len(detections)
                self.repo.bulk_insert_detections(detections)

                # Persist to Foundation SecurityEvidence repository for dashboard visibility
                for ev in evidence_records:
                    if not self.evidence_repo.exists(ev.event_id):
                        # Deterministically upsert entity
                        ent_id, ent_type, canon_name, attrs = resolve_entity({"entity_id": ev.entity_id})
                        self.entity_repo.upsert_entity(
                            entity_id=ent_id,
                            entity_type=ent_type,
                            canonical_name=canon_name,
                            attributes=attrs,
                            seen_at=ev.timestamp,
                        )
                        self.evidence_repo.insert_evidence_and_event(ev)
                        total_evidence_created += 1

                self.db.commit()

        return {
            "dataset_name": dataset_name or path.stem,
            "events_processed": total_events,
            "detections_generated": total_detections,
            "security_evidence_created": total_evidence_created,
        }

    def detect_events(
        self,
        events: List[NetworkEvent],
        persist: bool = True,
        dataset_name: str = "ad_hoc_detection",
    ) -> List[NetworkDetectionResult]:
        """Runs events through agent detectors."""
        detections, evidence_records = self.agent.process_batch(events, dataset_name=dataset_name)

        if persist:
            self.repo.bulk_insert_events(events)
            self.repo.bulk_insert_detections(detections)
            for ev in evidence_records:
                if not self.evidence_repo.exists(ev.event_id):
                    ent_id, ent_type, canon_name, attrs = resolve_entity({"entity_id": ev.entity_id})
                    self.entity_repo.upsert_entity(
                        entity_id=ent_id,
                        entity_type=ent_type,
                        canonical_name=canon_name,
                        attributes=attrs,
                        seen_at=ev.timestamp,
                    )
                    self.evidence_repo.insert_evidence_and_event(ev)
            self.db.commit()

        return detections

    def train_anomaly_model(
        self,
        file_path: Union[str, Path],
        dataset_name: Optional[str] = None,
        algorithm: str = "isolation_forest",
        contamination: float = 0.05,
    ) -> NetworkModelMetadata:
        """Trains candidate anomaly detector without overwriting active model."""
        path = Path(file_path)
        all_events: List[NetworkEvent] = []
        for batch in self.loader.load_from_file(path, dataset_name=dataset_name, batch_size=2000):
            all_events.extend(batch)

        if len(all_events) < 10:
            raise HACTMValidationError("Insufficient training data: requires at least 10 events")

        meta = self.agent.anomaly_detector.fit(all_events, dataset_name=dataset_name or path.stem)
        meta.status = "CANDIDATE"  # Must be explicitly activated (Section 88)
        self.agent.anomaly_detector.save_model(meta.model_id)
        self.repo.upsert_model(meta)
        return meta

    def evaluate(
        self,
        file_path: Union[str, Path],
        dataset_name: Optional[str] = None,
    ) -> NetworkEvaluationMetrics:
        """Evaluates detection engines against labeled ground truth."""
        path = Path(file_path)
        all_events: List[NetworkEvent] = []
        for batch in self.loader.load_from_file(path, dataset_name=dataset_name, batch_size=2000):
            all_events.extend(batch)

        detections, _ = self.agent.process_batch(all_events, dataset_name=dataset_name or path.stem)
        metrics = evaluate_detections(all_events, detections)

        # Record summary in active model
        active_model = self.db.query(NetworkModelDbModel).filter(NetworkModelDbModel.status == "ACTIVE").first()
        if active_model:
            active_model.evaluation_summary = metrics.model_dump()
            self.db.commit()

        return metrics

    def list_events(
        self,
        src_ip: Optional[str] = None,
        dst_ip: Optional[str] = None,
        protocol: Optional[str] = None,
        dst_port: Optional[int] = None,
        dataset: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[NetworkEventModel], int]:
        return self.repo.query_events(
            src_ip=src_ip,
            dst_ip=dst_ip,
            protocol=protocol,
            dst_port=dst_port,
            dataset=dataset,
            page=page,
            page_size=page_size,
        )

    def list_detections(
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
        return self.repo.query_detections(
            detector_type=detector_type,
            category=category,
            severity=severity,
            min_risk=min_risk,
            max_risk=max_risk,
            src_ip=src_ip,
            page=page,
            page_size=page_size,
        )

    def get_detection(self, detection_id: str) -> NetworkDetectionModel:
        det = self.repo.get_detection_by_id(detection_id)
        if not det:
            raise NotFoundError(f"Network detection '{detection_id}' not found")
        return det

    def get_metrics(self) -> Dict[str, Any]:
        return self.repo.get_network_metrics()

    def list_models(self) -> List[NetworkModelDbModel]:
        return self.repo.list_models()

    def activate_model(self, model_id: str) -> bool:
        success = self.repo.set_active_model(model_id)
        if not success:
            raise NotFoundError(f"Model '{model_id}' not found")
        self.agent.anomaly_detector.load_model(model_id)
        return True

    def submit_feedback(self, detection_id: str, label: AnalystLabel, note: Optional[str] = None):
        det = self.repo.get_detection_by_id(detection_id)
        if not det:
            raise NotFoundError(f"Detection '{detection_id}' not found")
        return self.repo.add_feedback(detection_id, label, note)

    def get_agent_health(self) -> Dict[str, Any]:
        return self.agent.health()
