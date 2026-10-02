"""
API Schemas for Evidence and Entity endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hactm.core.constants import SeverityLevel, EntityType


class EvidenceResponse(BaseModel):
    event_id: str
    agent_id: str
    entity_id: str
    event_type: str
    timestamp: datetime
    risk_score: float
    confidence: float
    uncertainty: float
    severity: str
    evidence: Dict[str, Any]

    source: Optional[str] = None
    source_type: Optional[str] = None
    dataset: Optional[str] = None
    dataset_name: Optional[str] = None
    dataset_version: Optional[str] = None
    schema_version: Optional[str] = "1.0.0"
    preprocessing_version: Optional[str] = "1.0.0"
    source_record_id: Optional[str] = None
    ingestion_run_id: Optional[str] = None

    security_tags: List[str] = Field(default_factory=list)
    security_group: Optional[str] = None
    security_zone: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Future phase extension placeholders
    calibrated_probability: Optional[float] = None
    agent_reliability: Optional[float] = None
    evidence_quality: Optional[float] = None
    recommended_action: Optional[str] = None

    class Config:
        from_attributes = True


class EntityResponse(BaseModel):
    entity_id: str
    entity_type: str
    canonical_name: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    first_seen: datetime
    last_seen: datetime
    event_count: int

    class Config:
        from_attributes = True


class EntityDetailResponse(EntityResponse):
    associated_evidence: List[EvidenceResponse] = Field(default_factory=list)


class IngestionRequest(BaseModel):
    file_path: Optional[str] = Field(None, description="Path to .csv, .json, or .jsonl file")
    records: Optional[List[Dict[str, Any]]] = Field(None, description="Inline list of records to ingest")
    source_name: Optional[str] = Field("api_payload", description="Name of the source or dataset")
    policy: str = Field("QUARANTINE_INVALID", description="STRICT, SKIP_INVALID, or QUARANTINE_INVALID")
    batch_size: int = Field(1000, ge=1, le=50000, description="Batch processing size")
    dataset_name: Optional[str] = None


class IngestionRunResponse(BaseModel):
    run_id: str
    source_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    total_records: int
    inserted: int
    duplicates: int
    invalid: int
    quarantined: int
    failed: int
    policy: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class MetricsOverviewResponse(BaseModel):
    total_events: int
    total_entities: int
    high_risk_events: int
    ingestion_health_pct: float
    risk_distribution: Dict[str, int]


class ReportRequest(BaseModel):
    entity_id: Optional[str] = None
    event_type: Optional[str] = None
    source: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_risk: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum cyber risk threshold between 0.0 and 1.0")


class ReportResponse(BaseModel):
    report_id: str = Field(..., description="Unique evidence report identifier")
    title: str = "Structured Security Evidence Report"
    generated_at: datetime
    filters: Dict[str, Any]
    summary: Dict[str, Any]
    evidence_count: int
    records: List[EvidenceResponse]
