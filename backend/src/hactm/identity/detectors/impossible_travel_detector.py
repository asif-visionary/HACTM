"""
Impossible Travel Heuristic Detector for Identity Security Agent.
"""

from typing import Any, Dict, Optional
from hactm.identity.models import IdentityDetectionResult, IdentityEvent
from hactm.core.constants import risk_score_to_severity


class ImpossibleTravelDetector:
    """
    Detects physically implausible travel velocity between consecutive logins.
    Only executes if reliable geographical coordinates exist in event telemetry.
    """

    def __init__(self, max_speed_kmh: float = 900.0, version: str = "1.0.0"):
        self.detector_id = "identity-impossible-travel-detector"
        self.version = version
        self.max_speed_kmh = max_speed_kmh

    def detect(self, event: IdentityEvent, features: Dict[str, Any]) -> Optional[IdentityDetectionResult]:
        if not features.get("impossible_travel_detected"):
            return None

        speed = features.get("calculated_speed_kmh", 0.0)
        prev_desc = features.get("prev_location_desc", "")

        risk_score = 0.85
        confidence = 0.86
        uncertainty = round(1.0 - confidence, 4)

        return IdentityDetectionResult(
            detection_id=f"det_id_travel_{event.authentication_event_id}",
            event_id=event.authentication_event_id,
            user_id=event.user_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="POSSIBLE_IMPOSSIBLE_TRAVEL",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation=f"Possible impossible travel detected for account '{event.user_id}': Required travel velocity ({speed:.0f} km/h) exceeds flight limit vs previous login {prev_desc}",
            features_used={
                "calculated_speed_kmh": speed,
                "prev_location_desc": prev_desc,
            },
            detector_version=self.version,
            reason_codes=["IDENTITY_IMPOSSIBLE_TRAVEL_VELOCITY"],
        )
