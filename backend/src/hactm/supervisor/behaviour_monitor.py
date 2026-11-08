"""
Central Agent Supervisor — Behaviour Monitor.
Establishes baseline operational profiles and detects anomalous behavioral deviations,
unusual task switching, excessive agent communication, and uncharacteristic tool usage.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict

from hactm.supervisor.schemas import AgentBehaviourResponse, AnomalyType, AnomalySeverity


class AgentBehaviourMonitor:
    """Monitors agent operational patterns, task switching, and communication volume."""

    def __init__(self):
        # Rolling event history: {agent_id: [(timestamp, event_type, duration_ms)]}
        self._history: Dict[str, List[Tuple[datetime, str, float]]] = defaultdict(list)
        # Tool call counts in current window: {agent_id: count}
        self._tool_counts: Dict[str, int] = defaultdict(int)
        # Handoff counts: {agent_id: count}
        self._handoff_counts: Dict[str, int] = defaultdict(int)
        # Communication message count: {agent_id: count}
        self._comm_counts: Dict[str, int] = defaultdict(int)

    def record_activity(self, agent_id: str, event_type: str, execution_ms: float = 0.0, is_tool_call: bool = False,
                        is_handoff: bool = False, is_comm: bool = False):
        """Records an agent operational activity."""
        now = datetime.now(timezone.utc)
        self._history[agent_id].append((now, event_type, execution_ms))
        if is_tool_call:
            self._tool_counts[agent_id] += 1
        if is_handoff:
            self._handoff_counts[agent_id] += 1
        if is_comm:
            self._comm_counts[agent_id] += 1

        # Prune events older than 15 minutes
        cutoff = now - timedelta(minutes=15)
        self._history[agent_id] = [e for e in self._history[agent_id] if e[0] >= cutoff]

    def evaluate_behaviour(self, agent_id: str) -> Tuple[AgentBehaviourResponse, List[Dict[str, str]]]:
        """
        Evaluates behavioural metrics and flags deviations against typical baseline envelopes.
        Returns: (behaviour_response, list_of_behavioural_anomalies)
        """
        now = datetime.now(timezone.utc)
        events = self._history.get(agent_id, [])
        anomalies = []
        flags = []

        # Calculate events in last 1 minute
        one_min_ago = now - timedelta(minutes=1)
        recent_1m = [e for e in events if e[0] >= one_min_ago]
        task_freq_1m = float(len(recent_1m))

        durations = [e[2] for e in events if e[2] > 0]
        avg_dur_ms = sum(durations) / len(durations) if durations else 0.0

        tool_cnt = self._tool_counts.get(agent_id, 0)
        handoff_cnt = self._handoff_counts.get(agent_id, 0)
        comm_vol = self._comm_counts.get(agent_id, 0)

        # Baseline Checks:
        # 1. Burst task switching (> 25 actions/minute)
        if task_freq_1m > 25:
            flags.append("BURST_ACTIVITY_SPIKE")
            anomalies.append({
                "type": AnomalyType.UNUSUAL_COMMUNICATION_PATTERN.value,
                "severity": AnomalySeverity.MEDIUM.value,
                "desc": f"Agent '{agent_id}' exhibits abnormal action velocity: {task_freq_1m} actions/min (baseline < 20)."
            })

        # 2. Excessive task handoffs (> 12 handoffs in window)
        if handoff_cnt > 12:
            flags.append("EXCESSIVE_HANDOFF_LOOP")
            anomalies.append({
                "type": AnomalyType.EXCESSIVE_TASK_DELEGATION.value,
                "severity": AnomalySeverity.HIGH.value,
                "desc": f"Agent '{agent_id}' triggered {handoff_cnt} handoffs in active window, indicating delegation loop."
            })

        # 3. Excessive tool invocation volume (> 30 tool calls without task completion)
        if tool_cnt > 30:
            flags.append("ELEVATED_TOOL_CALL_VOLUME")
            anomalies.append({
                "type": AnomalyType.BUDGET_EXCEEDED.value,
                "severity": AnomalySeverity.MEDIUM.value,
                "desc": f"Agent '{agent_id}' invoked {tool_cnt} tools in rolling window, exceeding typical consumption baseline."
            })

        # Compute composite anomaly score [0.0 - 1.0]
        anomaly_score = 0.0
        if flags:
            anomaly_score = min(1.0, len(flags) * 0.35)

        resp = AgentBehaviourResponse(
            agent_id=agent_id,
            task_frequency_per_min=task_freq_1m,
            avg_execution_ms=round(avg_dur_ms, 2),
            tool_request_count=tool_cnt,
            handoff_count=handoff_cnt,
            communication_volume=comm_vol,
            anomaly_score=round(anomaly_score, 2),
            active_flags=flags,
            baseline_deviation_ratio=round(1.0 + anomaly_score, 2),
        )
        return resp, anomalies

