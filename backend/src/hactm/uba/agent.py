"""
User Behavior Analytics (UBA) Agent Coordinator.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.

Agent ID: uba-agent
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
from hactm.uba.detectors.exfiltration_detector import DataExfiltrationDetector
from hactm.uba.detectors.resource_detector import ResourceDetector
from hactm.uba.detectors.statistical_detector import StatisticalAnomalyDetector
from hactm.uba.detectors.temporal_detector import TemporalDetector
from hactm.uba.evidence_adapter import uba_detection_to_security_evidence
from hactm.uba.features import extract_uba_features
from hactm.uba.models import UbaDetectionResult, UbaEvent
from hactm.uba.normalization import normalize_uba_event
from hactm.uba.profile_manager import ProfileManager


class UBAAgent(BaseSecurityAgent):
    """
    Stateful specialized security agent for user activity and insider threat indicator analysis.
    Maintains bounded user activity profiles and peer baselines.
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        cfg_file = config_path or Path(__file__).resolve().parent.parent.parent.parent / "configs" / "uba.yaml"
        self.config: Dict[str, Any] = {}
        if Path(cfg_file).exists():
            with open(cfg_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f).get("uba", {})

        self.agent_id = self.config.get("agent_id", "uba-agent")
        self.version = self.config.get("version", "1.0.0")

        # Profile Manager
        min_ev = self.config.get("profile", {}).get("min_events_for_baseline", 5)
        max_h = self.config.get("profile", {}).get("max_history_events", 1000)
        self.profile_mgr = ProfileManager(min_baseline_events=min_ev, max_history=max_h)

        # Telemetry State
        self.start_time = datetime.now(timezone.utc)
        self.events_processed = 0
        self.detections_generated = 0
        self.errors_count = 0
        self.insufficient_baseline_count = 0
        self.last_event_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self._latencies: deque = deque(maxlen=1000)

        self.initialize()

    def initialize(self) -> "UBAAgent":
        """Initializes detectors."""
        self.temporal_detector = TemporalDetector(version=self.version)
        self.resource_detector = ResourceDetector(version=self.version)
        exfil_thresh = self.config.get("detection", {}).get("data_transfer_threshold_bytes", 100_000_000)
        self.exfiltration_detector = DataExfiltrationDetector(version=self.version, threshold_bytes=exfil_thresh)
        z_thresh = self.config.get("detection", {}).get("zscore_threshold", 3.0)
        self.statistical_detector = StatisticalAnomalyDetector(zscore_threshold=z_thresh, version=self.version)
        return self

    def validate(self, raw_event: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(raw_event, dict):
            return False, ["Input raw_event must be a dictionary"]
        if not raw_event.get("user_id") and not raw_event.get("user") and not raw_event.get("account"):
            errors.append("Missing required user identifier (user_id/user/account)")
        return len(errors) == 0, errors

    def extract_features(self, event: UbaEvent) -> Dict[str, Any]:
        return extract_uba_features(event, self.profile_mgr)

    def detect(self, event: UbaEvent) -> List[UbaDetectionResult]:
        # Extract features against current historical baseline
        features = self.extract_features(event)

        # Update profile with current event for future baseline calculation
        self.profile_mgr.update_profile(event)

        if features.get("insufficient_baseline"):
            self.insufficient_baseline_count += 1
            # For new users with insufficient baseline, return explicit baseline status result or empty
            return [
                UbaDetectionResult(
                    detection_id=f"det_uba_base_{event.event_id}",
                    event_id=event.event_id,
                    user_id=event.user_id,
                    detector_type="HEURISTIC",
                    detector_id="uba-profile-manager",
                    category="INSUFFICIENT_BASELINE",
                    risk_score=0.05,
                    confidence=0.40,
                    uncertainty=0.60,
                    severity="LOW",
                    explanation=f"Insufficient historical activity baseline for user '{event.user_id}'",
                    features_used=features,
                    detector_version=self.version,
                    reason_codes=["INSUFFICIENT_HISTORICAL_BASELINE"],
                    is_insufficient_baseline=True,
                )
            ]

        detections: List[UbaDetectionResult] = []
        for detector in [
            self.temporal_detector,
            self.resource_detector,
            self.exfiltration_detector,
            self.statistical_detector,
        ]:
            try:
                res = detector.detect(event, features)
                if res:
                    detections.append(res)
            except Exception as e:
                self.errors_count += 1
                logger.error(f"Detector {detector.detector_id} failed on {event.event_id}: {e}")

        return detections

    def explain(self, detection: SecurityDetectionResult) -> str:
        return detection.explanation

    def calculate_risk(
        self, features: Dict[str, Any], detections: List[SecurityDetectionResult]
    ) -> Tuple[float, float, float]:
        if not detections:
            return 0.0, 0.90, 0.10
        max_risk = max(d.risk_score for d in detections)
        avg_conf = sum(d.confidence for d in detections) / len(detections)
        uncert = round(1.0 - avg_conf, 4)
        return max_risk, avg_conf, uncert

    def generate_evidence(
        self, detection: UbaDetectionResult, dataset_name: str = "uba_stream"
    ) -> SecurityEvidence:
        return uba_detection_to_security_evidence(detection, dataset_name=dataset_name)

    def process_event(self, raw_event: Dict[str, Any]) -> List[UbaDetectionResult]:
        t0 = time.perf_counter()
        valid, errs = self.validate(raw_event)
        if not valid:
            self.errors_count += 1
            logger.warning(f"Invalid UBA event: {errs}")
            return []

        event = normalize_uba_event(raw_event)
        dets = self.detect(event)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self._latencies.append(elapsed_ms)
        self.events_processed += 1
        self.detections_generated += len(dets)
        self.last_event_time = event.timestamp
        self.last_success_time = datetime.now(timezone.utc)

        return dets

    def process_batch(
        self, events: List[Dict[str, Any]], dataset_name: str = "uba_stream"
    ) -> Tuple[List[UbaDetectionResult], List[SecurityEvidence]]:
        all_dets: List[UbaDetectionResult] = []
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

        users_observed = len(self.profile_mgr.user_profiles)
        pct_insufficient = (
            round((self.insufficient_baseline_count / max(1, self.events_processed)) * 100, 1)
        )

        return {
            "agent_id": self.agent_id,
            "version": self.version,
            "status": "OPERATIONAL" if self.errors_count == 0 or self.events_processed > 0 else "DEGRADED",
            "uptime_seconds": round(uptime, 1),
            "events_processed": self.events_processed,
            "detections_generated": self.detections_generated,
            "errors_count": self.errors_count,
            "users_observed": users_observed,
            "percentage_users_insufficient_baseline": pct_insufficient,
            "last_event_time": self.last_event_time.isoformat() if self.last_event_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "processing_rate_events_per_sec": round(self.events_processed / uptime, 2),
            "average_latency_ms": round(avg_lat, 3),
            "active_detectors": [
                "TEMPORAL_DETECTOR", "RESOURCE_DETECTOR",
                "EXFILTRATION_DETECTOR", "STATISTICAL_DETECTOR"
            ],
        }

    def shutdown(self) -> None:
        logger.info(f"Shutting down {self.agent_id}")
