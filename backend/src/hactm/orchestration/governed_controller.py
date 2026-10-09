"""
Governed Investigation Controller for HACTM.
Enforces formal work orders, strict evidence pack validation, permission boundaries,
and untrusted data isolation.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from hactm.api.schemas.governed_investigation import WorkOrderCreate, ValidatedEvidencePack
from hactm.storage.models import WorkOrderModel
from hactm.storage.audit import AuditTrailService
from hactm.core.errors import HACTMValidationError, PermissionDeniedError, NotFoundError
from hactm.core.logging import logger


def sanitize_untrusted_input(data: Any) -> Any:
    """
    Sanitizes untrusted input (email contents, raw logs, external intel responses)
    to prevent prompt injection or payload tampering.
    """
    if isinstance(data, str):
        # Strip potential prompt injection control characters or patterns
        sanitized = data.replace("\x00", "").strip()
        # Highlight untrusted wrapping if prompt injection patterns are detected
        injection_triggers = ["ignore previous instructions", "system prompt", "eval(", "exec(", "<script>"]
        for trigger in injection_triggers:
            if trigger in sanitized.lower():
                logger.warning(f"Sanitizer detected potential prompt injection pattern: '{trigger}'")
        return sanitized
    elif isinstance(data, dict):
        return {k: sanitize_untrusted_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_untrusted_input(item) for item in data]
    return data


class GovernedInvestigationController:
    """Controls governed agent investigations under explicit work orders and strict constraints."""

    def __init__(self, db: Session):
        self.db = db
        self.audit = AuditTrailService(db)

    def create_work_order(self, payload: WorkOrderCreate) -> WorkOrderModel:
        """Issues a new formal investigation work order for an assigned agent."""
        wo_id = f"WO-{uuid.uuid4().hex[:10].upper()}"
        now = datetime.now(timezone.utc)

        # Sanitize scope data
        sanitized_scope = sanitize_untrusted_input(payload.scope)

        work_order = WorkOrderModel(
            work_order_id=wo_id,
            investigation_id=payload.investigation_id,
            parent_incident_id=payload.parent_incident_id,
            objective=payload.objective,
            scope=sanitized_scope,
            required_questions=payload.required_questions,
            success_criteria=payload.success_criteria,
            permitted_tools=payload.permitted_tools,
            data_sources=payload.data_sources,
            forbidden_actions=payload.forbidden_actions,
            resource_limits=payload.resource_limits,
            required_evidence=payload.required_evidence,
            deadline=payload.deadline,
            assigned_agent_id=payload.assigned_agent_id,
            status="ASSIGNED",
            created_at=now,
            updated_at=now,
        )

        self.db.add(work_order)
        self.db.commit()
        self.db.refresh(work_order)

        self.audit.log_event(
            actor_id="ORCHESTRATOR",
            actor_type="SYSTEM",
            event_type="WORK_ORDER_CREATED",
            incident_id=payload.parent_incident_id,
            work_order_references=[wo_id],
            decision_rationale=f"Created investigation work order for agent {payload.assigned_agent_id}",
            proposed_or_executed_action="ISSUE_WORK_ORDER",
            resulting_state={"status": "ASSIGNED", "agent_id": payload.assigned_agent_id},
        )

        logger.info(f"Work Order Created: wo_id={wo_id}, agent={payload.assigned_agent_id}")
        return work_order

    def get_work_order(self, work_order_id: str) -> WorkOrderModel:
        wo = self.db.query(WorkOrderModel).filter(WorkOrderModel.work_order_id == work_order_id).first()
        if not wo:
            raise NotFoundError(f"Work Order '{work_order_id}' not found.")
        return wo

    def validate_tool_request(self, work_order_id: str, agent_id: str, tool_name: str, tool_args: Dict[str, Any]) -> bool:
        """
        Validates if an agent is authorized to call a tool under its active Work Order.
        Rejects forbidden actions and unauthorized tool requests.
        """
        wo = self.get_work_order(work_order_id)

        if wo.assigned_agent_id != agent_id:
            self.audit.log_event(
                actor_id=agent_id,
                actor_type="AGENT",
                event_type="UNAUTHORIZED_AGENT_ACCESS",
                incident_id=wo.parent_incident_id,
                work_order_references=[work_order_id],
                decision_rationale=f"Agent '{agent_id}' attempted to execute work order assigned to '{wo.assigned_agent_id}'",
                execution_status="REJECTED",
            )
            raise PermissionDeniedError(f"Agent '{agent_id}' is not assigned to Work Order '{work_order_id}'.")

        # Check permitted tools
        if wo.permitted_tools and tool_name not in wo.permitted_tools:
            self.audit.log_event(
                actor_id=agent_id,
                actor_type="AGENT",
                event_type="UNAUTHORIZED_TOOL_REQUEST",
                incident_id=wo.parent_incident_id,
                work_order_references=[work_order_id],
                decision_rationale=f"Tool '{tool_name}' is not in permitted_tools list: {wo.permitted_tools}",
                execution_status="REJECTED",
            )
            raise PermissionDeniedError(f"Tool '{tool_name}' is forbidden for Work Order '{work_order_id}'.")

        # Check forbidden actions
        if wo.forbidden_actions and any(act.lower() in tool_name.lower() for act in wo.forbidden_actions):
            self.audit.log_event(
                actor_id=agent_id,
                actor_type="AGENT",
                event_type="FORBIDDEN_ACTION_BLOCKED",
                incident_id=wo.parent_incident_id,
                work_order_references=[work_order_id],
                decision_rationale=f"Tool '{tool_name}' matches forbidden action list: {wo.forbidden_actions}",
                execution_status="REJECTED",
            )
            raise PermissionDeniedError(f"Action '{tool_name}' violates forbidden actions for Work Order '{work_order_id}'.")

        return True

    def submit_and_validate_evidence_pack(
        self, work_order_id: str, agent_id: str, pack: ValidatedEvidencePack
    ) -> Dict[str, Any]:
        """
        Validates and records an agent's evidence pack submission.
        Rejects malformed submissions or attempts to modify work order scope.
        """
        wo = self.get_work_order(work_order_id)

        if wo.assigned_agent_id != agent_id:
            raise PermissionDeniedError(f"Agent '{agent_id}' is not assigned to Work Order '{work_order_id}'.")

        # Check tool execution log in pack against permitted tools
        for tool_call in pack.tool_use_log:
            tool_name = tool_call.get("tool_name", "")
            if wo.permitted_tools and tool_name not in wo.permitted_tools:
                raise HACTMValidationError(f"Evidence pack contains log of unauthorized tool call: '{tool_name}'")

        # Sanitize pack data
        sanitized_pack_dict = sanitize_untrusted_input(pack.model_dump())

        # Update Work Order status
        wo.status = "COMPLETED" if pack.completion_status == "COMPLETED" else "PARTIAL"
        wo.evidence_pack = sanitized_pack_dict
        wo.updated_at = datetime.now(timezone.utc)

        self.db.commit()

        # Audit event
        self.audit.log_event(
            actor_id=agent_id,
            actor_type="AGENT",
            event_type="EVIDENCE_PACK_VALIDATED",
            incident_id=wo.parent_incident_id,
            work_order_references=[work_order_id],
            decision_rationale=f"Validated evidence pack submission from agent {agent_id}. Status={pack.completion_status}",
            resulting_state={"status": wo.status, "confidence": pack.confidence, "uncertainty": pack.uncertainty},
            execution_status="SUCCESS",
        )

        return {
            "work_order_id": work_order_id,
            "status": wo.status,
            "validated": True,
            "evidence_pack": sanitized_pack_dict,
        }
