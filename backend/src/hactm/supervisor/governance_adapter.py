"""
Central Agent Supervisor — Governance and Enforcement Adapter.
Implements the 6-tier risk-based response framework (Level 0 Normal to Level 5 Human Security Review),
coordinates agent capability restrictions, backend isolation, safe task reassignment, and controlled recovery.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from hactm.supervisor.schemas import GovernanceLevel, SupervisorDecisionItem
from hactm.storage.models import SupervisorDecisionModel, AgentIsolationRecordModel, AgentRecoveryRecordModel
from hactm.api.routers.trust_passport import ISOLATED_AGENTS, REVOKED_CAPABILITIES
from hactm.storage.audit import AuditTrailService
from hactm.services.workspace_event_broadcaster import broadcaster
from hactm.core.logging import logger


class GovernanceAdapter:
    """Orchestrates governed containment, capability restriction, isolation, and recovery."""

    def __init__(self):
        self._decisions_log: List[SupervisorDecisionItem] = []

    def evaluate_and_enforce(
        self,
        agent_id: str,
        anomalies: List[Dict[str, Any]],
        incident_id: Optional[str] = None,
        operator_identity: str = "CAS_GOVERNANCE_CORE",
        db: Optional[Session] = None,
    ) -> SupervisorDecisionItem:
        """
        Determines the appropriate governance tier (Level 0-5) and executes authoritative containment.
        """
        now = datetime.now(timezone.utc)
        decision_id = f"DEC-{uuid.uuid4().hex[:8].upper()}"

        has_critical = any(a.get("severity") == "CRITICAL" for a in anomalies)
        high_count = sum(1 for a in anomalies if a.get("severity") == "HIGH")
        anomaly_count = len(anomalies)

        # 1. Determine Governance Level
        if has_critical:
            gov_level = GovernanceLevel.LEVEL_4_ISOLATED
            decision_type = "ISOLATE"
            justification = f"Critical security violation detected on '{agent_id}'. Initiating immediate isolation."
        elif high_count >= 2:
            gov_level = GovernanceLevel.LEVEL_3_RESTRICTED
            decision_type = "RESTRICT_CAPABILITY"
            justification = f"Multiple high-severity anomalies detected on '{agent_id}'. Restricting sensitive tools."
        elif high_count == 1:
            gov_level = GovernanceLevel.LEVEL_2_WARNING
            decision_type = "WARN"
            justification = f"High-severity operational anomaly detected on '{agent_id}'. Supervisory warning issued."
        elif anomaly_count > 0:
            gov_level = GovernanceLevel.LEVEL_1_OBSERVATION
            decision_type = "OBSERVE"
            justification = f"Minor deviation detected on '{agent_id}'. Elevated telemetry observation initiated."
        else:
            gov_level = GovernanceLevel.LEVEL_0_NORMAL
            decision_type = "NORMAL"
            justification = f"Agent '{agent_id}' is operating within normal parameters."

        action_payload: Dict[str, Any] = {}

        # 2. Execute Enforcement
        if decision_type == "ISOLATE":
            action_payload = self.isolate_agent(
                agent_id=agent_id,
                reason=justification,
                incident_id=incident_id,
                operator_identity=operator_identity,
                db=db,
            )
        elif decision_type == "RESTRICT_CAPABILITY":
            # Restrict network or exfiltration capabilities
            revoked_tools = ["arbitrary_shell", "network_packet_injector", "file_exfiltrator"]
            action_payload = self.restrict_capabilities(
                agent_id=agent_id,
                capabilities=revoked_tools,
                reason=justification,
                operator_identity=operator_identity,
                db=db,
            )

        decision_item = SupervisorDecisionItem(
            decision_id=decision_id,
            agent_id=agent_id,
            incident_id=incident_id,
            timestamp=now.isoformat(),
            governance_level=gov_level.value,
            decision_type=decision_type,
            justification=justification,
            action_payload=action_payload,
            work_orders_affected=[],
            operator_identity=operator_identity,
            status="EXECUTED",
        )

        self._decisions_log.append(decision_item)

        # 3. Log to Cryptographic Audit Chain & Database
        if db:
            try:
                db_dec = SupervisorDecisionModel(
                    decision_id=decision_id,
                    agent_id=agent_id,
                    incident_id=incident_id,
                    timestamp=now,
                    governance_level=gov_level.value,
                    decision_type=decision_type,
                    justification=justification,
                    action_payload=action_payload,
                    operator_identity=operator_identity,
                    status="EXECUTED",
                )
                db.add(db_dec)

                # SHA-256 Audit Trail
                audit = AuditTrailService(db)
                audit.log_event(
                    actor_id=operator_identity,
                    actor_type="SUPERVISOR",
                    event_type=f"CAS_DECISION_{decision_type}",
                    incident_id=incident_id,
                    decision_rationale=justification,
                    proposed_or_executed_action=f"LEVEL_{gov_level.value}_{decision_type}",
                    execution_status="EXECUTED",
                )
                db.commit()
            except Exception as e:
                logger.error(f"CAS Governance DB error: {e}")

        # 4. Broadcast SSE Event to Workspace
        broadcaster.publish_event(
            event_type="agent_warning_issued" if decision_type == "WARN" else "agent_isolated" if decision_type == "ISOLATE" else "agent_trust_updated",
            message=justification,
            agent_id=agent_id,
            incident_id=incident_id,
            data=decision_item.model_dump() if hasattr(decision_item, "model_dump") else decision_item.dict(),
        )

        return decision_item

    def isolate_agent(
        self,
        agent_id: str,
        reason: str,
        incident_id: Optional[str] = None,
        operator_identity: str = "CAS_GOVERNANCE",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Formally quarantines an agent, revoking tool access and notifying orchestrator."""
        now = datetime.now(timezone.utc)
        isolation_id = f"ISOL-{uuid.uuid4().hex[:8].upper()}"

        ISOLATED_AGENTS[agent_id] = {
            "isolated_at": now.isoformat(),
            "reason": reason,
            "incident_id": incident_id,
            "operator": operator_identity,
            "isolation_id": isolation_id,
        }

        # Broadcast isolation event
        broadcaster.publish_event(
            event_type="agent_isolated",
            message=f"Agent '{agent_id}' has been ISOLATED by Central Agent Supervisor: {reason}",
            agent_id=agent_id,
            incident_id=incident_id,
            data={"isolation_id": isolation_id, "reason": reason},
        )

        if db:
            try:
                rec = AgentIsolationRecordModel(
                    isolation_id=isolation_id,
                    agent_id=agent_id,
                    incident_id=incident_id,
                    isolated_at=now,
                    reason=reason,
                    is_active=1,
                    authorized_by=operator_identity,
                )
                db.add(rec)
                db.commit()
            except Exception as e:
                logger.error(f"Failed to record isolation in DB: {e}")

        return {"isolation_id": isolation_id, "status": "ISOLATED", "reason": reason}

    def restrict_capabilities(
        self,
        agent_id: str,
        capabilities: List[str],
        reason: str,
        operator_identity: str = "CAS_GOVERNANCE",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Restricts specific tools without fully isolating the agent."""
        if agent_id not in REVOKED_CAPABILITIES:
            REVOKED_CAPABILITIES[agent_id] = []
        for c in capabilities:
            if c not in REVOKED_CAPABILITIES[agent_id]:
                REVOKED_CAPABILITIES[agent_id].append(c)

        broadcaster.publish_event(
            event_type="agent_capability_restricted",
            message=f"Agent '{agent_id}' capabilities restricted by Supervisor: {capabilities}",
            agent_id=agent_id,
            data={"revoked": REVOKED_CAPABILITIES[agent_id], "reason": reason},
        )

        return {"status": "RESTRICTED", "revoked_capabilities": REVOKED_CAPABILITIES[agent_id]}

    def reinstate_agent(
        self,
        agent_id: str,
        operator_identity: str = "SECURITY_ADMIN",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Restores an isolated agent back to active status following authorized validation."""
        now = datetime.now(timezone.utc)
        was_isolated = agent_id in ISOLATED_AGENTS
        if was_isolated:
            del ISOLATED_AGENTS[agent_id]
        if agent_id in REVOKED_CAPABILITIES:
            del REVOKED_CAPABILITIES[agent_id]

        if db:
            try:
                # Close active isolation record
                active_rec = db.query(AgentIsolationRecordModel).filter(
                    AgentIsolationRecordModel.agent_id == agent_id,
                    AgentIsolationRecordModel.is_active == 1
                ).first()
                if active_rec:
                    active_rec.is_active = 0
                    active_rec.reinstated_at = now
                    active_rec.authorized_by = operator_identity

                audit = AuditTrailService(db)
                audit.log_event(
                    actor_id=operator_identity,
                    actor_type="HUMAN_ADMIN",
                    event_type="CAS_AGENT_REINSTATED",
                    decision_rationale=f"Agent '{agent_id}' successfully completed recovery and was reinstated.",
                    proposed_or_executed_action="REINSTATE_AGENT",
                    execution_status="EXECUTED",
                )
                db.commit()
            except Exception as e:
                logger.error(f"Error updating reinstatement in DB: {e}")

        broadcaster.publish_event(
            event_type="agent_reinstated",
            message=f"Agent '{agent_id}' has been formally reinstated by '{operator_identity}'.",
            agent_id=agent_id,
            data={"reinstated_at": now.isoformat(), "authorized_by": operator_identity},
        )

        return {"status": "REINSTATED", "agent_id": agent_id, "is_isolated": False}

    def get_recent_decisions(self, limit: int = 50) -> List[SupervisorDecisionItem]:
        return self._decisions_log[-limit:]
