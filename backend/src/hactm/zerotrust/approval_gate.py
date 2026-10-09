"""
Human Approval and Response Gate for HACTM Zero-Trust Engine.
Interposes between policy engine and enforcement layer for high-impact actions.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from hactm.api.schemas.approval import HIGH_IMPACT_ACTIONS, ApprovalRequestCreate, HumanApprovalDecision
from hactm.storage.models import ApprovalRequestModel
from hactm.storage.audit import AuditTrailService
from hactm.core.errors import HACTMValidationError, PermissionDeniedError, NotFoundError
from hactm.core.logging import logger

AUTHORIZED_APPROVER_ROLES = {"ANALYST", "ADMIN", "SECURITY_OPERATOR", "SOC_LEAD"}


class HumanApprovalGate:
    """Manages human approval workflows for high-impact response actions."""

    def __init__(self, db: Session, simulated_enforcement: bool = True):
        self.db = db
        self.simulated_enforcement = simulated_enforcement or (os.getenv("SIMULATED_ENFORCEMENT", "true").lower() == "true")
        self.audit = AuditTrailService(db)

    def is_high_impact_action(self, action_type: str, risk_score: float) -> bool:
        """Determines whether an action is high-impact requiring mandatory human approval."""
        act_upper = action_type.upper()
        if any(hi in act_upper for hi in HIGH_IMPACT_ACTIONS):
            return True
        # Any action with critical risk >= 0.85 requires human gate
        if risk_score >= 0.85:
            return True
        return False

    def propose_and_gate_action(self, payload: ApprovalRequestCreate, proposer_id: str = "POLICY_ENGINE") -> Dict[str, Any]:
        """
        Processes a proposed policy action. Low-risk reversible actions auto-approve if permitted.
        High-impact actions are held in PENDING_APPROVAL.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=payload.ttl_minutes)
        req_id = f"APPR-{uuid.uuid4().hex[:10].upper()}"

        high_impact = self.is_high_impact_action(payload.action_type, payload.risk_score)

        if high_impact:
            initial_status = "PENDING_APPROVAL"
            execution_status = "PENDING"
        else:
            # Low-risk action auto-approves under policy
            initial_status = "APPROVED"
            execution_status = "SIMULATED" if self.simulated_enforcement else "EXECUTED"

        request_model = ApprovalRequestModel(
            request_id=req_id,
            incident_id=payload.incident_id,
            entity_id=payload.entity_id,
            policy_id=payload.policy_id,
            action_type=payload.action_type.upper(),
            proposed_action=payload.proposed_action,
            risk_score=payload.risk_score,
            confidence=payload.confidence,
            uncertainty=payload.uncertainty,
            is_high_impact=1 if high_impact else 0,
            justification=payload.justification,
            expected_impact=payload.expected_impact,
            alternatives=payload.alternatives,
            supporting_evidence=payload.supporting_evidence,
            status=initial_status,
            execution_status=execution_status,
            expires_at=expires_at,
            created_at=now,
        )

        if not high_impact:
            request_model.approver_identity = "POLICY_AUTO_APPROVAL"
            request_model.approver_role = "SYSTEM_POLICY"
            request_model.approval_notes = "Auto-approved low-risk policy action"
            request_model.approval_timestamp = now
            request_model.execution_result = {
                "mode": "SIMULATED" if self.simulated_enforcement else "REAL",
                "result": "Low-risk action executed automatically",
                "timestamp": now.isoformat(),
            }
            request_model.verification_status = "VERIFIED"

        self.db.add(request_model)
        self.db.commit()
        self.db.refresh(request_model)

        # Audit event
        self.audit.log_event(
            actor_id=proposer_id,
            actor_type="SYSTEM" if proposer_id.startswith("POLICY") else "AGENT",
            event_type="POLICY_ACTION_PROPOSED",
            incident_id=payload.incident_id,
            evidence_references=[e.get("event_id") for e in payload.supporting_evidence if isinstance(e, dict) and "event_id" in e],
            decision_rationale=payload.justification,
            proposed_or_executed_action=payload.proposed_action,
            resulting_state={"status": initial_status, "is_high_impact": high_impact},
        )

        logger.info(f"Proposed Policy Action Gated: req_id={req_id}, high_impact={high_impact}, status={initial_status}")

        return {
            "request_id": req_id,
            "status": initial_status,
            "is_high_impact": high_impact,
            "execution_status": execution_status,
            "message": "Action held for human approval." if high_impact else "Low-risk action auto-approved.",
        }

    def _validate_approver(self, decision: HumanApprovalDecision):
        """Verifies that the approver is a valid authorized human analyst/admin and not an AI agent."""
        if decision.approver_identity.startswith("AGENT") or decision.approver_identity.startswith("AI_"):
            self.audit.log_event(
                actor_id=decision.approver_identity,
                actor_type="AGENT",
                event_type="APPROVAL_BYPASS_ATTEMPT_BLOCKED",
                decision_rationale="AI Agent attempted to self-approve a gated response action",
                execution_status="BLOCKED",
            )
            raise PermissionDeniedError("AI Agents are strictly forbidden from approving gated response actions.")

        if decision.approver_role.upper() not in AUTHORIZED_APPROVER_ROLES:
            raise PermissionDeniedError(f"Role '{decision.approver_role}' is not authorized to approve gated response actions.")

    def approve_action(self, decision: HumanApprovalDecision) -> ApprovalRequestModel:
        """Approves a pending response action after verifying human authorization."""
        self._validate_approver(decision)

        req = self.db.query(ApprovalRequestModel).filter(ApprovalRequestModel.request_id == decision.request_id).first()
        if not req:
            raise NotFoundError(f"Approval request '{decision.request_id}' not found.")

        now = datetime.now(timezone.utc)
        if req.expires_at and req.expires_at.replace(tzinfo=timezone.utc) < now:
            req.status = "EXPIRED"
            self.db.commit()
            raise HACTMValidationError(f"Approval request '{decision.request_id}' has expired.")

        if req.status != "PENDING_APPROVAL":
            raise HACTMValidationError(f"Approval request is in status '{req.status}', cannot approve.")

        req.status = "APPROVED"
        req.approver_identity = decision.approver_identity
        req.approver_role = decision.approver_role.upper()
        req.approval_notes = decision.notes
        req.approval_timestamp = now

        # Execute simulated or real response
        req.execution_status = "SIMULATED" if self.simulated_enforcement else "EXECUTED"
        req.execution_result = {
            "mode": "SIMULATED" if self.simulated_enforcement else "REAL",
            "action": req.proposed_action,
            "target_entity": req.entity_id,
            "executed_at": now.isoformat(),
            "status": "SUCCESS",
        }
        req.verification_status = "VERIFIED"

        self.db.commit()
        self.db.refresh(req)

        self.audit.log_event(
            actor_id=decision.approver_identity,
            actor_type="HUMAN_" + decision.approver_role.upper(),
            event_type="HUMAN_APPROVAL_GRANTED",
            incident_id=req.incident_id,
            decision_rationale=decision.notes or f"Approved by {decision.approver_identity}",
            proposed_or_executed_action=req.proposed_action,
            approver_identity=decision.approver_identity,
            approval_timestamp=now,
            execution_status=req.execution_status,
            resulting_state={"status": "APPROVED", "execution_status": req.execution_status},
        )

        logger.info(f"Human Approval Granted: req_id={req.request_id}, approver={decision.approver_identity}")
        return req

    def reject_action(self, decision: HumanApprovalDecision) -> ApprovalRequestModel:
        """Rejects a pending response action."""
        self._validate_approver(decision)

        req = self.db.query(ApprovalRequestModel).filter(ApprovalRequestModel.request_id == decision.request_id).first()
        if not req:
            raise NotFoundError(f"Approval request '{decision.request_id}' not found.")

        now = datetime.now(timezone.utc)
        req.status = "REJECTED"
        req.approver_identity = decision.approver_identity
        req.approver_role = decision.approver_role.upper()
        req.approval_notes = decision.notes
        req.approval_timestamp = now
        req.execution_status = "CANCELLED"
        req.execution_result = {"mode": "NONE", "status": "REJECTED_BY_HUMAN"}

        self.db.commit()
        self.db.refresh(req)

        self.audit.log_event(
            actor_id=decision.approver_identity,
            actor_type="HUMAN_" + decision.approver_role.upper(),
            event_type="HUMAN_APPROVAL_REJECTED",
            incident_id=req.incident_id,
            decision_rationale=decision.notes or f"Rejected by {decision.approver_identity}",
            proposed_or_executed_action=req.proposed_action,
            approver_identity=decision.approver_identity,
            approval_timestamp=now,
            execution_status="CANCELLED",
            resulting_state={"status": "REJECTED"},
        )

        logger.info(f"Human Approval Rejected: req_id={req.request_id}, approver={decision.approver_identity}")
        return req

    def request_more_evidence(self, decision: HumanApprovalDecision) -> ApprovalRequestModel:
        """Requests additional evidence for a pending action."""
        self._validate_approver(decision)

        req = self.db.query(ApprovalRequestModel).filter(ApprovalRequestModel.request_id == decision.request_id).first()
        if not req:
            raise NotFoundError(f"Approval request '{decision.request_id}' not found.")

        now = datetime.now(timezone.utc)
        req.status = "MORE_EVIDENCE_REQUESTED"
        req.approver_identity = decision.approver_identity
        req.approver_role = decision.approver_role.upper()
        req.approval_notes = decision.notes
        req.approval_timestamp = now

        self.db.commit()
        self.db.refresh(req)

        self.audit.log_event(
            actor_id=decision.approver_identity,
            actor_type="HUMAN_" + decision.approver_role.upper(),
            event_type="HUMAN_REQUESTED_MORE_EVIDENCE",
            incident_id=req.incident_id,
            decision_rationale=decision.notes or f"More evidence requested by {decision.approver_identity}",
            approver_identity=decision.approver_identity,
            approval_timestamp=now,
            resulting_state={"status": "MORE_EVIDENCE_REQUESTED"},
        )

        return req
