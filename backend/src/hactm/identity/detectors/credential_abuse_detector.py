"""
Credential Abuse / Brute-Force Detector for Identity Security Agent.
"""

from typing import Any, Dict, Optional
from hactm.identity.models import IdentityDetectionResult, IdentityEvent
from hactm.core.constants import risk_score_to_severity


class CredentialAbuseDetector:
    """Detects brute-force, password spraying, and credential stuffing indicators."""

    def __init__(self, failure_threshold: int = 5, version: str = "1.0.0"):
        self.detector_id = "identity-credential-abuse-detector"
        self.version = version
        self.failure_threshold = failure_threshold

    def detect(self, event: IdentityEvent, features: Dict[str, Any]) -> Optional[IdentityDetectionResult]:
        failures = features.get("recent_failures_count", 0)
        if failures < self.failure_threshold:
            return None

        score = min(1.0, 0.40 + (failures * 0.10))
        confidence = 0.88
        uncertainty = round(1.0 - confidence, 4)

        return IdentityDetectionResult(
            detection_id=f"det_id_abuse_{event.authentication_event_id}",
            event_id=event.authentication_event_id,
            user_id=event.user_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="CREDENTIAL_ABUSE_INDICATORS",
            risk_score=score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(score).value,
            explanation=f"Credential abuse indicators: {failures} failed login attempts observed in 5-minute rolling window for account '{event.user_id}'",
            features_used={
                "recent_failures_count": failures,
                "consecutive_failures": features.get("consecutive_failures"),
            },
            detector_version=self.version,
            reason_codes=["IDENTITY_HIGH_LOGIN_FAILURE_VELOCITY"],
        )
