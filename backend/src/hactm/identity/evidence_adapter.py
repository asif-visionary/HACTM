"""
Identity Evidence Adapter.
Converts IdentityDetectionResult to canonical SecurityEvidence.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from hactm.core.models import SecurityEvidence
from hactm.identity.models import IdentityDetectionResult


def identity_detection_to_security_evidence(
    detection: IdentityDetectionResult,
    dataset_name: str = "identity_stream",
    source_record_id: str = None
) -> SecurityEvidence:
    entity_id = f"user_identity:{detection.user_id}"

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
    }

    return SecurityEvidence(
        event_id=detection.event_id,
        agent_id="identity-authentication-agent",
        entity_id=entity_id,
        event_type="AUTHENTICATION",
        timestamp=detection.timestamp if isinstance(detection.timestamp, datetime) else datetime.now(timezone.utc),
        risk_score=detection.risk_score,
        confidence=detection.confidence,
        uncertainty=detection.uncertainty,
        evidence=evidence_dict,
        source=dataset_name,
        source_type="AUTHENTICATION_EVENT",
        dataset=dataset_name,
        event_category=detection.category,
        severity=detection.severity,
        dataset_name=dataset_name,
        source_record_id=source_record_id or detection.event_id,
    )
