"""
Performance Benchmark script for HACTM Orchestration Engine Engine.
Evaluates agent calls, CPU time, P95/P99 latency, and cost across 1K, 10K events.
"""

import time
import json
import os
from hactm.orchestration.models import AgentSelectionContext
from hactm.orchestration.registry import AgentRegistry
from hactm.orchestration.candidate_generator import CandidateAgentGenerator
from hactm.orchestration.scoring_engine import CandidateScoringEngine
from hactm.orchestration.information_gain import InformationGainEstimator
from hactm.orchestration.orchestrator import AdaptiveOrchestrator


def run_benchmark(num_events: int = 1000):
    print(f"\n==================================================")
    print(f"Running HACTM Orchestration Benchmark ({num_events} events)...")
    print(f"==================================================")

    registry = AgentRegistry()
    registry.register_default_agents()
    generator = CandidateAgentGenerator(registry)
    scoring_engine = CandidateScoringEngine()
    info_estimator = InformationGainEstimator()
    orchestrator = AdaptiveOrchestrator(registry, scoring_engine, info_estimator)

    event_types = ["suspicious_login", "phishing_email", "anomalous_data_transfer", "privilege_escalation"]

    start_time = time.time()
    latencies = []
    total_calls_all_agents = 0
    total_calls_adaptive = 0

    for i in range(num_events):
        ctx = AgentSelectionContext(
            context_id=f"ctx_bm_{i}",
            event_id=f"evt_bm_{i}",
            entity_ids=[f"usr_{i % 100}"],
            event_type=event_types[i % len(event_types)],
            current_risk=0.1 + (i % 90) / 100.0,
            current_uncertainty=0.2 + (i % 70) / 100.0,
        )

        t0 = time.time()
        decision = orchestrator.select_agents(ctx)
        t1 = time.time()

        latency_ms = (t1 - t0) * 1000.0
        latencies.append(latency_ms)

        total_calls_all_agents += 5  # Naive all-agent invocation
        total_calls_adaptive += len(decision.selected_agents)

    total_duration = time.time() - start_time
    latencies.sort()

    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    avg_latency = sum(latencies) / len(latencies)
    reduction_pct = ((total_calls_all_agents - total_calls_adaptive) / total_calls_all_agents) * 100.0

    print(f"Benchmark Results for {num_events} events:")
    print(f"  Total Elapsed Time: {total_duration:.2f} s")
    print(f"  Throughput: {num_events / total_duration:.1f} ops/sec")
    print(f"  Avg Latency: {avg_latency:.3f} ms")
    print(f"  P95 Latency: {p95:.3f} ms")
    print(f"  P99 Latency: {p99:.3f} ms")
    print(f"  Total Invocations (All Agents Baseline): {total_calls_all_agents}")
    print(f"  Total Invocations (Adaptive Orchestration):    {total_calls_adaptive}")
    print(f"  Invocation Cost Reduction:               {reduction_pct:.2f}%")

    out_dir = "results/orchestration/benchmarks"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"benchmark_{num_events}_events.json")

    results = {
        "num_events": num_events,
        "total_duration_sec": total_duration,
        "throughput_ops_sec": num_events / total_duration,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95,
        "p99_latency_ms": p99,
        "total_calls_all_agents": total_calls_all_agents,
        "total_calls_adaptive": total_calls_adaptive,
        "invocation_reduction_percent": reduction_pct,
    }

    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved benchmark results to {out_file}\n")
    return results


if __name__ == "__main__":
    run_benchmark(1000)
