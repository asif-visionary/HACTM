"""
Reliability Processing Engine.
Calculates contextual reliability, confidence intervals (Wilson Score), sample-size protection,
hierarchical agent/detector/domain reliability, and model-version inheritance rules.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

from hactm.reliability.models import (
    AgentReliabilityRecord,
    ReliabilityConfig,
    ReliabilityStatus,
)


class ReliabilityEngine:
    """Core Reliability Engine for HACTM Reliability & Trust."""

    def __init__(self, config: Optional[ReliabilityConfig] = None):
        self.config = config or ReliabilityConfig()

    def calculate_wilson_interval(
        self, successes: int, total: int, confidence_level: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Calculates Wilson score confidence interval for a binomial proportion.
        Returns (mean_estimate, lower_bound, upper_bound).
        """
        if total <= 0:
            return 0.5, 0.0, 1.0

        p_hat = float(successes) / float(total)

        # Standard normal z-value approximation for common confidence levels
        if abs(confidence_level - 0.99) < 0.005:
            z = 2.576
        elif abs(confidence_level - 0.90) < 0.005:
            z = 1.645
        else:  # default 0.95
            z = 1.96

        z2 = z * z
        denom = 1.0 + z2 / total
        center = (p_hat + z2 / (2.0 * total)) / denom

        spread = (z / denom) * math.sqrt(
            (p_hat * (1.0 - p_hat) / total) + (z2 / (4.0 * total * total))
        )

        lower = max(0.0, center - spread)
        upper = min(1.0, center + spread)
        return p_hat, lower, upper

    def evaluate_reliability(
        self,
        agent_id: str,
        true_positives: int,
        false_positives: int,
        true_negatives: int,
        false_negatives: int,
        detector_id: Optional[str] = None,
        domain: Optional[str] = None,
        model_version: str = "1.0.0",
        evaluation_window_start: Optional[datetime] = None,
        evaluation_window_end: Optional[datetime] = None,
        calibration_error: float = 0.05,
        uncertainty_quality: float = 0.85,
        stability_score: float = 1.0,
        drift_score: float = 0.0,
        evaluation_dataset: str = "synthetic_eval_v1",
        evaluation_method: str = "ground_truth_validation",
    ) -> AgentReliabilityRecord:
        """
        Calculates a complete AgentReliabilityRecord using ground truth outcomes.
        Guarantees anti-circularity by requiring explicit TP, FP, TN, FN counts.
        """
        now = datetime.now(timezone.utc)
        start_time = evaluation_window_start or now
        end_time = evaluation_window_end or now

        total_samples = true_positives + false_positives + true_negatives + false_negatives
        total_positive_predictions = true_positives + false_positives
        total_actual_positives = true_positives + false_negatives
        total_actual_negatives = true_negatives + false_positives

        # Precision calculation
        if total_positive_predictions > 0:
            precision = float(true_positives) / float(total_positive_predictions)
        else:
            precision = 0.5

        # Recall calculation
        if total_actual_positives > 0:
            recall = float(true_positives) / float(total_actual_positives)
        else:
            recall = 0.5

        # F1 score
        if (precision + recall) > 0:
            f1_score = 2.0 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0

        # False Positive Rate (FPR)
        if total_actual_negatives > 0:
            false_positive_rate = float(false_positives) / float(total_actual_negatives)
        else:
            false_positive_rate = 0.0

        # False Negative Rate (FNR)
        if total_actual_positives > 0:
            false_negative_rate = float(false_negatives) / float(total_actual_positives)
        else:
            false_negative_rate = 0.0

        # Wilson Confidence Interval on correctness (TP + TN) / Total
        correct_samples = true_positives + true_negatives
        mean_acc, lower_ci, upper_ci = self.calculate_wilson_interval(
            successes=correct_samples,
            total=total_samples,
            confidence_level=self.config.confidence_level,
        )

        # Base score from precision, recall, and f1
        w_prec = self.config.metric_weights.get("precision", 0.25)
        w_rec = self.config.metric_weights.get("recall", 0.20)
        w_f1 = self.config.metric_weights.get("f1", 0.15)
        w_cal = self.config.metric_weights.get("calibration_error", 0.15)
        w_unc = self.config.metric_weights.get("uncertainty_quality", 0.10)
        w_stab = self.config.metric_weights.get("stability", 0.10)
        w_drift = self.config.metric_weights.get("drift_penalty", 0.05)

        raw_score = (
            w_prec * precision
            + w_rec * recall
            + w_f1 * f1_score
            + w_unc * uncertainty_quality
            + w_stab * stability_score
            - w_cal * calibration_error
            - w_drift * (drift_score * self.config.drift_penalty_weight)
        )

        # Normalize score sum
        norm_factor = w_prec + w_rec + w_f1 + w_unc + w_stab
        if norm_factor > 0:
            raw_score = raw_score / norm_factor

        # Bound score between floor and ceiling
        reliability_score = max(
            self.config.minimum_reliability_floor,
            min(self.config.maximum_reliability_ceiling, raw_score),
        )

        # Determine Reliability Status with Small Sample Protection
        if total_samples < self.config.minimum_sample_threshold:
            status = ReliabilityStatus.INSUFFICIENT_DATA
            # For insufficient data, reduce reliability score towards neutral 0.5 and widen CI
            reliability_score = 0.50
            lower_ci = 0.10
            upper_ci = 0.90
        elif total_samples < 30:
            status = ReliabilityStatus.LIMITED_EVIDENCE
        elif drift_score >= 0.20:
            status = ReliabilityStatus.DRIFT_OBSERVED
        elif calibration_error >= 0.15:
            status = ReliabilityStatus.CALIBRATION_REQUIRED
        else:
            status = ReliabilityStatus.WELL_SUPPORTED

        rec_id = f"rel-{uuid.uuid4().hex[:12]}"
        return AgentReliabilityRecord(
            reliability_id=rec_id,
            agent_id=agent_id,
            detector_id=detector_id,
            domain=domain,
            model_version=model_version,
            evaluation_window_start=start_time,
            evaluation_window_end=end_time,
            sample_count=total_samples,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1_score, 4),
            false_positive_rate=round(false_positive_rate, 4),
            false_negative_rate=round(false_negative_rate, 4),
            calibration_error=round(calibration_error, 4),
            uncertainty_quality=round(uncertainty_quality, 4),
            stability_score=round(stability_score, 4),
            drift_score=round(drift_score, 4),
            reliability_score=round(reliability_score, 4),
            confidence_interval_lower=round(lower_ci, 4),
            confidence_interval_upper=round(upper_ci, 4),
            evaluation_dataset=evaluation_dataset,
            evaluation_method=evaluation_method,
            reliability_status=status,
            created_at=now,
            updated_at=now,
            metadata={
                "true_positives": true_positives,
                "false_positives": false_positives,
                "true_negatives": true_negatives,
                "false_negatives": false_negatives,
                "raw_score": round(raw_score, 4),
            },
        )

    def handle_model_version_change(
        self,
        agent_id: str,
        previous_record: Optional[AgentReliabilityRecord],
        new_version: str,
        allow_inheritance: bool = False,
        inheritance_decay: float = 0.80,
    ) -> AgentReliabilityRecord:
        """
        Handles model version transitions (e.g. Model v1 -> v2).
        If allow_inheritance is False, resets status to INSUFFICIENT_DATA as required by Section 20.
        """
        now = datetime.now(timezone.utc)
        rec_id = f"rel-{uuid.uuid4().hex[:12]}"

        if not previous_record or not allow_inheritance:
            return AgentReliabilityRecord(
                reliability_id=rec_id,
                agent_id=agent_id,
                detector_id=previous_record.detector_id if previous_record else None,
                domain=previous_record.domain if previous_record else None,
                model_version=new_version,
                evaluation_window_start=now,
                evaluation_window_end=now,
                sample_count=0,
                reliability_score=0.50,
                confidence_interval_lower=0.10,
                confidence_interval_upper=0.90,
                reliability_status=ReliabilityStatus.INSUFFICIENT_DATA,
                evaluation_method="version_change_reset",
                created_at=now,
                updated_at=now,
                metadata={"inherited_from_version": previous_record.model_version if previous_record else None, "inherited": False},
            )
        else:
            # Inherit with decay
            inherited_score = max(0.1, previous_record.reliability_score * inheritance_decay)
            return AgentReliabilityRecord(
                reliability_id=rec_id,
                agent_id=agent_id,
                detector_id=previous_record.detector_id,
                domain=previous_record.domain,
                model_version=new_version,
                evaluation_window_start=now,
                evaluation_window_end=now,
                sample_count=previous_record.sample_count,
                precision=previous_record.precision * inheritance_decay,
                recall=previous_record.recall * inheritance_decay,
                f1_score=previous_record.f1_score * inheritance_decay,
                reliability_score=round(inherited_score, 4),
                confidence_interval_lower=max(0.0, previous_record.confidence_interval_lower * inheritance_decay),
                confidence_interval_upper=min(1.0, previous_record.confidence_interval_upper),
                reliability_status=ReliabilityStatus.LIMITED_EVIDENCE,
                evaluation_method="version_change_inheritance",
                created_at=now,
                updated_at=now,
                metadata={"inherited_from_version": previous_record.model_version, "inherited": True, "decay": inheritance_decay},
            )
