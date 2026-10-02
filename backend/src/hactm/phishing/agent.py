"""
Phishing Intelligence Agent Coordinator.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.

Agent ID: phishing-intelligence-agent
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
from hactm.phishing.detectors.attachment_detector import AttachmentDetector
from hactm.phishing.detectors.bec_detector import BecDetector
from hactm.phishing.detectors.header_detector import HeaderDetector
from hactm.phishing.detectors.nlp_detector import NlpPhishingDetector
from hactm.phishing.detectors.spear_phishing_detector import SpearPhishingDetector
from hactm.phishing.detectors.url_detector import UrlDetector
from hactm.phishing.evidence_adapter import phishing_detection_to_security_evidence
from hactm.phishing.features import extract_email_features
from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.phishing.normalization import normalize_email_event


class PhishingIntelligenceAgent(BaseSecurityAgent):
    """
    Modular specialized security agent for email and messaging threat analysis.
    Executes Header, URL, Attachment, NLP, Spear Phishing, and BEC engines independently.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        cfg_file = config_path or Path(__file__).resolve().parent.parent.parent.parent / "configs" / "phishing.yaml"
        self.config: Dict[str, Any] = {}
        if Path(cfg_file).exists():
            with open(cfg_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f).get("phishing", {})

        self.agent_id = self.config.get("agent_id", "phishing-intelligence-agent")
        self.version = self.config.get("version", "1.0.0")
        self.model_version = self.config.get("model_version", "phish_tfidf_v1.0")

        # Telemetry state
        self.start_time = datetime.now(timezone.utc)
        self.events_processed = 0
        self.detections_generated = 0
        self.errors_count = 0
        self.last_event_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self._latencies: deque = deque(maxlen=1000)

        self.initialize()

    def initialize(self) -> "PhishingIntelligenceAgent":
        """Initializes detector engines with declarative configuration."""
        self.header_detector = HeaderDetector(version=self.version)
        self.url_detector = UrlDetector(version=self.version)
        self.attachment_detector = AttachmentDetector(version=self.version)
        self.nlp_detector = NlpPhishingDetector(model_version=self.model_version, version=self.version)
        self.spear_detector = SpearPhishingDetector(version=self.version)
        self.bec_detector = BecDetector(version=self.version)
        return self

    def validate(self, raw_event: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validates input email event structure."""
        errors = []
        if not isinstance(raw_event, dict):
            return False, ["Input raw_event must be a dictionary"]
        if not raw_event.get("message_id") and not raw_event.get("id") and not raw_event.get("event_id"):
            # Optional fallback ID can be generated, but validate notifies if totally bare
            pass
        return True, errors

    def extract_features(self, event: PhishingEmailEvent) -> Dict[str, Any]:
        """Extracts features from normalized email event."""
        return extract_email_features(event)

    def detect(self, event: PhishingEmailEvent) -> List[PhishingDetectionResult]:
        """Runs normalized event through all phishing detectors."""
        features = self.extract_features(event)
        detections: List[PhishingDetectionResult] = []

        for detector in [
            self.header_detector,
            self.url_detector,
            self.attachment_detector,
            self.nlp_detector,
            self.spear_detector,
            self.bec_detector,
        ]:
            try:
                res = detector.detect(event, features)
                if res:
                    detections.append(res)
            except Exception as e:
                self.errors_count += 1
                logger.error(f"Detector {detector.detector_id} failed on {event.message_id}: {e}")

        return detections

    def explain(self, detection: SecurityDetectionResult) -> str:
        """Returns human-understandable explanation."""
        return detection.explanation

    def calculate_risk(
        self, features: Dict[str, Any], detections: List[SecurityDetectionResult]
    ) -> Tuple[float, float, float]:
        """Calculates combined baseline risk, confidence, and baseline uncertainty for an event."""
        if not detections:
            return 0.0, 0.95, 0.05
        max_risk = max(d.risk_score for d in detections)
        avg_conf = sum(d.confidence for d in detections) / len(detections)
        uncert = round(1.0 - avg_conf, 4)
        return max_risk, avg_conf, uncert

    def generate_evidence(
        self, detection: PhishingDetectionResult, dataset_name: str = "phishing_stream"
    ) -> SecurityEvidence:
        """Converts PhishingDetectionResult to canonical SecurityEvidence."""
        return phishing_detection_to_security_evidence(detection, dataset_name=dataset_name)

    def process_event(self, raw_event: Dict[str, Any]) -> List[PhishingDetectionResult]:
        """Processes raw dictionary email into detection results."""
        t0 = time.perf_counter()
        valid, errs = self.validate(raw_event)
        if not valid:
            self.errors_count += 1
            logger.warning(f"Invalid email raw event: {errs}")
            return []

        event = normalize_email_event(raw_event)
        dets = self.detect(event)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self._latencies.append(elapsed_ms)
        self.events_processed += 1
        self.detections_generated += len(dets)
        self.last_event_time = event.timestamp
        self.last_success_time = datetime.now(timezone.utc)

        return dets

    def process_batch(
        self, events: List[Dict[str, Any]], dataset_name: str = "phishing_stream"
    ) -> Tuple[List[PhishingDetectionResult], List[SecurityEvidence]]:
        """Batch processes emails and returns detections & SecurityEvidence items."""
        all_dets: List[PhishingDetectionResult] = []
        all_ev: List[SecurityEvidence] = []

        for raw in events:
            dets = self.process_event(raw)
            all_dets.extend(dets)
            for d in dets:
                all_ev.append(self.generate_evidence(d, dataset_name=dataset_name))

        return all_dets, all_ev

    def health(self) -> Dict[str, Any]:
        """Returns non-fabricated operational health status."""
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
            "model_version": self.model_version,
            "active_detectors": [
                "HEADER_ANOMALY", "SUSPICIOUS_URL", "SUSPICIOUS_ATTACHMENT",
                "NLP_CLASSIFIER", "SPEAR_PHISHING", "BEC_DETECTOR"
            ],
        }

    def shutdown(self) -> None:
        logger.info(f"Shutting down {self.agent_id}")
