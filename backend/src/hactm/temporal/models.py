"""
Data structures and models for Temporal Evidence Engine.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TemporalRelationshipType(str, Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    SIMULTANEOUS = "SIMULTANEOUS"
    WITHIN_WINDOW = "WITHIN_WINDOW"
    REPEATED = "REPEATED"
    BURST = "BURST"
    GAP = "GAP"
    LONG_TERM_PATTERN = "LONG_TERM_PATTERN"


class TemporalRelationship(BaseModel):
    """Pairwise temporal relationship between two security evidence records."""
    relationship_id: str
    source_evidence_id: str
    target_evidence_id: str
    relationship_type: TemporalRelationshipType
    time_difference_seconds: float
    confidence: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TemporalRevision(BaseModel):
    """Late-arriving event revision log preventing silent mutation of historical assessments."""
    revision_id: str
    previous_result_id: str
    new_event_id: str
    revision_reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SequencePatternMatch(BaseModel):
    """Detected temporal sequence of events across domains."""
    sequence_id: str
    entity_id: str
    event_ids: List[str]
    domains: List[str]
    time_span_seconds: float
    pattern_name: str
    confidence: float
    is_cross_session: bool = False
