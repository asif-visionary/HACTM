"""
Attachment Metadata Detector for Phishing Intelligence Agent.
"""

from typing import Any, Dict, List, Optional
from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.core.constants import risk_score_to_severity


class AttachmentDetector:
    """Detects double-extension attachments, dangerous executables, and archive metadata."""

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "phishing-attachment-detector"
        self.version = version

    def detect(self, event: PhishingEmailEvent, features: Dict[str, Any]) -> Optional[PhishingDetectionResult]:
        reason_codes = []
        explanation_parts = []
        score = 0.0

        if features.get("has_double_ext"):
            score += 0.85
            reason_codes.append("ATTACHMENT_DOUBLE_EXTENSION")
            explanation_parts.append("Contains suspicious double-extension attachment (e.g. invoice.pdf.exe)")

        if features.get("has_executable"):
            score += 0.70
            reason_codes.append("ATTACHMENT_EXECUTABLE_FILE")
            explanation_parts.append("Contains executable or script attachment extension")

        if features.get("has_archive"):
            score += 0.25
            reason_codes.append("ATTACHMENT_ARCHIVE_CONTAINER")
            explanation_parts.append("Contains compressed archive attachment")

        if not reason_codes:
            return None

        risk_score = min(1.0, score)
        confidence = 0.90
        uncertainty = round(1.0 - confidence, 4)

        return PhishingDetectionResult(
            detection_id=f"det_att_{event.message_id}",
            event_id=event.message_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="SUSPICIOUS_ATTACHMENT",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation="; ".join(explanation_parts),
            features_used={
                "num_attachments": features.get("num_attachments"),
                "has_double_ext": features.get("has_double_ext"),
                "has_executable": features.get("has_executable"),
                "has_archive": features.get("has_archive"),
            },
            detector_version=self.version,
            reason_codes=reason_codes,
        )
