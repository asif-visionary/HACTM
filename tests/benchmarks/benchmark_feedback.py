"""
Benchmark script for Closed-Loop Adaptation Closed-Loop Feedback & Continuous Adaptation.
Measures latency and throughput at 1K, 10K, and 100K event scale.
"""

import time
from datetime import datetime, timezone
from hactm.feedback.models import (
    FeedbackEvent,
    FeedbackSourceType,
    FeedbackType,
    ValidationStatus,
    DecisionReplayRequest,
    CounterfactualRequest,
)
from hactm.feedback.router import FeedbackRouter
from hactm.feedback.adaptation_engine import AdaptationEngine
from hactm.feedback.replay_engine import DecisionReplayEngine, CounterfactualEngine


def benchmark_feedback_routing(scale: int = 1000):
    router = FeedbackRouter()
    fb = FeedbackEvent(
        feedback_id="bench_fb",
        source_type=FeedbackSourceType.ANALYST_VALIDATION,
        source_id="analyst_bench",
        event_type=FeedbackType.DETECTION_FEEDBACK,
        decision_id="dec_bench",
        agent_ids=["network_agent"],
        evidence_ids=["ev_1", "ev_2"],
        validation_status=ValidationStatus.ANALYST_CONFIRMED,
        details={"observed_outcome": "ATTACK_CONFIRMED"},
    )
    ctx = {"expected_info_gain": 0.70}

    start = time.perf_counter()
    for _ in range(scale):
        router.route_feedback(fb, ctx)
    duration = time.perf_counter() - start

    avg_ms = (duration / scale) * 1000.0
    throughput = scale / duration
    print(f"[{scale} Events] Feedback Routing Total: {duration:.4f}s | Avg: {avg_ms:.4f}ms/op | Throughput: {throughput:.1f} ops/sec")
    return avg_ms, throughput


def benchmark_decision_replay(scale: int = 1000):
    replay_eng = DecisionReplayEngine()
    req = DecisionReplayRequest(target_decision_id="dec_bench")
    hist = {"decision": "STEP_UP_2FA", "risk_score": 0.55}

    start = time.perf_counter()
    for _ in range(scale):
        replay_eng.replay_decision(req, hist)
    duration = time.perf_counter() - start

    avg_ms = (duration / scale) * 1000.0
    throughput = scale / duration
    print(f"[{scale} Events] Decision Replay Total: {duration:.4f}s | Avg: {avg_ms:.4f}ms/op | Throughput: {throughput:.1f} ops/sec")
    return avg_ms, throughput


if __name__ == "__main__":
    print("==================================================")
    print("HACTM CLOSED-LOOP ADAPTATION FEEDBACK & ADAPTATION BENCHMARKS")
    print("==================================================")
    benchmark_feedback_routing(1000)
    benchmark_feedback_routing(10000)
    benchmark_decision_replay(1000)
    benchmark_decision_replay(10000)
    print("==================================================")
