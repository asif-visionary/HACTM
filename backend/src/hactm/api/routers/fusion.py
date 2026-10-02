"""
FastAPI Router for Evidence Fusion Cross-Domain Evidence Fusion and Unified Cyber Risk.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from hactm.storage.database import get_db
from hactm.services.fusion_service import FusionService
from hactm.api.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/v1", tags=["Cross-Domain Evidence Fusion & Unified Cyber Risk"])


class FusionRunRequest(BaseModel):
    entity_id: str = Field(..., description="Target entity ID to correlate and fuse evidence for")
    window_seconds: float = Field(1800.0, ge=60.0, le=86400.0, description="Temporal correlation window in seconds")
    previous_fusion_id: Optional[str] = Field(None, description="Previous fusion ID if executing a late evidence revision")


@router.get("/fusion/results", response_model=PaginatedResponse[Dict[str, Any]])
def get_fusion_results(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    entity_id: Optional[str] = Query(None),
    risk_category: Optional[str] = Query(None),
    min_risk: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_risk: Optional[float] = Query(None, ge=0.0, le=1.0),
    correlation_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieves paginated cross-domain fusion results with optional filters."""
    service = FusionService(db)
    res = service.get_fusion_results(
        page=page,
        page_size=page_size,
        entity_id=entity_id,
        risk_category=risk_category,
        min_risk=min_risk,
        max_risk=max_risk,
        correlation_type=correlation_type,
    )
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.get("/fusion/results/{fusion_id}", response_model=SingleResponse[Dict[str, Any]])
def get_fusion_by_id(fusion_id: str, db: Session = Depends(get_db)):
    """Retrieves a single FusionResult by fusion_id."""
    service = FusionService(db)
    result = service.get_fusion_by_id(fusion_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fusion result '{fusion_id}' not found")
    return SingleResponse(data=result)


@router.post("/fusion/run", response_model=SingleResponse[Dict[str, Any]])
def run_evidence_fusion(payload: FusionRunRequest, db: Session = Depends(get_db)):
    """Executes cross-domain evidence fusion pipeline for a target entity."""
    service = FusionService(db)
    result = service.run_fusion_for_entity(
        entity_id=payload.entity_id,
        window_seconds=payload.window_seconds,
        previous_fusion_id=payload.previous_fusion_id,
    )
    return SingleResponse(data=result)


@router.post("/fusion/evaluate", response_model=SingleResponse[Dict[str, Any]])
def evaluate_evidence_fusion(db: Session = Depends(get_db)):
    """Runs empirical evaluation suite comparing fusion baselines and ablation studies."""
    service = FusionService(db)
    eval_results = service.evaluate_fusion()
    return SingleResponse(data=eval_results)


@router.get("/fusion/conflicts", response_model=PaginatedResponse[Dict[str, Any]])
def get_evidence_conflicts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Retrieves evidence conflicts detected during cross-domain fusion."""
    service = FusionService(db)
    res = service.get_conflicts(page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.get("/fusion/coverage", response_model=SingleResponse[Dict[str, Any]])
def get_fusion_coverage(entity_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Retrieves expected vs available domain coverage ratio metrics."""
    service = FusionService(db)
    metrics = service.get_metrics()
    return SingleResponse(data={
        "expected_domains": [
            "network-security-agent",
            "phishing-intelligence-agent",
            "uba-agent",
            "identity-authentication-agent",
            "transaction-security-agent",
        ],
        "average_domain_coverage": metrics.get("average_domain_coverage", 0.20),
        "total_fusions_evaluated": metrics.get("total_fusions", 0),
    })


@router.get("/risk/entities/{entity_id}", response_model=SingleResponse[Dict[str, Any]])
def get_entity_unified_risk(entity_id: str, db: Session = Depends(get_db)):
    """Retrieves current Unified Cyber Risk Score and risk history for an entity."""
    service = FusionService(db)
    risk_info = service.get_entity_risk(entity_id)
    return SingleResponse(data=risk_info)


@router.get("/risk/history/{entity_id}", response_model=SingleResponse[Dict[str, Any]])
def get_entity_risk_history(entity_id: str, db: Session = Depends(get_db)):
    """Retrieves historical risk timeline records for an entity."""
    service = FusionService(db)
    risk_info = service.get_entity_risk(entity_id)
    return SingleResponse(data={"entity_id": entity_id, "history": risk_info.get("history", [])})


@router.get("/fusion/metrics", response_model=SingleResponse[Dict[str, Any]])
def get_fusion_metrics(db: Session = Depends(get_db)):
    """Retrieves aggregate Evidence Fusion evidence fusion metrics."""
    service = FusionService(db)
    metrics = service.get_metrics()
    return SingleResponse(data=metrics)


@router.get("/fusion/config", response_model=SingleResponse[Dict[str, Any]])
def get_fusion_config():
    """Retrieves current active evidence fusion configuration parameters."""
    engine = FusionService(None).engine
    return SingleResponse(data={
        "algorithm": engine.algorithm,
        "version": engine.version,
        "config_version": engine.config_version,
        "weights": engine.weight_calculator.config_weights,
        "expected_domains": engine.risk_calculator.expected_domains,
        "risk_thresholds": engine.risk_calculator.risk_thresholds,
    })
