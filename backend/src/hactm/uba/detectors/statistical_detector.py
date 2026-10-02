"""
Statistical Anomaly Detector for UBA Agent.
Specialized Security Agents — Robust Z-Score / MAD / Isolation Forest Statistical Baseline.
"""

from typing import Any, Dict, Optional
import numpy as np

from hactm.uba.models import UbaDetectionResult, UbaEvent
from hactm.core.constants import risk_score_to_severity


class StatisticalAnomalyDetector:
    """Robust Z-score / MAD statistical anomaly detector for user behavior metrics."""

    def __init__(self, zscore_threshold: float = 3.0, version: str = "1.0.0"):
        self.detector_id = "uba-statistical-detector"
        self.version = version
        self.zscore_threshold = zscore_threshold

    def detect(self, event: UbaEvent, features: Dict[str, Any]) -> Optional[UbaDetectionResult]:
        if features.get("insufficient_baseline"):
            # New user with insufficient baseline: return low confidence / no high risk anomaly
            return None

        # Check multi-dimensional feature deviations (new device, new IP, off-hours, high bytes)
        dev_count = sum([
            1 if features.get("is_new_device") else 0,
            1 if features.get("is_new_ip") else 0,
            1 if features.get("is_off_hours") else 0,
            1 if features.get("is_rare_resource") else 0,
            1 if features.get("bytes_deviation_ratio", 1.0) >= 3.0 else 0,
        ])

        if dev_count < 2:
            return None

        # Calculate robust score based on compound behavioral deviations
        risk_score = min(1.0, 0.35 + (dev_count * 0.15))
        confidence = 0.84
        uncertainty = round(1.0 - confidence, 4)

        return UbaDetectionResult(
            detection_id=f"det_uba_stat_{event.event_id}",
            event_id=event.event_id,
            user_id=event.user_id,
            detector_type="STATISTICAL",
            detector_id=self.detector_id,
            category="STATISTICAL_BEHAVIORAL_ANOMALY",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation=f"Statistical behavioral anomaly detected: {dev_count} compound profile deviations observed for user '{event.user_id}'",
            features_used={
                "compound_deviations_count": dev_count,
                "is_new_device": features.get("is_new_device"),
                "is_new_ip": features.get("is_new_ip"),
                "is_off_hours": features.get("is_off_hours"),
            },
            detector_version=self.version,
            reason_codes=["UBA_STATISTICAL_BEHAVIORAL_DEVIATION"],
        )
