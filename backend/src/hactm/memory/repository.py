"""
Repository for Adaptive Evidence Memory database interactions.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func, and_, or_

from hactm.storage.models import (
    EvidenceMemoryModel,
    MemoryAccessLogModel,
    MemoryTransitionLogModel,
    MemorySummaryModel,
)
from hactm.memory.models import (
    EvidenceMemoryEntry,
    MemoryTier,
    MemoryRetrievalQuery,
    MemorySummary,
)

SENSITIVE_KEYS = {
    "password", "passphrase", "otp", "token", "auth_token", "jwt",
    "secret", "private_key", "biometric", "raw_biometric", "card_number",
    "cvv", "cc_num", "ssn", "payment_credential"
}


def sanitize_payload(data: Any) -> Any:
    """Recursively redacts sensitive credentials/privacy fields."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(s in k.lower() for s in SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED_PRIVACY]"
            else:
                sanitized[k] = sanitize_payload(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_payload(item) for item in data]
    return data


class MemoryRepository:
    """Persistence repository for Evidence Memory, transitions, logs, and summaries."""

    def __init__(self, session: Session):
        self.session = session

    def store_entry(self, entry: EvidenceMemoryEntry) -> EvidenceMemoryModel:
        """Stores or updates a memory entry with transactional safety."""
        existing = self.session.query(EvidenceMemoryModel).filter_by(memory_id=entry.memory_id).first()
        clean_meta = sanitize_payload(entry.metadata)

        if existing:
            existing.importance_score = entry.importance_score
            existing.memory_tier = entry.memory_tier.value
            existing.access_count = entry.access_count
            existing.last_accessed_at = entry.last_accessed_at
            existing.expires_at = entry.expires_at
            existing.retrieval_count = entry.retrieval_count
            existing.summary = entry.summary
            existing.metadata_json = clean_meta
            model_obj = existing
        else:
            model_obj = EvidenceMemoryModel(
                memory_id=entry.memory_id,
                evidence_id=entry.evidence_id,
                entity_ids=entry.entity_ids,
                event_type=entry.event_type,
                domain=entry.domain,
                timestamp=entry.timestamp,
                risk_score=entry.risk_score,
                confidence=entry.confidence,
                uncertainty=entry.uncertainty,
                importance_score=entry.importance_score,
                memory_tier=entry.memory_tier.value,
                access_count=entry.access_count,
                last_accessed_at=entry.last_accessed_at,
                created_at=entry.created_at,
                expires_at=entry.expires_at,
                retrieval_count=entry.retrieval_count,
                source_dataset=entry.source_dataset,
                agent_id=entry.agent_id,
                detector_id=entry.detector_id,
                model_version=entry.model_version,
                summary=entry.summary,
                metadata_json=clean_meta,
            )
            self.session.add(model_obj)

        self.session.commit()
        return model_obj

    def get_by_id(self, memory_id: str) -> Optional[EvidenceMemoryModel]:
        return self.session.query(EvidenceMemoryModel).filter_by(memory_id=memory_id).first()

    def get_by_evidence_id(self, evidence_id: str) -> Optional[EvidenceMemoryModel]:
        return self.session.query(EvidenceMemoryModel).filter_by(evidence_id=evidence_id).first()

    def query_entries(self, query: MemoryRetrievalQuery) -> List[EvidenceMemoryModel]:
        """Retrieves ranked memory entries based on multi-dimensional query criteria."""
        q = self.session.query(EvidenceMemoryModel)

        if query.memory_tier:
            q = q.filter(EvidenceMemoryModel.memory_tier == query.memory_tier.value)
        if query.domain:
            q = q.filter(EvidenceMemoryModel.domain == query.domain)
        if query.event_type:
            q = q.filter(EvidenceMemoryModel.event_type == query.event_type)
        if query.risk_min is not None:
            q = q.filter(EvidenceMemoryModel.risk_score >= query.risk_min)
        if query.importance_min is not None:
            q = q.filter(EvidenceMemoryModel.importance_score >= query.importance_min)
        if query.start_time:
            q = q.filter(EvidenceMemoryModel.timestamp >= query.start_time)
        if query.end_time:
            q = q.filter(EvidenceMemoryModel.timestamp <= query.end_time)

        # Entity filtering via JSON array or specific match
        if query.entity_id:
            # SQLite JSON search or string match in JSON array
            q = q.filter(
                or_(
                    func.json_extract(EvidenceMemoryModel.entity_ids, '$').like(f'%"{query.entity_id}"%'),
                    EvidenceMemoryModel.memory_id.like(f"%{query.entity_id}%")
                )
            )

        # Multi-factor ranking: importance, recency, risk
        q = q.order_by(
            EvidenceMemoryModel.importance_score.desc(),
            EvidenceMemoryModel.timestamp.desc(),
            EvidenceMemoryModel.risk_score.desc(),
        )

        return q.limit(query.max_results).all()

    def log_access(self, memory_id: str, requesting_component: str, reason: str, rank: int = 1, query_id: Optional[str] = None):
        """Records an access log entry and increments retrieval stats."""
        access_entry = MemoryAccessLogModel(
            memory_id=memory_id,
            query_id=query_id,
            reason=reason,
            retrieval_rank=rank,
            requesting_component=requesting_component,
            access_time=datetime.now(timezone.utc),
        )
        self.session.add(access_entry)
        
        mem = self.get_by_id(memory_id)
        if mem:
            mem.access_count += 1
            mem.retrieval_count += 1
            mem.last_accessed_at = datetime.now(timezone.utc)
        self.session.commit()

    def log_transition(self, memory_id: str, previous_tier: str, new_tier: str, reason: str, importance: float):
        """Logs auditable tier transitions (HOT -> WARM, WARM -> HOT, etc.)."""
        trans = MemoryTransitionLogModel(
            memory_id=memory_id,
            previous_tier=previous_tier,
            new_tier=new_tier,
            reason=reason,
            importance_score=importance,
            timestamp=datetime.now(timezone.utc),
        )
        self.session.add(trans)
        
        mem = self.get_by_id(memory_id)
        if mem:
            mem.memory_tier = new_tier
        self.session.commit()

    def store_summary(self, summary: MemorySummary) -> MemorySummaryModel:
        sum_obj = MemorySummaryModel(
            summary_id=summary.summary_id,
            entity_id=summary.entity_id,
            source_evidence_ids=summary.source_evidence_ids,
            summary_version=summary.summary_version,
            algorithm_version=summary.algorithm_version,
            summary_text=summary.summary_text,
            created_at=summary.created_at,
        )
        self.session.add(sum_obj)
        self.session.commit()
        return sum_obj

    def count_by_tier(self) -> Dict[str, int]:
        results = self.session.query(
            EvidenceMemoryModel.memory_tier, func.count(EvidenceMemoryModel.memory_id)
        ).group_by(EvidenceMemoryModel.memory_tier).all()
        counts = {"HOT": 0, "WARM": 0, "COLD": 0}
        for tier, count in results:
            if tier in counts:
                counts[tier] = count
        return counts
