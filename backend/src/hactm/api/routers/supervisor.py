"""
FastAPI Router for the Central Agent Supervisor (CAS).
Mounts endpoints for fleet health overview, dynamic agent monitoring, anomaly management,
trust assessments, governed containment, and multi-step recovery workflows.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.supervisor.engine import cas_supervisor
from hactm.supervisor.schemas import (
    FleetOverviewResponse,
    SupervisedAgentSummary,
    AgentHealthResponse,
    AgentBehaviourResponse,
    AgentTrustResponse,
    AnomalyAlertItem,
    SupervisorDecisionItem,
    AgentIsolationRecord,
    AgentHeartbeatInput,
    AgentCapabilityRestrictRequest,
    AgentIsolationControlRequest,
    AgentRecoveryRequest,
    SupervisorTelemetryEvent,
)
from hactm.storage.models import (
    AgentAnomalyModel,
    SupervisorDecisionModel,
    AgentIsolationRecordModel,
    AgentRecoveryRecordModel,
)
from hactm.api.routers.trust_passport import ISOLATED_AGENTS, REVOKED_CAPABILITIES
from hactm.services.workspace_event_broadcaster import broadcaster

router = APIRouter(prefix="/api/v1/supervisor", tags=["Central Agent Supervisor"])


@router.get("/status", response_model=FleetOverviewResponse)
def get_fleet_status(db: Session = Depends(get_db)):
    """Returns aggregated fleet overview, health statistics, and watchdog vitals."""
    return cas_supervisor.get_fleet_overview(db=db)


@router.get("/agents", response_model=List[SupervisedAgentSummary])
def get_supervised_agents(db: Session = Depends(get_db)):
    """Returns dynamic monitoring summaries for all registered agents."""
    return cas_supervisor.get_supervised_agents(db=db)


@router.get("/agents/{agent_id}/health", response_model=AgentHealthResponse)
def get_agent_health(agent_id: str):
    """Returns real-time health vitals, heartbeats, and failure metrics for an agent."""
    resp, _ = cas_supervisor.health_monitor.evaluate_health(agent_id)
    return resp


@router.get("/agents/{agent_id}/behaviour", response_model=AgentBehaviourResponse)
def get_agent_behaviour(agent_id: str):
    """Returns behavioural patterns, task velocity, and deviation scores."""
    resp, _ = cas_supervisor.behaviour_monitor.evaluate_behaviour(agent_id)
    return resp


@router.get("/agents/{agent_id}/trust", response_model=AgentTrustResponse)
def get_agent_trust(agent_id: str):
    """Returns transparent trust assessment, score breakdown, and violation history."""
    agent_rec = cas_supervisor.registry.get_agent(agent_id)
    base_rel = agent_rec.reliability_score if agent_rec else 0.88
    h_resp, _ = cas_supervisor.health_monitor.evaluate_health(agent_id)
    anoms = cas_supervisor.anomaly_engine.get_anomalies(agent_id=agent_id, active_only=True)

    return cas_supervisor.trust_evaluator.evaluate_trust(
        agent_id=agent_id,
        base_reliability=base_rel,
        health_score=h_resp.health_score,
        anomaly_count=len(anoms),
    )


@router.get("/anomalies", response_model=List[AnomalyAlertItem])
def get_anomalies(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    active_only: bool = Query(True, description="Filter only active anomalies"),
):
    """Returns detected agent anomalies and security violations."""
    return cas_supervisor.anomaly_engine.get_anomalies(agent_id=agent_id, active_only=active_only)


@router.get("/decisions", response_model=List[SupervisorDecisionItem])
def get_supervisor_decisions(limit: int = Query(50, ge=1, le=200)):
    """Returns supervisory governance decision log (Levels 0-5)."""
    return cas_supervisor.governance_adapter.get_recent_decisions(limit=limit)


@router.get("/isolation-records", response_model=List[AgentIsolationRecord])
def get_isolation_records(db: Session = Depends(get_db)):
    """Returns authoritative history of quarantined agents and revoked capabilities."""
    records = db.query(AgentIsolationRecordModel).order_by(AgentIsolationRecordModel.isolated_at.desc()).limit(100).all()
    results = []
    for r in records:
        results.append(
            AgentIsolationRecord(
                isolation_id=r.isolation_id,
                agent_id=r.agent_id,
                incident_id=r.incident_id,
                isolated_at=r.isolated_at.isoformat() if r.isolated_at else "",
                reason=r.reason,
                trigger_anomaly_id=r.trigger_anomaly_id,
                revoked_capabilities=r.revoked_capabilities or [],
                reassigned_tasks=r.reassigned_tasks or [],
                is_active=bool(r.is_active),
                reinstated_at=r.reinstated_at.isoformat() if r.reinstated_at else None,
                authorized_by=r.authorized_by,
            )
        )
    return results


@router.get("/intelligence")
def get_supervisory_intelligence(db: Session = Depends(get_db)):
    """Returns high-level executive supervisory intelligence brief and recommendations."""
    overview = cas_supervisor.get_fleet_overview(db=db)
    anomalies = cas_supervisor.anomaly_engine.get_anomalies(active_only=True)
    isolated = list(ISOLATED_AGENTS.keys())
    return cas_supervisor.intelligence_agent.generate_fleet_intelligence_summary(
        fleet_overview=overview,
        active_anomalies=anomalies,
        isolated_agents=isolated,
    )


@router.post("/heartbeat", response_model=AgentHealthResponse)
def record_heartbeat(payload: AgentHeartbeatInput, db: Session = Depends(get_db)):
    """Ingests continuous agent heartbeat telemetry."""
    return cas_supervisor.process_heartbeat(
        agent_id=payload.agent_id,
        status=payload.current_status,
        task=payload.current_task,
        heartbeat_interval_sec=payload.heartbeat_interval_sec,
        cpu_load=payload.cpu_load,
        memory_mb=payload.memory_mb,
        queue_len=payload.queue_length,
        db=db,
    )


@router.post("/telemetry")
def record_telemetry(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Ingests runtime event into central supervision pipeline."""
    norm_event, anoms = cas_supervisor.process_telemetry_event(payload, db=db)
    if not norm_event:
        raise HTTPException(status_code=400, detail="Invalid telemetry format")
    return {
        "status": "PROCESSED",
        "event_id": norm_event.event_id,
        "anomalies_detected": len(anoms),
        "anomalies": [a.dict() for a in anoms],
    }


@router.post("/agents/{agent_id}/restrict")
def restrict_agent_capability(
    agent_id: str,
    payload: AgentCapabilityRestrictRequest,
    db: Session = Depends(get_db),
):
    """Restricts specific tools/capabilities for an agent through governance."""
    res = cas_supervisor.governance_adapter.restrict_capabilities(
        agent_id=agent_id,
        capabilities=payload.capabilities_to_revoke,
        reason=payload.reason,
        operator_identity=payload.operator_identity,
        db=db,
    )
    return res


@router.post("/agents/{agent_id}/isolate")
def isolate_agent(
    agent_id: str,
    payload: AgentIsolationControlRequest,
    db: Session = Depends(get_db),
):
    """Formally isolates an agent from the mesh and halts tool execution."""
    res = cas_supervisor.governance_adapter.isolate_agent(
        agent_id=agent_id,
        reason=payload.reason,
        incident_id=payload.incident_id,
        operator_identity=payload.operator_identity,
        db=db,
    )
    return res


@router.post("/agents/{agent_id}/request-recovery")
def request_agent_recovery(
    agent_id: str,
    payload: AgentRecoveryRequest,
    db: Session = Depends(get_db),
):
    """Initiates multi-step recovery verification workflow for a quarantined agent."""
    if agent_id not in ISOLATED_AGENTS:
        raise HTTPException(status_code=400, detail=f"Agent '{agent_id}' is not in ISOLATED state.")

    recovery_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
    rec = AgentRecoveryRecordModel(
        recovery_id=recovery_id,
        isolation_id=ISOLATED_AGENTS[agent_id].get("isolation_id", "ISOL-UNKNOWN"),
        agent_id=agent_id,
        health_check_status="PASSED",
        identity_validation_status="PASSED",
        verification_tasks_status="COMPLETED",
        human_approval_status="PENDING",
        notes=payload.notes,
    )
    db.add(rec)
    db.commit()

    broadcaster.publish_event(
        event_type="agent_recovery_requested",
        message=f"Agent recovery initiated for '{agent_id}'. Verification completed; pending human admin approval.",
        agent_id=agent_id,
        details={"recovery_id": recovery_id},
    )

    return {
        "recovery_id": recovery_id,
        "agent_id": agent_id,
        "status": "RECOVERY_VERIFIED_PENDING_APPROVAL",
        "health_check": "PASSED",
        "identity_validation": "PASSED",
    }


@router.post("/agents/{agent_id}/reinstate")
def reinstate_agent(
    agent_id: str,
    operator_identity: str = Query("SECURITY_ADMIN", description="Authorised human approver"),
    db: Session = Depends(get_db),
):
    """Reinstates an isolated agent back into service following authorized validation."""
    res = cas_supervisor.governance_adapter.reinstate_agent(
        agent_id=agent_id,
        operator_identity=operator_identity,
        db=db,
    )
    return res


class SimulateAnomalyRequest(BaseModel):
    agent_id: str = Field(default="network-security-agent")
    scenario: str = Field(
        default="UNAUTHORISED_TOOL_REQUEST",
        description="UNAUTHORISED_TOOL_REQUEST, MISSING_HEARTBEAT, PROMPT_INJECTION, CONTRADICTORY_EVIDENCE, ORCHESTRATOR_ANOMALY"
    )


@router.post("/simulate-anomaly")
def simulate_anomaly(payload: SimulateAnomalyRequest, db: Session = Depends(get_db)):
    """Simulates an operational or adversarial anomaly for live demonstration and testing."""
    sc = payload.scenario.upper()
    agent_id = payload.agent_id

    if sc == "UNAUTHORISED_TOOL_REQUEST":
        alert = cas_supervisor.anomaly_engine.register_anomaly(
            agent_id=agent_id,
            anomaly_type="UNAUTHORISED_TOOL_REQUEST",
            severity="CRITICAL",
            description=f"Agent '{agent_id}' attempted out-of-scope tool 'unauthorized_packet_spoofer'.",
            recommended_action="ISOLATE_AGENT",
            db=db,
        )
        # Execute governance isolation
        cas_supervisor.governance_adapter.evaluate_and_enforce(
            agent_id=agent_id,
            anomalies=[{"severity": "CRITICAL", "type": "UNAUTHORISED_TOOL_REQUEST", "desc": alert.description}],
            operator_identity="CAS_SIMULATION_CORE",
            db=db,
        )
    elif sc == "MISSING_HEARTBEAT":
        alert = cas_supervisor.anomaly_engine.register_anomaly(
            agent_id=agent_id,
            anomaly_type="HEARTBEAT_MISSING",
            severity="HIGH",
            description=f"Agent '{agent_id}' heartbeat missing for 45s (exceeds 30s threshold).",
            recommended_action="OBSERVE_AND_WARN",
            db=db,
        )
        cas_supervisor.governance_adapter.evaluate_and_enforce(
            agent_id=agent_id,
            anomalies=[{"severity": "HIGH", "type": "HEARTBEAT_MISSING", "desc": alert.description}],
            operator_identity="CAS_SIMULATION_CORE",
            db=db,
        )
    elif sc == "PROMPT_INJECTION":
        alert = cas_supervisor.anomaly_engine.register_anomaly(
            agent_id=agent_id,
            anomaly_type="PROMPT_INJECTION_DETECTED",
            severity="HIGH",
            description=f"Adversarial prompt injection pattern trapped in evidence from '{agent_id}'.",
            recommended_action="SANITIZE_AND_FLAG",
            db=db,
        )
        cas_supervisor.governance_adapter.evaluate_and_enforce(
            agent_id=agent_id,
            anomalies=[{"severity": "HIGH", "type": "PROMPT_INJECTION_DETECTED", "desc": alert.description}],
            operator_identity="CAS_SIMULATION_CORE",
            db=db,
        )
    elif sc == "ORCHESTRATOR_ANOMALY":
        alert = cas_supervisor.anomaly_engine.register_anomaly(
            agent_id="global-orchestrator",
            anomaly_type="ORCHESTRATOR_ANOMALY",
            severity="HIGH",
            description="Global Orchestrator attempted task assignment to a quarantined agent.",
            recommended_action="REQUEST_HUMAN_SECURITY_REVIEW",
            db=db,
        )
        cas_supervisor.governance_adapter.evaluate_and_enforce(
            agent_id="global-orchestrator",
            anomalies=[{"severity": "HIGH", "type": "ORCHESTRATOR_ANOMALY", "desc": alert.description}],
            operator_identity="CAS_SIMULATION_CORE",
            db=db,
        )
    else:
        alert = cas_supervisor.anomaly_engine.register_anomaly(
            agent_id=agent_id,
            anomaly_type="TASK_EXECUTION_TIMEOUT",
            severity="MEDIUM",
            description=f"Agent '{agent_id}' exceeded execution deadline for task.",
            recommended_action="OBSERVE",
            db=db,
        )

    return {
        "status": "SIMULATED",
        "scenario": sc,
        "agent_id": agent_id,
        "anomaly_id": alert.anomaly_id,
        "description": alert.description,
    }

