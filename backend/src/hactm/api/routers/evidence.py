"""
Security Evidence Router for HACTM.
Handles listing with filtering, pagination, inspection, and creation.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from hactm.api.schemas.common import PaginatedResponse, PaginationMeta, SingleResponse
from hactm.api.schemas.evidence import EvidenceResponse
from hactm.core.models import SecurityEvidence
from hactm.services.evidence_service import EvidenceService
from hactm.storage.database import get_db

router = APIRouter(prefix="/evidence", tags=["Security Evidence"])


@router.get("", response_model=PaginatedResponse[EvidenceResponse])
def get_evidence_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Page size (max 500)"),
    search: Optional[str] = Query(None, description="Search across IDs, source, event_type"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    entity_id: Optional[str] = Query(None, description="Filter by resolved entity ID"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    dataset: Optional[str] = Query(None, description="Filter by dataset"),
    severity: Optional[str] = Query(None, description="Filter by severity level (LOW, MEDIUM, HIGH, CRITICAL)"),
    min_risk: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum risk score"),
    max_risk: Optional[float] = Query(None, ge=0.0, le=1.0, description="Maximum risk score"),
    start_time: Optional[datetime] = Query(None, description="Start timestamp (UTC)"),
    end_time: Optional[datetime] = Query(None, description="End timestamp (UTC)"),
    db: Session = Depends(get_db),
):
    service = EvidenceService(db)
    items, total = service.list_evidence(
        search=search,
        event_type=event_type,
        entity_id=entity_id,
        agent_id=agent_id,
        source=source,
        dataset=dataset,
        severity=severity,
        min_risk=min_risk,
        max_risk=max_risk,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size,
    )

    data = [EvidenceResponse.model_validate(item) for item in items]
    return PaginatedResponse(
        data=data,
        pagination=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/{event_id}", response_model=SingleResponse[EvidenceResponse])
def get_evidence_by_id(
    event_id: str,
    db: Session = Depends(get_db),
):
    service = EvidenceService(db)
    evidence = service.get_by_event_id(event_id)
    return SingleResponse(data=EvidenceResponse.model_validate(evidence))


@router.post("", response_model=SingleResponse[EvidenceResponse], status_code=status.HTTP_201_CREATED)
def create_evidence(
    payload: SecurityEvidence,
    db: Session = Depends(get_db),
):
    service = EvidenceService(db)
    saved = service.create_evidence(payload)
    return SingleResponse(data=EvidenceResponse.model_validate(saved))
