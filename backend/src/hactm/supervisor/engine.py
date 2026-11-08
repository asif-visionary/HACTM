"""
Central Agent Supervisor (CAS) — Core Supervisory Engine.
Orchestrates continuous multi-agent health tracking, behavioural profiling, tool gateway monitoring,
evidence integrity verification, transparent trust assessment, and governed autonomous containment.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from hactm.supervisor.schemas import (
    FleetOverviewResponse,
    SupervisedAgentSummary,
    AgentHealthResponse,
    AgentBehaviourResponse,
    AgentTrustResponse,
    AnomalyAlertItem,
    SupervisorDecisionItem,
    SupervisorTelemetryEvent,
)
from hactm.supervisor.collector import TelemetryCollector
from hactm.supervisor.health_monitor import AgentHealthMonitor
from hactm.supervisor.behaviour_monitor import AgentBehaviourMonitor
from hactm.supervisor.tool_monitor import ToolActivityMonitor
from hactm.supervisor.evidence_monitor import EvidenceIntegrityMonitor
from hactm.supervisor.trust_evaluator import AgentTrustEvaluator
from hactm.supervisor.anomaly_engine import AnomalyDetectionEngine
from hactm.supervisor.intelligence_agent import SupervisorIntelligenceAgent
from hactm.supervisor.governance_adapter import GovernanceAdapter
from hactm.supervisor.orchestrator_monitor import OrchestratorMonitor
from hactm.supervisor.watchdog import SupervisorWatchdog
from hactm.orchestration.registry import AgentRegistry
from hactm.api.routers.trust_passport import ISOLATED_AGENTS, REVOKED_CAPABILITIES, AGENT_DEPARTMENTS
from hactm.services.workspace_event_broadcaster import broadcaster
from hactm.core.logging import logger


class CentralAgentSupervisor:
    """Core Supervisory Engine maintaining continuous, evidence-based oversight over HACTM agents."""

    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or AgentRegistry()
        self.collector = TelemetryCollector(self.registry)
        self.health_monitor = AgentHealthMonitor()
        self.behaviour_monitor = AgentBehaviourMonitor()
        self.tool_monitor = ToolActivityMonitor()
        self.evidence_monitor = EvidenceIntegrityMonitor()
        self.trust_evaluator = AgentTrustEvaluator()
        self.anomaly_engine = AnomalyDetectionEngine()
        self.intelligence_agent = SupervisorIntelligenceAgent()
        self.governance_adapter = GovernanceAdapter()
        self.orchestrator_monitor = OrchestratorMonitor()
        self.watchdog = SupervisorWatchdog()

        # Seed initial agent registrations from authoritative registry
        self._seed_registered_agents()

    def _seed_registered_agents(self):
        """Initializes supervisor vitals for all registered agents in registry."""
        for agent in self.registry.get_all_agents():
            self.health_monitor.update_heartbeat(
                agent_id=agent.agent_id,
                status="OPERATIONAL" if not agent.agent_id in ISOLATED_AGENTS else "ISOLATED",
                task=None,
                interval_sec=10.0,
            )

    def process_telemetry_event(
        self,
        raw_event: Dict[str, Any],
        db: Optional[Session] = None,
    ) -> Tuple[Optional[SupervisorTelemetryEvent], List[AnomalyAlertItem]]:
        """
        Executes the complete 12-step Central Supervision Pipeline on incoming runtime events.
        """
        t_start = time.perf_counter()
        norm_event, err = self.collector.collect_event(raw_event)
        if not norm_event:
            self.watchdog.record_event_processed(0.1, is_error=True)
            return None, []

        agent_id = norm_event.agent_id
        event_type = norm_event.event_type
        incident_id = norm_event.incident_id
        detected_anomalies: List[AnomalyAlertItem] = []

        # 1. Behaviour Monitoring Update
        is_tool = "tool" in event_type.lower()
        is_handoff = "handoff" in event_type.lower()
        is_comm = "comm" in event_type.lower() or "message" in event_type.lower()
        exec_ms = float(norm_event.payload.get("execution_ms", 0.0))
        self.behaviour_monitor.record_activity(
            agent_id=agent_id,
            event_type=event_type,
            execution_ms=exec_ms,
            is_tool_call=is_tool,
            is_handoff=is_handoff,
            is_comm=is_comm,
        )

        # 2. Evaluate Behaviour Deviations
        beh_resp, beh_anoms = self.behaviour_monitor.evaluate_behaviour(agent_id)
        for b_anom in beh_anoms:
            alert = self.anomaly_engine.register_anomaly(
                agent_id=agent_id,
                anomaly_type=b_anom["type"],
                severity=b_anom["severity"],
                description=b_anom["desc"],
                incident_id=incident_id,
                source="BEHAVIOUR_MONITOR",
                recommended_action="OBSERVE",
                db=db,
            )
            detected_anomalies.append(alert)

        # 3. Check Evidence Integrity if event payload contains security evidence
        evidence_payload = norm_event.payload.get("evidence")
        if evidence_payload and isinstance(evidence_payload, dict):
            ev_ok, ev_anom = self.evidence_monitor.inspect_evidence(evidence_payload, agent_id)
            if not ev_ok and ev_anom:
                alert = self.anomaly_engine.register_anomaly(
                    agent_id=agent_id,
                    anomaly_type=ev_anom["type"],
                    severity=ev_anom["severity"],
                    description=ev_anom["desc"],
                    incident_id=incident_id,
                    evidence_references=[ev_anom.get("evidence_id", "EVD")],
                    source="EVIDENCE_MONITOR",
                    recommended_action=ev_anom.get("recommended_action", "FLAG"),
                    db=db,
                )
                detected_anomalies.append(alert)

        # 4. Re-evaluate Trust Assessment
        health_resp, _ = self.health_monitor.evaluate_health(agent_id)
        agent_rec = self.registry.get_agent(agent_id)
        base_rel = agent_rec.reliability_score if agent_rec else 0.88
        active_anoms_count = len(self.anomaly_engine.get_anomalies(agent_id=agent_id, active_only=True))
        has_crit = any(a.severity == "CRITICAL" for a in detected_anomalies)

        trust_resp = self.trust_evaluator.evaluate_trust(
            agent_id=agent_id,
            base_reliability=base_rel,
            health_score=health_resp.health_score,
            anomaly_count=active_anoms_count,
            critical_anomaly=has_crit,
        )

        # 5. Risk-Based Governance Evaluation
        if detected_anomalies:
            anom_dicts = [{"severity": a.severity, "type": a.anomaly_type, "desc": a.description} for a in detected_anomalies]
            decision = self.governance_adapter.evaluate_and_enforce(
                agent_id=agent_id,
                anomalies=anom_dicts,
                incident_id=incident_id,
                operator_identity="CAS_SUPERVISOR_CORE",
                db=db,
            )

        elapsed_ms = (time.perf_counter() - t_start) * 1000.0
        self.watchdog.record_event_processed(elapsed_ms)
        return norm_event, detected_anomalies

    def process_heartbeat(
        self,
        agent_id: str,
        status: str = "OPERATIONAL",
        task: Optional[str] = None,
        heartbeat_interval_sec: float = 10.0,
        cpu_load: float = 0.0,
        memory_mb: float = 0.0,
        queue_len: int = 0,
        db: Optional[Session] = None,
    ) -> AgentHealthResponse:
        """Processes and records an incoming heartbeat."""
        self.health_monitor.update_heartbeat(
            agent_id=agent_id,
            status=status,
            task=task,
            interval_sec=heartbeat_interval_sec,
            cpu_load=cpu_load,
            memory_mb=memory_mb,
            queue_len=queue_len,
        )
        self.collector.record_heartbeat(
            agent_id=agent_id,
            status=status,
            task=task,
            interval_sec=heartbeat_interval_sec,
            cpu_load=cpu_load,
            memory_mb=memory_mb,
            queue_len=queue_len,
            db=db,
        )

        health_resp, anomalies = self.health_monitor.evaluate_health(agent_id)
        for a in anomalies:
            self.anomaly_engine.register_anomaly(
                agent_id=agent_id,
                anomaly_type=a["type"],
                severity=a["severity"],
                description=a["desc"],
                source="HEALTH_MONITOR",
                db=db,
            )

        return health_resp

    def get_fleet_overview(self, db: Optional[Session] = None) -> FleetOverviewResponse:
        """Aggregates real-time fleet health and supervisory statistics."""
        now_iso = datetime.now(timezone.utc).isoformat()
        agents = self.registry.get_all_agents()
        total = len(agents)

        healthy_cnt = 0
        observation_cnt = 0
        anomalies_cnt = 0
        restricted_cnt = 0
        isolated_cnt = 0
        offline_cnt = 0

        for ag in agents:
            h_resp, _ = self.health_monitor.evaluate_health(ag.agent_id)
            anoms = self.anomaly_engine.get_anomalies(agent_id=ag.agent_id, active_only=True)
            is_isol = ag.agent_id in ISOLATED_AGENTS
            has_revoked = ag.agent_id in REVOKED_CAPABILITIES

            if is_isol:
                isolated_cnt += 1
            elif has_revoked:
                restricted_cnt += 1
            elif not h_resp.is_online:
                offline_cnt += 1
            elif anoms:
                anomalies_cnt += 1
            elif h_resp.health_score < 0.80:
                observation_cnt += 1
            else:
                healthy_cnt += 1

        total_active_alerts = len(self.anomaly_engine.get_anomalies(active_only=True))
        diag = self.watchdog.check_health()

        return FleetOverviewResponse(
            total_registered_agents=total,
            healthy_agents=healthy_cnt,
            agents_under_observation=observation_cnt,
            agents_with_anomalies=anomalies_cnt,
            restricted_agents=restricted_cnt,
            isolated_agents=isolated_cnt,
            offline_agents=offline_cnt,
            active_monitoring_alerts=total_active_alerts,
            supervisor_health=diag["supervisor_health"],
            event_ingestion_latency_ms=diag["average_processing_latency_ms"],
            processing_queue_length=diag["queue_length"],
            watchdog_status=diag["watchdog_status"],
            last_updated_at=now_iso,
        )

    def get_supervised_agents(self, db: Optional[Session] = None) -> List[SupervisedAgentSummary]:
        """Returns structured summaries for all registered agents in the supervisory mesh."""
        summaries = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for ag in self.registry.get_all_agents():
            h_resp, _ = self.health_monitor.evaluate_health(ag.agent_id)
            anoms = self.anomaly_engine.get_anomalies(agent_id=ag.agent_id, active_only=True)
            trust_resp = self.trust_evaluator.evaluate_trust(
                agent_id=ag.agent_id,
                base_reliability=ag.reliability_score,
                health_score=h_resp.health_score,
                anomaly_count=len(anoms),
            )
            is_isol = ag.agent_id in ISOLATED_AGENTS
            revoked_count = len(REVOKED_CAPABILITIES.get(ag.agent_id, []))

            summary = SupervisedAgentSummary(
                agent_id=ag.agent_id,
                name=ag.agent_name,
                department=AGENT_DEPARTMENTS.get(ag.agent_id, "Specialized Cyber Security"),
                agent_type="Specialist Autonomous Agent",
                health=h_resp.status,
                trust_status=trust_resp.trust_status.value,
                trust_score=trust_resp.trust_score,
                current_task=h_resp.active_task or "Monitoring telemetry stream",
                last_heartbeat=h_resp.last_heartbeat,
                status="ISOLATED" if is_isol else "RESTRICTED" if revoked_count > 0 else h_resp.status,
                recent_anomalies_count=len(anoms),
                is_isolated=is_isol,
                revoked_capabilities_count=revoked_count,
            )
            summaries.append(summary)

        return summaries


# Global Singleton Central Agent Supervisor Instance
cas_supervisor = CentralAgentSupervisor()

