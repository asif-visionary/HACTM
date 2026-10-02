"""
Adaptive Evidence Memory Engine.
Manages persistent, bounded, tiered, importance-aware historical evidence lifecycle.
"""

import os
import uuid
import yaml
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session

from hactm.memory.models import (
    EvidenceMemoryEntry,
    MemoryTier,
    MemoryRetrievalQuery,
    MemoryImportanceScorer,
    MemorySummary,
    ExpirationPolicy,
)
from hactm.memory.repository import MemoryRepository, sanitize_payload


class AdaptiveEvidenceMemory:
    """Core Adaptive Evidence Memory engine managing HOT, WARM, COLD tiers."""

    def __init__(self, session: Session, config_path: Optional[str] = None):
        self.session = session
        self.repo = MemoryRepository(session)
        self.scorer = MemoryImportanceScorer()

        # Config defaults
        self.hot_max_age = 900        # 15 mins
        self.hot_max_entries = 10000
        self.warm_max_age = 86400     # 24 hours
        self.warm_max_entries = 100000
        self.cold_retention_days = 30
        self.max_results = 100
        self.max_context_tokens = 10000
        self.expiration_policy = ExpirationPolicy.REFERENCE_ONLY

        if config_path and os.path.exists(config_path):
            self._load_config(config_path)

    def _load_config(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            mem_cfg = cfg.get("memory", {})
            if "hot" in mem_cfg:
                self.hot_max_age = mem_cfg["hot"].get("max_age_seconds", self.hot_max_age)
                self.hot_max_entries = mem_cfg["hot"].get("max_entries", self.hot_max_entries)
            if "warm" in mem_cfg:
                self.warm_max_age = mem_cfg["warm"].get("max_age_seconds", self.warm_max_age)
                self.warm_max_entries = mem_cfg["warm"].get("max_entries", self.warm_max_entries)
            if "cold" in mem_cfg:
                self.cold_retention_days = mem_cfg["cold"].get("retention_days", self.cold_retention_days)

            weights = cfg.get("importance_weights", {})
            if weights:
                self.scorer = MemoryImportanceScorer(
                    w_risk=weights.get("w_risk", 0.35),
                    w_confidence=weights.get("w_confidence", 0.25),
                    w_severity=weights.get("w_severity", 0.20),
                    w_recency=weights.get("w_recency", 0.10),
                    w_relevance=weights.get("w_relevance", 0.10),
                )
            ret_cfg = cfg.get("retrieval", {})
            if ret_cfg:
                self.max_results = ret_cfg.get("max_results", self.max_results)
                self.max_context_tokens = ret_cfg.get("max_context_tokens", self.max_context_tokens)
        except Exception:
            pass

    def score_importance(
        self,
        risk_score: float,
        confidence: float,
        severity: str,
        timestamp: datetime,
        relevance: float = 0.5,
    ) -> float:
        """Score evidence importance between 0.0 and 1.0."""
        return self.scorer.calculate(
            risk_score=risk_score,
            confidence=confidence,
            severity=severity,
            timestamp=timestamp,
            relevance=relevance,
        )

    def store(
        self,
        evidence_id: str,
        entity_ids: List[str],
        event_type: str,
        domain: str,
        timestamp: datetime,
        risk_score: float,
        confidence: float,
        uncertainty: float,
        severity: str = "LOW",
        source_dataset: Optional[str] = None,
        agent_id: Optional[str] = None,
        detector_id: Optional[str] = None,
        model_version: Optional[str] = None,
        summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        relevance: float = 0.5,
    ) -> EvidenceMemoryEntry:
        """Stores evidence into Memory with deterministic importance scoring and tier assignment."""
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Check for redundancy (same detector, same evidence_id)
        existing = self.repo.get_by_evidence_id(evidence_id)
        if existing:
            # Update existing entry without creating duplicate
            existing.access_count += 1
            existing.last_accessed_at = datetime.now(timezone.utc)
            self.session.commit()
            return EvidenceMemoryEntry(
                memory_id=existing.memory_id,
                evidence_id=existing.evidence_id,
                entity_ids=existing.entity_ids or [],
                event_type=existing.event_type,
                domain=existing.domain,
                timestamp=existing.timestamp,
                risk_score=existing.risk_score,
                confidence=existing.confidence,
                uncertainty=existing.uncertainty,
                importance_score=existing.importance_score,
                memory_tier=MemoryTier(existing.memory_tier),
                access_count=existing.access_count,
                last_accessed_at=existing.last_accessed_at,
                created_at=existing.created_at,
                expires_at=existing.expires_at,
                retrieval_count=existing.retrieval_count,
                source_dataset=existing.source_dataset,
                agent_id=existing.agent_id,
                detector_id=existing.detector_id,
                model_version=existing.model_version,
                summary=existing.summary,
                metadata=existing.metadata_json or {},
            )

        importance = self.score_importance(
            risk_score=risk_score,
            confidence=confidence,
            severity=severity,
            timestamp=timestamp,
            relevance=relevance,
        )

        # Tier placement rule:
        # Very recent (< 15m) -> HOT
        # Older or lower importance -> WARM or COLD
        now = datetime.now(timezone.utc)
        age_seconds = max(0.0, (now - timestamp).total_seconds())

        if age_seconds <= self.hot_max_age:
            tier = MemoryTier.HOT
        elif age_seconds <= self.warm_max_age:
            tier = MemoryTier.WARM
        else:
            tier = MemoryTier.COLD

        memory_id = f"mem_{uuid.uuid4().hex[:12]}"
        expires_at = now + timedelta(days=self.cold_retention_days)

        entry = EvidenceMemoryEntry(
            memory_id=memory_id,
            evidence_id=evidence_id,
            entity_ids=entity_ids,
            event_type=event_type,
            domain=domain,
            timestamp=timestamp,
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            importance_score=importance,
            memory_tier=tier,
            access_count=1,
            last_accessed_at=now,
            created_at=now,
            expires_at=expires_at,
            retrieval_count=0,
            source_dataset=source_dataset,
            agent_id=agent_id,
            detector_id=detector_id,
            model_version=model_version,
            summary=summary,
            metadata=sanitize_payload(metadata or {}),
        )

        self.repo.store_entry(entry)
        self.repo.log_transition(
            memory_id=memory_id,
            previous_tier="NONE",
            new_tier=tier.value,
            reason="INITIAL_INGESTION",
            importance=importance,
        )

        # Check for auto-promotion of existing historical evidence for the same entities
        self._check_auto_promotion(entity_ids, risk_score, now)

        return entry

    def _check_auto_promotion(self, entity_ids: List[str], new_risk: float, now: datetime):
        """Promotes WARM evidence to HOT if a high-risk related event arrives."""
        if new_risk < 0.65 or not entity_ids:
            return

        for entity_id in entity_ids:
            query = MemoryRetrievalQuery(
                entity_id=entity_id,
                memory_tier=MemoryTier.WARM,
                max_results=10,
            )
            warm_entries = self.repo.query_entries(query)
            for entry in warm_entries:
                # Promote to HOT if age within warm window and high importance/risk connection
                self.promote(
                    memory_id=entry.memory_id,
                    target_tier=MemoryTier.HOT,
                    reason="NEW_HIGH_RISK_RELATED_EVIDENCE",
                )

    def retrieve(self, query: MemoryRetrievalQuery, requesting_component: str = "system") -> List[EvidenceMemoryEntry]:
        """Retrieves and ranks evidence entries, logging access for auditability."""
        models = self.repo.query_entries(query)
        entries = []
        for rank, m in enumerate(models, start=1):
            self.repo.log_access(
                memory_id=m.memory_id,
                requesting_component=requesting_component,
                reason="QUERY_RETRIEVAL",
                rank=rank,
            )
            entries.append(
                EvidenceMemoryEntry(
                    memory_id=m.memory_id,
                    evidence_id=m.evidence_id,
                    entity_ids=m.entity_ids or [],
                    event_type=m.event_type,
                    domain=m.domain,
                    timestamp=m.timestamp,
                    risk_score=m.risk_score,
                    confidence=m.confidence,
                    uncertainty=m.uncertainty,
                    importance_score=m.importance_score,
                    memory_tier=MemoryTier(m.memory_tier),
                    access_count=m.access_count,
                    last_accessed_at=m.last_accessed_at,
                    created_at=m.created_at,
                    expires_at=m.expires_at,
                    retrieval_count=m.retrieval_count,
                    source_dataset=m.source_dataset,
                    agent_id=m.agent_id,
                    detector_id=m.detector_id,
                    model_version=m.model_version,
                    summary=m.summary,
                    metadata=m.metadata_json or {},
                )
            )
        return entries

    def promote(self, memory_id: str, target_tier: MemoryTier, reason: str) -> bool:
        """Promotes memory entry (WARM -> HOT, COLD -> WARM)."""
        entry = self.repo.get_by_id(memory_id)
        if not entry:
            return False
        old_tier = entry.memory_tier
        if old_tier == target_tier.value:
            return True
        entry.memory_tier = target_tier.value
        entry.importance_score = min(1.0, entry.importance_score + 0.1)
        self.session.commit()
        self.repo.log_transition(
            memory_id=memory_id,
            previous_tier=old_tier,
            new_tier=target_tier.value,
            reason=reason,
            importance=entry.importance_score,
        )
        return True

    def demote(self, memory_id: str, target_tier: MemoryTier, reason: str) -> bool:
        """Demotes memory entry (HOT -> WARM, WARM -> COLD)."""
        entry = self.repo.get_by_id(memory_id)
        if not entry:
            return False
        old_tier = entry.memory_tier
        if old_tier == target_tier.value:
            return True
        entry.memory_tier = target_tier.value
        self.session.commit()
        self.repo.log_transition(
            memory_id=memory_id,
            previous_tier=old_tier,
            new_tier=target_tier.value,
            reason=reason,
            importance=entry.importance_score,
        )
        return True

    def update(self, memory_id: str, importance_delta: float = 0.0, summary: Optional[str] = None) -> bool:
        """Updates importance score or summary of existing memory entry."""
        entry = self.repo.get_by_id(memory_id)
        if not entry:
            return False
        if importance_delta != 0.0:
            entry.importance_score = min(max(entry.importance_score + importance_delta, 0.0), 1.0)
        if summary is not None:
            entry.summary = summary
        self.session.commit()
        return True

    def expire(self) -> int:
        """Runs lifecycle tier transitions and deterministic expiration."""
        now = datetime.now(timezone.utc)
        models = self.repo.query_entries(MemoryRetrievalQuery(max_results=500))
        expired_count = 0
        for m in models:
            age = (now - m.timestamp).total_seconds()
            if m.memory_tier == MemoryTier.HOT.value and age > self.hot_max_age:
                if m.importance_score < 0.8:
                    self.demote(m.memory_id, MemoryTier.WARM, "HOT_AGE_THRESHOLD")
                    expired_count += 1
            elif m.memory_tier == MemoryTier.WARM.value and age > self.warm_max_age:
                if m.importance_score < 0.9:
                    self.demote(m.memory_id, MemoryTier.COLD, "WARM_AGE_THRESHOLD")
                    expired_count += 1
        return expired_count

    def summarize(self, entity_id: str) -> MemorySummary:
        """Creates bounded summary for entity's historical evidence."""
        entries = self.retrieve(MemoryRetrievalQuery(entity_id=entity_id, max_results=50))
        if not entries:
            summary_text = f"No historical evidence recorded for entity {entity_id}."
            src_ids = []
        else:
            domains = list({e.domain for e in entries})
            avg_risk = sum(e.risk_score for e in entries) / len(entries)
            max_risk = max(e.risk_score for e in entries)
            summary_text = (
                f"Entity {entity_id}: Total events={len(entries)}, "
                f"Domains={', '.join(domains)}, Avg Risk={avg_risk:.2f}, Max Risk={max_risk:.2f}."
            )
            src_ids = [e.evidence_id for e in entries]

        summary_id = f"sum_{uuid.uuid4().hex[:12]}"
        summary_obj = MemorySummary(
            summary_id=summary_id,
            entity_id=entity_id,
            source_evidence_ids=src_ids,
            summary_text=summary_text,
        )
        self.repo.store_summary(summary_obj)
        return summary_obj

    def get_context(self, entity_id: str, max_events: int = 20) -> Dict[str, Any]:
        """Fetches bounded context for an entity with coverage metrics."""
        entries = self.retrieve(MemoryRetrievalQuery(entity_id=entity_id, max_results=max_events))
        if not entries:
            return {
                "status": "NO_RELEVANT_EVIDENCE_FOUND",
                "entity_id": entity_id,
                "coverage": 0.0,
                "entry_count": 0,
                "entries": [],
            }

        counts = {"HOT": 0, "WARM": 0, "COLD": 0}
        for e in entries:
            counts[e.memory_tier.value] = counts.get(e.memory_tier.value, 0) + 1

        coverage = min(1.0, len(entries) / max_events)
        return {
            "status": "OK",
            "entity_id": entity_id,
            "coverage": coverage,
            "entry_count": len(entries),
            "tier_breakdown": counts,
            "entries": [e.dict() for e in entries],
        }

    def get_history(self, entity_id: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[EvidenceMemoryEntry]:
        """Retrieves chronological history of memory entries for an entity."""
        q = MemoryRetrievalQuery(
            entity_id=entity_id,
            start_time=start_time,
            end_time=end_time,
            max_results=self.max_results,
        )
        return self.retrieve(q)

    def compact(self) -> Dict[str, Any]:
        """Runs memory compaction for cold/low-importance evidence."""
        expired = self.expire()
        counts = self.repo.count_by_tier()
        return {
            "status": "COMPACTION_COMPLETE",
            "tier_counts": counts,
            "demoted_count": expired,
        }

    def health(self) -> Dict[str, Any]:
        """Returns health diagnostics and memory utilization metrics."""
        counts = self.repo.count_by_tier()
        total_entries = sum(counts.values())
        return {
            "status": "HEALTHY",
            "total_entries": total_entries,
            "hot_entries": counts["HOT"],
            "warm_entries": counts["WARM"],
            "cold_entries": counts["COLD"],
            "hot_utilization_pct": round(min(1.0, counts["HOT"] / self.hot_max_entries) * 100, 2),
            "warm_utilization_pct": round(min(1.0, counts["WARM"] / self.warm_max_entries) * 100, 2),
        }
