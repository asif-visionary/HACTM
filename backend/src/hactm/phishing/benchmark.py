"""
Phishing Security Agent Performance Benchmark Suite.
Measures actual throughput (events/sec), mean latency, P95, P99, CPU, and RAM.
"""

import gc
import psutil
import time
from typing import Any, Dict, List
import numpy as np

from hactm.phishing.agent import PhishingIntelligenceAgent
from hactm.phishing.loader import generate_synthetic_phishing_dataset


def run_phishing_benchmark(scales: List[int] = [1000, 10000]) -> List[Dict[str, Any]]:
    """Runs performance benchmark for PhishingIntelligenceAgent across specified dataset scales."""
    agent = PhishingIntelligenceAgent()
    process = psutil.Process()
    results = []

    for scale in scales:
        dataset = generate_synthetic_phishing_dataset(count=scale, anomaly_ratio=0.3)
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
            "agent_id": "phishing-intelligence-agent",
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
