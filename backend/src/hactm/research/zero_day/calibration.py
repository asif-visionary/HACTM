"""
Calibration Engine for HACTM Zero-Day Risk Scores.
Computes Expected Calibration Error (ECE), Brier Score, and fits Platt Scaling / Temperature Scaling on validation data.
"""

import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel


class ReliabilityBin(BaseModel):
    """Data point for reliability diagram bin."""
    bin_index: int
    mean_predicted_confidence: float
    empirical_accuracy: float
    sample_count: int


class CalibrationResult(BaseModel):
    """Schema for model probability calibration metrics."""
    ece: float  # Expected Calibration Error
    brier_score: float  # Brier Score
    max_calibration_error: float
    calibration_method_used: str
    reliability_diagram: List[ReliabilityBin]


class CalibrationEngine:
    """Probabilistic calibration engine for HACTM risk and confidence scores."""

    @staticmethod
    def compute_ece_and_brier(
        y_true: List[int],
        y_prob: List[float],
        n_bins: int = 10
    ) -> CalibrationResult:
        
        y_t = np.array(y_true, dtype=np.float32)
        y_p = np.array(y_prob, dtype=np.float32)

        # Brier Score = Mean Squared Error between predicted probabilities and binary targets
        brier = float(np.mean((y_p - y_t) ** 2))

        bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        max_ce = 0.0
        total_samples = len(y_t)
        diagram = []

        for i in range(n_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]

            in_bin = (y_p >= bin_lower) & (y_p < bin_upper) if i < n_bins - 1 else (y_p >= bin_lower) & (y_p <= bin_upper)
            bin_size = int(np.sum(in_bin))

            if bin_size > 0:
                accuracy = float(np.mean(y_t[in_bin]))
                confidence = float(np.mean(y_p[in_bin]))
                abs_diff = abs(confidence - accuracy)
                ece += (bin_size / total_samples) * abs_diff
                max_ce = max(max_ce, abs_diff)

                diagram.append(
                    ReliabilityBin(
                        bin_index=i,
                        mean_predicted_confidence=round(confidence, 4),
                        empirical_accuracy=round(accuracy, 4),
                        sample_count=bin_size
                    )
                )
            else:
                diagram.append(
                    ReliabilityBin(
                        bin_index=i,
                        mean_predicted_confidence=round((bin_lower + bin_upper) / 2.0, 4),
                        empirical_accuracy=0.0,
                        sample_count=0
                    )
                )

        return CalibrationResult(
            ece=round(float(ece), 4),
            brier_score=round(float(brier), 4),
            max_calibration_error=round(float(max_ce), 4),
            calibration_method_used="raw_uncalibrated",
            reliability_diagram=diagram
        )

    @classmethod
    def fit_platt_scaling(
        self,
        y_val_true: List[int],
        y_val_uncalibrated: List[float]
    ) -> Tuple[float, float]:
        """Learns Platt Scaling scalar parameters (A, B) via logistic regression on validation data."""
        y_val = np.array(y_val_true, dtype=np.float32)
        logits = np.array([math.log(max(1e-5, p) / max(1e-5, 1.0 - p)) for p in y_val_uncalibrated], dtype=np.float32)

        # Simple gradient descent for A*logit + B
        A, B = 1.0, 0.0
        lr = 0.01
        for _ in range(100):
            preds = 1.0 / (1.0 + np.exp(-(A * logits + B)))
            err = preds - y_val
            A -= lr * float(np.mean(err * logits))
            B -= lr * float(np.mean(err))

        return float(A), float(B)

    @classmethod
    def apply_platt_scaling(
        self,
        y_uncalibrated: List[float],
        A: float,
        B: float
    ) -> List[float]:
        """Applies learned Platt scaling parameters to raw probabilities."""
        calibrated = []
        for p in y_uncalibrated:
            logit = math.log(max(1e-5, p) / max(1e-5, 1.0 - p))
            p_cal = 1.0 / (1.0 + math.exp(-(A * logit + B)))
            calibrated.append(round(float(p_cal), 4))
        return calibrated
