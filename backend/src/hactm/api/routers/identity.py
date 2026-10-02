"""
Identity & Authentication REST API Router.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.identity_service import IdentityService
from hactm.identity.loader import generate_synthetic_identity_dataset

router = APIRouter(prefix="/api/v1/identity", tags=["Identity & Authentication Security"])


@router.get("/events")
def get_identity_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    service = IdentityService(db)
    items, total = service.repo.list_events(page=page, limit=limit)
    if not items and total == 0:
        synth = generate_synthetic_identity_dataset(count=20)
        service.process_raw_events(synth)
        items, total = service.repo.list_events(page=page, limit=limit)

    return {
        "items": [
            {
                "authentication_event_id": e.authentication_event_id,
                "user_id": e.user_id,
                "account_id": e.account_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "device_id": e.device_id,
                "source_ip": e.source_ip,
                "authentication_method": e.authentication_method,
                "authentication_status": e.authentication_status,
                "two_factor_used": e.two_factor_used,
                "two_factor_result": e.two_factor_result,
            }
            for e in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post("/events")
def ingest_identity_events(
    payload: List[Dict[str, Any]],
    dataset_name: str = Query("identity_stream"),
    db: Session = Depends(get_db)
):
    if not payload:
        raise HTTPException(status_code=400, detail="Empty request payload")
    service = IdentityService(db)
    return service.process_raw_events(payload, dataset_name=dataset_name)


@router.get("/detections")
def get_identity_detections(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    min_risk: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    service = IdentityService(db)
    items, total = service.repo.list_detections(page=page, limit=limit, min_risk=min_risk)
    return {
        "items": [
            {
                "detection_id": d.detection_id,
                "event_id": d.event_id,
                "user_id": d.user_id,
                "agent_id": d.agent_id,
                "detector_type": d.detector_type,
                "detector_id": d.detector_id,
                "category": d.category,
                "risk_score": d.risk_score,
                "confidence": d.confidence,
                "uncertainty": d.uncertainty,
                "severity": d.severity,
                "explanation": d.explanation,
                "reason_codes": d.reason_codes,
                "features_used": d.features_used,
                "timestamp": d.timestamp.isoformat() if d.timestamp else None,
            }
            for d in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/metrics")
def get_identity_metrics(db: Session = Depends(get_db)):
    service = IdentityService(db)
    eval_res = service.evaluate()
    health_res = service.agent.health()
    return {
        "agent_health": health_res,
        "evaluation": eval_res.model_dump(),
    }
