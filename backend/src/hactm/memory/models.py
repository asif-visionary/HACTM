"""
Data structures and models for Adaptive Evidence Memory.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MemoryTier(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"


class ExpirationPolicy(str, Enum):
    DELETE = "DELETE"
    ARCHIVE = "ARCHIVE"
    REFERENCE_ONLY = "REFERENCE_ONLY"


class EvidenceMemoryEntry(BaseModel):
    """Memory entry wrapping SecurityEvidence references with adaptive metadata."""
    memory_id: str
    evidence_id: str
    entity_ids: List[str] = Field(default_factory=list)
    event_type: str
    domain: str
    timestamp: datetime
    risk_score: float
    confidence: float
    uncertainty: float
    importance_score: float = 0.5
    memory_tier: MemoryTier = MemoryTier.HOT
    access_count: int = 0
    last_accessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    retrieval_count: int = 0
    source_dataset: Optional[str] = None
    agent_id: Optional[str] = None
    detector_id: Optional[str] = None
    model_version: Optional[str] = None
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryRetrievalQuery(BaseModel):
    """Filter parameters for historical memory retrieval."""
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    event_type: Optional[str] = None
    domain: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    risk_min: Optional[float] = None
    importance_min: Optional[float] = None
    related_entity: Optional[str] = None
    memory_tier: Optional[MemoryTier] = None
    max_results: int = 100
    max_context_tokens: int = 10000


class MemoryImportanceScorer:
    """Calculates deterministic importance score ∈ [0, 1] for evidence memory placement."""

    def __init__(
        self,
        w_risk: float = 0.35,
        w_confidence: float = 0.25,
        w_severity: float = 0.20,
        w_recency: float = 0.10,
        w_relevance: float = 0.10,
    ):
        self.w_risk = w_risk
        self.w_confidence = w_confidence
        self.w_severity = w_severity
        self.w_recency = w_recency
        self.w_relevance = w_relevance

    def calculate(
        self,
        risk_score: float,
        confidence: float,
        severity: str,
        timestamp: datetime,
        relevance: float = 0.5,
        reference_time: Optional[datetime] = None,
    ) -> float:
        """Computes transparent importance score normalized between 0.0 and 1.0."""
        # Convert severity string to score [0, 1]
        severity_map = {"LOW": 0.25, "MODERATE": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}
        sev_score = severity_map.get(severity.upper() if severity else "LOW", 0.25)

        # Calculate recency decay over 24h (86400s)
        now = reference_time or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age_seconds = max(0.0, (now - timestamp).total_seconds())
        recency_score = max(0.0, 1.0 - (age_seconds / 86400.0))

        raw_score = (
            self.w_risk * min(max(risk_score, 0.0), 1.0)
            + self.w_confidence * min(max(confidence, 0.0), 1.0)
            + self.w_severity * sev_score
            + self.w_recency * recency_score
            + self.w_relevance * min(max(relevance, 0.0), 1.0)
        )
        total_weight = self.w_risk + self.w_confidence + self.w_severity + self.w_recency + self.w_relevance
        normalized = raw_score / total_weight if total_weight > 0 else raw_score
        return round(min(max(normalized, 0.0), 1.0), 4)


class MemorySummary(BaseModel):
    """Summarized historical evidence for memory compaction."""
    summary_id: str
    entity_id: str
    source_evidence_ids: List[str]
    summary_version: str = "1.0.0"
    algorithm_version: str = "1.0.0"
    summary_text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
