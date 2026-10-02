"""
Pydantic Schemas & Enums for Evaluation - Evaluation, Scalability & Research Report Generation.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ResultStatus(str, Enum):
    COMPLETED = "COMPLETED"
    NOT_RUN = "NOT_RUN"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class RunStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReportStatus(str, Enum):
    QUEUED = "QUEUED"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReportFormat(str, Enum):
    PDF = "PDF"
    JSON = "JSON"
    CSV = "CSV"


class SplitStrategy(str, Enum):
    RANDOM_SPLIT = "RANDOM_SPLIT"
    STRATIFIED_SPLIT = "STRATIFIED_SPLIT"
    TIME_AWARE_SPLIT = "TIME_AWARE_SPLIT"
    CROSS_SESSION_SPLIT = "CROSS_SESSION_SPLIT"
    CROSS_DATASET_SPLIT = "CROSS_DATASET_SPLIT"


class SegmentationMode(str, Enum):
    NO_SEGMENTATION = "NO_SEGMENTATION"
    STATIC_SEGMENTATION = "STATIC_SEGMENTATION"
    DYNAMIC_SEGMENTATION = "DYNAMIC_SEGMENTATION"


class EvaluationDataset(BaseModel):
    dataset_id: str
    dataset_name: str
    version: str
    domain: str  # NETWORK, PHISHING, UBA, IDENTITY, TRANSACTION, CROSS_DOMAIN
    source: str
    license: str = "OPEN_RESEARCH"
    collection_period: Optional[str] = None
    sample_count: int
    split_strategy: SplitStrategy = SplitStrategy.TIME_AWARE_SPLIT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExperimentConfig(BaseModel):
    experiment_id: str
    experiment_name: str
    dataset_id: str
    dataset_version: str
    workload_size: int
    seed: int = 42
    system_version: str = "1.0.0"
    agent_versions: Dict[str, str] = Field(default_factory=dict)
    model_versions: Dict[str, str] = Field(default_factory=dict)
    policy_versions: Dict[str, str] = Field(default_factory=dict)
    configuration_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExperimentRun(BaseModel):
    run_id: str
    experiment_id: str
    status: RunStatus = RunStatus.QUEUED
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    environment: Dict[str, Any] = Field(default_factory=dict)
    host_information: Dict[str, Any] = Field(default_factory=dict)
    metrics_summary: Dict[str, Any] = Field(default_factory=dict)
    artifacts_path: Optional[str] = None
    error_log: Optional[str] = None


class MetricResult(BaseModel):
    metric_id: str
    run_id: str
    domain: str
    metric_name: str
    metric_value: Optional[float] = None
    metric_unit: str
    status: ResultStatus = ResultStatus.COMPLETED
    formula_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaselineResult(BaseModel):
    baseline_id: str
    run_id: str
    baseline_name: str
    f1_score: Optional[float] = None
    fpr: Optional[float] = None
    fnr: Optional[float] = None
    ece: Optional[float] = None
    brier_score: Optional[float] = None
    agent_invocations: Optional[int] = None
    latency_ms: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AblationResult(BaseModel):
    ablation_id: str
    run_id: str
    ablation_name: str
    removed_component: str
    f1_score: Optional[float] = None
    ece: Optional[float] = None
    policy_churn: Optional[float] = None
    stability_status: str
    delta_from_full_system: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ScalabilityResult(BaseModel):
    result_id: str
    run_id: str
    workload_size: int
    events_per_sec: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    cpu_percent: float
    ram_mb: float
    storage_mb: float
    agent_calls: int
    scaling_efficiency: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SegmentationResult(BaseModel):
    result_id: str
    run_id: str
    segmentation_mode: SegmentationMode
    blast_radius_score: float
    lateral_reachability_nodes: int
    containment_time_ms: Optional[float] = None
    false_isolation_rate: float
    policy_violation_rate: float
    enforcement_latency_ms: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationReport(BaseModel):
    report_id: str
    title: str
    experiment_id: str
    format: ReportFormat
    status: ReportStatus = ReportStatus.QUEUED
    artifact_path: Optional[str] = None
    summary_metrics: Dict[str, Any] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)
    reproducibility_checksum: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
