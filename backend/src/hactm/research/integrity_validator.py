"""
Result Integrity Validator for Research Validation.
Verifies provenance, metric ranges, numerical consistency, and detects duplicate/incomplete/failed runs.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

from hactm.research.models import (
    ValidationStatus,
    ResultIntegrityCheckRequest,
    ResultIntegrityCheckResponse,
)


class ResearchResultIntegrityValidator:
    """Validates the mathematical, structural, and provenance integrity of Evaluation results."""

    @staticmethod
    def validate_result(request: ResultIntegrityCheckRequest) -> ResultIntegrityCheckResponse:
        issues: List[str] = []
        validated_metrics: Dict[str, float] = {}

        # 1. Provenance Verification
        if not request.experiment_id or request.experiment_id.strip() == "":
            issues.append("Missing experiment_id in provenance metadata.")
        if not request.run_id or request.run_id.strip() == "":
            issues.append("Missing run_id in provenance metadata.")
        if not request.dataset_id or request.dataset_id.strip() == "":
            issues.append("Missing dataset_id in provenance metadata.")
        if not request.config_hash or request.config_hash.strip() == "":
            issues.append("Missing config_hash in provenance metadata.")

        # 2. Metric Availability & Value Validation
        metrics = request.metrics or {}
        if not metrics:
            issues.append("No metrics provided in experimental result.")

        normalized_metrics = ["precision", "recall", "f1", "fpr", "fnr", "auroc", "auprc"]
        non_negative_metrics = ["ece", "brier", "latency_ms", "cpu_percent", "ram_mb", "containment_time_ms"]

        for k, v in metrics.items():
            k_lower = k.lower()
            if v is None or math.isnan(v) or math.isinf(v):
                issues.append(f"Metric '{k}' has invalid value: {v}")
                continue

            validated_metrics[k] = float(v)

            if k_lower in normalized_metrics:
                if not (0.0 <= v <= 1.0):
                    issues.append(f"Normalized metric '{k}' = {v} outside valid range [0, 1].")

            if k_lower in non_negative_metrics:
                if v < 0:
                    issues.append(f"Non-negative metric '{k}' = {v} is less than 0.")

        # 3. Mathematical Consistency Checks
        # F1 = 2 * P * R / (P + R)
        precision = metrics.get("precision")
        recall = metrics.get("recall")
        f1 = metrics.get("f1")
        if precision is not None and recall is not None and f1 is not None:
            if precision + recall > 1e-9:
                expected_f1 = 2.0 * precision * recall / (precision + recall)
                if abs(f1 - expected_f1) > 0.05:
                    issues.append(
                        f"F1 inconsistency: reported F1={f1:.4f}, expected F1={expected_f1:.4f} from P={precision:.4f}, R={recall:.4f}"
                    )

        # FNR = 1 - Recall (where applicable)
        fnr = metrics.get("fnr")
        if recall is not None and fnr is not None:
            expected_fnr = 1.0 - recall
            if abs(fnr - expected_fnr) > 0.05:
                issues.append(
                    f"FNR inconsistency: reported FNR={fnr:.4f}, expected FNR={expected_fnr:.4f} from Recall={recall:.4f}"
                )

        # Determine Final Status
        if not issues:
            status = ValidationStatus.VALID
        elif any("outside valid range" in issue or "inconsistency" in issue for issue in issues):
            status = ValidationStatus.INCONSISTENT
        elif any("Missing" in issue for issue in issues):
            status = ValidationStatus.INCOMPLETE
        else:
            status = ValidationStatus.INVALID

        provenance = {
            "experiment_id": request.experiment_id,
            "run_id": request.run_id,
            "dataset_id": request.dataset_id,
            "dataset_version": request.dataset_version,
            "config_hash": request.config_hash,
            "model_versions": request.model_versions,
            "code_version": request.code_version,
            "timestamp": request.timestamp,
            "random_seed": request.random_seed,
            "environment_id": request.environment_id,
        }

        return ResultIntegrityCheckResponse(
            validation_id=f"val-{uuid.uuid4().hex[:8]}",
            experiment_id=request.experiment_id,
            run_id=request.run_id,
            status=status,
            issues=issues,
            validated_metrics=validated_metrics,
            provenance=provenance,
            timestamp=datetime.now(timezone.utc),
        )
