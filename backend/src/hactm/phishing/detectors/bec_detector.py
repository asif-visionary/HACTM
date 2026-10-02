"""
Business Email Compromise (BEC) Detector for Phishing Intelligence Agent.
"""

from typing import Any, Dict, List, Optional
from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.core.constants import risk_score_to_severity


class BecDetector:
    """
    Detects Business Email Compromise (BEC) indicators such as executive impersonation,
    reply-to mismatch combined with urgent financial/payment requests.
    """

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "phishing-bec-detector"
        self.version = version

    def detect(self, event: PhishingEmailEvent, features: Dict[str, Any]) -> Optional[PhishingDetectionResult]:
        reason_codes = []
        explanation_parts = []
        score = 0.0

        bec_cnt = features.get("bec_count", 0)
        fin_cnt = features.get("financial_count", 0)
        reply_to_mismatch = features.get("reply_to_mismatch", False)

        if bec_cnt > 0 and fin_cnt > 0:
            score += 0.50
            reason_codes.append("BEC_EXECUTIVE_FINANCIAL_REQUEST")
            explanation_parts.append("Executive role wording combined with urgent financial/wire transfer request")

        if reply_to_mismatch and fin_cnt > 0:
            score += 0.40
            reason_codes.append("BEC_REPLY_TO_MISMATCH_FINANCIAL")
            explanation_parts.append("Reply-To mismatch on financial transaction request")

        if not reason_codes or score < 0.40:
            return None

        risk_score = min(1.0, score)
        confidence = 0.86
        uncertainty = round(1.0 - confidence, 4)

        return PhishingDetectionResult(
            detection_id=f"det_bec_{event.message_id}",
            event_id=event.message_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="BEC_INDICATORS",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation="BEC indicators detected: " + "; ".join(explanation_parts),
            features_used={
                "bec_count": bec_cnt,
                "financial_count": fin_cnt,
                "reply_to_mismatch": reply_to_mismatch,
            },
            detector_version=self.version,
            reason_codes=reason_codes,
            is_bec=True,
        )
