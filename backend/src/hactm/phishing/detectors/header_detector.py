"""
Header Detector for Phishing Intelligence Agent.
"""

from typing import Any, Dict, List, Optional
from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.core.constants import SeverityLevel, risk_score_to_severity


class HeaderDetector:
    """Detects email header anomalies and sender mismatches."""

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "phishing-header-detector"
        self.version = version

    def detect(self, event: PhishingEmailEvent, features: Dict[str, Any]) -> Optional[PhishingDetectionResult]:
        reason_codes = []
        explanation_parts = []
        score = 0.0

        if features.get("reply_to_mismatch"):
            score += 0.45
            reason_codes.append("HEADER_REPLY_TO_MISMATCH")
            explanation_parts.append(f"Sender/Reply-To domain mismatch (Sender: '{features.get('sender_domain')}', Reply-To: '{event.reply_to}')")

        if features.get("return_path_mismatch"):
            score += 0.25
            reason_codes.append("HEADER_RETURN_PATH_MISMATCH")
            explanation_parts.append(f"Sender/Return-Path domain mismatch")

        if features.get("spf_fail"):
            score += 0.30
            reason_codes.append("SPF_AUTHENTICATION_FAILURE")
            explanation_parts.append("SPF authentication failed")

        if features.get("dkim_fail"):
            score += 0.25
            reason_codes.append("DKIM_AUTHENTICATION_FAILURE")
            explanation_parts.append("DKIM signature verification failed")

        if features.get("dmarc_fail"):
            score += 0.35
            reason_codes.append("DMARC_AUTHENTICATION_FAILURE")
            explanation_parts.append("DMARC policy check failed")

        if not reason_codes:
            return None

        risk_score = min(1.0, score)
        confidence = 0.85 if features.get("auth_evidence_present") else 0.70
        uncertainty = round(1.0 - confidence, 4)

        return PhishingDetectionResult(
            detection_id=f"det_hdr_{event.message_id}",
            event_id=event.message_id,
            detector_type="RULE",
            detector_id=self.detector_id,
            category="EMAIL_HEADER_ANOMALY",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation="; ".join(explanation_parts),
            features_used={
                "reply_to_mismatch": features.get("reply_to_mismatch"),
                "return_path_mismatch": features.get("return_path_mismatch"),
                "spf_fail": features.get("spf_fail"),
                "dkim_fail": features.get("dkim_fail"),
                "dmarc_fail": features.get("dmarc_fail"),
            },
            detector_version=self.version,
            reason_codes=reason_codes,
        )
