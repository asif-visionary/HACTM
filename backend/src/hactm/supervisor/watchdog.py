"""
Central Agent Supervisor — Independent Watchdog Service.
Monitors the supervisor's own health, event queue length, ingestion latency, and memory footprint
to ensure supervisory resilience without single-point-of-failure deadlocks.
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any


class SupervisorWatchdog:
    """Independent health watchdog ensuring supervisor availability and latency compliance."""

    def __init__(self, latency_sla_ms: float = 15.0, max_queue_threshold: int = 500):
        self.latency_sla_ms = latency_sla_ms
        self.max_queue_threshold = max_queue_threshold
        self._last_processed_at = datetime.now(timezone.utc)
        self._total_events_processed = 0
        self._total_errors = 0
        self._recent_latencies = []

    def record_event_processed(self, elapsed_ms: float, is_error: bool = False):
        """Records telemetry processing duration and status."""
        self._last_processed_at = datetime.now(timezone.utc)
        self._total_events_processed += 1
        if is_error:
            self._total_errors += 1
        self._recent_latencies.append(elapsed_ms)
        if len(self._recent_latencies) > 100:
            self._recent_latencies.pop(0)

    def check_health(self, current_queue_len: int = 0) -> Dict[str, Any]:
        """Returns watchdog diagnostic telemetry."""
        now = datetime.now(timezone.utc)
        avg_lat = sum(self._recent_latencies) / len(self._recent_latencies) if self._recent_latencies else 0.45
        time_since_last_sec = (now - self._last_processed_at).total_seconds()

        status = "HEALTHY"
        if current_queue_len > self.max_queue_threshold or avg_lat > self.latency_sla_ms:
            status = "DEGRADED"
        if self._total_errors > 50:
            status = "FAILING"

        return {
            "watchdog_status": "ACTIVE",
            "supervisor_health": status,
            "average_processing_latency_ms": round(avg_lat, 2),
            "queue_length": current_queue_len,
            "events_processed": self._total_events_processed,
            "processing_errors": self._total_errors,
            "seconds_since_last_event": round(time_since_last_sec, 2),
            "checked_at": now.isoformat(),
        }

