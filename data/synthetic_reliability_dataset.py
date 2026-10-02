"""
Generates synthetic multi-domain security dataset with ground-truth labels,
calibration gaps, drift shifts, and detector disagreement for Reliability & Trust evaluation.
"""

import json
import os
import random
from datetime import datetime, timezone


def generate_synthetic_dataset(output_path: str = "data/sample/synthetic_reliability_dataset.json", count: int = 500):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    random.seed(42)
    now = datetime.now(timezone.utc)

    records = []
    agents = [
        "network-security-agent",
        "phishing-intelligence-agent",
        "uba-agent",
        "identity-authentication-agent",
        "transaction-security-agent",
    ]

    for i in range(count):
        is_attack = 1 if (i % 4 == 0) else 0
        agent = agents[i % len(agents)]

        # Simulate detector raw confidence with varying calibration
        if is_attack:
            raw_conf = random.uniform(0.70, 0.99)
            risk = random.uniform(0.75, 0.98)
        else:
            raw_conf = random.uniform(0.05, 0.40)
            risk = random.uniform(0.02, 0.35)

        # Inject drift on subset after record index 350
        has_drift = (i > 350 and agent == "uba-agent")
        if has_drift:
            raw_conf = random.uniform(0.60, 0.85)  # Overconfident on normal activity

        rec = {
            "event_id": f"syn-ev-{i+1:05d}",
            "agent_id": agent,
            "detector_id": f"{agent}-det-1",
            "domain": agent.split("-")[0],
            "entity_id": f"usr-{(i % 30) + 1:03d}",
            "event_type": f"{agent.split('-')[0]}_event",
            "timestamp": now.isoformat(),
            "risk_score": round(risk, 4),
            "confidence": round(raw_conf, 4),
            "severity": "CRITICAL" if risk > 0.85 else ("HIGH" if risk > 0.65 else "LOW"),
            "ground_truth": is_attack,
            "has_drift": has_drift,
            "evidence": {
                "sample_index": i,
                "feature_vector": [random.random() for _ in range(5)],
            },
        }
        records.append(rec)

    with open(output_path, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Generated {count} synthetic evaluation records at {output_path}")
    return records


if __name__ == "__main__":
    generate_synthetic_dataset()
