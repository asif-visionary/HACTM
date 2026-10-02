"""
LLM Agent Failure Benchmark Pipeline.
Ingests AI Agent Failure dataset for Agent Reliability and Adaptive Orchestration research.
Extracts failure taxonomy, severity statistics, and reputation calibration metrics.
"""

import csv
import json
import logging
from pathlib import Path
from collections import Counter
from typing import Dict, Any, List, Optional

logger = logging.getLogger("hactm.datasets.agent_failure")


class AgentFailurePipeline:
    """Ingests LLM Agent Failure benchmark dataset into Agent Reliability metrics."""

    def __init__(self, base_data_dir: Optional[Path] = None):
        self.base_dir = base_data_dir or Path(__file__).resolve().parents[5] / "data"
        self.raw_dir = self.base_dir / "raw" / "agent_reliability" / "llm_agent_failure"
        self.processed_dir = self.base_dir / "processed" / "agent_reliability"
        self.splits_dir = self.base_dir / "splits" / "agent_reliability"

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.splits_dir.mkdir(parents=True, exist_ok=True)

    def process_agent_failures(self) -> Dict[str, Any]:
        """Ingests failure benchmark records and computes failure taxonomy & reliability calibration."""
        csv_files = list(self.raw_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError("No Agent Failure CSV file found.")

        target_file = csv_files[0]
        records = []
        failure_types = Counter()
        domain_counts = Counter()
        severity_counts = Counter()

        with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                ftype = row.get("failure_type", "Unknown").strip()
                domain = row.get("domain", "General").strip()
                severity = row.get("failure_severity", "Medium").strip()

                failure_types[ftype] += 1
                domain_counts[domain] += 1
                severity_counts[severity] += 1

                record = {
                    "task_id": row.get("task_id", f"task_{count}"),
                    "domain": domain,
                    "difficulty": row.get("difficulty", "Medium"),
                    "prompt_snippet": row.get("prompt", "")[:120],
                    "expected_answer_snippet": row.get("expected_answer", "")[:120],
                    "agent_answer_snippet": row.get("agent_answer", "")[:120],
                    "failure_type": ftype,
                    "failure_severity": severity,
                    "notes": row.get("notes", "")[:150],
                    "dataset_source": "llm_agent_failure_benchmark"
                }
                records.append(record)
                count += 1

        out_file = self.processed_dir / "llm_agent_failure_processed.json"
        
        # Calculate reliability calibration metrics for adaptive orchestration
        total = len(records)
        calibration_data = {
            "total_benchmark_tasks": total,
            "failure_taxonomy": dict(failure_types),
            "domain_breakdown": dict(domain_counts),
            "severity_breakdown": dict(severity_counts),
            "failure_probabilities": {k: round(v / total, 4) for k, v in failure_types.items()} if total > 0 else {},
            "records": records
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(calibration_data, f, indent=2)

        # Generate splits
        n = len(records)
        train_idx = int(n * 0.8)
        val_idx = int(n * 0.9)
        splits = {
            "train": len(records[:train_idx]),
            "validation": len(records[train_idx:val_idx]),
            "test": len(records[val_idx:])
        }
        with open(self.splits_dir / "agent_failure_split.json", "w", encoding="utf-8") as f:
            json.dump(splits, f, indent=2)

        return {
            "dataset": "LLM_Agent_Failure_Benchmark",
            "total_processed": total,
            "failure_types": dict(failure_types),
            "output_file": str(out_file)
        }
