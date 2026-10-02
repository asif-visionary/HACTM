"""
Entities Router for HACTM.
Handles deterministic entity listing, search, and entity details with associated evidence.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from hactm.api.schemas.common import PaginatedResponse, PaginationMeta, SingleResponse
from hactm.api.schemas.evidence import EntityDetailResponse, EntityResponse, EvidenceResponse
from hactm.services.entity_service import EntityService
from hactm.storage.database import get_db

router = APIRouter(prefix="/entities", tags=["Entities"])


@router.get("", response_model=PaginatedResponse[EntityResponse])
def get_entities_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Page size"),
    query: Optional[str] = Query(None, description="Search by ID or canonical name"),
    entity_type: Optional[str] = Query(None, description="Filter by type (IP, EMAIL, USER, HOST, DEVICE)"),
    db: Session = Depends(get_db),
):
    service = EntityService(db)
    items, total = service.list_entities(
        query=query,
        entity_type=entity_type,
        page=page,
        page_size=page_size,
    )

    data = [EntityResponse.model_validate(e) for e in items]
    return PaginatedResponse(
        data=data,
        pagination=PaginationMeta(page=page, page_size=page_size, total=total),
    )


@router.get("/{entity_id}", response_model=SingleResponse[EntityDetailResponse])
def get_entity_detail(
    entity_id: str,
    evidence_limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = EntityService(db)
    entity, associated_ev = service.get_entity_with_evidence(entity_id, limit=evidence_limit)
    evidence_dtos = [EvidenceResponse.model_validate(ev) for ev in associated_ev]

    detail = EntityDetailResponse(
        entity_id=entity.entity_id,
        entity_type=entity.entity_type,
        canonical_name=entity.canonical_name,
        attributes=entity.attributes or {},
        first_seen=entity.first_seen,
        last_seen=entity.last_seen,
        event_count=entity.event_count,
        associated_evidence=evidence_dtos,
    )
    return SingleResponse(data=detail)
