"""
Identity & Authentication Biometric Evaluation Adapter.
Consumes NIST FRTE/FATE public benchmark metrics (FMR, FNMR, DET curves, operating points)
for Identity Agent threshold calibration without processing restricted biometric data.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("hactm.datasets.identity")


class IdentityBiometricAdapter:
    """Adapts NIST FRTE/FATE public evaluation metrics into HACTM Identity Agent parameters."""

    def __init__(self, base_data_dir: Optional[Path] = None):
        self.base_dir = base_data_dir or Path(__file__).resolve().parents[5] / "data"
        self.raw_dir = self.base_dir / "raw" / "identity" / "nist_frte_fate"
        self.processed_dir = self.base_dir / "processed" / "identity"
        self.splits_dir = self.base_dir / "splits" / "identity"

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.splits_dir.mkdir(parents=True, exist_ok=True)

    def load_nist_benchmarks(self) -> Dict[str, Any]:
        """Loads NIST FRTE/FATE evaluation report metrics."""
        report_file = self.raw_dir / "nist_frte_fate_benchmarks.json"
        if not report_file.exists():
            raise FileNotFoundError(f"NIST benchmark report not found at {report_file}")

        with open(report_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Calibrate Identity Agent Operating Thresholds based on NIST FMR/FNMR curves
        calibrated_thresholds = {
            "high_security_visa": {
                "match_threshold": data["metrics"]["1:1_verification"]["visa_photos"]["operating_threshold"],
                "target_fmr": data["metrics"]["1:1_verification"]["visa_photos"]["FMR_10_minus_4"],
                "fnmr": data["metrics"]["1:1_verification"]["visa_photos"]["FNMR"]
            },
            "border_control": {
                "match_threshold": data["metrics"]["1:1_verification"]["border_photos"]["operating_threshold"],
                "target_fmr": data["metrics"]["1:1_verification"]["border_photos"]["FMR_10_minus_4"],
                "fnmr": data["metrics"]["1:1_verification"]["border_photos"]["FNMR"]
            },
            "unconstrained_wild": {
                "match_threshold": data["metrics"]["1:1_verification"]["wild_photos"]["operating_threshold"],
                "target_fmr": data["metrics"]["1:1_verification"]["wild_photos"]["FMR_10_minus_4"],
                "fnmr": data["metrics"]["1:1_verification"]["wild_photos"]["FNMR"]
            }
        }

        output_data = {
            "evaluation_program": data["evaluation_program"],
            "official_urls": data["official_urls"],
            "calibrated_thresholds": calibrated_thresholds,
            "disclaimer": data["disclaimer"]
        }

        out_file = self.processed_dir / "nist_identity_benchmarks_processed.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

        return output_data
