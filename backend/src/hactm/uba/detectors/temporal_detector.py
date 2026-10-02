"""
Temporal Behavior Detector for UBA Agent.
"""

from typing import Any, Dict, Optional
from hactm.uba.models import UbaDetectionResult, UbaEvent
from hactm.core.constants import risk_score_to_severity


class TemporalDetector:
    """Detects off-hours login or unusual time-of-day activity."""

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "uba-temporal-detector"
        self.version = version

    def detect(self, event: UbaEvent, features: Dict[str, Any]) -> Optional[UbaDetectionResult]:
        if features.get("insufficient_baseline"):
            return None

        if not features.get("is_off_hours"):
            return None

        risk_score = 0.35  # Moderate risk indicator, NOT proof of maliciousness
        confidence = 0.75
        uncertainty = round(1.0 - confidence, 4)

        return UbaDetectionResult(
            detection_id=f"det_uba_time_{event.event_id}",
            event_id=event.event_id,
            user_id=event.user_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="UNUSUAL_ACTIVITY_TIME",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation=f"Unusual activity time for user '{event.user_id}' at hour {features.get('hour_of_day')}:00 UTC",
            features_used={
                "hour_of_day": features.get("hour_of_day"),
                "is_off_hours": True,
            },
            detector_version=self.version,
            reason_codes=["UBA_OFF_HOURS_ACTIVITY"],
        )
