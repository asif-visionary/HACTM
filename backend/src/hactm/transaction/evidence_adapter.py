"""
Transaction Evidence Adapter.
Converts TransactionDetectionResult to canonical SecurityEvidence.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from hactm.core.models import SecurityEvidence
from hactm.transaction.models import TransactionDetectionResult


def transaction_detection_to_security_evidence(
    detection: TransactionDetectionResult,
    dataset_name: str = "transaction_stream",
    source_record_id: str = None
) -> SecurityEvidence:
    entity_id = f"financial_account:{detection.account_id}"

    evidence_dict: Dict[str, Any] = {
        "detection_id": detection.detection_id,
        "account_id": detection.account_id,
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
        agent_id="transaction-security-agent",
        entity_id=entity_id,
        event_type="TRANSACTION",
        timestamp=detection.timestamp if isinstance(detection.timestamp, datetime) else datetime.now(timezone.utc),
        risk_score=detection.risk_score,
        confidence=detection.confidence,
        uncertainty=detection.uncertainty,
        evidence=evidence_dict,
        source=dataset_name,
        source_type="TRANSACTION_EVENT",
        dataset=dataset_name,
        event_category=detection.category,
        severity=detection.severity,
        dataset_name=dataset_name,
        source_record_id=source_record_id or detection.event_id,
    )
