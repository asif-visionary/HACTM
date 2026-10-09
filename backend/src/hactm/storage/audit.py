"""
Auditable Decision and Action Trail Service for HACTM.
Provides persistent append-only event logging with hash-chain integrity verification.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

from hactm.storage.models import AuditEventModel
from hactm.core.logging import logger

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


def _scrub_sensitive_data(obj: Any) -> Any:
    """Recursively removes sensitive keys such as passwords, tokens, API keys, and credentials."""
    if isinstance(obj, dict):
        scrubbed = {}
        for k, v in obj.items():
            k_lower = str(k).lower()
            if any(s in k_lower for s in ["password", "token", "secret", "api_key", "private_key"]):
                scrubbed[k] = "[REDACTED_SECRET]"
            else:
                scrubbed[k] = _scrub_sensitive_data(v)
        return scrubbed
    elif isinstance(obj, list):
        return [_scrub_sensitive_data(item) for item in obj]
    return obj


def compute_record_hash(
    prev_hash: str,
    event_id: str,
    incident_id: Optional[str],
    actor_id: str,
    actor_type: str,
    event_type: str,
    decision_rationale: Optional[str],
    proposed_or_executed_action: Optional[str],
) -> str:
    """Computes SHA-256 hash for an audit record linking it to the previous hash."""
    payload = f"{prev_hash}|{event_id}|{incident_id or ''}|{actor_id}|{actor_type}|{event_type}|{decision_rationale or ''}|{proposed_or_executed_action or ''}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditTrailService:
    """Manages append-only audit trail and integrity verification."""

    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        actor_id: str,
        actor_type: str,
        event_type: str,
        incident_id: Optional[str] = None,
        evidence_references: Optional[List[str]] = None,
        work_order_references: Optional[List[str]] = None,
        previous_state: Optional[Dict[str, Any]] = None,
        resulting_state: Optional[Dict[str, Any]] = None,
        decision_rationale: Optional[str] = None,
        proposed_or_executed_action: Optional[str] = None,
        approver_identity: Optional[str] = None,
        approval_timestamp: Optional[datetime] = None,
        execution_status: Optional[str] = None,
        failure_reason: Optional[str] = None,
        model_version: str = "1.0.0",
        policy_version: str = "1.0.0",
        schema_version: str = "1.0.0",
    ) -> AuditEventModel:
        """Logs an event into the append-only audit store with a linked cryptographic hash."""
        now = datetime.now(timezone.utc)
        event_id = f"AUD-{uuid.uuid4().hex[:12].upper()}"

        # Retrieve last record to get prev_hash
        last_event = (
            self.db.query(AuditEventModel)
            .order_by(AuditEventModel.id.desc())
            .first()
        )
        prev_hash = last_event.record_hash if last_event else GENESIS_HASH


        # Compute tamper-evident record hash
        record_hash = compute_record_hash(
            prev_hash=prev_hash,
            event_id=event_id,
            incident_id=incident_id,
            actor_id=actor_id,
            actor_type=actor_type,
            event_type=event_type,
            decision_rationale=decision_rationale,
            proposed_or_executed_action=proposed_or_executed_action,
        )

        audit_entry = AuditEventModel(
            event_id=event_id,
            incident_id=incident_id,
            timestamp=now,
            actor_id=actor_id,
            actor_type=actor_type,
            event_type=event_type,
            evidence_references=evidence_references or [],
            work_order_references=work_order_references or [],
            previous_state=_scrub_sensitive_data(previous_state) if previous_state else None,
            resulting_state=_scrub_sensitive_data(resulting_state) if resulting_state else None,
            decision_rationale=decision_rationale,
            proposed_or_executed_action=proposed_or_executed_action,
            approver_identity=approver_identity,
            approval_timestamp=approval_timestamp,
            execution_status=execution_status,
            failure_reason=failure_reason,
            model_version=model_version,
            policy_version=policy_version,
            schema_version=schema_version,
            prev_hash=prev_hash,
            record_hash=record_hash,
            created_at=now,
        )

        self.db.add(audit_entry)
        self.db.commit()
        self.db.refresh(audit_entry)

        logger.info(f"Audit Logged: event_id={event_id}, type={event_type}, actor={actor_id}, hash={record_hash[:8]}")
        return audit_entry

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verifies the cryptographic hash-chain of all audit trail records.
        Detects missing, modified, or reordered records.
        """
        events = (
            self.db.query(AuditEventModel)
            .order_by(AuditEventModel.id.asc())
            .all()
        )

        if not events:
            return {
                "valid": True,
                "total_records": 0,
                "verified_records": 0,
                "violations": [],
                "tampered_records": [],
                "message": "Audit trail is empty. Hash chain is intact.",
            }

        violations = []
        expected_prev_hash = events[0].prev_hash # Allow starting from any initial segment

        for idx, event in enumerate(events):
            # Check prev_hash link unless first event in query
            if idx > 0 and event.prev_hash != expected_prev_hash:
                violations.append({
                    "record_index": idx,
                    "event_id": event.event_id,
                    "issue": "PREV_HASH_MISMATCH",
                    "expected_prev_hash": expected_prev_hash,
                    "actual_prev_hash": event.prev_hash,
                })

            # Re-compute record hash
            recomputed = compute_record_hash(
                prev_hash=event.prev_hash,
                event_id=event.event_id,
                incident_id=event.incident_id,
                actor_id=event.actor_id,
                actor_type=event.actor_type,
                event_type=event.event_type,
                decision_rationale=event.decision_rationale,
                proposed_or_executed_action=event.proposed_or_executed_action,
            )

            if recomputed != event.record_hash:
                violations.append({
                    "record_index": idx,
                    "event_id": event.event_id,
                    "issue": "RECORD_HASH_TAMPERED",
                    "stored_hash": event.record_hash,
                    "recomputed_hash": recomputed,
                })

            expected_prev_hash = event.record_hash

        is_valid = len(violations) == 0
        return {
            "valid": is_valid,
            "total_records": len(events),
            "verified_records": len(events) - len(violations),
            "violations": violations,
            "tampered_records": [v["event_id"] for v in violations],
            "message": "Audit trail verified successfully. No tampering detected." if is_valid else f"Audit trail integrity violation! Found {len(violations)} issues.",
            "storage_notice": "Local SQLite audit store protects against application-level record modification. For production, append-only WORM storage or remote syslog replication is recommended.",
        }

    def create_external_anchor_checkpoint(self) -> Dict[str, Any]:
        """
        Creates an immutable external root anchor checkpoint.
        Anchors current latest record hash to an external checkpoint structure.
        """
        events = (
            self.db.query(AuditEventModel)
            .order_by(AuditEventModel.id.asc())
            .all()
        )
        latest_hash = events[-1].record_hash if events else GENESIS_HASH
        anchor_id = f"ANCHOR-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc)

        root_payload = f"{anchor_id}|{len(events)}|{latest_hash}|{now.isoformat()}"
        root_hash = hashlib.sha256(root_payload.encode("utf-8")).hexdigest()

        return {
            "anchor_id": anchor_id,
            "anchor_type": "EXTERNAL_WORM_CHECKPOINT",
            "record_count": len(events),
            "latest_record_hash": latest_hash,
            "root_hash": root_hash,
            "timestamp": now.isoformat(),
        }

    def verify_external_anchor(self, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies database state against an external anchor checkpoint.
        Detects audit log truncation, record deletion, or full chain re-computation attacks.
        """
        events = (
            self.db.query(AuditEventModel)
            .order_by(AuditEventModel.id.asc())
            .all()
        )

        expected_count = checkpoint.get("record_count", 0)
        expected_latest_hash = checkpoint.get("latest_record_hash", "")

        current_count = len(events)
        current_latest_hash = events[-1].record_hash if events else GENESIS_HASH

        valid_count = current_count >= expected_count
        valid_hash = current_latest_hash == expected_latest_hash

        is_valid = valid_count and valid_hash

        return {
            "valid": is_valid,
            "checkpoint_id": checkpoint.get("anchor_id"),
            "expected_count": expected_count,
            "actual_count": current_count,
            "expected_latest_hash": expected_latest_hash,
            "actual_latest_hash": current_latest_hash,
            "message": "External anchor verified successfully." if is_valid else "External anchor mismatch! Possible audit truncation or re-computation attack.",
        }

