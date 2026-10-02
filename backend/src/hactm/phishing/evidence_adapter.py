"""
Phishing Evidence Adapter.
Converts PhishingDetectionResult to canonical SecurityEvidence.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from hactm.core.models import SecurityEvidence
from hactm.phishing.models import PhishingDetectionResult


def phishing_detection_to_security_evidence(
    detection: PhishingDetectionResult,
    dataset_name: str = "phishing_stream",
    source_record_id: str = None
) -> SecurityEvidence:
    entity_id = f"email_msg:{detection.event_id}"

    evidence_dict: Dict[str, Any] = {
        "detection_id": detection.detection_id,
        "detector_type": detection.detector_type,
        "detector_id": detection.detector_id,
        "detector_version": detection.detector_version,
        "category": detection.category,
        "reason_codes": detection.reason_codes,
        "explanation": detection.explanation,
        "features_used": detection.features_used,
        "is_spear_phishing": detection.is_spear_phishing,
        "is_bec": detection.is_bec,
        "matched_rules": detection.matched_rules,
    }

    return SecurityEvidence(
        event_id=detection.event_id,
        agent_id="phishing-intelligence-agent",
        entity_id=entity_id,
        event_type="EMAIL_PHISHING",
        timestamp=detection.timestamp if isinstance(detection.timestamp, datetime) else datetime.now(timezone.utc),
        risk_score=detection.risk_score,
        confidence=detection.confidence,
        uncertainty=detection.uncertainty,
        evidence=evidence_dict,
        source=dataset_name,
        source_type="EMAIL",
        dataset=dataset_name,
        event_category=detection.category,
        severity=detection.severity,
        dataset_name=dataset_name,
        source_record_id=source_record_id or detection.event_id,
    )
