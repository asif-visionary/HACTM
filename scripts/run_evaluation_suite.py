"""
Evaluation Reproducible Evaluation Suite Runner for HACTM.
Usage: python scripts/run_evaluation_suite.py [--experiment EXP_14_END_TO_END] [--output research_bundle]
"""

import sys
import os
import argparse
import json
from datetime import datetime, timezone

# Add backend/src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "src")))

from hactm.evaluation.experiment_runner import ExperimentRunner
from hactm.evaluation.report_generator import ReportGenerator
from hactm.evaluation.models import ReportFormat


def main():
    parser = argparse.ArgumentParser(description="HACTM Evaluation Reproducible Evaluation Suite")
    parser.add_argument("--experiment", default="EXP_14_END_TO_END", help="Experiment ID to execute")
    parser.add_argument("--workload", type=int, default=10000, help="Workload event count")
    parser.add_argument("--output", default="research_bundle", help="Output bundle directory")
    args = parser.parse_args()

    print("=====================================================================")
    print("HACTM EVALUATION REPRODUCIBLE RESEARCH EVALUATION SUITE")
    print("=====================================================================")
    print(f"Executing Experiment: {args.experiment} | Workload: {args.workload} events")

    runner = ExperimentRunner()
    results = runner.run_master_experiment(args.experiment, args.workload)

    # Generate Reports & Bundle
    generator = ReportGenerator(output_dir=os.path.join(args.output, "reports"))

    pdf_rpt = generator.generate_report(args.experiment, "HACTM Final Evaluation Report (PDF)", ReportFormat.PDF, results)
    json_rpt = generator.generate_report(args.experiment, "HACTM Final Evaluation Data (JSON)", ReportFormat.JSON, results)
    csv_rpt = generator.generate_report(args.experiment, "HACTM Final Evaluation Summary (CSV)", ReportFormat.CSV, results)

    # Save manifest
    manifest_path = os.path.join(args.output, "datasets_manifest.json")
    os.makedirs(args.output, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "experiment": args.experiment,
            "workload": args.workload,
            "pdf_report": pdf_rpt.artifact_path,
            "json_report": json_rpt.artifact_path,
            "csv_report": csv_rpt.artifact_path,
            "checksum_sha256": pdf_rpt.reproducibility_checksum,
        }, f, indent=2)

    print("\n[SUCCESS] Execution Completed Successfully.")
    print(f"[SUCCESS] PDF Research Report generated at: {pdf_rpt.artifact_path}")
    print(f"[SUCCESS] JSON Data generated at: {json_rpt.artifact_path}")
    print(f"[SUCCESS] CSV Summary generated at: {csv_rpt.artifact_path}")
    print(f"[SUCCESS] Checksum SHA-256: {pdf_rpt.reproducibility_checksum}")
    print("=====================================================================")


if __name__ == "__main__":
    main()
