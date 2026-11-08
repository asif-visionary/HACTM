"""
Central Agent Supervisor — Orchestrator Monitor.
Monitors Regional Orchestrators and the Global Adaptive Orchestrator for task assignment anomalies,
delegation loops, failure to respect agent isolation, and unauthorized scope deviations.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from hactm.supervisor.schemas import AnomalyType, AnomalySeverity
from hactm.api.routers.trust_passport import ISOLATED_AGENTS
from hactm.core.logging import logger


class OrchestratorMonitor:
    """Watchdog for Regional and Global Orchestrator operations."""

    def __init__(self):
        self._orchestrator_events: List[Dict[str, Any]] = []

    def inspect_orchestrator_action(
        self,
        orchestrator_id: str,
        action_type: str,
        target_agent_id: Optional[str] = None,
        work_order_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Inspects an orchestration dispatch or replanning action.
        Returns: (is_compliant, anomaly_if_detected)
        """
        now = datetime.now(timezone.utc)
        self._orchestrator_events.append({
            "timestamp": now.isoformat(),
            "orchestrator_id": orchestrator_id,
            "action_type": action_type,
            "target_agent_id": target_agent_id,
        })

        # 1. Check if orchestrator attempts to dispatch work to an ISOLATED agent
        if target_agent_id and target_agent_id in ISOLATED_AGENTS:
            anomaly = {
                "type": AnomalyType.ORCHESTRATOR_ANOMALY.value,
                "severity": AnomalySeverity.CRITICAL.value,
                "agent_id": orchestrator_id,
                "desc": (
                    f"Orchestrator '{orchestrator_id}' attempted to assign task to quarantined agent "
                    f"'{target_agent_id}' ({ISOLATED_AGENTS[target_agent_id].get('reason')})."
                ),
                "recommended_action": "REJECT_ASSIGNMENT_AND_REPLAN",
            }
            logger.error(f"CAS Orchestrator Monitor: {anomaly['desc']}")
            return False, anomaly

        # 2. Check for excessive replanning loops (> 10 replan actions in single investigation)
        recent_replan = [e for e in self._orchestrator_events[-20:] if e.get("action_type") == "INVESTIGATION_REPLAN"]
        if len(recent_replan) > 10:
            anomaly = {
                "type": AnomalyType.EXCESSIVE_TASK_DELEGATION.value,
                "severity": AnomalySeverity.HIGH.value,
                "agent_id": orchestrator_id,
                "desc": f"Orchestrator '{orchestrator_id}' generated {len(recent_replan)} replanning cycles, indicating orchestration thrashing.",
                "recommended_action": "REQUEST_HUMAN_SECURITY_REVIEW",
            }
            return False, anomaly

        return True, None

