"""
Central Agent Supervisor (CAS) Pydantic Schemas and Contracts.
Defines versioned schemas for telemetry events, health metrics, behavioural observations,
anomalies, trust assessments, supervisory decisions, isolation records, and recovery workflows.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentTrustStatus(str, Enum):
    TRUSTED = "TRUSTED"
    NORMAL = "NORMAL"
    UNDER_OBSERVATION = "UNDER_OBSERVATION"
    SUSPICIOUS = "SUSPICIOUS"
    RESTRICTED = "RESTRICTED"
    ISOLATED = "ISOLATED"
    REVOKED = "REVOKED"


class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyType(str, Enum):
    HEARTBEAT_MISSING = "HEARTBEAT_MISSING"
    UNEXPECTED_OFFLINE = "UNEXPECTED_OFFLINE"
    STUCK_ANALYSING = "STUCK_ANALYSING"
    REPEATED_FAILURES = "REPEATED_FAILURES"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    UNAUTHORISED_TOOL_REQUEST = "UNAUTHORISED_TOOL_REQUEST"
    FORBIDDEN_TOOL_REQUEST = "FORBIDDEN_TOOL_REQUEST"
    OUT_OF_SCOPE_TOOL = "OUT_OF_SCOPE_TOOL"
    REVOKED_CAPABILITY_USE = "REVOKED_CAPABILITY_USE"
    ISOLATED_AGENT_EXECUTION = "ISOLATED_AGENT_EXECUTION"
    EVIDENCE_SCHEMA_INVALID = "EVIDENCE_SCHEMA_INVALID"
    EVIDENCE_CONTRADICTION = "EVIDENCE_CONTRADICTION"
    PROMPT_INJECTION_DETECTED = "PROMPT_INJECTION_DETECTED"
    MALICIOUS_TOOL_OUTPUT = "MALICIOUS_TOOL_OUTPUT"
    UNUSUAL_COMMUNICATION_PATTERN = "UNUSUAL_COMMUNICATION_PATTERN"
    EXCESSIVE_TASK_DELEGATION = "EXCESSIVE_TASK_DELEGATION"
    APPROVAL_BYPASS_ATTEMPT = "APPROVAL_BYPASS_ATTEMPT"
    ORCHESTRATOR_ANOMALY = "ORCHESTRATOR_ANOMALY"
    SUPERVISOR_HEALTH_DEGRADED = "SUPERVISOR_HEALTH_DEGRADED"


class GovernanceLevel(int, Enum):
    LEVEL_0_NORMAL = 0
    LEVEL_1_OBSERVATION = 1
    LEVEL_2_WARNING = 2
    LEVEL_3_RESTRICTED = 3
    LEVEL_4_ISOLATED = 4
    LEVEL_5_HUMAN_SECURITY_REVIEW = 5


# Telemetry Ingestion Schemas
class SupervisorTelemetryEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Type of monitoring event")
    tenant_id: str = Field(default="enterprise_primary")
    agent_id: str = Field(..., description="Target or emitting agent ID")
    incident_id: Optional[str] = None
    task_id: Optional[str] = None
    severity: Optional[str] = "MEDIUM"
    source: str = Field(default="AGENT_RUNTIME")
    payload: Dict[str, Any] = Field(default_factory=dict)
    evidence_refs: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = "1.0"


class AgentHeartbeatInput(BaseModel):
    agent_id: str
    current_status: str = "OPERATIONAL"
    current_task: Optional[str] = None
    heartbeat_interval_sec: float = 10.0
    cpu_load: float = 0.0
    memory_mb: float = 0.0
    queue_length: int = 0
    timestamp: Optional[str] = None


# Detailed Response Schemas
class AgentHealthResponse(BaseModel):
    agent_id: str
    status: str
    is_online: bool
    last_heartbeat: str
    heartbeat_interval_sec: float
    time_since_heartbeat_sec: float
    active_task: Optional[str] = None
    consecutive_failures: int = 0
    is_stuck: bool = False
    cpu_load: float = 0.0
    memory_mb: float = 0.0
    queue_length: int = 0
    health_score: float = 1.0


class AgentBehaviourResponse(BaseModel):
    agent_id: str
    task_frequency_per_min: float
    avg_execution_ms: float
    tool_request_count: int
    handoff_count: int
    communication_volume: int
    anomaly_score: float
    active_flags: List[str] = Field(default_factory=list)
    baseline_deviation_ratio: float = 1.0


class AgentTrustResponse(BaseModel):
    agent_id: str
    trust_status: AgentTrustStatus
    trust_score: float
    reliability_score: float
    compliance_score: float
    uncertainty: float
    recent_anomalies_count: int
    violation_history: List[str] = Field(default_factory=list)
    revoked_capabilities: List[str] = Field(default_factory=list)
    is_isolated: bool
    reasoning_summary: str
    last_assessed_at: str


class AnomalyAlertItem(BaseModel):
    anomaly_id: str
    agent_id: str
    incident_id: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: str
    anomaly_type: str
    severity: str
    source: str
    description: str
    evidence_references: List[str] = Field(default_factory=list)
    recommended_action: str
    status: str


class SupervisorDecisionItem(BaseModel):
    decision_id: str
    agent_id: str
    incident_id: Optional[str] = None
    timestamp: str
    governance_level: int
    decision_type: str
    justification: str
    action_payload: Dict[str, Any] = Field(default_factory=dict)
    work_orders_affected: List[str] = Field(default_factory=list)
    operator_identity: str
    status: str


class AgentIsolationRecord(BaseModel):
    isolation_id: str
    agent_id: str
    incident_id: Optional[str] = None
    isolated_at: str
    reason: str
    trigger_anomaly_id: Optional[str] = None
    revoked_capabilities: List[str] = Field(default_factory=list)
    reassigned_tasks: List[str] = Field(default_factory=list)
    is_active: bool
    reinstated_at: Optional[str] = None
    authorized_by: str


class AgentRecoveryRequest(BaseModel):
    agent_id: str
    reason: str
    operator_identity: str = "SECURITY_ADMIN"
    notes: Optional[str] = None


class AgentCapabilityRestrictRequest(BaseModel):
    agent_id: str
    capabilities_to_revoke: List[str]
    reason: str
    operator_identity: str = "SECURITY_ADMIN"


class AgentIsolationControlRequest(BaseModel):
    agent_id: str
    reason: str
    incident_id: Optional[str] = None
    reassign_outstanding_tasks: bool = True
    operator_identity: str = "SECURITY_ADMIN"


class FleetOverviewResponse(BaseModel):
    total_registered_agents: int
    healthy_agents: int
    agents_under_observation: int
    agents_with_anomalies: int
    restricted_agents: int
    isolated_agents: int
    offline_agents: int
    active_monitoring_alerts: int
    supervisor_health: str = "HEALTHY"
    event_ingestion_latency_ms: float = 0.5
    processing_queue_length: int = 0
    watchdog_status: str = "ACTIVE"
    last_updated_at: str


class SupervisedAgentSummary(BaseModel):
    agent_id: str
    name: str
    department: str
    agent_type: str
    health: str
    trust_status: str
    trust_score: float
    current_task: Optional[str] = None
    last_heartbeat: str
    status: str
    recent_anomalies_count: int
    is_isolated: bool
    revoked_capabilities_count: int

