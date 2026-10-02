"""
Resource & Privilege Abuse Detector for UBA Agent.
"""

from typing import Any, Dict, Optional
from hactm.uba.models import UbaDetectionResult, UbaEvent
from hactm.core.constants import risk_score_to_severity


class ResourceDetector:
    """Detects rare resource access, unusual application usage, and privilege escalation indicators."""

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "uba-resource-detector"
        self.version = version

    def detect(self, event: UbaEvent, features: Dict[str, Any]) -> Optional[UbaDetectionResult]:
        if features.get("insufficient_baseline"):
            return None

        reason_codes = []
        explanation_parts = []
        score = 0.0

        if features.get("is_rare_resource"):
            score += 0.40
            reason_codes.append("UBA_RARE_RESOURCE_ACCESS")
            explanation_parts.append(f"Access to resource outside user baseline: '{event.resource}'")

        if features.get("is_new_app"):
            score += 0.30
            reason_codes.append("UBA_UNUSUAL_APPLICATION_USE")
            explanation_parts.append(f"Use of application outside user baseline: '{event.application}'")

        if features.get("is_privilege_escalation"):
            score += 0.55
            reason_codes.append("UBA_PRIVILEGE_ELEVATION_INDICATOR")
            explanation_parts.append(f"Privilege elevation action observed: '{event.action}' as '{event.privilege_level}'")

        if not reason_codes:
            return None

        risk_score = min(1.0, score)
        confidence = 0.80
        uncertainty = round(1.0 - confidence, 4)

        return UbaDetectionResult(
            detection_id=f"det_uba_res_{event.event_id}",
            event_id=event.event_id,
            user_id=event.user_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="RESOURCE_ACCESS_ANOMALY",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation="; ".join(explanation_parts),
            features_used={
                "is_rare_resource": features.get("is_rare_resource"),
                "is_new_app": features.get("is_new_app"),
                "is_privilege_escalation": features.get("is_privilege_escalation"),
            },
            detector_version=self.version,
            reason_codes=reason_codes,
        )
