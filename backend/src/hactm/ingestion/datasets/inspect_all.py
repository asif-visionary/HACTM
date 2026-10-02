"""
Schema and Content Inspector for Downloaded HACTM Datasets.
Uses standard Python modules (csv, json) for high-performance schema inspection without external dependencies.
"""

import csv
import json
from pathlib import Path
from collections import Counter

def inspect_datasets():
    base_dir = Path(__file__).resolve().parents[5] / "data"
    raw_dir = base_dir / "raw"

    report = {}

    # 1. ToN-IoT
    ton_file = raw_dir / "network" / "ton_iot" / "train_test_network.csv"
    if ton_file.exists():
        with open(ton_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            sample = next(reader, {})
            row_count = 1 + sum(1 for _ in reader)
        report["ToN-IoT"] = {
            "file": ton_file.name,
            "total_rows": row_count,
            "columns": cols,
            "sample_row": sample
        }

    # 2. BoT-IoT
    bot_files = list((raw_dir / "network" / "bot_iot").glob("*.csv"))
    if bot_files:
        bot_file = bot_files[0]
        with open(bot_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            sample = next(reader, {})
        report["BoT-IoT"] = {
            "sample_file": bot_file.name,
            "file_count": len(bot_files),
            "columns": cols,
            "sample_row": sample
        }

    # 3. Phishing Emails
    phish_files = list((raw_dir / "phishing" / "phishing_legitimate_emails").glob("*.csv"))
    if phish_files:
        p_file = phish_files[0]
        with open(p_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            sample = next(reader, {})
            labels = Counter()
            labels[sample.get("Email Type", sample.get("label", ""))] += 1
            for row in reader:
                labels[row.get("Email Type", row.get("label", ""))] += 1
        report["Phishing_Emails"] = {
            "file": p_file.name,
            "columns": cols,
            "sample_row": {k: (v[:60] + "..." if isinstance(v, str) and len(v) > 60 else v) for k, v in sample.items()},
            "labels": dict(labels)
        }

    # 4. NIST FRTE/FATE
    nist_file = raw_dir / "identity" / "nist_frte_fate" / "nist_frte_fate_benchmarks.json"
    if nist_file.exists():
        with open(nist_file, "r", encoding="utf-8") as f:
            n_data = json.load(f)
        report["NIST_FRTE_FATE"] = {
            "file": nist_file.name,
            "program": n_data.get("evaluation_program"),
            "metrics": n_data.get("metrics")
        }

    # 5. MISP Galaxy
    misp_dir = raw_dir / "threat_intelligence" / "misp_galaxy"
    json_files = list(misp_dir.rglob("*.json"))
    report["MISP_Galaxy"] = {
        "json_files_count": len(json_files),
        "sample_clusters": [f.name for f in json_files if "clusters" in str(f)][:5]
    }

    # 6. LLM Agent Failure Benchmark
    agent_files = list((raw_dir / "agent_reliability" / "llm_agent_failure").glob("*.csv"))
    if agent_files:
        a_file = agent_files[0]
        with open(a_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            cols = reader.fieldnames
            sample = next(reader, {})
        report["LLM_Agent_Failure"] = {
            "file": a_file.name,
            "columns": cols,
            "sample_row": sample
        }

    print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    inspect_datasets()
