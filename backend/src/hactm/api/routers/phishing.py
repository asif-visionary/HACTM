"""
Phishing Intelligence REST API Router.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.phishing_service import PhishingService
from hactm.phishing.loader import generate_synthetic_phishing_dataset

router = APIRouter(prefix="/api/v1/phishing", tags=["Phishing Intelligence"])


@router.get("/events")
def get_phishing_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    service = PhishingService(db)
    items, total = service.repo.list_events(page=page, limit=limit)
    if not items and total == 0:
        # Seed synthetic events if empty for demo
        synth = generate_synthetic_phishing_dataset(count=20)
        service.process_raw_events(synth)
        items, total = service.repo.list_events(page=page, limit=limit)

    return {
        "items": [
            {
                "message_id": e.message_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "sender": e.sender,
                "recipient": e.recipient,
                "subject": e.subject,
                "sender_domain": e.sender_domain,
                "urls_count": len(e.urls or []),
                "attachments_count": len(e.attachments or []),
            }
            for e in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post("/events")
def ingest_phishing_events(
    payload: List[Dict[str, Any]],
    dataset_name: str = Query("phishing_stream"),
    db: Session = Depends(get_db)
):
    if not payload:
        raise HTTPException(status_code=400, detail="Empty request payload")
    service = PhishingService(db)
    return service.process_raw_events(payload, dataset_name=dataset_name)


@router.get("/detections")
def get_phishing_detections(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    min_risk: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    service = PhishingService(db)
    items, total = service.repo.list_detections(page=page, limit=limit, min_risk=min_risk)
    return {
        "items": [
            {
                "detection_id": d.detection_id,
                "event_id": d.event_id,
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


@router.get("/models")
def list_phishing_models(db: Session = Depends(get_db)):
    service = PhishingService(db)
    models = service.model_registry.list_models(agent_id="phishing-intelligence-agent")
    return [
        {
            "model_id": m.model_id,
            "version": m.version,
            "algorithm": m.algorithm,
            "status": m.status,
            "training_time": m.training_time.isoformat() if m.training_time else None,
            "evaluation_metrics": m.evaluation_metrics,
        }
        for m in models
    ]


@router.get("/metrics")
def get_phishing_metrics(db: Session = Depends(get_db)):
    service = PhishingService(db)
    eval_res = service.evaluate()
    health_res = service.agent.health()
    return {
        "agent_health": health_res,
        "evaluation": eval_res.model_dump(),
    }
