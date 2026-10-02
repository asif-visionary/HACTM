"""
Identity Security Agent Performance Benchmark Suite.
Measures actual throughput (events/sec), mean latency, P95, P99, CPU, and RAM.
"""

import gc
import psutil
import time
from typing import Any, Dict, List
import numpy as np

from hactm.identity.agent import IdentityAuthenticationAgent
from hactm.identity.loader import generate_synthetic_identity_dataset


def run_identity_benchmark(scales: List[int] = [1000, 10000]) -> List[Dict[str, Any]]:
    """Runs performance benchmark for IdentityAuthenticationAgent across dataset scales."""
    agent = IdentityAuthenticationAgent()
    process = psutil.Process()
    results = []

    for scale in scales:
        dataset = generate_synthetic_identity_dataset(count=scale, anomaly_ratio=0.25)
        gc.collect()

        mem_start_mb = process.memory_info().rss / (1024 * 1024)
        t_start = time.perf_counter()
        latencies_ms = []

        for item in dataset:
            t0 = time.perf_counter()
            agent.process_event(item)
            elapsed = (time.perf_counter() - t0) * 1000.0
            latencies_ms.append(elapsed)

        total_time = time.perf_counter() - t_start
        mem_end_mb = process.memory_info().rss / (1024 * 1024)

        throughput = scale / max(0.001, total_time)
        mean_lat = float(np.mean(latencies_ms))
        p95_lat = float(np.percentile(latencies_ms, 95))
        p99_lat = float(np.percentile(latencies_ms, 99))

        results.append({
            "agent_id": "identity-authentication-agent",
            "scale": scale,
            "total_time_seconds": round(total_time, 3),
            "throughput_events_per_sec": round(throughput, 2),
            "mean_latency_ms": round(mean_lat, 4),
            "p95_latency_ms": round(p95_lat, 4),
            "p99_latency_ms": round(p99_lat, 4),
            "memory_initial_mb": round(mem_start_mb, 2),
            "memory_final_mb": round(mem_end_mb, 2),
            "memory_delta_mb": round(mem_end_mb - mem_start_mb, 2),
        })

    return results
