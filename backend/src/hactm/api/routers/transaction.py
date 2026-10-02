"""
Transaction Security REST API Router.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.transaction_service import TransactionService
from hactm.transaction.loader import generate_synthetic_transaction_dataset

router = APIRouter(prefix="/api/v1/transactions", tags=["Transaction Security"])


@router.get("/events")
def get_transaction_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    service = TransactionService(db)
    items, total = service.repo.list_events(page=page, limit=limit)
    if not items and total == 0:
        synth = generate_synthetic_transaction_dataset(count=20)
        service.process_raw_events(synth)
        items, total = service.repo.list_events(page=page, limit=limit)

    return {
        "items": [
            {
                "transaction_id": e.transaction_id,
                "account_id": e.account_id,
                "user_id": e.user_id,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "amount": e.amount,
                "currency": e.currency,
                "merchant_id": e.merchant_id,
                "recipient_id": e.recipient_id,
                "transaction_type": e.transaction_type,
                "channel": e.channel,
                "status": e.status,
            }
            for e in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.post("/events")
def ingest_transaction_events(
    payload: List[Dict[str, Any]],
    dataset_name: str = Query("transaction_stream"),
    db: Session = Depends(get_db)
):
    if not payload:
        raise HTTPException(status_code=400, detail="Empty request payload")
    service = TransactionService(db)
    return service.process_raw_events(payload, dataset_name=dataset_name)


@router.get("/detections")
def get_transaction_detections(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    min_risk: Optional[float] = Query(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db)
):
    service = TransactionService(db)
    items, total = service.repo.list_detections(page=page, limit=limit, min_risk=min_risk)
    return {
        "items": [
            {
                "detection_id": d.detection_id,
                "event_id": d.event_id,
                "account_id": d.account_id,
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
def get_transaction_metrics(db: Session = Depends(get_db)):
    service = TransactionService(db)
    eval_res = service.evaluate()
    health_res = service.agent.health()
    return {
        "agent_health": health_res,
        "evaluation": eval_res.model_dump(),
    }
