"""
Entity Repository for HACTM.
Handles deterministic entity retrieval, search, and state upserts.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session

from hactm.storage.models import EntityModel, SecurityEvidenceModel
from hactm.core.constants import EntityType


class EntityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, entity_id: str) -> Optional[EntityModel]:
        # First check identity map and database
        entity = self.db.get(EntityModel, entity_id)
        if entity:
            return entity
        # Check pending new entities in current un-flushed session
        for obj in self.db.new:
            if isinstance(obj, EntityModel) and obj.entity_id == entity_id:
                return obj
        return None

    def upsert_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        canonical_name: str,
        attributes: Dict[str, Any],
        seen_at: datetime
    ) -> EntityModel:
        """
        Deterministically creates or updates an entity.
        Maintains earliest first_seen, latest last_seen, and increments event_count.
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            entity = EntityModel(
                entity_id=entity_id,
                entity_type=entity_type.value if hasattr(entity_type, "value") else str(entity_type),
                canonical_name=canonical_name,
                attributes=attributes,
                first_seen=seen_at,
                last_seen=seen_at,
                event_count=1,
            )
            self.db.add(entity)
            self.db.flush()
        else:
            def _to_utc(dt: datetime) -> datetime:
                if dt.tzinfo is None:
                    return dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)

            seen_at_utc = _to_utc(seen_at)
            first_seen_utc = _to_utc(entity.first_seen)
            last_seen_utc = _to_utc(entity.last_seen)

            if seen_at_utc < first_seen_utc:
                entity.first_seen = seen_at_utc
            if seen_at_utc > last_seen_utc:
                entity.last_seen = seen_at_utc
            entity.event_count += 1
            # Merge non-empty attributes
            merged_attrs = dict(entity.attributes or {})
            merged_attrs.update(attributes)
            entity.attributes = merged_attrs

        return entity

    def list_entities(
        self,
        query: Optional[str] = None,
        entity_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[EntityModel], int]:
        stmt = select(EntityModel)

        if entity_type:
            stmt = stmt.filter(EntityModel.entity_type == entity_type.upper())

        if query:
            pattern = f"%{query.strip()}%"
            stmt = stmt.filter(
                or_(
                    EntityModel.entity_id.ilike(pattern),
                    EntityModel.canonical_name.ilike(pattern),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        # Order and paginate
        offset = (page - 1) * page_size
        stmt = stmt.order_by(EntityModel.last_seen.desc()).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().all())

        return items, total

    def count_total(self) -> int:
        return self.db.query(func.count(EntityModel.entity_id)).scalar() or 0
