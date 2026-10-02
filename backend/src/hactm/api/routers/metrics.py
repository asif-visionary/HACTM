"""
Metrics Router for HACTM.
Provides live SOC dashboard KPI cards, observed risk distribution, and chronological evidence timeline.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from hactm.api.schemas.common import SingleResponse
from hactm.api.schemas.evidence import EvidenceResponse, MetricsOverviewResponse
from hactm.services.evidence_service import EvidenceService
from hactm.storage.database import get_db

router = APIRouter(prefix="/metrics", tags=["Metrics & Observability"])


@router.get("/overview", response_model=SingleResponse[MetricsOverviewResponse])
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Computes exact Foundation KPI figures and observed cyber risk distribution.
    All data is derived from actual stored evidence - no fabricated values.
    """
    service = EvidenceService(db)
    metrics = service.get_overview_metrics()
    return SingleResponse(data=MetricsOverviewResponse(**metrics))


@router.get("/timeline", response_model=SingleResponse[List[EvidenceResponse]])
def get_evidence_timeline(
    limit: int = Query(20, ge=1, le=100, description="Number of recent evidence events"),
    db: Session = Depends(get_db)
):
    """
    Returns recent evidence events ordered chronologically for the Evidence Timeline.
    Strictly marked as 'Evidence Timeline' (NOT attack-chain inference).
    """
    service = EvidenceService(db)
    items = service.get_timeline(limit=limit)
    data = [EvidenceResponse.model_validate(item) for item in items]
    return SingleResponse(data=data)
