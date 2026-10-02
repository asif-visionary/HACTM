"""
Pydantic Schemas for Research Validation Validation & Publication Readiness.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    INCOMPLETE = "INCOMPLETE"
    INCONSISTENT = "INCONSISTENT"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class ClaimStatus(str, Enum):
    DIRECTLY_SUPPORTED = "DIRECTLY_SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    NOT_TESTED = "NOT_TESTED"
    CONTRADICTED = "CONTRADICTED"


class AuditStatus(str, Enum):
    SECURITY_PASS = "SECURITY_PASS"
    SECURITY_WARNINGS = "SECURITY_WARNINGS"
    SECURITY_FAILURE = "SECURITY_FAILURE"


class ReproducibilityStatus(str, Enum):
    REPRODUCED = "REPRODUCED"
    PARTIALLY_REPRODUCED = "PARTIALLY_REPRODUCED"
    FAILED = "FAILED"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"


class HypothesisStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    NOT_TESTED = "NOT_TESTED"


# 1. Result Integrity Validation Models
class ResultIntegrityCheckRequest(BaseModel):
    experiment_id: str
    run_id: str
    dataset_id: str
    dataset_version: str
    config_hash: str
    model_versions: Dict[str, str] = Field(default_factory=dict)
    code_version: str = "1.0.0"
    timestamp: str
    random_seed: int = 42
    environment_id: str = "env-default"
    metrics: Dict[str, float] = Field(default_factory=dict)
    sample_counts: Dict[str, int] = Field(default_factory=dict)


class ResultIntegrityCheckResponse(BaseModel):
    validation_id: str
    experiment_id: str
    run_id: str
    status: ValidationStatus
    issues: List[str] = Field(default_factory=list)
    validated_metrics: Dict[str, float] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# 2. Statistical Validation Models
class DescriptiveStats(BaseModel):
    metric: str
    sample_size: int
    mean: float
    median: float
    std_dev: float
    variance: float
    min_val: float
    max_val: float
    iqr: float
    p50: float
    p90: float
    p95: float
    p99: float


class ConfidenceIntervalResult(BaseModel):
    metric: str
    sample_size: int
    estimate: float
    confidence_level: float = 0.95
    lower_bound: float
    upper_bound: float
    method: str = "bootstrap"


class PairedAnalysisResult(BaseModel):
    test_name: str
    metric: str
    baseline: float
    proposed_method: float
    sample_size: int
    statistic: float
    p_value: float
    effect_size: float
    confidence_interval: List[float]
    assumptions: List[str]


class EffectSizeResult(BaseModel):
    metric: str
    baseline: float
    proposed: float
    cohens_d: Optional[float] = None
    cliffs_delta: Optional[float] = None
    absolute_difference: float
    relative_change: Optional[float] = None


class MultipleComparisonResult(BaseModel):
    comparison_family: str
    correction_method: str # Bonferroni, Benjamini-Hochberg
    raw_p_values: Dict[str, float]
    adjusted_p_values: Dict[str, float]


class StatisticalValidationResponse(BaseModel):
    experiment_id: str
    descriptive_stats: List[DescriptiveStats]
    confidence_intervals: List[ConfidenceIntervalResult]
    paired_analyses: List[PairedAnalysisResult] = Field(default_factory=list)
    effect_sizes: List[EffectSizeResult] = Field(default_factory=list)
    multiple_comparison: Optional[MultipleComparisonResult] = None


# 3. Sensitivity & Robustness Models
class SensitivityItem(BaseModel):
    parameter_name: str
    category: str
    original_value: float
    tested_value: float
    metric: str
    baseline_result: float
    perturbed_result: float
    absolute_change: float
    relative_change: float


class SensitivityAnalysisResponse(BaseModel):
    experiment_id: str
    total_evaluations: int
    sensitivity_items: List[SensitivityItem]


class RobustnessItem(BaseModel):
    perturbation_type: str
    category: str # INPUT_NOISE, EVIDENCE_DEGRADATION, OPERATIONAL_DEGRADATION
    metric: str
    baseline_metric: float
    perturbed_metric: float
    absolute_change: float
    relative_change: float
    degradation_percentage: float


class RobustnessAnalysisResponse(BaseModel):
    experiment_id: str
    robustness_items: List[RobustnessItem]


# 4. Cross-Dataset / Cross-Scenario / Cross-Session / Temporal Validation Models
class CrossDatasetItem(BaseModel):
    training_dataset: str
    validation_dataset: str
    test_dataset: str
    feature_schema: str
    model_version: str
    performance_f1: float
    performance_drop: float
    applicability: str # APPLICABLE, NOT_APPLICABLE
    applicability_reason: Optional[str] = None


class CrossDatasetResponse(BaseModel):
    results: List[CrossDatasetItem]


class CrossSessionItem(BaseModel):
    mode: str # SESSION_LOCAL, FIXED_HISTORICAL, ADAPTIVE_EVIDENCE_MEMORY
    cross_session_detection_f1: float
    context_completeness: float
    memory_hit_rate: float
    false_correlation_rate: float
    retrieval_latency_ms: float
    graph_query_latency_ms: float


class CrossSessionResponse(BaseModel):
    results: List[CrossSessionItem]


class TemporalValidationResponse(BaseModel):
    train_period: str
    test_period: str
    temporal_performance_f1: float
    performance_degradation: float
    drift_indicator: float
    calibration_degradation: float
    temporal_leakage_prevented: bool = True


# 5. Hypotheses & Claims Models
class HypothesisItem(BaseModel):
    hypothesis_id: str # H1..H9
    title: str
    description: str
    supporting_experiments: List[str]
    measured_metrics: Dict[str, float]
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    status: HypothesisStatus
    reasoning: str


class HypothesesResponse(BaseModel):
    hypotheses: List[HypothesisItem]


class ResearchClaimItem(BaseModel):
    claim_id: str
    claim_text: str
    category: str
    supporting_experiments: List[str]
    status: ClaimStatus
    evidence_details: Dict[str, Any]
    limitations: List[str]


class ClaimValidationRequest(BaseModel):
    claims: List[str]


class ClaimValidationResponse(BaseModel):
    validated_claims: List[ResearchClaimItem]


# 6. Threats to Validity Models
class ThreatsToValidityResponse(BaseModel):
    internal_validity: List[str]
    external_validity: List[str]
    construct_validity: List[str]
    statistical_conclusion_validity: List[str]


# 7. Reproducibility & Environment Capture Models
class EnvironmentMetadata(BaseModel):
    python_version: str
    os_info: str
    cpu_info: Dict[str, Any]
    memory_info: Dict[str, Any]
    gpu_info: Dict[str, Any]
    installed_packages_count: int
    environment_hash: str


class DatasetManifestItem(BaseModel):
    dataset_id: str
    version: str
    source: str
    acquisition_date: str
    checksum: str
    license: str
    preprocessing_version: str
    feature_schema: str


class ReproducibilityReport(BaseModel):
    reproducibility_id: str
    status: ReproducibilityStatus
    config_hash: str
    environment: EnvironmentMetadata
    datasets_manifest: List[DatasetManifestItem]
    seed_reproducible: bool
    notes: str


# 8. Security & Ethics Audit Models
class SecurityAuditResponse(BaseModel):
    audit_id: str
    status: AuditStatus
    data_findings: List[str]
    code_findings: List[str]
    report_findings: List[str]
    checked_items: Dict[str, bool]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# 9. Provenance & Traceability Models
class ProvenanceNode(BaseModel):
    node_id: str
    node_type: str # DATASET, PREPROCESSING, MODEL, CONFIG, EXPERIMENT, RUN, METRICS, STATS, FIGURE_TABLE, CLAIM
    details: Dict[str, Any]
    children: List[str] = Field(default_factory=list)


class ResearchProvenanceGraph(BaseModel):
    nodes: Dict[str, ProvenanceNode]
    root_datasets: List[str]


class TraceabilityMatrixItem(BaseModel):
    requirement_id: str
    requirement_name: str
    implementation_component: str
    experiment_id: str
    metric: str
    result_summary: str
    claim_id: str


class TraceabilityMatrixResponse(BaseModel):
    items: List[TraceabilityMatrixItem]


# 10. Publication & Readiness Models
class PublicationGenerateRequest(BaseModel):
    title: str = "HACTM: Hierarchical Adaptive Cyber Trust Mesh for Heterogeneous Security Evidence Orchestration"
    authors: List[str] = Field(default_factory=lambda: ["HACTM Research Group"])
    include_latex: bool = True
    include_markdown: bool = True
    include_bibtex: bool = True


class PublicationGenerateResponse(BaseModel):
    package_id: str
    manuscript_md_path: str
    manuscript_tex_path: Optional[str] = None
    references_bib_path: str
    figures_generated: List[str]
    tables_generated: List[str]
    research_bundle_path: str
    checksum: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PublicationReadinessDimension(BaseModel):
    name: str
    status: str # COMPLETE, PARTIAL, INCOMPLETE, NOT_APPLICABLE
    details: str


class PublicationReadinessResponse(BaseModel):
    dimensions: List[PublicationReadinessDimension]
    experiments_completed: int
    experiments_failed: int
    experiments_partial: int
    results_validated: int
    hypotheses_evaluated: int
    claims_validated: int
    reproducibility_status: ReproducibilityStatus
    security_audit_status: AuditStatus
