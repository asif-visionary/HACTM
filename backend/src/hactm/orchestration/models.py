"""
Pydantic Data Models and Schemas for Orchestration:
Adaptive Agent Selection and Resource-Aware Evidence Orchestration.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class AgentAvailabilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    DISABLED = "DISABLED"


class OrchestrationStrategy(str, Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    HYBRID = "HYBRID"


class SelectionMethod(str, Enum):
    ALL_AGENTS = "ALL_AGENTS"
    STATIC_MAPPING = "STATIC_MAPPING"
    RISK_THRESHOLD = "RISK_THRESHOLD"
    RELIABILITY_AWARE = "RELIABILITY_AWARE"
    RELIABILITY_UNCERTAINTY_AWARE = "RELIABILITY_UNCERTAINTY_AWARE"
    FULL_ADAPTIVE_ORCHESTRATION = "FULL_ADAPTIVE_ORCHESTRATION"


class StoppingReason(str, Enum):
    UNCERTAINTY_BELOW_THRESHOLD = "UNCERTAINTY_BELOW_THRESHOLD"
    RISK_STABLE = "RISK_STABLE"
    INSUFFICIENT_EXPECTED_GAIN = "INSUFFICIENT_EXPECTED_GAIN"
    RESOURCE_BUDGET_EXHAUSTED = "RESOURCE_BUDGET_EXHAUSTED"
    LATENCY_BUDGET_EXHAUSTED = "LATENCY_BUDGET_EXHAUSTED"
    SUFFICIENT_COVERAGE_ACHIEVED = "SUFFICIENT_COVERAGE_ACHIEVED"
    POLICY_REQUIRE_HUMAN_REVIEW = "POLICY_REQUIRE_HUMAN_REVIEW"
    MAX_ROUNDS_REACHED = "MAX_ROUNDS_REACHED"


class AgentCapability(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    capability_name: str
    target_entity_type: Optional[str] = None
    supported_attack_stage: Optional[str] = None
    description: Optional[str] = None


class AgentCost(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    cpu_cost: float = 1.0
    memory_cost: float = 1.0
    inference_cost: float = 1.0
    network_cost: float = 1.0
    communication_cost: float = 1.0
    latency_cost: float = 1.0
    storage_cost: float = 1.0
    total_normalized_cost: float = 1.0


class AgentRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    agent_name: str
    domain: str
    capabilities: List[str] = Field(default_factory=list)
    supported_event_types: List[str] = Field(default_factory=list)
    supported_entity_types: List[str] = Field(default_factory=list)
    supported_attack_categories: List[str] = Field(default_factory=list)
    reliability_score: float = 0.85
    reliability_lower_bound: float = 0.75
    reliability_upper_bound: float = 0.95
    uncertainty_profile: Dict[str, float] = Field(default_factory=dict)
    average_latency_ms: float = 150.0
    p95_latency_ms: float = 300.0
    computational_cost: float = 1.0
    communication_cost: float = 0.5
    availability_status: AgentAvailabilityStatus = AgentAvailabilityStatus.AVAILABLE
    current_model_version: str = "1.0.0"
    drift_status: str = "STABLE"
    calibration_status: str = "CALIBRATED"
    enabled: bool = True
    configuration_version: str = "1.0.0"
    last_updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentSelectionContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    context_id: str
    event_id: Optional[str] = None
    entity_ids: List[str] = Field(default_factory=list)
    event_type: str
    domains_observed: List[str] = Field(default_factory=list)
    current_risk: float = 0.0
    current_uncertainty: float = 1.0
    evidence_count: int = 0
    evidence_quality: float = 1.0
    temporal_context: Dict[str, Any] = Field(default_factory=dict)
    graph_context: Dict[str, Any] = Field(default_factory=dict)
    attack_chain_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    missing_domains: List[str] = Field(default_factory=list)
    missing_evidence_types: List[str] = Field(default_factory=list)
    previous_agent_calls: List[str] = Field(default_factory=list)
    latency_budget_ms: float = 1000.0
    resource_budget: Dict[str, Any] = Field(default_factory=dict)
    policy_constraints: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExpectedInformationGain(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    context_id: str
    estimated_gain: float = Field(..., ge=0.0, le=1.0)
    estimation_method: str = "historical_empirical_gain"
    supporting_samples: int = 10
    confidence: float = 0.85
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RedundancyScore(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    redundancy_score: float = Field(..., ge=0.0, le=1.0)
    overlapping_domains: List[str] = Field(default_factory=list)
    overlapping_features: List[str] = Field(default_factory=list)


class SelectionScore(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    agent_id: str
    relevance_score: float = 0.0
    reliability_score: float = 0.0
    expected_gain: float = 0.0
    cost_score: float = 0.0
    latency_score: float = 0.0
    diversity_score: float = 0.0
    redundancy_penalty: float = 0.0
    final_score: float = 0.0
    reason_codes: List[str] = Field(default_factory=list)
    explanation: str = ""


class SelectionRound(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    round_id: str
    context_id: str
    round_number: int
    selected_agent: str
    selection_score: float
    expected_gain: float = 0.0
    actual_gain: float = 0.0
    cost: float = 1.0
    latency: float = 150.0
    resulting_uncertainty: float = 0.5
    resulting_risk: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentInvocationRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invocation_id: str
    context_id: str
    agent_id: str
    detector_id: Optional[str] = None
    model_version: str = "1.0.0"
    selection_round: int = 1
    selection_score: float = 0.0
    expected_gain: float = 0.0
    actual_gain: float = 0.0
    reliability_at_selection: float = 0.85
    uncertainty_before: float = 1.0
    uncertainty_after: float = 0.5
    risk_before: float = 0.0
    risk_after: float = 0.0
    cost_estimate: float = 1.0
    actual_cost: float = 1.0
    latency_estimate: float = 150.0
    actual_latency: float = 140.0
    reason_codes: List[str] = Field(default_factory=list)
    invocation_status: str = "SUCCESS"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentSelectionDecision(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    decision_id: str
    context_id: str
    candidate_agents: List[str] = Field(default_factory=list)
    selected_agents: List[str] = Field(default_factory=list)
    selection_method: SelectionMethod = SelectionMethod.FULL_ADAPTIVE_ORCHESTRATION
    selection_scores: Dict[str, float] = Field(default_factory=dict)
    candidate_details: List[SelectionScore] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    expected_total_gain: float = 0.0
    expected_total_cost: float = 0.0
    expected_latency: float = 0.0
    stopping_reason: StoppingReason = StoppingReason.UNCERTAINTY_BELOW_THRESHOLD
    configuration_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentSelectionConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    method: SelectionMethod = SelectionMethod.FULL_ADAPTIVE_ORCHESTRATION
    strategy: OrchestrationStrategy = OrchestrationStrategy.HYBRID

    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "relevance": 0.25,
            "expected_information_gain": 0.25,
            "reliability": 0.15,
            "uncertainty_reduction": 0.15,
            "temporal_relevance": 0.10,
            "chain_relevance": 0.10,
            "diversity": 0.05,
            "redundancy_penalty": 0.10,
            "cost_penalty": 0.10,
            "latency_penalty": 0.10,
            "drift_penalty": 0.05,
            "calibration_penalty": 0.05,
        }
    )

    constraints: Dict[str, Any] = Field(
        default_factory=lambda: {
            "max_agent_calls": 3,
            "max_parallel_agents": 2,
            "max_total_cost": 5.0,
            "latency_budget_ms": 1000.0,
        }
    )

    stopping: Dict[str, float] = Field(
        default_factory=lambda: {
            "uncertainty_threshold": 0.25,
            "minimum_expected_gain": 0.05,
            "risk_stability_threshold": 0.05,
        }
    )

    version: str = "1.0.0"
