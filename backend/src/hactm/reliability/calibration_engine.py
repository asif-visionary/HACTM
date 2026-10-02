"""
Reliability & Trust Confidence Calibration Engine.
Evaluates Expected Calibration Error (ECE), Maximum Calibration Error (MCE), Brier score,
and applies post-hoc calibration methods (Temperature Scaling, Platt Scaling, Isotonic Regression).
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

from hactm.reliability.models import CalibrationRecord


class CalibrationEngine:
    """Confidence Calibration and Scaling Engine for HACTM Reliability & Trust."""

    def __init__(self, num_bins: int = 10):
        self.num_bins = max(5, num_bins)

    def evaluate_calibration(
        self,
        agent_id: str,
        predicted_confidences: List[float],
        observed_outcomes: List[int],  # 1 for correct/true positive, 0 for incorrect/false positive
        detector_id: Optional[str] = None,
        model_version: str = "1.0.0",
        dataset: str = "synthetic_eval_v1",
        calibration_method: str = "temperature_scaling",
        temperature: float = 1.0,
    ) -> CalibrationRecord:
        """
        Evaluates ECE, MCE, Brier score, and reliability diagram data bins given predicted
        confidences and observed ground-truth outcomes (0 or 1).
        """
        now = datetime.now(timezone.utc)
        n = len(predicted_confidences)

        if n == 0 or len(observed_outcomes) != n:
            cal_id = f"cal-{uuid.uuid4().hex[:12]}"
            return CalibrationRecord(
                calibration_id=cal_id,
                agent_id=agent_id,
                detector_id=detector_id,
                model_version=model_version,
                dataset=dataset,
                evaluation_window_start=now,
                evaluation_window_end=now,
                sample_count=0,
                ece=0.0,
                mce=0.0,
                brier_score=0.0,
                calibration_method=calibration_method,
                pre_calibration_metric=0.0,
                post_calibration_metric=0.0,
                calibration_parameters={"temperature": temperature},
                reliability_diagram_data={"bins": []},
                created_at=now,
            )

        # 1. Calculate Brier Score = (1/N) * sum((confidence - outcome)^2)
        brier_score = sum((c - y) ** 2 for c, y in zip(predicted_confidences, observed_outcomes)) / float(n)

        # 2. Reliability Diagram Bins & ECE / MCE
        bins_data = []
        bin_boundaries = [i / float(self.num_bins) for i in range(self.num_bins + 1)]

        ece = 0.0
        mce = 0.0

        for i in range(self.num_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]

            # Collect samples in bin range
            bin_indices = [
                idx
                for idx, c in enumerate(predicted_confidences)
                if (c >= bin_lower and (c < bin_upper or (i == self.num_bins - 1 and c <= bin_upper)))
            ]

            bin_size = len(bin_indices)
            if bin_size > 0:
                bin_conf = sum(predicted_confidences[idx] for idx in bin_indices) / float(bin_size)
                bin_acc = sum(observed_outcomes[idx] for idx in bin_indices) / float(bin_size)
                abs_gap = abs(bin_conf - bin_acc)

                ece += (bin_size / float(n)) * abs_gap
                mce = max(mce, abs_gap)

                bins_data.append({
                    "bin_index": i,
                    "bin_lower": round(bin_lower, 2),
                    "bin_upper": round(bin_upper, 2),
                    "count": bin_size,
                    "avg_confidence": round(bin_conf, 4),
                    "avg_accuracy": round(bin_acc, 4),
                    "gap": round(abs_gap, 4),
                })
            else:
                bins_data.append({
                    "bin_index": i,
                    "bin_lower": round(bin_lower, 2),
                    "bin_upper": round(bin_upper, 2),
                    "count": 0,
                    "avg_confidence": round((bin_lower + bin_upper) / 2.0, 4),
                    "avg_accuracy": 0.0,
                    "gap": 0.0,
                })

        # Calculate calibrated confidences after temperature scaling
        calibrated_confidences = [self.calibrate_confidence(c, method=calibration_method, temperature=temperature) for c in predicted_confidences]
        post_brier = sum((c - y) ** 2 for c, y in zip(calibrated_confidences, observed_outcomes)) / float(n)

        cal_id = f"cal-{uuid.uuid4().hex[:12]}"
        return CalibrationRecord(
            calibration_id=cal_id,
            agent_id=agent_id,
            detector_id=detector_id,
            model_version=model_version,
            dataset=dataset,
            evaluation_window_start=now,
            evaluation_window_end=now,
            sample_count=n,
            ece=round(ece, 4),
            mce=round(mce, 4),
            brier_score=round(brier_score, 4),
            calibration_method=calibration_method,
            pre_calibration_metric=round(brier_score, 4),
            post_calibration_metric=round(post_brier, 4),
            calibration_parameters={"temperature": temperature, "num_bins": self.num_bins},
            reliability_diagram_data={"bins": bins_data, "ece": round(ece, 4), "mce": round(mce, 4)},
            created_at=now,
        )

    def calibrate_confidence(
        self,
        raw_confidence: float,
        method: str = "temperature_scaling",
        temperature: float = 1.25,
        platt_a: float = 1.0,
        platt_b: float = 0.0,
    ) -> float:
        """
        Applies confidence scaling (Temperature, Platt, or Isotonic proxy).
        Returns calibrated confidence strictly bounded in [0, 1].
        """
        raw_confidence = max(0.001, min(0.999, raw_confidence))

        if method == "temperature_scaling":
            # Logit transformation with temperature scaling
            logit = math.log(raw_confidence / (1.0 - raw_confidence))
            scaled_logit = logit / max(0.1, temperature)
            calibrated = 1.0 / (1.0 + math.exp(-scaled_logit))
        elif method == "platt_scaling":
            logit = math.log(raw_confidence / (1.0 - raw_confidence))
            scaled_logit = platt_a * logit + platt_b
            calibrated = 1.0 / (1.0 + math.exp(-scaled_logit))
        elif method == "isotonic":
            # Stepwise isotonic calibration mapping
            if raw_confidence > 0.85:
                calibrated = raw_confidence * 0.90
            elif raw_confidence < 0.30:
                calibrated = raw_confidence * 0.70
            else:
                calibrated = raw_confidence * 0.85
        else:
            calibrated = raw_confidence

        return max(0.0, min(1.0, round(calibrated, 4)))
