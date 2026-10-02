"""
Entity Service for HACTM.
Handles entity inspection and associated evidence resolution.
"""

from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from hactm.core.errors import NotFoundError
from hactm.storage.models import EntityModel, SecurityEvidenceModel
from hactm.storage.repositories.entity_repo import EntityRepository
from hactm.storage.repositories.evidence_repo import EvidenceRepository


class EntityService:
    def __init__(self, db: Session):
        self.db = db
        self.entity_repo = EntityRepository(db)
        self.evidence_repo = EvidenceRepository(db)

    def get_by_id(self, entity_id: str) -> EntityModel:
        entity = self.entity_repo.get_by_id(entity_id)
        if not entity:
            raise NotFoundError(f"Entity '{entity_id}' not found")
        return entity

    def get_entity_with_evidence(self, entity_id: str, limit: int = 25) -> Tuple[EntityModel, List[SecurityEvidenceModel]]:
        entity = self.get_by_id(entity_id)
        associated_evidence = self.evidence_repo.get_by_entity(entity_id, limit=limit)
        return entity, associated_evidence

    def list_entities(
        self,
        query: Optional[str] = None,
        entity_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[EntityModel], int]:
        return self.entity_repo.list_entities(
            query=query,
            entity_type=entity_type,
            page=page,
            page_size=page_size,
        )
