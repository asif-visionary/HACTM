"""
Performance Benchmark script for HACTM Zero-Trust Engine Zero-Trust Policy Engine.
Evaluates decision evaluation latency, throughput (ops/sec), P95/P99 latency, and blast-radius metrics across 1K, 10K events.
"""

import time
import json
import os
from hactm.zerotrust.models import (
    ZeroTrustDecisionContext,
    SubjectType,
    ResourceType,
    ActionType,
    SecurityZoneName,
    EnforcementMode,
)
from hactm.zerotrust.policy_engine import ZeroTrustPolicyEngine
from hactm.zerotrust.micro_segmentation import MicroSegmentationEngine


def run_benchmark(num_events: int = 1000):
    print(f"\n==================================================")
    print(f"Running HACTM Zero-Trust Engine Zero-Trust Benchmark ({num_events} decisions)...")
    print(f"==================================================")

    engine = ZeroTrustPolicyEngine(enforcement_mode=EnforcementMode.DRY_RUN)
    micro_engine = MicroSegmentationEngine()

    actions = [ActionType.READ, ActionType.WRITE, ActionType.TRANSFER, ActionType.ADMINISTER]
    zones = [SecurityZoneName.USER_ZONE, SecurityZoneName.APPLICATION_ZONE, SecurityZoneName.DATABASE_ZONE]

    start_time = time.time()
    latencies = []
    decisions_count = {"ALLOW": 0, "VERIFY": 0, "QUARANTINE": 0, "BLOCK": 0, "MONITOR": 0, "ESCALATE": 0}

    for i in range(num_events):
        ctx = ZeroTrustDecisionContext(
            context_id=f"ctx_bm_{i}",
            subject_id=f"usr_{i % 100}",
            subject_type=SubjectType.USER,
            resource_id=f"res_{i % 20}",
            resource_type=ResourceType.APPLICATION,
            requested_action=actions[i % len(actions)],
            current_risk=0.1 + (i % 90) / 100.0,
            uncertainty=0.05 + (i % 50) / 100.0,
            security_zone=zones[i % len(zones)],
        )

        t0 = time.time()
        record = engine.evaluate_decision(ctx)
        t1 = time.time()

        latency_ms = (t1 - t0) * 1000.0
        latencies.append(latency_ms)
        decisions_count[record.decision.value] += 1

    total_duration = time.time() - start_time
    latencies.sort()

    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    avg_latency = sum(latencies) / len(latencies)
    blast_metrics = micro_engine.calculate_blast_radius_reduction()

    print(f"Benchmark Results for {num_events} Zero-Trust Policy Decisions:")
    print(f"  Total Elapsed Time: {total_duration:.2f} s")
    print(f"  Throughput: {num_events / total_duration:.1f} ops/sec")
    print(f"  Avg Decision Latency: {avg_latency:.3f} ms")
    print(f"  P95 Decision Latency: {p95:.3f} ms")
    print(f"  P99 Decision Latency: {p99:.3f} ms")
    print(f"  Decision Breakdown: {decisions_count}")
    print(f"  Blast Radius Reduction: {blast_metrics['blast_radius_reduction_percent']}%")

    out_dir = "results/zero_trust/benchmarks"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"benchmark_{num_events}_decisions.json")

    results = {
        "num_events": num_events,
        "total_duration_sec": total_duration,
        "throughput_ops_sec": num_events / total_duration,
        "avg_latency_ms": avg_latency,
        "p95_latency_ms": p95,
        "p99_latency_ms": p99,
        "decisions_breakdown": decisions_count,
        "blast_radius_reduction": blast_metrics,
    }

    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved benchmark results to {out_file}\n")
    return results


if __name__ == "__main__":
    run_benchmark(1000)
