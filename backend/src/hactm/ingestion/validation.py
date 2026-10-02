"""
Record and Schema Validation for Ingestion Pipeline.
Enforces strict semantic constraints on risk scores, confidence, uncertainty,
timestamps, and required identifiers.
"""

from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from pydantic import ValidationError

from hactm.core.constants import (
    MAX_CONFIDENCE_SCORE,
    MAX_RISK_SCORE,
    MAX_UNCERTAINTY_SCORE,
    MIN_CONFIDENCE_SCORE,
    MIN_RISK_SCORE,
    MIN_UNCERTAINTY_SCORE,
)
from hactm.core.errors import HACTMValidationError
from hactm.core.models import SecurityEvidence
from hactm.ingestion.entity_resolution import resolve_entity
from hactm.ingestion.normalization import normalize_record, normalize_timestamp


def validate_and_build_evidence(raw_record: Dict[str, Any], default_agent_id: str = "HACTM_INGESTION") -> SecurityEvidence:
    """
    Validates a raw dictionary record and constructs a canonical SecurityEvidence object.
    Raises HACTMValidationError if constraints are violated.
    """
    if not isinstance(raw_record, dict):
        raise HACTMValidationError("Record must be a key-value dictionary", details={"received_type": type(raw_record).__name__})

    # Step 1: Normalization
    try:
        norm = normalize_record(raw_record)
    except Exception as e:
        raise HACTMValidationError(f"Normalization failed: {str(e)}", details={"error": str(e)})

    # Step 2: Validate Required Identifiers
    event_id = norm.get("event_id")
    if not event_id or not str(event_id).strip():
        raise HACTMValidationError("Missing or empty required field: 'event_id'")
    norm["event_id"] = str(event_id).strip()

    # Step 3: Agent ID default if missing
    agent_id = norm.get("agent_id") or default_agent_id
    norm["agent_id"] = str(agent_id).strip()

    # Step 4: Resolve Entity Deterministically if needed
    entity_id, ent_type, canon_name, ent_attrs = resolve_entity(norm)
    norm["entity_id"] = entity_id

    # Step 5: Event Type
    event_type = norm.get("event_type") or "NETWORK"
    norm["event_type"] = str(event_type).strip().upper()

    # Step 6: Timestamp Validation
    raw_ts = norm.get("timestamp")
    if raw_ts is None:
        raise HACTMValidationError("Missing required field: 'timestamp'")
    if not isinstance(raw_ts, datetime):
        try:
            norm["timestamp"] = normalize_timestamp(raw_ts)
        except Exception as e:
            raise HACTMValidationError(f"Invalid timestamp value: {raw_ts} ({e})")

    # Step 7: Risk Score Validation (0.0 to 1.0)
    raw_risk = norm.get("risk_score")
    if raw_risk is None:
        raise HACTMValidationError("Missing required field: 'risk_score'")
    try:
        risk_score = float(raw_risk)
    except (ValueError, TypeError):
        raise HACTMValidationError(f"Invalid risk_score '{raw_risk}': must be a floating-point number")

    if risk_score < MIN_RISK_SCORE or risk_score > MAX_RISK_SCORE:
        raise HACTMValidationError(
            f"Constraint violation: risk_score must be between {MIN_RISK_SCORE} and {MAX_RISK_SCORE}, got {risk_score}"
        )
    norm["risk_score"] = risk_score

    # Step 8: Confidence Validation (0.0 to 1.0)
    raw_conf = norm.get("confidence")
    if raw_conf is None:
        # Default confidence if not provided
        confidence = 1.0
    else:
        try:
            confidence = float(raw_conf)
        except (ValueError, TypeError):
            raise HACTMValidationError(f"Invalid confidence '{raw_conf}': must be a floating-point number")
        if confidence < MIN_CONFIDENCE_SCORE or confidence > MAX_CONFIDENCE_SCORE:
            raise HACTMValidationError(
                f"Constraint violation: confidence must be between {MIN_CONFIDENCE_SCORE} and {MAX_CONFIDENCE_SCORE}, got {confidence}"
            )
    norm["confidence"] = confidence

    # Step 9: Uncertainty Validation (0.0 to 1.0)
    raw_unc = norm.get("uncertainty")
    if raw_unc is None:
        # Default uncertainty derived as 1.0 - confidence if not specified
        uncertainty = round(max(0.0, min(1.0, 1.0 - confidence)), 4)
    else:
        try:
            uncertainty = float(raw_unc)
        except (ValueError, TypeError):
            raise HACTMValidationError(f"Invalid uncertainty '{raw_unc}': must be a floating-point number")
        if uncertainty < MIN_UNCERTAINTY_SCORE or uncertainty > MAX_UNCERTAINTY_SCORE:
            raise HACTMValidationError(
                f"Constraint violation: uncertainty must be between {MIN_UNCERTAINTY_SCORE} and {MAX_UNCERTAINTY_SCORE}, got {uncertainty}"
            )
    norm["uncertainty"] = uncertainty

    # Step 10: Evidence Payload Validation
    evidence_payload = norm.get("evidence")
    if evidence_payload is None:
        # Construct evidence payload from remaining non-core fields
        core_keys = {
            "event_id", "agent_id", "entity_id", "event_type", "timestamp",
            "risk_score", "confidence", "uncertainty", "source", "source_type",
            "dataset", "dataset_name", "dataset_version", "severity",
            "raw_event_id", "parent_event_id", "session_id", "correlation_id",
            "security_tags", "security_group", "security_zone"
        }
        evidence_payload = {k: v for k, v in norm.items() if k not in core_keys and v is not None}
        norm["evidence"] = evidence_payload
    elif isinstance(evidence_payload, str):
        try:
            norm["evidence"] = json.loads(evidence_payload)
        except Exception:
            norm["evidence"] = {"raw": evidence_payload}
    elif not isinstance(evidence_payload, dict):
        norm["evidence"] = {"data": evidence_payload}

    # Step 11: Security tags parsing
    raw_tags = norm.get("security_tags")
    if isinstance(raw_tags, str):
        norm["security_tags"] = [t.strip() for t in raw_tags.split(",") if t.strip()]

    # Construct Pydantic model
    try:
        return SecurityEvidence(**norm)
    except ValidationError as e:
        raise HACTMValidationError(f"Schema validation error: {e}", details={"errors": e.errors()})
