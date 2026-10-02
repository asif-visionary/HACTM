"""
Security Evidence Adapter for Network Security Agent.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Maps NetworkDetectionResult instances into canonical Foundation SecurityEvidence models.
Ensures conflicting detections are retained as separate evidence records (Section 36).
"""

from datetime import datetime, timezone
from typing import Any, Dict
from hactm.core.constants import PREPROCESSING_VERSION, SCHEMA_VERSION
from hactm.core.models import SecurityEvidence
from hactm.network.models import NetworkDetectionResult


def detection_to_security_evidence(
    detection: NetworkDetectionResult,
    dataset_name: str = "network_telemetry",
) -> SecurityEvidence:
    """
    Transforms a NetworkDetectionResult into canonical Foundation SecurityEvidence.
    Primary entity is resolved to source IP, destination IP preserved in evidence payload.
    """
    primary_entity = f"IP:{detection.src_ip}" if detection.src_ip else "IP:UNKNOWN"

    # Evidence payload structured for analysts and future Evidence Fusion fusion
    evidence_payload: Dict[str, Any] = {
        "detector_type": detection.detector_type.value,
        "detector_id": detection.detector_id,
        "detector_version": detection.detector_version,
        "category": detection.category,
        "explanation": detection.explanation,
        "reason_codes": detection.reason_codes,
        "features_used": detection.features_used,
        "processing_time_ms": detection.processing_time_ms,
        "destination_ip": detection.dst_ip,
        "dst_ip": detection.dst_ip,
        "signature_id": detection.signature_id,
        "model_version": detection.model_version,
    }

    # Format security tags
    tags = [
        "network_security_agent",
        detection.detector_type.value.lower(),
        detection.category.lower().replace(" ", "_").replace("/", "_"),
    ]

    return SecurityEvidence(
        event_id=f"{detection.event_id}_{detection.detector_type.value.lower()}",
        agent_id="network-security-agent",
        entity_id=primary_entity,
        event_type="NETWORK",
        timestamp=detection.timestamp,
        risk_score=detection.risk_score,
        confidence=detection.confidence,
        uncertainty=detection.uncertainty,
        severity=detection.severity,
        evidence=evidence_payload,
        source="network-security-agent",
        source_type="FLOW",
        dataset=dataset_name,
        dataset_name=dataset_name,
        schema_version=SCHEMA_VERSION,
        preprocessing_version=PREPROCESSING_VERSION,
        security_tags=tags,
    )


def calculate_risk_and_confidence(
    detector_type: Any,
    severity: Any,
    raw_anomaly_score: Any = None,
) -> tuple[float, float, float]:
    """
    Transparent risk scoring, detector confidence, and Network Security Agent baseline uncertainty.
    Sections 33, 34, 35:
    - Signature: High confidence (0.90), deterministic uncertainty (0.10)
    - Heuristic: Medium confidence (0.80), uncertainty (0.20)
    - Anomaly: Score-driven risk with documented baseline confidence (0.75) and uncertainty (0.25)
    """
    sev_str = severity.value if hasattr(severity, "value") else str(severity).upper()
    det_str = detector_type.value if hasattr(detector_type, "value") else str(detector_type).upper()

    sev_base = {
        "LOW": 0.25,
        "MEDIUM": 0.55,
        "HIGH": 0.85,
        "CRITICAL": 0.95,
    }.get(sev_str, 0.50)

    if det_str == "SIGNATURE":
        risk = sev_base
        confidence = 0.90
        uncertainty = 0.10
    elif det_str == "HEURISTIC":
        risk = round(sev_base * 0.90, 4)
        confidence = 0.80
        uncertainty = 0.20
    elif det_str == "ANOMALY":
        if raw_anomaly_score is not None:
            risk = round(float(raw_anomaly_score), 4)
        else:
            risk = sev_base
        confidence = 0.75
        uncertainty = 0.25
    else:
        risk = sev_base
        confidence = 0.70
        uncertainty = 0.30

    return risk, confidence, uncertainty
