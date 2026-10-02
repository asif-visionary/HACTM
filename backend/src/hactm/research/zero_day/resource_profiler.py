"""
Resource Profiler and Operational Latency / Time-to-Alert Measurement Subsystem for HACTM.
Measures CPU, Memory, Model Size, Throughput (events/sec P50/P95/P99), and Time-to-Alert lifecycle stages.
"""

import time
import os
import psutil
import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class TimeToAlertBreakdown(BaseModel):
    """Lifecycle latency measurement from event occurrence to enforcement."""
    event_id: str
    event_occurrence_ts: float
    detection_ts: float
    alert_generation_ts: float
    policy_decision_ts: float
    enforcement_ts: float

    detection_latency_ms: float
    alert_latency_ms: float
    policy_latency_ms: float
    enforcement_latency_ms: float
    total_response_latency_ms: float


class ResourceUtilizationResult(BaseModel):
    """Resource footprint and throughput measurement report."""
    cpu_percent: float
    memory_mb: float
    model_size_mb: float
    inference_latency_ms: float
    throughput_events_per_sec: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    disk_footprint_mb: float = 0.0


class ResourceProfiler:
    """Measures operational resource usage, throughput, and time-to-alert latency metrics."""

    @staticmethod
    def measure_throughput_and_latencies(
        latencies_ms: List[float],
        total_duration_sec: float,
        model_filepath: Optional[str] = None
    ) -> ResourceUtilizationResult:
        
        proc = psutil.Process(os.getpid())
        cpu_usage = proc.cpu_percent(interval=None)
        mem_mb = proc.memory_info().rss / (1024.0 * 1024.0)

        model_size_mb = 0.0
        if model_filepath and os.path.exists(model_filepath):
            model_size_mb = os.path.getsize(model_filepath) / (1024.0 * 1024.0)

        if latencies_ms:
            mean_lat = float(np.mean(latencies_ms))
            p50 = float(np.percentile(latencies_ms, 50))
            p95 = float(np.percentile(latencies_ms, 95))
            p99 = float(np.percentile(latencies_ms, 99))
            throughput = len(latencies_ms) / max(0.001, total_duration_sec)
        else:
            mean_lat, p50, p95, p99, throughput = 0.0, 0.0, 0.0, 0.0, 0.0

        return ResourceUtilizationResult(
            cpu_percent=round(cpu_usage, 2),
            memory_mb=round(mem_mb, 2),
            model_size_mb=round(model_size_mb, 2),
            inference_latency_ms=round(mean_lat, 3),
            throughput_events_per_sec=round(throughput, 2),
            p50_latency_ms=round(p50, 3),
            p95_latency_ms=round(p95, 3),
            p99_latency_ms=round(p99, 3)
        )

    @staticmethod
    def record_time_to_alert(
        event_id: str,
        occurrence_ts: float,
        detection_ts: float,
        alert_gen_ts: float,
        policy_dec_ts: float,
        enforcement_ts: float
    ) -> TimeToAlertBreakdown:
        
        det_lat = (detection_ts - occurrence_ts) * 1000.0
        alert_lat = (alert_gen_ts - detection_ts) * 1000.0
        pol_lat = (policy_dec_ts - alert_gen_ts) * 1000.0
        enf_lat = (enforcement_ts - policy_dec_ts) * 1000.0
        tot_lat = (enforcement_ts - occurrence_ts) * 1000.0

        return TimeToAlertBreakdown(
            event_id=event_id,
            event_occurrence_ts=occurrence_ts,
            detection_ts=detection_ts,
            alert_generation_ts=alert_gen_ts,
            policy_decision_ts=policy_dec_ts,
            enforcement_ts=enforcement_ts,
            detection_latency_ms=round(det_lat, 3),
            alert_latency_ms=round(alert_lat, 3),
            policy_latency_ms=round(pol_lat, 3),
            enforcement_latency_ms=round(enf_lat, 3),
            total_response_latency_ms=round(tot_lat, 3)
        )
