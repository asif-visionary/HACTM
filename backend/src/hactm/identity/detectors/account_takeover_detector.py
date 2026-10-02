"""
Account Takeover Indicator Detector for Identity Security Agent.
"""

from typing import Any, Dict, Optional
from hactm.identity.models import IdentityDetectionResult, IdentityEvent
from hactm.core.constants import risk_score_to_severity


class AccountTakeoverDetector:
    """
    Detects account takeover indicators (e.g. successful login following multiple failures on new device/IP).
    Outputs "account takeover indicators" terminology.
    """

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "identity-ato-detector"
        self.version = version

    def detect(self, event: IdentityEvent, features: Dict[str, Any]) -> Optional[IdentityDetectionResult]:
        # Triggers primarily on SUCCESS after previous failures on new device/IP
        if event.authentication_status != "SUCCESS":
            return None

        consec_fails = features.get("consecutive_failures", 0)
        is_new_device = features.get("is_new_device", False)
        is_new_ip = features.get("is_new_ip", False)
        mfa_failed = features.get("mfa_failed", False)

        reason_codes = []
        explanation_parts = []
        score = 0.0

        if consec_fails >= 3:
            score += 0.45
            reason_codes.append("ATO_SUCCESS_AFTER_MULTIPLE_FAILURES")
            explanation_parts.append(f"Successful login immediately following {consec_fails} failed attempts")

        if is_new_device or is_new_ip:
            score += 0.30
            reason_codes.append("ATO_UNUSUAL_DEVICE_IP_NOVELTY")
            explanation_parts.append("Login from previously unseen device or IP address")

        if mfa_failed:
            score += 0.35
            reason_codes.append("ATO_2FA_VERIFICATION_ANOMALY")
            explanation_parts.append("Associated 2FA failure/challenge failure")

        if not reason_codes or score < 0.45:
            return None

        risk_score = min(1.0, score)
        confidence = 0.85
        uncertainty = round(1.0 - confidence, 4)

        return IdentityDetectionResult(
            detection_id=f"det_id_ato_{event.authentication_event_id}",
            event_id=event.authentication_event_id,
            user_id=event.user_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="ACCOUNT_TAKEOVER_INDICATORS",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation="Account takeover indicators: " + "; ".join(explanation_parts),
            features_used={
                "consecutive_failures": consec_fails,
                "is_new_device": is_new_device,
                "is_new_ip": is_new_ip,
                "mfa_failed": mfa_failed,
            },
            detector_version=self.version,
            reason_codes=reason_codes,
        )
