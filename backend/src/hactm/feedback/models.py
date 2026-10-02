"""
Pydantic Schemas & Enums for Closed-Loop Adaptation - Closed-Loop Cyber Trust Feedback & Continuous Adaptation.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ObservedOutcome(str, Enum):
    ACCESS_LEGITIMATE = "ACCESS_LEGITIMATE"
    ACCESS_UNAUTHORIZED = "ACCESS_UNAUTHORIZED"
    ATTACK_CONFIRMED = "ATTACK_CONFIRMED"
    ATTACK_NOT_CONFIRMED = "ATTACK_NOT_CONFIRMED"
    PHISHING_CONFIRMED = "PHISHING_CONFIRMED"
    PHISHING_NOT_CONFIRMED = "PHISHING_NOT_CONFIRMED"
    ACCOUNT_COMPROMISE_CONFIRMED = "ACCOUNT_COMPROMISE_CONFIRMED"
    TRANSACTION_FRAUD_CONFIRMED = "TRANSACTION_FRAUD_CONFIRMED"
    FALSE_ALARM = "FALSE_ALARM"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    UNKNOWN = "UNKNOWN"


class ValidationStatus(str, Enum):
    PENDING = "PENDING"
    VALIDATED_TRUE_POSITIVE = "VALIDATED_TRUE_POSITIVE"
    VALIDATED_FALSE_POSITIVE = "VALIDATED_FALSE_POSITIVE"
    VALIDATED_TRUE_NEGATIVE = "VALIDATED_TRUE_NEGATIVE"
    VALIDATED_FALSE_NEGATIVE = "VALIDATED_FALSE_NEGATIVE"
    PARTIALLY_VALIDATED = "PARTIALLY_VALIDATED"
    UNRESOLVED = "UNRESOLVED"
    ANALYST_CONFIRMED = "ANALYST_CONFIRMED"
    GROUND_TRUTH_CONFIRMED = "GROUND_TRUTH_CONFIRMED"
    FEEDBACK_CONFLICT = "FEEDBACK_CONFLICT"
    RETRACTED = "RETRACTED"


class FeedbackSourceType(str, Enum):
    GROUND_TRUTH_DATASET = "GROUND_TRUTH_DATASET"
    CONTROLLED_EXPERIMENT = "CONTROLLED_EXPERIMENT"
    ANALYST_VALIDATION = "ANALYST_VALIDATION"
    INCIDENT_INVESTIGATION = "INCIDENT_INVESTIGATION"
    SUCCESSFUL_2FA = "SUCCESSFUL_2FA"
    FAILED_2FA = "FAILED_2FA"
    CONFIRMED_PHISHING_REPORT = "CONFIRMED_PHISHING_REPORT"
    CONFIRMED_ACCOUNT_COMPROMISE = "CONFIRMED_ACCOUNT_COMPROMISE"
    CONFIRMED_TRANSACTION_FRAUD = "CONFIRMED_TRANSACTION_FRAUD"
    CONFIRMED_NETWORK_ATTACK = "CONFIRMED_NETWORK_ATTACK"
    VERIFIED_POLICY_VIOLATION = "VERIFIED_POLICY_VIOLATION"
    CONTROLLED_ATTACK_EXPERIMENT = "CONTROLLED_ATTACK_EXPERIMENT"
    SECURITY_TEST_ENVIRONMENT = "SECURITY_TEST_ENVIRONMENT"


class FeedbackTrustLevel(str, Enum):
    GROUND_TRUTH = "GROUND_TRUTH"
    CONTROLLED_EXPERIMENT = "CONTROLLED_EXPERIMENT"
    ANALYST_CONFIRMED = "ANALYST_CONFIRMED"
    MULTI_SOURCE_VALIDATED = "MULTI_SOURCE_VALIDATED"
    SINGLE_SOURCE = "SINGLE_SOURCE"
    UNRESOLVED = "UNRESOLVED"


class FeedbackType(str, Enum):
    DETECTION_FEEDBACK = "DETECTION_FEEDBACK"
    AGENT_FEEDBACK = "AGENT_FEEDBACK"
    POLICY_FEEDBACK = "POLICY_FEEDBACK"
    VERIFICATION_FEEDBACK = "VERIFICATION_FEEDBACK"
    SEGMENTATION_FEEDBACK = "SEGMENTATION_FEEDBACK"
    INCIDENT_FEEDBACK = "INCIDENT_FEEDBACK"
    ANALYST_FEEDBACK = "ANALYST_FEEDBACK"
    DATASET_FEEDBACK = "DATASET_FEEDBACK"
    DRIFT_FEEDBACK = "DRIFT_FEEDBACK"


class AdaptationMode(str, Enum):
    STATIC = "STATIC"
    OBSERVE = "OBSERVE"
    ADVISORY = "ADVISORY"
    SHADOW = "SHADOW"
    CONTROLLED = "CONTROLLED"
    ACTIVE = "ACTIVE"


class ApprovalStatus(str, Enum):
    PROPOSED = "PROPOSED"
    AUTO_APPROVED = "AUTO_APPROVED"
    ANALYST_APPROVED = "ANALYST_APPROVED"
    EXPERIMENT_APPROVED = "EXPERIMENT_APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    ROLLED_BACK = "ROLLED_BACK"


class ModelRegistryStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    SHADOW = "SHADOW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class DriftResponseAction(str, Enum):
    NO_ACTION = "NO_ACTION"
    MONITOR = "MONITOR"
    RECALIBRATE = "RECALIBRATE"
    REVIEW_FEATURES = "REVIEW_FEATURES"
    RETRAIN_CANDIDATE = "RETRAIN_CANDIDATE"
    ROLLBACK_MODEL = "ROLLBACK_MODEL"
    REDUCE_AGENT_INFLUENCE = "REDUCE_AGENT_INFLUENCE"
    REQUIRE_VALIDATION = "REQUIRE_VALIDATION"


class SecurityDecisionOutcome(BaseModel):
    outcome_id: str
    decision_id: str
    subject_id: str
    resource_id: Optional[str] = None
    original_decision: str
    observed_outcome: ObservedOutcome
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validation_source: Optional[str] = None
    validation_confidence: float = 1.0
    analyst_id: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    incident_id: Optional[str] = None
    ground_truth_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    validated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeedbackEvent(BaseModel):
    feedback_id: str
    source_type: FeedbackSourceType
    source_id: str
    event_type: FeedbackType
    subject_id: Optional[str] = None
    decision_id: Optional[str] = None
    outcome_id: Optional[str] = None
    agent_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    policy_ids: List[str] = Field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.PENDING
    trust_level: FeedbackTrustLevel = FeedbackTrustLevel.UNRESOLVED
    quality_score: float = 0.0
    feedback_weight: float = 1.0
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FeedbackQuality(BaseModel):
    source_reliability: float = Field(ge=0.0, le=1.0)
    validation_strength: float = Field(ge=0.0, le=1.0)
    evidence_completeness: float = Field(ge=0.0, le=1.0)
    temporal_proximity: float = Field(ge=0.0, le=1.0)
    independence: float = Field(ge=0.0, le=1.0)
    consistency: float = Field(ge=0.0, le=1.0)
    reproducibility: float = Field(ge=0.0, le=1.0)
    feedback_quality_score: float = Field(ge=0.0, le=1.0)


class PolicyEffectivenessRecord(BaseModel):
    record_id: str
    policy_id: str
    policy_version: str = "1.0.0"
    evaluation_window: str = "24h"
    decisions_count: int = 0
    allowed_count: int = 0
    monitored_count: int = 0
    verification_count: int = 0
    quarantined_count: int = 0
    blocked_count: int = 0
    false_block_count: int = 0
    missed_attack_count: int = 0
    policy_violation_count: int = 0
    legitimate_access_rate: float = 1.0
    security_effectiveness: float = 1.0
    decision_latency_ms: float = 0.0
    review_required: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdaptationProposal(BaseModel):
    proposal_id: str
    component: str  # AGENT_RELIABILITY, SELECTION_WEIGHT, POLICY_THRESHOLD, MODEL
    target_id: str
    parameter_name: str
    current_value: float
    proposed_value: float
    change_delta: float
    adaptation_mode: AdaptationMode = AdaptationMode.SHADOW
    approval_status: ApprovalStatus = ApprovalStatus.PROPOSED
    trigger_reason: str
    supporting_feedback_ids: List[str] = Field(default_factory=list)
    evaluation_results: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdaptationRecord(BaseModel):
    adaptation_id: str
    proposal_id: Optional[str] = None
    component: str
    parameter_name: str
    previous_value: float
    proposed_value: float
    applied_value: float
    trigger: str
    feedback_ids: List[str] = Field(default_factory=list)
    evaluation_id: Optional[str] = None
    approval_status: ApprovalStatus
    operator: str = "SYSTEM"
    configuration_version: str = "1.0.0"
    rollback_reference: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdaptationReview(BaseModel):
    review_id: str
    proposal_id: str
    reviewer: str
    decision: ApprovalStatus  # ANALYST_APPROVED, REJECTED, DEFER
    reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelVersion(BaseModel):
    version_id: str
    model_id: str
    agent_id: str
    detector_id: Optional[str] = None
    version: str
    parent_version: Optional[str] = None
    training_dataset: Optional[str] = None
    dataset_version: Optional[str] = None
    feature_schema_version: str = "1.0.0"
    training_config_version: str = "1.0.0"
    calibration_version: str = "1.0.0"
    metrics: Dict[str, float] = Field(default_factory=dict)
    robustness_metrics: Dict[str, float] = Field(default_factory=dict)
    status: ModelRegistryStatus = ModelRegistryStatus.CANDIDATE
    is_champion: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: Optional[datetime] = None
    retired_at: Optional[datetime] = None


class ModelEvaluation(BaseModel):
    evaluation_id: str
    champion_version_id: str
    challenger_version_id: str
    dataset_version: Optional[str] = None
    sample_count: int = 0
    champion_metrics: Dict[str, float]
    challenger_metrics: Dict[str, float]
    comparison_summary: Dict[str, Any]
    recommendation: str  # PROMOTE, REJECT, CONTINUE_SHADOW
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FalsePositiveAnalysis(BaseModel):
    event_id: str
    agent_id: str
    detector_id: Optional[str] = None
    decision_id: str
    policy_id: Optional[str] = None
    predicted_state: str
    validated_state: str
    likely_contributing_factors: List[str]
    evidence_quality: float
    uncertainty: float
    calibration: float
    context: Dict[str, Any]
    remediation_candidate: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FalseNegativeAnalysis(BaseModel):
    event_id: str
    missed_agent: str
    missed_detector: Optional[str] = None
    attack_category: str
    available_evidence: List[str]
    missing_evidence: List[str]
    policy_state: str
    model_version: str
    drift_state: str
    contributing_factors: List[str]
    remediation_candidate: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RootCauseCandidate(BaseModel):
    candidate_id: str
    incident_id: str
    category: str
    affected_component: str
    evidence_ids: List[str]
    confidence: float
    validation_status: ValidationStatus
    remediation_candidate: str


class DecisionReplayRequest(BaseModel):
    target_decision_id: str
    replayed_at_time: Optional[datetime] = None
    override_policy_version: Optional[str] = None
    override_model_version: Optional[str] = None
    override_reliability_weights: Optional[Dict[str, float]] = None


class DecisionReplayResult(BaseModel):
    replay_id: str
    target_decision_id: str
    replayed_at_time: datetime
    original_decision: str
    replayed_decision: str
    matches_original: bool
    differences: Dict[str, Any]
    reconstruction_metadata: Dict[str, Any]


class CounterfactualRequest(BaseModel):
    scenario_name: str
    decision_ids: List[str]
    disable_reliability_weighting: bool = False
    static_agent_selection: bool = False
    disable_temporal_memory: bool = False
    static_segmentation: bool = False
    policy_version: Optional[str] = None


class CounterfactualResult(BaseModel):
    run_id: str
    scenario_name: str
    decision_ids: List[str]
    parameters_modified: Dict[str, Any]
    original_outcomes_summary: Dict[str, Any]
    simulated_outcomes_summary: Dict[str, Any]
    impact_analysis: Dict[str, Any]


class AdaptationStabilityMetric(BaseModel):
    metric_id: str
    window_start: datetime
    window_end: datetime
    policy_churn: float
    selection_churn: float
    threshold_variance: float
    reliability_volatility: float
    rollback_frequency: float
    adaptation_frequency: float
    is_stable: bool


class LearningDatasetVersion(BaseModel):
    dataset_id: str
    dataset_version: str
    source: str
    collection_start: datetime
    collection_end: datetime
    sample_count: int
    label_version: str = "1.0.0"
    validation_method: str = "TIME_AWARE_SPLIT"
    feature_schema: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
