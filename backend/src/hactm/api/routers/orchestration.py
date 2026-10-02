"""
Orchestration Engine API Router.
Provides REST endpoints for adaptive agent selection, orchestration decisions,
invocations, metrics, evaluations, and configurations.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from hactm.orchestration.models import (
    AgentRecord,
    AgentSelectionContext,
    AgentSelectionDecision,
    AgentInvocationRecord,
    AgentSelectionConfig,
    SelectionMethod,
    StoppingReason,
)
from sqlalchemy.orm import Session
from hactm.storage.database import get_db
from hactm.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/api/v1/orchestration", tags=["Orchestration"])

# Helper dependency to get OrchestrationService
def get_service(db: Session = Depends(get_db)) -> OrchestrationService:
    return OrchestrationService(db=db)


class SelectionRequest(BaseModel):
    context: AgentSelectionContext
    config: Optional[AgentSelectionConfig] = None


class InvocationRequest(BaseModel):
    decision_id: str
    selected_agent_ids: List[str]
    context: AgentSelectionContext


@router.get("/agents", response_model=List[AgentRecord])

def list_agents(
    domain: Optional[str] = Query(None, description="Filter agents by domain"),
    enabled_only: bool = Query(True, description="Only return enabled agents"),
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/agents - List registered agents with capability metadata."""
    return service.list_agents(domain=domain, enabled_only=enabled_only)


@router.get("/candidates")
def generate_candidates(
    context_id: str,
    event_type: str,
    domain: Optional[str] = None,
    entity_ids: Optional[List[str]] = Query(None),
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/candidates - Deterministic candidate generation for context."""
    # Construct minimal selection context for candidate generation
    ctx = AgentSelectionContext(
        context_id=context_id,
        event_id=f"evt_{context_id}",
        entity_ids=entity_ids or ["usr_default"],
        event_type=event_type,
        domains_observed=[domain] if domain else [],
    )
    candidates = service.get_candidates(ctx)
    return {"context_id": context_id, "candidates": candidates, "count": len(candidates)}


@router.post("/select", response_model=AgentSelectionDecision)
def select_agents(
    req: SelectionRequest,
    service: OrchestrationService = Depends(get_service),
):
    """POST /api/v1/orchestration/select - Run adaptive agent selection on provided context."""
    try:
        return service.select_agents(req.context, config=req.config)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent selection failed: {str(e)}",
        )


@router.post("/invoke")
def invoke_agents(
    req: InvocationRequest,
    service: OrchestrationService = Depends(get_service),
):
    """POST /api/v1/orchestration/invoke - Execute selection round and update closed-loop context."""
    try:
        results = service.execute_orchestration_loop(req.context)
        return {
            "decision_id": req.decision_id,
            "status": "completed",
            "orchestration_summary": results,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent invocation failed: {str(e)}",
        )


@router.get("/decisions")
def list_decisions(
    limit: int = Query(50, ge=1, le=500),
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/decisions - Retrieve history of selection decisions."""
    return service.list_decisions(limit=limit)


@router.get("/decisions/{decision_id}")
def get_decision(
    decision_id: str,
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/decisions/{decision_id} - Retrieve specific decision details."""
    decision = service.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return decision


@router.get("/invocations")
def list_invocations(
    limit: int = Query(50, ge=1, le=500),
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/invocations - Retrieve invocation history."""
    return service.list_invocations(limit=limit)


@router.get("/invocations/{invocation_id}")
def get_invocation(
    invocation_id: str,
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/invocations/{invocation_id} - Retrieve specific invocation."""
    inv = service.get_invocation(invocation_id)
    if not inv:
        raise HTTPException(status_code=404, detail=f"Invocation {invocation_id} not found")
    return inv


@router.get("/history")
def get_history(
    limit: int = Query(50, ge=1, le=500),
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/history - Retrieve historical decision logs for research optimization."""
    return service.get_history(limit=limit)


@router.get("/metrics")
def get_metrics(
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/metrics - Retrieve operational & efficiency metrics."""
    return service.get_metrics()


@router.get("/evaluation")
def run_evaluation(
    num_events: int = Query(10, ge=1, le=100),
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/evaluation - Run baseline comparison, ablations, & scenario benchmarks."""
    return service.run_research_evaluation(num_events=num_events)


@router.get("/config", response_model=AgentSelectionConfig)
def get_config(
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/config - Get active selection configuration & weights."""
    return service.config


@router.get("/health")
def get_orchestration_health(
    service: OrchestrationService = Depends(get_service),
):
    """GET /api/v1/orchestration/health - Check health and status of registered agents."""
    agents = service.list_agents()
    available_count = sum(1 for a in agents if str(a.get("availability_status", "")).upper() in ["AVAILABLE", "AGENTAVAILABILITYSTATUS.AVAILABLE"] and a.get("enabled") in [True, "true"])
    return {
        "status": "healthy" if available_count > 0 else "degraded",
        "total_registered_agents": len(agents),
        "available_agents": available_count,
        "agents_drift_observed": sum(1 for a in agents if str(a.get("drift_status", "")).upper() != "STABLE"),
    }
