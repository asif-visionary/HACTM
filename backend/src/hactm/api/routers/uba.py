"""
UBA REST API Router.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.uba_service import UbaService
from hactm.uba.loader import generate_synthetic_uba_dataset

router = APIRouter(prefix="/api/v1/uba", tags=["User Behavior Analytics"])


@router.get("/events")
def get_uba_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    service = UbaService(db)
    items, total = service.repo.list_events(page=page, limit=limit)
    if not items and total == 0:
        synth = generate_synthetic_uba_dataset(count=25)
        service.process_raw_events(synth)
        items, total = service.repo.list_events(page=page, limit=limit)

    return {
        "items": [
            {
                "event_id": e.event_id,
                "user_id": e.user_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "action": e.action,
                "resource": e.resource,
                "application": e.application,
                "bytes_transferred": e.bytes_transferred,
                "privilege_level": e.privilege_level,
            }
            for e in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post("/events")
def ingest_uba_events(
    payload: List[Dict[str, Any]],
    dataset_name: str = Query("uba_stream"),
    db: Session = Depends(get_db)
):
    if not payload:
        raise HTTPException(status_code=400, detail="Empty request payload")
    service = UbaService(db)
    return service.process_raw_events(payload, dataset_name=dataset_name)


@router.get("/detections")
def get_uba_detections(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    min_risk: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    service = UbaService(db)
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


@router.get("/profiles")
def get_uba_profiles(db: Session = Depends(get_db)):
    service = UbaService(db)
    profiles = service.repo.list_profiles()
    return [
        {
            "user_id": p.user_id,
            "peer_group": p.peer_group,
            "first_seen": p.first_seen.isoformat() if p.first_seen else None,
            "last_seen": p.last_seen.isoformat() if p.last_seen else None,
            "event_count": p.event_count,
            "normal_login_hours": p.normal_login_hours,
            "known_devices": p.known_devices,
            "known_applications": p.known_applications,
            "typical_resources": p.typical_resources,
            "avg_bytes_transferred": p.avg_bytes_transferred,
        }
        for m in [1]
        for p in profiles
    ]


@router.get("/metrics")
def get_uba_metrics(db: Session = Depends(get_db)):
    service = UbaService(db)
    eval_res = service.evaluate()
    health_res = service.agent.health()
    return {
        "agent_health": health_res,
        "evaluation": eval_res.model_dump(),
    }
