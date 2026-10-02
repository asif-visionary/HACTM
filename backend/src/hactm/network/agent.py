"""
Network Security Agent Coordinator.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Orchestrates:
- Signature Detection
- Heuristic Sliding-Window Behavioral Detection
- Statistical / ML Anomaly Detection
Produces validated NetworkDetectionResult and SecurityEvidence without autonomous blocking.
Tracks operational agent health and throughput metrics.
"""

from collections import deque
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import yaml

from hactm.core.logging import logger
from hactm.core.models import SecurityEvidence
from hactm.network.detectors.anomaly import AnomalyDetector
from hactm.network.detectors.heuristic import HeuristicDetector
from hactm.network.detectors.signature import SignatureDetector
from hactm.network.ml_ids.detector import MLIDSDetector
from hactm.network.evidence_adapter import detection_to_security_evidence
from hactm.network.models import NetworkDetectionResult, NetworkEvent


class NetworkSecurityAgent:
    """
    Stateful coordinator for network-level threat and anomaly detection.
    """
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        cfg_file = config_path or Path(__file__).resolve().parent.parent.parent.parent / "configs" / "network_detection.yaml"
        self.config: Dict[str, Any] = {}
        if Path(cfg_file).exists():
            with open(cfg_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f).get("network", {})

        self.agent_id = self.config.get("agent_id", "network-security-agent")
        self.version = self.config.get("version", "1.0.0")

        # Health & Telemetry State
        self.start_time = datetime.now()
        self.events_processed = 0
        self.detections_generated = 0
        self.errors_count = 0
        self.last_event_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        self._latencies: deque = deque(maxlen=1000)

        # Initialize Detectors
        self.initialize()

    def initialize(self) -> "NetworkSecurityAgent":
        """Initializes detector engines, loads signatures, and resets runtime buffers."""
        self._init_detectors()
        return self

    def _init_detectors(self) -> None:
        port_cfg = self.config.get("port_scan", {})
        host_cfg = self.config.get("host_scan", {})
        flood_cfg = self.config.get("connection_rate", {})
        late_cfg = self.config.get("lateness", {})

        # 1. Signature Engine
        sig_file = self.config.get("signatures", {}).get("rule_file")
        self.signature_detector = SignatureDetector(signatures_file=sig_file)

        # 2. Heuristic Engine
        self.heuristic_detector = HeuristicDetector(
            port_scan_window=port_cfg.get("window_seconds", 30),
            port_scan_threshold=port_cfg.get("distinct_ports_threshold", 15),
            host_scan_window=host_cfg.get("window_seconds", 30),
            host_scan_threshold=host_cfg.get("distinct_hosts_threshold", 10),
            flood_window=flood_cfg.get("window_seconds", 10),
            flood_threshold=flood_cfg.get("threshold", 100),
            allowed_lateness_seconds=late_cfg.get("allowed_lateness_seconds", 60),
        )

        # 3. Anomaly Engine
        anom_cfg = self.config.get("anomaly", {})
        self.anomaly_detector = AnomalyDetector(
            algorithm=anom_cfg.get("algorithm", "isolation_forest"),
            contamination=anom_cfg.get("contamination", 0.05),
            features=anom_cfg.get("features"),
        )

        # 4. Integrated cstub/ml-ids ML Engine
        self.ml_ids_detector = MLIDSDetector(
            decision_threshold=self.config.get("ml_ids", {}).get("threshold", 0.50)
        )

    def process_event(self, event: NetworkEvent) -> List[NetworkDetectionResult]:
        """
        Runs event through Signature, Heuristic, Anomaly, and integrated cstub/ml-ids ML engines.
        Returns all generated detection results without dropping conflicting evidence.
        """
        t0 = time.perf_counter()
        detections: List[NetworkDetectionResult] = []

        # 1. Signature detection
        try:
            sig_res = self.signature_detector.detect(event)
            if sig_res:
                detections.append(sig_res)
        except Exception as e:
            self.errors_count += 1
            logger.error(f"Signature detector failed on event {event.event_id}: {e}")

        # 2. Heuristic detection
        try:
            heur_res = self.heuristic_detector.detect(event)
            if heur_res:
                detections.append(heur_res)
        except Exception as e:
            self.errors_count += 1
            logger.error(f"Heuristic detector failed on event {event.event_id}: {e}")

        # 3. Anomaly detection
        try:
            anom_res = self.anomaly_detector.detect(event)
            if anom_res:
                detections.append(anom_res)
        except Exception as e:
            self.errors_count += 1
            logger.error(f"Anomaly detector failed on event {event.event_id}: {e}")

        # 4. Integrated cstub/ml-ids ML Detection
        try:
            mlids_res = self.ml_ids_detector.detect(event)
            if mlids_res:
                detections.append(mlids_res)
        except Exception as e:
            self.errors_count += 1
            logger.error(f"cstub/ml-ids detector failed on event {event.event_id}: {e}")

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self._latencies.append(elapsed_ms)
        self.events_processed += 1
        self.detections_generated += len(detections)
        self.last_event_time = event.timestamp
        self.last_success_time = datetime.now()

        return detections

    def process_batch(
        self, events: List[NetworkEvent], dataset_name: str = "network_stream"
    ) -> Tuple[List[NetworkDetectionResult], List[SecurityEvidence]]:
        """
        Processes a batch of events and yields corresponding canonical SecurityEvidence.
        """
        all_detections: List[NetworkDetectionResult] = []
        all_evidence: List[SecurityEvidence] = []

        for ev in events:
            dets = self.process_event(ev)
            all_detections.extend(dets)
            for d in dets:
                all_evidence.append(detection_to_security_evidence(d, dataset_name=dataset_name))

        return all_detections, all_evidence

    def detect(self, event: NetworkEvent) -> List[NetworkDetectionResult]:
        """Direct detection alias for single NetworkEvent."""
        return self.process_event(event)

    def generate_evidence(
        self, detection: NetworkDetectionResult, dataset_name: str = "network_stream"
    ) -> SecurityEvidence:
        """Converts a NetworkDetectionResult into standard SecurityEvidence."""
        return detection_to_security_evidence(detection, dataset_name=dataset_name)

    def health(self) -> Dict[str, Any]:
        """Returns non-fabricated live agent health and performance metrics."""
        now = datetime.now()
        uptime_seconds = max(1.0, (now - self.start_time).total_seconds())
        avg_latency = float(sum(self._latencies) / len(self._latencies)) if self._latencies else 0.0

        return {
            "agent_id": self.agent_id,
            "version": self.version,
            "status": "OPERATIONAL" if self.errors_count == 0 or self.events_processed > 0 else "DEGRADED",
            "uptime_seconds": round(uptime_seconds, 1),
            "events_processed": self.events_processed,
            "detections_generated": self.detections_generated,
            "errors_count": self.errors_count,
            "last_event_time": self.last_event_time.isoformat() if self.last_event_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
            "processing_rate_events_per_sec": round(self.events_processed / uptime_seconds, 2),
            "average_latency_ms": round(avg_latency, 3),
            "active_detectors": ["SIGNATURE", "HEURISTIC", "ANOMALY", "ML_IDS"],
        }

    def shutdown(self) -> None:
        logger.info(f"Shutting down Network Security Agent {self.agent_id}")
