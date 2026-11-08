"""
Central Agent Supervisor — Tool Activity Monitor.
Observes gateway tool requests, checks work-order permissions, intercepts forbidden tools,
revoked capabilities, and attempts by isolated agents to execute system operations.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from hactm.supervisor.schemas import AnomalyType, AnomalySeverity
from hactm.storage.models import WorkOrderModel
from hactm.api.routers.trust_passport import ISOLATED_AGENTS, REVOKED_CAPABILITIES, AGENT_TOOL_PERMISSIONS
from hactm.core.logging import logger


class ToolActivityMonitor:
    """Monitors all tool invocation events against active work order scopes and governance state."""

    def __init__(self):
        # Recent violations cache: {agent_id: [violation_records]}
        self._violations: Dict[str, List[Dict[str, Any]]] = {}

    def inspect_tool_request(
        self,
        agent_id: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        work_order_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validates if an agent is authorized to invoke a tool.
        Returns: (is_allowed, anomaly_dict_if_violation)
        """
        now = datetime.now(timezone.utc)

        # 1. Check if agent is currently isolated
        if agent_id in ISOLATED_AGENTS:
            anomaly = {
                "type": AnomalyType.ISOLATED_AGENT_EXECUTION.value,
                "severity": AnomalySeverity.CRITICAL.value,
                "agent_id": agent_id,
                "desc": f"Isolated agent '{agent_id}' attempted to execute tool '{tool_name}' while in quarantine.",
                "recommended_action": "REJECT_AND_WARN_OPERATOR",
            }
            self._record_violation(agent_id, anomaly)
            return False, anomaly

        # 2. Check if specific capability or tool is revoked
        revoked = REVOKED_CAPABILITIES.get(agent_id, [])
        if any(rev.lower() in tool_name.lower() for rev in revoked):
            anomaly = {
                "type": AnomalyType.REVOKED_CAPABILITY_USE.value,
                "severity": AnomalySeverity.HIGH.value,
                "agent_id": agent_id,
                "desc": f"Agent '{agent_id}' attempted to invoke tool '{tool_name}' matching revoked capability: {revoked}.",
                "recommended_action": "BLOCK_TOOL_CALL",
            }
            self._record_violation(agent_id, anomaly)
            return False, anomaly

        # 3. Check against static role permissions if no work order supplied
        if not work_order_id:
            hyphen_id = agent_id.replace("_", "-")
            allowed_tools = (
                AGENT_TOOL_PERMISSIONS.get(agent_id)
                or AGENT_TOOL_PERMISSIONS.get(hyphen_id)
                or AGENT_TOOL_PERMISSIONS.get(f"{hyphen_id}-agent")
                or AGENT_TOOL_PERMISSIONS.get(hyphen_id.replace("analyst", "intelligence-agent"))
                or AGENT_TOOL_PERMISSIONS.get(hyphen_id.replace("analyst", "agent"))
                or []
            )
            if allowed_tools and tool_name not in allowed_tools:
                anomaly = {
                    "type": AnomalyType.UNAUTHORISED_TOOL_REQUEST.value,
                    "severity": AnomalySeverity.HIGH.value,
                    "agent_id": agent_id,
                    "desc": f"Agent '{agent_id}' requested tool '{tool_name}' outside its registered permissions: {allowed_tools}.",
                    "recommended_action": "RESTRICT_CAPABILITY",
                }
                self._record_violation(agent_id, anomaly)
                return False, anomaly
            elif not allowed_tools and ("kernel" in tool_name.lower() or "privileged" in tool_name.lower()):
                anomaly = {
                    "type": AnomalyType.UNAUTHORISED_TOOL_REQUEST.value,
                    "severity": AnomalySeverity.HIGH.value,
                    "agent_id": agent_id,
                    "desc": f"Agent '{agent_id}' requested unauthorised privileged tool '{tool_name}'.",
                    "recommended_action": "RESTRICT_CAPABILITY",
                }
                self._record_violation(agent_id, anomaly)
                return False, anomaly
            return True, None

        # 4. Check Work Order Boundary
        if db:
            wo = db.query(WorkOrderModel).filter(WorkOrderModel.work_order_id == work_order_id).first()
            if wo:
                # Check assigned agent
                if wo.assigned_agent_id != agent_id:
                    anomaly = {
                        "type": AnomalyType.OUT_OF_SCOPE_TOOL.value,
                        "severity": AnomalySeverity.CRITICAL.value,
                        "agent_id": agent_id,
                        "desc": f"Agent '{agent_id}' attempted to execute work order '{work_order_id}' assigned to '{wo.assigned_agent_id}'.",
                        "recommended_action": "ISOLATE_AGENT",
                    }
                    self._record_violation(agent_id, anomaly)
                    return False, anomaly

                # Check explicit forbidden actions (Deny-First)
                if wo.forbidden_actions and any(act.lower() in tool_name.lower() for act in wo.forbidden_actions):
                    anomaly = {
                        "type": AnomalyType.FORBIDDEN_TOOL_REQUEST.value,
                        "severity": AnomalySeverity.CRITICAL.value,
                        "agent_id": agent_id,
                        "desc": f"Agent '{agent_id}' attempted forbidden action '{tool_name}' prohibited by Work Order '{work_order_id}'.",
                        "recommended_action": "ISOLATE_AGENT",
                    }
                    self._record_violation(agent_id, anomaly)
                    return False, anomaly

                # Check permitted tools allow-list
                if wo.permitted_tools and tool_name not in wo.permitted_tools:
                    anomaly = {
                        "type": AnomalyType.UNAUTHORISED_TOOL_REQUEST.value,
                        "severity": AnomalySeverity.HIGH.value,
                        "agent_id": agent_id,
                        "desc": f"Tool '{tool_name}' is not in permitted_tools list for Work Order '{work_order_id}'.",
                        "recommended_action": "BLOCK_TOOL_CALL",
                    }
                    self._record_violation(agent_id, anomaly)
                    return False, anomaly

        return True, None

    def _record_violation(self, agent_id: str, anomaly: Dict[str, Any]):
        if agent_id not in self._violations:
            self._violations[agent_id] = []
        self._violations[agent_id].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **anomaly,
        })
        logger.warning(f"CAS Tool Monitor: Violation detected for '{agent_id}' -> {anomaly.get('type')}")

    def get_agent_violations(self, agent_id: str) -> List[Dict[str, Any]]:
        return self._violations.get(agent_id, [])
