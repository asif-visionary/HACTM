"""
Spear Phishing Detector for Phishing Intelligence Agent.
"""

from typing import Any, Dict, List, Optional
from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.core.constants import risk_score_to_severity


class SpearPhishingDetector:
    """
    Detects targeted spear-phishing indicators (personalization, role-specific language).
    Outputs "spear-phishing indicators detected" terminology rather than premature confirmation.
    """

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "phishing-spear-detector"
        self.version = version

    def detect(self, event: PhishingEmailEvent, features: Dict[str, Any]) -> Optional[PhishingDetectionResult]:
        reason_codes = []
        explanation_parts = []
        score = 0.0

        is_personalized = features.get("is_personalized", False)
        cred_cnt = features.get("credential_count", 0)
        has_url_or_att = features.get("num_urls", 0) > 0 or features.get("num_attachments", 0) > 0

        if is_personalized:
            score += 0.35
            reason_codes.append("SPEAR_PHISHING_RECIPIENT_PERSONALIZATION")
            explanation_parts.append("Personalized recipient identification in message body")

        if is_personalized and (cred_cnt > 0 or has_url_or_att):
            score += 0.40
            reason_codes.append("SPEAR_PHISHING_TARGETED_LURE")
            explanation_parts.append("Targeted request with credential/link lure toward specific recipient")

        if not reason_codes or score < 0.40:
            return None

        risk_score = min(1.0, score)
        confidence = 0.82
        uncertainty = round(1.0 - confidence, 4)

        return PhishingDetectionResult(
            detection_id=f"det_spear_{event.message_id}",
            event_id=event.message_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="SPEAR_PHISHING_INDICATORS",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation="Spear-phishing indicators detected: " + "; ".join(explanation_parts),
            features_used={
                "is_personalized": is_personalized,
                "credential_count": cred_cnt,
                "num_urls": features.get("num_urls"),
            },
            detector_version=self.version,
            reason_codes=reason_codes,
            is_spear_phishing=True,
        )
