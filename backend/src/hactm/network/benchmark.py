"""
Network Security Agent Benchmark Suite.
Measures throughput, mean latency, P95, P99 latency, CPU, and memory across event scales.
Strictly records real measurements without fabrication.
"""

import time
import os
import psutil
from typing import Dict, Any, List
from datetime import datetime, timezone

from hactm.network.models import NetworkEvent
from hactm.network.agent import NetworkSecurityAgent


def generate_benchmark_events(count: int) -> List[NetworkEvent]:
    """Generates synthetic network events in memory for benchmarking."""
    events = []
    base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    for i in range(count):
        src_ip = f"192.168.1.{(i % 250) + 1}"
        dst_ip = f"10.0.0.{(i % 50) + 1}"
        dst_port = 80 if i % 10 != 0 else (22 if i % 20 == 0 else 443)
        protocol = "TCP" if i % 5 != 0 else "UDP"
        
        event = NetworkEvent(
            event_id=f"BM-EVT-{i:07d}",
            timestamp=base_time,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=10000 + (i % 50000),
            dst_port=dst_port,
            protocol=protocol,
            duration=0.05 + (i % 10) * 0.01,
            flow_bytes=500 + (i % 2000),
            flow_packets=5 + (i % 20),
            forward_bytes=250 + (i % 1000),
            backward_bytes=250 + (i % 1000),
            forward_packets=3 + (i % 10),
            backward_packets=2 + (i % 10),
            tcp_flags="SYN,ACK" if protocol == "TCP" else None,
            flow_rate=10000.0,
            packet_rate=100.0,
            dataset="benchmark_synthetic",
            dataset_version="1.0",
            source_record_id=str(i)
        )
        events.append(event)
    return events


def run_network_benchmark(scales: List[int] = None) -> List[Dict[str, Any]]:
    """Runs network agent benchmark over specified event counts."""
    if scales is None:
        scales = [1000, 10000]

    process = psutil.Process(os.getpid())
    results = []

    for scale in scales:
        agent = NetworkSecurityAgent()
        agent.initialize()
        
        events = generate_benchmark_events(scale)
        latencies_ms: List[float] = []

        cpu_start = process.cpu_percent(interval=None)
        mem_start_mb = process.memory_info().rss / (1024 * 1024)
        t_start = time.perf_counter()

        detections_count = 0
        for evt in events:
            evt_start = time.perf_counter()
            dets = agent.process_event(evt)
            evt_end = time.perf_counter()
            latencies_ms.append((evt_end - evt_start) * 1000.0)
            detections_count += len(dets)

        t_total = time.perf_counter() - t_start
        cpu_end = process.cpu_percent(interval=None)
        mem_end_mb = process.memory_info().rss / (1024 * 1024)

        latencies_sorted = sorted(latencies_ms)
        mean_latency = sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0
        p95_idx = int(0.95 * len(latencies_sorted))
        p99_idx = int(0.99 * len(latencies_sorted))
        p95 = latencies_sorted[min(p95_idx, len(latencies_sorted) - 1)] if latencies_sorted else 0.0
        p99 = latencies_sorted[min(p99_idx, len(latencies_sorted) - 1)] if latencies_sorted else 0.0
        throughput = scale / t_total if t_total > 0 else 0.0

        res = {
            "scale": scale,
            "total_time_seconds": round(t_total, 4),
            "throughput_events_per_sec": round(throughput, 2),
            "mean_latency_ms": round(mean_latency, 4),
            "p95_latency_ms": round(p95, 4),
            "p99_latency_ms": round(p99, 4),
            "detections_generated": detections_count,
            "cpu_percent": round(cpu_end, 2),
            "memory_delta_mb": round(mem_end_mb - mem_start_mb, 2),
            "memory_final_mb": round(mem_end_mb, 2)
        }
        results.append(res)

    return results
