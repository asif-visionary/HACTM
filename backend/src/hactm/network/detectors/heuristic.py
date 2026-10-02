"""
Heuristic Behavioral Network Detectors.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Implements bounded-window sliding heuristics for:
- Port-Scan Detection (distinct destination ports threshold within window W)
- Host-Scan / Network Sweep (distinct destination hosts threshold within window W)
- Connection-Flood Anomaly (connection attempts threshold within window W)
Features memory bounding (TTL/deque cleanup) and handles out-of-order / late events.
"""

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import time
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

from hactm.core.constants import SeverityLevel
from hactm.network.detectors.base import BaseDetector
from hactm.network.models import DetectorType, NetworkDetectionResult, NetworkEvent


class FlowEntry:
    """Lightweight bounded memory item for sliding window state."""
    __slots__ = ("timestamp", "dst_ip", "dst_port", "event_id")

    def __init__(self, timestamp: datetime, dst_ip: str, dst_port: Optional[int], event_id: str):
        self.timestamp = timestamp
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.event_id = event_id


class HeuristicDetector(BaseDetector):
    """
    Sliding-window behavioral heuristic engine.
    """
    detector_type = DetectorType.HEURISTIC
    detector_id = "network-heuristic-engine"
    detector_version = "1.0.0"

    def __init__(
        self,
        port_scan_window: int = 30,
        port_scan_threshold: int = 15,
        host_scan_window: int = 30,
        host_scan_threshold: int = 10,
        flood_window: int = 10,
        flood_threshold: int = 100,
        allowed_lateness_seconds: int = 60,
        max_buffer_per_src: int = 500,
    ):
        self.port_scan_window = port_scan_window
        self.port_scan_threshold = port_scan_threshold
        self.host_scan_window = host_scan_window
        self.host_scan_threshold = host_scan_threshold
        self.flood_window = flood_window
        self.flood_threshold = flood_threshold
        self.allowed_lateness_seconds = allowed_lateness_seconds
        self.max_buffer_per_src = max_buffer_per_src

        # Bounded sliding window stores: src_ip -> deque of FlowEntry
        self._history: Dict[str, Deque[FlowEntry]] = defaultdict(lambda: deque(maxlen=self.max_buffer_per_src))
        self._last_cleanup = time.time()

    def _cleanup_expired(self, current_ts: datetime, max_window: int) -> None:
        """Evicts entries older than the maximum window from memory."""
        cutoff = current_ts - timedelta(seconds=max_window + self.allowed_lateness_seconds)
        empty_keys = []
        for src_ip, dq in self._history.items():
            while dq and dq[0].timestamp < cutoff:
                dq.popleft()
            if not dq:
                empty_keys.append(src_ip)
        for k in empty_keys:
            del self._history[k]

    def detect(self, event: NetworkEvent) -> Optional[NetworkDetectionResult]:
        t0 = time.perf_counter()
        now_ts = event.timestamp
        src_ip = event.src_ip

        # Periodic bounded memory garbage collection
        if time.time() - self._last_cleanup > 30:
            self._cleanup_expired(now_ts, max(self.port_scan_window, self.host_scan_window, self.flood_window))
            self._last_cleanup = time.time()

        dq = self._history[src_ip]

        # Check late event condition
        late_event = False
        if dq and (dq[-1].timestamp - now_ts).total_seconds() > self.allowed_lateness_seconds:
            late_event = True

        # Append flow entry
        entry = FlowEntry(
            timestamp=now_ts,
            dst_ip=event.dst_ip,
            dst_port=event.dst_port,
            event_id=event.event_id,
        )
        dq.append(entry)

        # Evaluate Port Scan Heuristic
        port_cutoff = now_ts - timedelta(seconds=self.port_scan_window)
        distinct_ports: Set[int] = set()
        distinct_hosts: Set[str] = set()
        connection_count = 0

        # Iterate in temporal window
        for item in reversed(dq):
            if item.timestamp < port_cutoff:
                break
            connection_count += 1
            if item.dst_port is not None:
                distinct_ports.add(item.dst_port)
            distinct_hosts.add(item.dst_ip)

        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)

        # 1. Port Scan Check
        if len(distinct_ports) >= self.port_scan_threshold:
            explanation = (
                f"Heuristic Flag: Possible Port Scan. Source '{src_ip}' contacted {len(distinct_ports)} distinct "
                f"destination ports within {self.port_scan_window}s window (Threshold: {self.port_scan_threshold})."
            )
            return NetworkDetectionResult(
                detection_id=f"DET-HEUR-PORTSCAN-{event.event_id}",
                event_id=event.event_id,
                detector_type=DetectorType.HEURISTIC,
                detector_id="heuristic-port-scan",
                detector_version=self.detector_version,
                category="Reconnaissance / Port Scan",
                risk_score=0.78,
                confidence=0.88,
                uncertainty=0.12,
                severity=SeverityLevel.HIGH,
                reason_codes=["PORT_SCAN_THRESHOLD_EXCEEDED"],
                explanation=explanation,
                features_used={
                    "distinct_destination_ports": len(distinct_ports),
                    "window_seconds": self.port_scan_window,
                    "threshold": self.port_scan_threshold,
                    "late_event": late_event,
                },
                timestamp=datetime.now(timezone.utc),
                processing_time_ms=elapsed_ms,
                src_ip=src_ip,
                dst_ip=event.dst_ip,
            )

        # 2. Host Sweep Check
        host_cutoff = now_ts - timedelta(seconds=self.host_scan_window)
        sweep_hosts: Set[str] = set()
        for item in reversed(dq):
            if item.timestamp < host_cutoff:
                break
            sweep_hosts.add(item.dst_ip)

        if len(sweep_hosts) >= self.host_scan_threshold:
            explanation = (
                f"Heuristic Flag: Possible Host Sweep. Source '{src_ip}' contacted {len(sweep_hosts)} distinct "
                f"destination hosts within {self.host_scan_window}s window (Threshold: {self.host_scan_threshold})."
            )
            return NetworkDetectionResult(
                detection_id=f"DET-HEUR-HOSTSWEEP-{event.event_id}",
                event_id=event.event_id,
                detector_type=DetectorType.HEURISTIC,
                detector_id="heuristic-host-sweep",
                detector_version=self.detector_version,
                category="Reconnaissance / Host Sweep",
                risk_score=0.75,
                confidence=0.85,
                uncertainty=0.15,
                severity=SeverityLevel.HIGH,
                reason_codes=["HOST_SWEEP_THRESHOLD_EXCEEDED"],
                explanation=explanation,
                features_used={
                    "distinct_destination_hosts": len(sweep_hosts),
                    "window_seconds": self.host_scan_window,
                    "threshold": self.host_scan_threshold,
                    "late_event": late_event,
                },
                timestamp=datetime.now(timezone.utc),
                processing_time_ms=elapsed_ms,
                src_ip=src_ip,
                dst_ip=event.dst_ip,
            )

        # 3. Connection Flood Check
        flood_cutoff = now_ts - timedelta(seconds=self.flood_window)
        flood_conns = 0
        for item in reversed(dq):
            if item.timestamp < flood_cutoff:
                break
            flood_conns += 1

        if flood_conns >= self.flood_threshold:
            explanation = (
                f"Heuristic Flag: Connection Rate Anomaly. Source '{src_ip}' initiated {flood_conns} connections "
                f"within {self.flood_window}s window (Threshold: {self.flood_threshold})."
            )
            return NetworkDetectionResult(
                detection_id=f"DET-HEUR-CONNFLOD-{event.event_id}",
                event_id=event.event_id,
                detector_type=DetectorType.HEURISTIC,
                detector_id="heuristic-connection-flood",
                detector_version=self.detector_version,
                category="Traffic Anomaly / Connection Rate",
                risk_score=0.68,
                confidence=0.82,
                uncertainty=0.18,
                severity=SeverityLevel.MEDIUM,
                reason_codes=["CONNECTION_RATE_ANOMALY"],
                explanation=explanation,
                features_used={
                    "connections_in_window": flood_conns,
                    "window_seconds": self.flood_window,
                    "threshold": self.flood_threshold,
                    "late_event": late_event,
                },
                timestamp=datetime.now(timezone.utc),
                processing_time_ms=elapsed_ms,
                src_ip=src_ip,
                dst_ip=event.dst_ip,
            )

        return None
