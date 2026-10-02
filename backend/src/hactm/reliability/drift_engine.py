"""
Reliability & Trust Drift Detection Engine.
Monitors feature, prediction, and performance shifts using Population Stability Index (PSI),
Jensen-Shannon divergence, and performance degradation tracking.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

from hactm.reliability.models import (
    DriftRecord,
    DriftPolicyAction,
    DriftSeverity,
)


class DriftEngine:
    """Baseline Drift Engine for HACTM Reliability & Trust."""

    def __init__(self, psi_threshold: float = 0.20, num_bins: int = 10):
        self.psi_threshold = psi_threshold
        self.num_bins = num_bins

    def calculate_psi(self, reference_samples: List[float], current_samples: List[float]) -> float:
        """
        Calculates Population Stability Index (PSI) between reference and current samples.
        """
        if not reference_samples or not current_samples:
            return 0.0

        n_ref = len(reference_samples)
        n_cur = len(current_samples)

        # Quantile binning based on reference distribution
        min_val = min(min(reference_samples), min(current_samples))
        max_val = max(max(reference_samples), max(current_samples))
        if abs(max_val - min_val) < 1e-9:
            return 0.0

        step = (max_val - min_val) / float(self.num_bins)
        bins = [min_val + i * step for i in range(self.num_bins + 1)]

        psi = 0.0
        eps = 1e-4  # Avoid log(0) and div-by-zero

        for i in range(self.num_bins):
            b_low = bins[i]
            b_high = bins[i + 1]

            ref_count = sum(1 for x in reference_samples if b_low <= x <= b_high if (i < self.num_bins - 1 or x <= b_high))
            cur_count = sum(1 for x in current_samples if b_low <= x <= b_high if (i < self.num_bins - 1 or x <= b_high))

            ref_pct = max(eps, float(ref_count) / float(n_ref))
            cur_pct = max(eps, float(cur_count) / float(n_cur))

            bin_psi = (cur_pct - ref_pct) * math.log(cur_pct / ref_pct)
            psi += bin_psi

        return max(0.0, round(psi, 4))

    def calculate_js_divergence(self, p_dist: List[float], q_dist: List[float]) -> float:
        """
        Calculates Jensen-Shannon Divergence between two probability distributions.
        """
        if len(p_dist) != len(q_dist) or not p_dist:
            return 0.0

        eps = 1e-9
        p = [max(eps, x) for x in p_dist]
        q = [max(eps, x) for x in q_dist]

        p_sum = sum(p)
        q_sum = sum(q)

        p = [x / p_sum for x in p]
        q = [x / q_sum for x in q]

        m = [0.5 * (p[i] + q[i]) for i in range(len(p))]

        kl_pm = sum(p[i] * math.log(p[i] / m[i]) for i in range(len(p)))
        kl_qm = sum(q[i] * math.log(q[i] / m[i]) for i in range(len(q)))

        js_div = 0.5 * kl_pm + 0.5 * kl_qm
        return max(0.0, round(js_div, 4))

    def monitor_drift(
        self,
        agent_id: str,
        feature_or_signal: str,
        reference_values: List[float],
        current_values: List[float],
        detector_id: Optional[str] = None,
        model_version: str = "1.0.0",
        drift_method: str = "PSI",
        threshold: Optional[float] = None,
        reference_window_start: Optional[datetime] = None,
        reference_window_end: Optional[datetime] = None,
        current_window_start: Optional[datetime] = None,
        current_window_end: Optional[datetime] = None,
    ) -> DriftRecord:
        """
        Executes drift evaluation for a signal/feature and determines policy action.
        """
        now = datetime.now(timezone.utc)
        thresh = threshold if threshold is not None else self.psi_threshold

        if drift_method == "JS_DIVERGENCE":
            drift_score = self.calculate_js_divergence(reference_values, current_values)
        else:  # PSI default
            drift_score = self.calculate_psi(reference_values, current_values)

        drift_detected = drift_score >= thresh

        # Determine severity and policy action
        if drift_score >= 0.35:
            severity = DriftSeverity.HIGH
            policy_action = DriftPolicyAction.REQUIRE_RECALIBRATION
        elif drift_score >= 0.20:
            severity = DriftSeverity.MODERATE
            policy_action = DriftPolicyAction.PENALIZE_RELIABILITY
        elif drift_score >= 0.10:
            severity = DriftSeverity.LOW
            policy_action = DriftPolicyAction.MONITOR
        else:
            severity = DriftSeverity.NONE
            policy_action = DriftPolicyAction.IGNORE

        drift_id = f"drift-{uuid.uuid4().hex[:12]}"
        return DriftRecord(
            drift_id=drift_id,
            agent_id=agent_id,
            detector_id=detector_id,
            feature_or_signal=feature_or_signal,
            reference_window_start=reference_window_start or now,
            reference_window_end=reference_window_end or now,
            current_window_start=current_window_start or now,
            current_window_end=current_window_end or now,
            drift_method=drift_method,
            drift_score=drift_score,
            threshold=thresh,
            drift_detected=drift_detected,
            severity=severity,
            model_version=model_version,
            policy_action=policy_action,
            created_at=now,
        )
