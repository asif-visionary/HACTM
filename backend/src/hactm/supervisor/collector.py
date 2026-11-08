"""
Central Agent Supervisor — Telemetry Collector.
Captures, validates, normalizes, and verifies provenance of all agent runtime events.
Ensures unknown agents are flagged rather than silently registered as trusted.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from hactm.supervisor.schemas import SupervisorTelemetryEvent, AnomalyType, AnomalySeverity
from hactm.orchestration.registry import AgentRegistry
from hactm.storage.models import AgentHeartbeatModel
from hactm.core.logging import logger


class TelemetryCollector:
    """Collects and normalizes runtime telemetry from HACTM agents and orchestrators."""

    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or AgentRegistry()
        self._event_buffer: List[SupervisorTelemetryEvent] = []
        self._max_buffer = 1000

    def collect_event(self, raw_event: Dict[str, Any]) -> Tuple[Optional[SupervisorTelemetryEvent], Optional[str]]:
        """
        Validates, normalizes, and stamps an incoming runtime event.
        Returns: (event, error_message)
        """
        try:
            event_id = raw_event.get("event_id") or f"SUP-EVT-{uuid.uuid4().hex[:8].upper()}"
            agent_id = raw_event.get("agent_id")
            event_type = raw_event.get("event_type", "generic_telemetry")

            if not agent_id:
                return None, "Missing mandatory field 'agent_id'"

            # Validate agent against authoritative registry
            is_known = self.registry.get_agent(agent_id) is not None
            # Allow known orchestrators and test agents
            if not is_known and agent_id not in ["global-orchestrator", "regional-orchestrator", "threat-intelligence-agent"]:
                # Flag unknown agent attempting telemetry injection
                logger.warning(f"CAS Collector: Detected telemetry from UNKNOWN agent '{agent_id}'")

            norm_event = SupervisorTelemetryEvent(
                event_id=event_id,
                event_type=event_type,
                tenant_id=raw_event.get("tenant_id", "enterprise_primary"),
                agent_id=agent_id,
                incident_id=raw_event.get("incident_id"),
                task_id=raw_event.get("task_id"),
                severity=raw_event.get("severity", "MEDIUM"),
                source=raw_event.get("source", "AGENT_RUNTIME"),
                payload=raw_event.get("payload", {}),
                evidence_refs=raw_event.get("evidence_refs", []),
                timestamp=raw_event.get("timestamp") or datetime.now(timezone.utc).isoformat(),
                schema_version=raw_event.get("schema_version", "1.0"),
            )

            # Circular buffer append
            self._event_buffer.append(norm_event)
            if len(self._event_buffer) > self._max_buffer:
                self._event_buffer.pop(0)

            return norm_event, None

        except Exception as e:
            logger.error(f"CAS Collector Error: {e}")
            return None, str(e)

    def record_heartbeat(self, agent_id: str, status: str = "OPERATIONAL", task: Optional[str] = None,
                         cpu_load: float = 0.0, memory_mb: float = 0.0, queue_len: int = 0,
                         interval_sec: float = 10.0, db: Optional[Session] = None) -> AgentHeartbeatModel:
        """Records an agent heartbeat to memory and database."""
        now = datetime.now(timezone.utc)
        hb = AgentHeartbeatModel(
            agent_id=agent_id,
            timestamp=now,
            heartbeat_interval_sec=interval_sec,
            current_status=status,
            current_task=task,
            cpu_load=cpu_load,
            memory_mb=memory_mb,
            queue_length=queue_len,
        )
        if db:
            db.add(hb)
            db.commit()
            db.refresh(hb)
        return hb

    def get_recent_events(self, limit: int = 100, agent_id: Optional[str] = None) -> List[SupervisorTelemetryEvent]:
        """Returns recent telemetry events from buffer."""
        if agent_id:
            filtered = [e for e in self._event_buffer if e.agent_id == agent_id]
            return filtered[-limit:]
        return self._event_buffer[-limit:]

