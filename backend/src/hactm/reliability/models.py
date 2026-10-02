"""
Pydantic Data Models and Schemas for Reliability & Trust:
Reliability, Uncertainty, Calibration, Agent Reputation, Evidence Quality, and Drift Awareness.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ReliabilityStatus(str, Enum):
    WELL_SUPPORTED = "WELL_SUPPORTED"
    LIMITED_EVIDENCE = "LIMITED_EVIDENCE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    DRIFT_OBSERVED = "DRIFT_OBSERVED"
    CALIBRATION_REQUIRED = "CALIBRATION_REQUIRED"


class DriftPolicyAction(str, Enum):
    IGNORE = "IGNORE"
    MONITOR = "MONITOR"
    PENALIZE_RELIABILITY = "PENALIZE_RELIABILITY"
    REQUIRE_RECALIBRATION = "REQUIRE_RECALIBRATION"


class DriftSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReliabilityConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "precision": 0.25,
            "recall": 0.20,
            "f1": 0.15,
            "calibration_error": 0.15,
            "uncertainty_quality": 0.10,
            "stability": 0.10,
            "drift_penalty": 0.05,
        }
    )
    minimum_sample_threshold: int = Field(10, description="Minimum samples required before marking as WELL_SUPPORTED")
    smoothing_method: str = Field("laplace", description="laplace or additive")
    smoothing_alpha: float = Field(1.0, description="Smoothing parameter")
    confidence_interval_method: str = Field("wilson", description="wilson, bootstrap, or bayesian")
    confidence_level: float = Field(0.95, description="CI confidence level (e.g. 0.95 for 95%)")
    freshness_decay_lambda: float = Field(0.001, description="Decay rate per hour")
    stability_weighting: float = Field(0.15, description="Weight of temporal stability in score")
    calibration_weighting: float = Field(0.20, description="Weight of calibration error penalty")
    drift_penalty_weight: float = Field(0.25, description="Penalty coefficient when drift is detected")
    domain_weighting: float = Field(0.10, description="Weight for domain specificity vs global")
    minimum_reliability_floor: float = Field(0.05, description="Absolute lower bound on reliability score")
    maximum_reliability_ceiling: float = Field(0.99, description="Absolute upper bound on reliability score")
    version: str = Field("1.0.0", description="Reliability model version")


class AgentReliabilityRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reliability_id: str
    agent_id: str
    detector_id: Optional[str] = None
    domain: Optional[str] = None
    model_version: str = "1.0.0"
    evaluation_window_start: datetime
    evaluation_window_end: datetime
    sample_count: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    calibration_error: float = 0.0
    uncertainty_quality: float = 0.0
    stability_score: float = 1.0
    drift_score: float = 0.0
    reliability_score: float = 0.5
    confidence_interval_lower: float = 0.0
    confidence_interval_upper: float = 1.0
    evaluation_dataset: Optional[str] = "synthetic_eval_v1"
    evaluation_method: str = "empirical_validation"
    reliability_status: ReliabilityStatus = ReliabilityStatus.WELL_SUPPORTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceUncertainty(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uncertainty_id: str
    evidence_id: str
    agent_id: str
    detector_id: Optional[str] = None
    uncertainty_score: float = Field(..., ge=0.0, le=1.0)
    uncertainty_type: str = Field("PROXY", description="ALEATORIC, EPISTEMIC, DISAGREEMENT, INCOMPLETENESS, OOD, PROXY")
    source: Optional[str] = None
    calculation_method: str = "entropy_disagreement_composite"
    contributing_factors: Dict[str, Any] = Field(default_factory=dict)
    model_version: Optional[str] = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CalibrationRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    calibration_id: str
    agent_id: str
    detector_id: Optional[str] = None
    model_version: str = "1.0.0"
    dataset: Optional[str] = "synthetic_eval_v1"
    evaluation_window_start: datetime
    evaluation_window_end: datetime
    sample_count: int = 0
    ece: float = 0.0
    mce: float = 0.0
    brier_score: float = 0.0
    calibration_method: str = "temperature_scaling"
    pre_calibration_metric: Optional[float] = None
    post_calibration_metric: Optional[float] = None
    calibration_parameters: Dict[str, Any] = Field(default_factory=dict)
    reliability_diagram_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceQuality(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quality_id: str
    evidence_id: str
    quality_score: float = Field(..., ge=0.0, le=1.0)
    completeness_score: float = Field(1.0, ge=0.0, le=1.0)
    validity_score: float = Field(1.0, ge=0.0, le=1.0)
    freshness_score: float = Field(1.0, ge=0.0, le=1.0)
    consistency_score: float = Field(1.0, ge=0.0, le=1.0)
    relevance_score: float = Field(1.0, ge=0.0, le=1.0)
    source_quality_score: float = Field(1.0, ge=0.0, le=1.0)
    missing_fields: List[str] = Field(default_factory=list)
    quality_flags: List[str] = Field(default_factory=list)
    assessment_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DriftRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    drift_id: str
    agent_id: str
    detector_id: Optional[str] = None
    feature_or_signal: str
    reference_window_start: datetime
    reference_window_end: datetime
    current_window_start: datetime
    current_window_end: datetime
    drift_method: str = "PSI"
    drift_score: float = 0.0
    threshold: float = 0.20
    drift_detected: bool = False
    severity: DriftSeverity = DriftSeverity.LOW
    model_version: Optional[str] = "1.0.0"
    policy_action: DriftPolicyAction = DriftPolicyAction.MONITOR
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DetectorDisagreement(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    disagreement_id: str
    event_id: str
    entity_id: str
    detector_count: int
    participating_detectors: List[str]
    risk_scores: Dict[str, float]
    confidence_scores: Dict[str, float]
    risk_variance: float
    confidence_variance: float
    categorical_disagreement: bool
    disagreement_score: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConflictRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conflict_id: str
    evidence_ids: List[str]
    entity_id: str
    conflict_type: str
    risk_range: Dict[str, float] = Field(default_factory=dict)
    disagreement_score: float = 0.0
    likely_causes: List[str] = Field(default_factory=list)
    resolution_status: str = "OPEN"
    resolution_method: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentReputation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    reputation_score: float = Field(0.8, ge=0.0, le=1.0)
    historical_precision: float = 0.8
    historical_recall: float = 0.8
    stability_score: float = 1.0
    calibration_score: float = 0.9
    drift_score: float = 0.0
    coverage_score: float = 1.0
    last_evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evaluation_count: int = 0
    confidence_interval_lower: float = 0.7
    confidence_interval_upper: float = 0.9
    reputation_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MissingEvidenceRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: str
    entity_id: str
    expected_agent: str
    expected_domain: str
    missing_agent: str
    reason: str = "No telemetry received in evaluation window"
    window_start: datetime
    window_end: datetime
    coverage_impact: float = 0.25
    coverage_gap: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReliabilityEvaluation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evaluation_id: str
    evaluation_type: str
    agent_id: Optional[str] = None
    detector_id: Optional[str] = None
    dataset: Optional[str] = "synthetic_eval_v1"
    dataset_version: Optional[str] = "1.0.0"
    evaluation_window_start: Optional[datetime] = None
    evaluation_window_end: Optional[datetime] = None
    sample_count: int = 0
    results_summary: Dict[str, Any] = Field(default_factory=dict)
    configuration_version: str = "1.0.0"
    environment_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
