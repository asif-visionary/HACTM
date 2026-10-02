"""
2FA / MFA Anomaly Detector for Identity Security Agent.
"""

from typing import Any, Dict, Optional
from hactm.identity.models import IdentityDetectionResult, IdentityEvent
from hactm.core.constants import risk_score_to_severity


class MfaAnomalyDetector:
    """Detects 2FA/MFA failures, timeouts, and bypass indicators."""

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "identity-mfa-detector"
        self.version = version

    def detect(self, event: IdentityEvent, features: Dict[str, Any]) -> Optional[IdentityDetectionResult]:
        tfa_result = event.two_factor_result
        if not tfa_result or tfa_result not in {"FAILED", "TIMEOUT", "BYPASS"}:
            return None

        reason_codes = []
        explanation_parts = []
        score = 0.0

        if tfa_result == "FAILED":
            score = 0.50
            reason_codes.append("MFA_VERIFICATION_FAILED")
            explanation_parts.append(f"Two-factor authentication failed ({event.two_factor_used})")
        elif tfa_result == "TIMEOUT":
            score = 0.40
            reason_codes.append("MFA_VERIFICATION_TIMEOUT")
            explanation_parts.append("Two-factor authentication challenge timed out")
        elif tfa_result == "BYPASS":
            score = 0.75
            reason_codes.append("MFA_BYPASS_INDICATOR")
            explanation_parts.append("Two-factor authentication bypass indicator present")

        confidence = 0.90
        uncertainty = round(1.0 - confidence, 4)

        return IdentityDetectionResult(
            detection_id=f"det_id_mfa_{event.authentication_event_id}",
            event_id=event.authentication_event_id,
            user_id=event.user_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="MFA_AUTHENTICATION_ANOMALY",
            risk_score=score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(score).value,
            explanation="; ".join(explanation_parts),
            features_used={
                "two_factor_used": event.two_factor_used,
                "two_factor_result": tfa_result,
            },
            detector_version=self.version,
            reason_codes=reason_codes,
        )
