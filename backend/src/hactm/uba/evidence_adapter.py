"""
UBA Evidence Adapter.
Converts UbaDetectionResult to canonical SecurityEvidence.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from hactm.core.models import SecurityEvidence
from hactm.uba.models import UbaDetectionResult


def uba_detection_to_security_evidence(
    detection: UbaDetectionResult,
    dataset_name: str = "uba_stream",
    source_record_id: str = None
) -> SecurityEvidence:
    entity_id = f"user_account:{detection.user_id}"

    evidence_dict: Dict[str, Any] = {
        "detection_id": detection.detection_id,
        "user_id": detection.user_id,
        "detector_type": detection.detector_type,
        "detector_id": detection.detector_id,
        "detector_version": detection.detector_version,
        "category": detection.category,
        "reason_codes": detection.reason_codes,
        "explanation": detection.explanation,
        "features_used": detection.features_used,
        "is_insufficient_baseline": detection.is_insufficient_baseline,
    }

    return SecurityEvidence(
        event_id=detection.event_id,
        agent_id="uba-agent",
        entity_id=entity_id,
        event_type="USER_BEHAVIOR",
        timestamp=detection.timestamp if isinstance(detection.timestamp, datetime) else datetime.now(timezone.utc),
        risk_score=detection.risk_score,
        confidence=detection.confidence,
        uncertainty=detection.uncertainty,
        evidence=evidence_dict,
        source=dataset_name,
        source_type="USER_ACTIVITY",
        dataset=dataset_name,
        event_category=detection.category,
        severity=detection.severity,
        dataset_name=dataset_name,
        source_record_id=source_record_id or detection.event_id,
    )
