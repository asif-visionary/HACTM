"""
Central Agent Supervisor — Agent Health Monitor.
Continuously tracks heartbeats, execution timeouts, task failures, stuck states,
and queue saturation across all registered agents and orchestrators.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from hactm.supervisor.schemas import AgentHealthResponse, AnomalyType, AnomalySeverity
from hactm.storage.models import AgentHeartbeatModel


class AgentHealthMonitor:
    """Monitors operational vitals and runtime health for HACTM agents."""

    def __init__(self, heartbeat_timeout_multiplier: float = 3.0, stuck_task_threshold_sec: float = 30.0):
        self.timeout_mult = heartbeat_timeout_multiplier
        self.stuck_threshold_sec = stuck_task_threshold_sec
        # Runtime in-memory state tracking: {agent_id: {last_heartbeat, status, task, task_start, failures}}
        self._agent_vitals: Dict[str, Dict] = {}

    def update_heartbeat(self, agent_id: str, status: str = "OPERATIONAL", task: Optional[str] = None,
                         interval_sec: float = 10.0, cpu_load: float = 0.0, memory_mb: float = 0.0,
                         queue_len: int = 0):
        """Updates runtime vitals when a heartbeat arrives."""
        now = datetime.now(timezone.utc)
        current = self._agent_vitals.get(agent_id, {
            "consecutive_failures": 0,
            "task_start_time": None,
            "current_task": None,
        })

        # Track task transition
        task_start = current.get("task_start_time")
        if task and task != current.get("current_task"):
            task_start = now
        elif not task:
            task_start = None

        self._agent_vitals[agent_id] = {
            "last_heartbeat": now,
            "status": status,
            "current_task": task,
            "task_start_time": task_start,
            "interval_sec": interval_sec,
            "cpu_load": cpu_load,
            "memory_mb": memory_mb,
            "queue_len": queue_len,
            "consecutive_failures": current.get("consecutive_failures", 0),
        }

    def record_task_failure(self, agent_id: str):
        """Increments consecutive failure counter for an agent."""
        if agent_id in self._agent_vitals:
            self._agent_vitals[agent_id]["consecutive_failures"] = self._agent_vitals[agent_id].get("consecutive_failures", 0) + 1

    def record_task_success(self, agent_id: str):
        """Resets consecutive failure counter on task completion."""
        if agent_id in self._agent_vitals:
            self._agent_vitals[agent_id]["consecutive_failures"] = 0
            self._agent_vitals[agent_id]["current_task"] = None
            self._agent_vitals[agent_id]["task_start_time"] = None

    def evaluate_health(self, agent_id: str) -> Tuple[AgentHealthResponse, List[Dict[str, str]]]:
        """
        Evaluates health vitals for a given agent.
        Returns: (health_response, list_of_detected_health_anomalies)
        """
        now = datetime.now(timezone.utc)
        vitals = self._agent_vitals.get(agent_id)
        anomalies = []

        if not vitals:
            # Agent never reported heartbeat
            return AgentHealthResponse(
                agent_id=agent_id,
                status="OFFLINE",
                is_online=False,
                last_heartbeat=now.isoformat(),
                heartbeat_interval_sec=10.0,
                time_since_heartbeat_sec=999.0,
                active_task=None,
                consecutive_failures=0,
                is_stuck=False,
                health_score=0.0,
            ), [{"type": AnomalyType.UNEXPECTED_OFFLINE.value, "severity": AnomalySeverity.HIGH.value, "desc": f"Agent '{agent_id}' has no heartbeat record."}]

        last_hb: datetime = vitals["last_heartbeat"]
        interval = vitals.get("interval_sec", 10.0)
        elapsed_sec = (now - last_hb).total_seconds()
        is_online = elapsed_sec <= (interval * self.timeout_mult)

        # Check missing heartbeat
        if not is_online:
            anomalies.append({
                "type": AnomalyType.HEARTBEAT_MISSING.value,
                "severity": AnomalySeverity.HIGH.value if elapsed_sec > 60 else AnomalySeverity.MEDIUM.value,
                "desc": f"Missing heartbeat from '{agent_id}': {elapsed_sec:.1f}s elapsed (expected every {interval}s)."
            })

        # Check stuck in ANALYSING or task
        current_task = vitals.get("current_task")
        task_start = vitals.get("task_start_time")
        is_stuck = False
        if current_task and task_start:
            task_duration = (now - task_start).total_seconds()
            if task_duration > self.stuck_threshold_sec:
                is_stuck = True
                anomalies.append({
                    "type": AnomalyType.STUCK_ANALYSING.value,
                    "severity": AnomalySeverity.HIGH.value,
                    "desc": f"Agent '{agent_id}' stuck in task '{current_task}' for {task_duration:.1f}s (threshold: {self.stuck_threshold_sec}s)."
                })

        # Check repeated failures
        failures = vitals.get("consecutive_failures", 0)
        if failures >= 3:
            anomalies.append({
                "type": AnomalyType.REPEATED_FAILURES.value,
                "severity": AnomalySeverity.HIGH.value,
                "desc": f"Agent '{agent_id}' experienced {failures} consecutive task failures."
            })

        # Compute health score [0.0, 1.0]
        health_score = 1.0
        if not is_online:
            health_score -= 0.50
        if is_stuck:
            health_score -= 0.30
        if failures > 0:
            health_score -= min(0.40, failures * 0.15)
        health_score = max(0.0, round(health_score, 2))

        status_str = "OPERATIONAL"
        if not is_online:
            status_str = "OFFLINE"
        elif is_stuck or health_score < 0.5:
            status_str = "DEGRADED"

        resp = AgentHealthResponse(
            agent_id=agent_id,
            status=status_str,
            is_online=is_online,
            last_heartbeat=last_hb.isoformat(),
            heartbeat_interval_sec=interval,
            time_since_heartbeat_sec=round(elapsed_sec, 2),
            active_task=current_task,
            consecutive_failures=failures,
            is_stuck=is_stuck,
            cpu_load=vitals.get("cpu_load", 0.0),
            memory_mb=vitals.get("memory_mb", 0.0),
            queue_length=vitals.get("queue_len", 0),
            health_score=health_score,
        )
        return resp, anomalies

