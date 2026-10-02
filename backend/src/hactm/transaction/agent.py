"""
Transaction Security Agent Coordinator.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.

Agent ID: transaction-security-agent
"""

from collections import deque
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import yaml

from hactm.core.agent_base import BaseSecurityAgent, SecurityDetectionResult
from hactm.core.logging import logger
from hactm.core.models import SecurityEvidence
from hactm.transaction.detectors.amount_anomaly_detector import AmountAnomalyDetector
from hactm.transaction.detectors.recipient_anomaly_detector import RecipientAnomalyDetector
from hactm.transaction.detectors.velocity_detector import VelocityDetector
from hactm.transaction.evidence_adapter import transaction_detection_to_security_evidence
from hactm.transaction.features import AccountTransactionBaseline
from hactm.transaction.models import TransactionDetectionResult, TransactionEvent
from hactm.transaction.normalization import normalize_transaction_event


class TransactionSecurityAgent(BaseSecurityAgent):
    """
    Modular specialized security agent for financial transaction anomaly and fraud indicator detection.
    Safety: Purely analytical evidence-generation engine. NEVER executes financial transactions.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        cfg_file = config_path or Path(__file__).resolve().parent.parent.parent.parent / "configs" / "transaction.yaml"
        self.config: Dict[str, Any] = {}
        if Path(cfg_file).exists():
            with open(cfg_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f).get("transaction", {})

        self.agent_id = self.config.get("agent_id", "transaction-security-agent")
        self.version = self.config.get("version", "1.0.0")

        self.baseline_mgr = AccountTransactionBaseline()

        # Telemetry State
        self.start_time = datetime.now(timezone.utc)
        self.events_processed = 0
        self.detections_generated = 0
        self.errors_count = 0
        self.last_event_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self._latencies: deque = deque(maxlen=1000)

        self.initialize()

    def initialize(self) -> "TransactionSecurityAgent":
        """Initializes detectors."""
        vel_thresh = self.config.get("velocity", {}).get("max_transactions_threshold", 5)
        self.velocity_detector = VelocityDetector(max_threshold=vel_thresh, version=self.version)
        z_thresh = self.config.get("amount_anomaly", {}).get("zscore_threshold", 3.0)
        self.amount_detector = AmountAnomalyDetector(zscore_threshold=z_thresh, version=self.version)
        self.recipient_detector = RecipientAnomalyDetector(version=self.version)
        return self

    def validate(self, raw_event: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(raw_event, dict):
            return False, ["Input raw_event must be a dictionary"]
        if not raw_event.get("account_id") and not raw_event.get("account"):
            errors.append("Missing required account identifier")
        if "amount" not in raw_event and "value" not in raw_event:
            errors.append("Missing required transaction amount")
        return len(errors) == 0, errors

    def extract_features(self, event: TransactionEvent) -> Dict[str, Any]:
        return self.baseline_mgr.record_and_extract_features(event)

    def detect(self, event: TransactionEvent) -> List[TransactionDetectionResult]:
        features = self.extract_features(event)
        detections: List[TransactionDetectionResult] = []

        for detector in [
            self.velocity_detector,
            self.amount_detector,
            self.recipient_detector,
        ]:
            try:
                res = detector.detect(event, features)
                if res:
                    detections.append(res)
            except Exception as e:
                self.errors_count += 1
                logger.error(f"Detector {detector.detector_id} failed on {event.transaction_id}: {e}")

        return detections

    def explain(self, detection: SecurityDetectionResult) -> str:
        return detection.explanation

    def calculate_risk(
        self, features: Dict[str, Any], detections: List[SecurityDetectionResult]
    ) -> Tuple[float, float, float]:
        if not detections:
            return 0.0, 0.95, 0.05
        max_risk = max(d.risk_score for d in detections)
        avg_conf = sum(d.confidence for d in detections) / len(detections)
        uncert = round(1.0 - avg_conf, 4)
        return max_risk, avg_conf, uncert

    def generate_evidence(
        self, detection: TransactionDetectionResult, dataset_name: str = "transaction_stream"
    ) -> SecurityEvidence:
        return transaction_detection_to_security_evidence(detection, dataset_name=dataset_name)

    def process_event(self, raw_event: Dict[str, Any]) -> List[TransactionDetectionResult]:
        t0 = time.perf_counter()
        valid, errs = self.validate(raw_event)
        if not valid:
            self.errors_count += 1
            logger.warning(f"Invalid Transaction event: {errs}")
            return []

        event = normalize_transaction_event(raw_event)
        dets = self.detect(event)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self._latencies.append(elapsed_ms)
        self.events_processed += 1
        self.detections_generated += len(dets)
        self.last_event_time = event.timestamp
        self.last_success_time = datetime.now(timezone.utc)

        return dets

    def process_batch(
        self, events: List[Dict[str, Any]], dataset_name: str = "transaction_stream"
    ) -> Tuple[List[TransactionDetectionResult], List[SecurityEvidence]]:
        all_dets: List[TransactionDetectionResult] = []
        all_ev: List[SecurityEvidence] = []

        for raw in events:
            dets = self.process_event(raw)
            all_dets.extend(dets)
            for d in dets:
                all_ev.append(self.generate_evidence(d, dataset_name=dataset_name))

        return all_dets, all_ev

    def health(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        uptime = max(1.0, (now - self.start_time).total_seconds())
        avg_lat = float(sum(self._latencies) / len(self._latencies)) if self._latencies else 0.0

        return {
            "agent_id": self.agent_id,
            "version": self.version,
            "status": "OPERATIONAL" if self.errors_count == 0 or self.events_processed > 0 else "DEGRADED",
            "uptime_seconds": round(uptime, 1),
            "events_processed": self.events_processed,
            "detections_generated": self.detections_generated,
            "errors_count": self.errors_count,
            "last_event_time": self.last_event_time.isoformat() if self.last_event_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "processing_rate_events_per_sec": round(self.events_processed / uptime, 2),
            "average_latency_ms": round(avg_lat, 3),
            "active_detectors": [
                "VELOCITY_DETECTOR", "AMOUNT_ANOMALY_DETECTOR",
                "RECIPIENT_NOVELTY_DETECTOR"
            ],
        }

    def shutdown(self) -> None:
        logger.info(f"Shutting down {self.agent_id}")
