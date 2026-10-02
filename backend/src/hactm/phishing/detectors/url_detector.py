"""
URL Detector for Phishing Intelligence Agent.
"""

from typing import Any, Dict, List, Optional
from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.core.constants import risk_score_to_severity


class UrlDetector:
    """Detects suspicious URL structures, IP hostnames, punycode, and domain mismatches."""

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "phishing-url-detector"
        self.version = version

    def detect(self, event: PhishingEmailEvent, features: Dict[str, Any]) -> Optional[PhishingDetectionResult]:
        reason_codes = []
        explanation_parts = []
        score = 0.0

        if features.get("has_ip_url"):
            score += 0.50
            reason_codes.append("URL_IP_HOSTNAME_PRESENT")
            explanation_parts.append("Contains raw IP address in URL hostname")

        if features.get("has_punycode_url"):
            score += 0.45
            reason_codes.append("URL_PUNYCODE_PRESENT")
            explanation_parts.append("Contains Internationalized Domain Name (Punycode xn--) in URL")

        if features.get("has_mismatch_url"):
            score += 0.40
            reason_codes.append("URL_SENDER_DOMAIN_MISMATCH")
            explanation_parts.append("URL domain mismatches sender domain")

        if features.get("max_subdomains", 0) >= 3:
            score += 0.25
            reason_codes.append("URL_EXCESSIVE_SUBDOMAINS")
            explanation_parts.append(f"Excessive subdomains in URL ({features.get('max_subdomains')} levels)")

        if features.get("max_url_len", 0) > 150:
            score += 0.15
            reason_codes.append("URL_EXCESSIVE_LENGTH")
            explanation_parts.append("Extremely long URL detected")

        if not reason_codes:
            return None

        risk_score = min(1.0, score)
        confidence = 0.88
        uncertainty = round(1.0 - confidence, 4)

        return PhishingDetectionResult(
            detection_id=f"det_url_{event.message_id}",
            event_id=event.message_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="SUSPICIOUS_URL",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation="; ".join(explanation_parts),
            features_used={
                "num_urls": features.get("num_urls"),
                "has_ip_url": features.get("has_ip_url"),
                "has_punycode_url": features.get("has_punycode_url"),
                "has_mismatch_url": features.get("has_mismatch_url"),
                "max_subdomains": features.get("max_subdomains"),
            },
            detector_version=self.version,
            reason_codes=reason_codes,
        )
