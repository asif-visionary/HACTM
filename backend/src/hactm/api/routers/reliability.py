"""
FastAPI Router for Reliability Processing, Calibration, Uncertainty, Drift, and Reputation.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from hactm.storage.database import get_db
from hactm.services.reliability_service import ReliabilityService
from hactm.reliability.models import ReliabilityConfig
from hactm.api.schemas.common import SingleResponse, PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/api/v1/reliability", tags=["Reliability Processing & Uncertainty Layer"])


class EvaluateAgentRequest(BaseModel):
    agent_id: str = Field(..., description="Target security agent ID")
    true_positives: int = Field(..., ge=0)
    false_positives: int = Field(..., ge=0)
    true_negatives: int = Field(..., ge=0)
    false_negatives: int = Field(..., ge=0)
    detector_id: Optional[str] = None
    domain: Optional[str] = None
    model_version: str = "1.0.0"
    calibration_error: float = 0.05
    drift_score: float = 0.0
    dataset: str = "synthetic_eval_v1"
    change_reason: str = "Empirical ground truth evaluation run"


class EvaluateCalibrationRequest(BaseModel):
    agent_id: str = Field(...)
    predicted_confidences: List[float] = Field(...)
    observed_outcomes: List[int] = Field(...)
    detector_id: Optional[str] = None
    model_version: str = "1.0.0"
    dataset: str = "synthetic_eval_v1"
    calibration_method: str = "temperature_scaling"
    temperature: float = 1.2


class EvaluateDriftRequest(BaseModel):
    agent_id: str = Field(...)
    feature_or_signal: str = Field(...)
    reference_values: List[float] = Field(...)
    current_values: List[float] = Field(...)
    detector_id: Optional[str] = None
    model_version: str = "1.0.0"
    drift_method: str = "PSI"


@router.get("/health", response_model=SingleResponse[Dict[str, Any]])
def get_reliability_health(db: Session = Depends(get_db)):
    """Retrieves operational health and record status for Reliability & Trust."""
    service = ReliabilityService(db)
    return SingleResponse(data=service.get_health())


@router.get("/config", response_model=SingleResponse[Dict[str, Any]])
def get_reliability_config(db: Session = Depends(get_db)):
    """Retrieves active ReliabilityConfig parameters and thresholds."""
    service = ReliabilityService(db)
    return SingleResponse(data=service.config.model_dump())


@router.get("/agents", response_model=PaginatedResponse[Dict[str, Any]])
def list_agent_reliabilities(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    agent_id: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieves paginated agent-level reliability records."""
    service = ReliabilityService(db)
    res = service.list_reliability_records(agent_id=agent_id, domain=domain, status=status, page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.get("/agents/{agent_id}", response_model=SingleResponse[Dict[str, Any]])
def get_agent_reliability_by_id(agent_id: str, db: Session = Depends(get_db)):
    """Retrieves latest reliability evaluation record for a specific agent."""
    service = ReliabilityService(db)
    record = service.get_agent_reliability(agent_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reliability record for agent '{agent_id}' not found.")
    return SingleResponse(data=record)


@router.get("/detectors", response_model=PaginatedResponse[Dict[str, Any]])
def list_detector_reliabilities(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    detector_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieves paginated detector-level reliability records."""
    service = ReliabilityService(db)
    res = service.list_reliability_records(agent_id=agent_id, detector_id=detector_id, page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.get("/detectors/{detector_id}", response_model=SingleResponse[Dict[str, Any]])
def get_detector_reliability_by_id(detector_id: str, agent_id: str = Query("network-security-agent"), db: Session = Depends(get_db)):
    """Retrieves latest reliability evaluation for a specific detector."""
    service = ReliabilityService(db)
    record = service.get_agent_reliability(agent_id, detector_id=detector_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reliability record for detector '{detector_id}' not found.")
    return SingleResponse(data=record)


@router.get("/history/{agent_id}", response_model=PaginatedResponse[Dict[str, Any]])
def get_reliability_history(
    agent_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Retrieves historical audit trail of reliability score updates for an agent."""
    service = ReliabilityService(db)
    res = service.list_history(agent_id, page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.post("/evaluate", response_model=SingleResponse[Dict[str, Any]])
def evaluate_reliability(payload: EvaluateAgentRequest, db: Session = Depends(get_db)):
    """Triggers empirical ground-truth reliability evaluation for an agent or detector."""
    service = ReliabilityService(db)
    result = service.evaluate_agent(
        agent_id=payload.agent_id,
        true_positives=payload.true_positives,
        false_positives=payload.false_positives,
        true_negatives=payload.true_negatives,
        false_negatives=payload.false_negatives,
        detector_id=payload.detector_id,
        domain=payload.domain,
        model_version=payload.model_version,
        calibration_error=payload.calibration_error,
        drift_score=payload.drift_score,
        dataset=payload.dataset,
        change_reason=payload.change_reason,
    )
    return SingleResponse(data=result)


@router.get("/calibration", response_model=PaginatedResponse[Dict[str, Any]])
def list_calibration_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    agent_id: Optional[str] = Query(None),
    detector_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieves confidence calibration evaluation metrics and reliability diagrams."""
    service = ReliabilityService(db)
    res = service.list_calibration(agent_id=agent_id, detector_id=detector_id, page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.post("/calibration/evaluate", response_model=SingleResponse[Dict[str, Any]])
def evaluate_calibration(payload: EvaluateCalibrationRequest, db: Session = Depends(get_db)):
    """Evaluates ECE, MCE, Brier score, and applies post-hoc confidence calibration."""
    service = ReliabilityService(db)
    res = service.evaluate_calibration(
        agent_id=payload.agent_id,
        predicted_confidences=payload.predicted_confidences,
        observed_outcomes=payload.observed_outcomes,
        detector_id=payload.detector_id,
        model_version=payload.model_version,
        dataset=payload.dataset,
        calibration_method=payload.calibration_method,
        temperature=payload.temperature,
    )
    return SingleResponse(data=res)


@router.get("/drift", response_model=PaginatedResponse[Dict[str, Any]])
def list_drift_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    agent_id: Optional[str] = Query(None),
    drift_detected: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieves feature and distribution drift monitoring records."""
    service = ReliabilityService(db)
    res = service.list_drift(agent_id=agent_id, drift_detected=drift_detected, page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.post("/drift/evaluate", response_model=SingleResponse[Dict[str, Any]])
def evaluate_drift(payload: EvaluateDriftRequest, db: Session = Depends(get_db)):
    """Triggers PSI or JS-divergence drift monitoring between reference and current samples."""
    service = ReliabilityService(db)
    res = service.evaluate_drift(
        agent_id=payload.agent_id,
        feature_or_signal=payload.feature_or_signal,
        reference_values=payload.reference_values,
        current_values=payload.current_values,
        detector_id=payload.detector_id,
        model_version=payload.model_version,
        drift_method=payload.drift_method,
    )
    return SingleResponse(data=res)


@router.get("/conflicts", response_model=PaginatedResponse[Dict[str, Any]])
def list_conflicts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    entity_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieves evidence conflict and diagnostic cause records."""
    service = ReliabilityService(db)
    res = service.list_conflicts(entity_id=entity_id, page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.get("/uncertainty", response_model=PaginatedResponse[Dict[str, Any]])
def list_uncertainty(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    agent_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieves evidence uncertainty score records."""
    service = ReliabilityService(db)
    res = service.list_uncertainty(agent_id=agent_id, page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.get("/quality", response_model=PaginatedResponse[Dict[str, Any]])
def list_evidence_quality(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    evidence_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieves multi-dimensional evidence quality assessments."""
    service = ReliabilityService(db)
    res = service.list_quality(evidence_id=evidence_id, page=page, page_size=page_size)
    return PaginatedResponse(
        data=res["items"],
        pagination=PaginationMeta(page=res["page"], page_size=res["page_size"], total=res["total"]),
    )


@router.post("/research/evaluate", response_model=SingleResponse[Dict[str, Any]])
def run_research_evaluation(db: Session = Depends(get_db)):
    """Executes full empirical research evaluation suite comparing Baselines A-F and Ablations A1-A8."""
    service = ReliabilityService(db)
    res = service.run_research_evaluation()
    return SingleResponse(data=res)
