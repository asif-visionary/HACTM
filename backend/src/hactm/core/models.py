"""
Core Domain Schemas for HACTM.
Includes the canonical SecurityEvidence, Event, Entity, and Ingestion models.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from hactm.core.constants import (
    MAX_CONFIDENCE_SCORE,
    MAX_RISK_SCORE,
    MAX_UNCERTAINTY_SCORE,
    MIN_CONFIDENCE_SCORE,
    MIN_RISK_SCORE,
    MIN_UNCERTAINTY_SCORE,
    PREPROCESSING_VERSION,
    SCHEMA_VERSION,
    EntityType,
    SeverityLevel,
    risk_score_to_severity,
)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class SecurityEvidence(BaseModel):
    """
    Common SecurityEvidence Data Model.
    Foundation canonical evidence contract for HACTM.
    """
    # Required Fields
    event_id: str = Field(..., min_length=1, description="Unique identifier for the security event")
    agent_id: str = Field(..., min_length=1, description="Identifier of the emitting or source agent/loader")
    entity_id: str = Field(..., min_length=1, description="Canonical resolved entity identifier")
    event_type: str = Field(..., min_length=1, description="Type of cyber security event (e.g. NETWORK, AUTHENTICATION)")
    timestamp: datetime = Field(..., description="UTC timestamp of the observed event")
    risk_score: float = Field(
        ...,
        ge=MIN_RISK_SCORE,
        le=MAX_RISK_SCORE,
        description="Cyber Risk Score: 0.0 (lowest risk/benign) to 1.0 (highest risk/critical anomaly)"
    )
    confidence: float = Field(
        ...,
        ge=MIN_CONFIDENCE_SCORE,
        le=MAX_CONFIDENCE_SCORE,
        description="Confidence score: 0.0 to 1.0"
    )
    uncertainty: float = Field(
        ...,
        ge=MIN_UNCERTAINTY_SCORE,
        le=MAX_UNCERTAINTY_SCORE,
        description="Uncertainty metric: 0.0 to 1.0"
    )
    evidence: Dict[str, Any] = Field(
        ...,
        description="Structured dictionary of evidentiary parameters and telemetry"
    )

    # Optional Fields
    source: Optional[str] = Field(None, description="Data source name (e.g., CIC-IDS2017, Syslog)")
    source_type: Optional[str] = Field(None, description="Type of data source (e.g. CSV, PCAP, API)")
    dataset: Optional[str] = Field(None, description="Dataset group or repository name")
    event_category: Optional[str] = Field(None, description="Detailed sub-category")
    severity: Optional[SeverityLevel] = Field(None, description="Mapped severity level: LOW, MEDIUM, HIGH, CRITICAL")
    raw_event_id: Optional[str] = Field(None, description="Original event ID from source")
    parent_event_id: Optional[str] = Field(None, description="Upstream parent event identifier")
    session_id: Optional[str] = Field(None, description="User or connection session ID")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier across telemetry")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Future-Phase Extension Placeholders (MUST NOT be fabricated in Foundation)
    calibrated_probability: Optional[float] = Field(None, description="Reserved for Reliability & Trust calibration")
    agent_reliability: Optional[float] = Field(None, description="Reserved for Reliability & Trust reliability")
    evidence_quality: Optional[float] = Field(None, description="Reserved for Reliability & Trust quality assessment")
    recommended_action: Optional[str] = Field(None, description="Reserved for Zero-Trust Engine enforcement")

    # Research Reproducibility & Lineage
    dataset_name: Optional[str] = Field(None, description="Lineage: Name of ingested dataset")
    dataset_version: Optional[str] = Field(None, description="Lineage: Version of source dataset")
    schema_version: str = Field(default=SCHEMA_VERSION, description="Lineage: SecurityEvidence schema version")
    preprocessing_version: str = Field(default=PREPROCESSING_VERSION, description="Lineage: Preprocessing version")
    source_record_id: Optional[str] = Field(None, description="Lineage: Specific row or index in source file")
    ingestion_run_id: Optional[str] = Field(None, description="Lineage: ID of ingestion batch run")

    # Security Context
    security_tags: List[str] = Field(default_factory=list, description="Security contextual tags")
    security_group: Optional[str] = Field(None, description="Logical security group")
    security_zone: Optional[str] = Field(None, description="Network or asset zone (e.g., DMZ, Internal)")

    @field_validator("timestamp", "created_at", "updated_at", mode="before")
    @classmethod
    def validate_utc_timestamps(cls, v: Any) -> Any:
        if isinstance(v, str):
            from dateutil import parser
            dt = parser.parse(v)
            return ensure_utc(dt)
        if isinstance(v, datetime):
            return ensure_utc(v)
        return v

    @model_validator(mode="after")
    def populate_defaults_and_severity(self) -> "SecurityEvidence":
        if self.severity is None:
            self.severity = risk_score_to_severity(self.risk_score)
        if self.dataset and not self.dataset_name:
            self.dataset_name = self.dataset
        return self


class Entity(BaseModel):
    """
    Resolved Entity model in HACTM.
    Deterministic representation of an actor, host, IP, or account.
    """
    entity_id: str = Field(..., min_length=1, description="Deterministic canonical entity identifier")
    entity_type: EntityType = Field(default=EntityType.UNKNOWN, description="Classified entity category")
    canonical_name: str = Field(..., description="Human or system readable canonical name")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata and canonical attributes")
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_count: int = Field(default=1, ge=0, description="Total evidence events associated with entity")

    @field_validator("first_seen", "last_seen", mode="before")
    @classmethod
    def validate_utc(cls, v: Any) -> Any:
        if isinstance(v, str):
            from dateutil import parser
            dt = parser.parse(v)
            return ensure_utc(dt)
        if isinstance(v, datetime):
            return ensure_utc(v)
        return v


class Event(BaseModel):
    """
    Simplified Event model corresponding to the ingested security event telemetry.
    """
    event_id: str
    entity_id: str
    event_type: str
    timestamp: datetime
    source: Optional[str] = None
    risk_score: float
    severity: SeverityLevel
    raw_data: Optional[Dict[str, Any]] = None


class IngestionResult(BaseModel):
    """
    Idempotent batch ingestion summary response.
    """
    run_id: str
    inserted: int = 0
    duplicates: int = 0
    invalid: int = 0
    quarantined: int = 0
    failed: int = 0
    total: int = 0
