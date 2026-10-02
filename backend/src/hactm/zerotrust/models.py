"""
Pydantic Data Models and Schemas for Zero-Trust Engine:
Zero-Trust Policy Decision + Dynamic Security Context + Micro-Segmentation + Step-Up Verification + Policy Audit.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    VERIFY = "VERIFY"
    QUARANTINE = "QUARANTINE"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class EnforcementMode(str, Enum):
    DRY_RUN = "DRY_RUN"
    SIMULATION = "SIMULATION"
    CONTROLLED_ENFORCEMENT = "CONTROLLED_ENFORCEMENT"


class SubjectType(str, Enum):
    USER = "USER"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"
    DEVICE = "DEVICE"
    APPLICATION = "APPLICATION"
    WORKLOAD = "WORKLOAD"
    ADMIN = "ADMIN"
    THIRD_PARTY = "THIRD_PARTY"


class ResourceType(str, Enum):
    APPLICATION = "APPLICATION"
    API = "API"
    DATABASE = "DATABASE"
    SERVER = "SERVER"
    FILE = "FILE"
    WORKLOAD = "WORKLOAD"
    NETWORK_SEGMENT = "NETWORK_SEGMENT"
    TRANSACTION = "TRANSACTION"
    ADMIN_INTERFACE = "ADMIN_INTERFACE"


class ActionType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    EXECUTE = "EXECUTE"
    LOGIN = "LOGIN"
    ADMINISTER = "ADMINISTER"
    TRANSFER = "TRANSFER"
    TRANSACT = "TRANSACT"
    ACCESS_API = "ACCESS_API"
    CONNECT = "CONNECT"
    DOWNLOAD = "DOWNLOAD"
    UPLOAD = "UPLOAD"


class SecurityZoneName(str, Enum):
    USER_ZONE = "USER_ZONE"
    APPLICATION_ZONE = "APPLICATION_ZONE"
    DATABASE_ZONE = "DATABASE_ZONE"
    ADMIN_ZONE = "ADMIN_ZONE"
    PRODUCTION_ZONE = "PRODUCTION_ZONE"
    THIRD_PARTY_ZONE = "THIRD_PARTY_ZONE"
    QUARANTINE_ZONE = "QUARANTINE_ZONE"


class AuthenticationAssuranceLevel(str, Enum):
    AAL0 = "AAL0"
    AAL1 = "AAL1"
    AAL2 = "AAL2"
    AAL3 = "AAL3"


class BiometricStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUESTED = "REQUESTED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"


class SubjectModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subject_id: str
    subject_type: SubjectType = SubjectType.USER
    roles: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    is_authenticated: bool = True
    assurance_level: AuthenticationAssuranceLevel = AuthenticationAssuranceLevel.AAL1


class ResourceModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resource_id: str
    resource_type: ResourceType = ResourceType.APPLICATION
    sensitivity: str = "MODERATE"  # LOW, MODERATE, HIGH, CRITICAL
    criticality: str = "MODERATE"  # LOW, MODERATE, HIGH, CRITICAL
    security_zone: SecurityZoneName = SecurityZoneName.APPLICATION_ZONE
    owner: str = "SYSTEM"
    required_assurance_level: AuthenticationAssuranceLevel = AuthenticationAssuranceLevel.AAL1
    allowed_subject_groups: List[str] = Field(default_factory=list)


class SecurityTag(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tag_id: str
    entity_id: str
    tag: str
    confidence: float = 1.0
    source_evidence_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    policy_version: str = "1.0.0"
    status: str = "ACTIVE"  # ACTIVE, EXPIRED, REVOKED


class SecurityGroup(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    group_id: str
    name: str
    description: Optional[str] = None
    membership_rule: Dict[str, Any] = Field(default_factory=dict)
    members: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    policy_version: str = "1.0.0"


class MicroSegment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    segment_id: str
    name: str
    zone: SecurityZoneName = SecurityZoneName.APPLICATION_ZONE
    subject_groups: List[str] = Field(default_factory=list)
    resource_groups: List[str] = Field(default_factory=list)
    allowed_actions: List[ActionType] = Field(default_factory=list)
    denied_actions: List[ActionType] = Field(default_factory=list)
    required_assurance: AuthenticationAssuranceLevel = AuthenticationAssuranceLevel.AAL1
    conditions: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 100
    enabled: bool = True
    policy_version: str = "1.0.0"


class ZeroTrustDecisionContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    context_id: str
    subject_id: str
    subject_type: SubjectType = SubjectType.USER
    resource_id: str
    resource_type: ResourceType = ResourceType.APPLICATION
    requested_action: ActionType = ActionType.READ
    identity_state: Dict[str, Any] = Field(default_factory=dict)
    device_state: Dict[str, Any] = Field(default_factory=dict)
    network_state: Dict[str, Any] = Field(default_factory=dict)
    application_state: Dict[str, Any] = Field(default_factory=dict)
    transaction_state: Dict[str, Any] = Field(default_factory=dict)
    current_risk: float = 0.0
    uncertainty: float = 0.0
    evidence_quality: float = 1.0
    reliability_state: Dict[str, Any] = Field(default_factory=dict)
    security_tags: List[str] = Field(default_factory=list)
    security_group: List[str] = Field(default_factory=list)
    security_zone: SecurityZoneName = SecurityZoneName.USER_ZONE
    attack_chain_context: List[Any] = Field(default_factory=list)
    temporal_context: Dict[str, Any] = Field(default_factory=dict)
    authentication_state: Dict[str, Any] = Field(default_factory=dict)
    two_factor_state: str = "NOT_REQUIRED"  # NOT_REQUIRED, REQUIRED, VERIFIED, FAILED
    biometric_verification_state: BiometricStatus = BiometricStatus.NOT_REQUIRED
    policy_context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Policy(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    policy_id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    priority: int = 100
    enabled: bool = True
    scope: str = "GLOBAL"
    conditions: Dict[str, Any] = Field(default_factory=dict)
    required_assurance: AuthenticationAssuranceLevel = AuthenticationAssuranceLevel.AAL1
    decision: PolicyDecision = PolicyDecision.VERIFY
    actions: List[str] = Field(default_factory=list)
    expiration: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author: str = "SYSTEM"
    configuration_version: str = "1.0.0"


class PolicyDecisionRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    decision_id: str
    subject_id: str
    resource_id: str
    requested_action: ActionType = ActionType.READ
    decision: PolicyDecision = PolicyDecision.VERIFY
    cyber_risk_score: float = 0.0
    confidence: float = 1.0
    uncertainty: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)
    applicable_policy_ids: List[str] = Field(default_factory=list)
    policy_versions: Dict[str, str] = Field(default_factory=dict)
    security_tags: List[str] = Field(default_factory=list)
    security_groups: List[str] = Field(default_factory=list)
    security_zone: SecurityZoneName = SecurityZoneName.USER_ZONE
    authentication_assurance: AuthenticationAssuranceLevel = AuthenticationAssuranceLevel.AAL1
    enforcement_mode: EnforcementMode = EnforcementMode.DRY_RUN
    enforcement_status: str = "SIMULATED"
    explanation: Optional[str] = None
    reasons: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "1.0.0"


class EnforcementAction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action_id: str
    decision_id: str
    action_type: str  # ALLOW, MONITOR, REQUIRE_2FA, REQUIRE_BIOMETRIC, QUARANTINE, BLOCK, ISOLATE, RATE_LIMIT, ESCALATE
    target: str
    mode: EnforcementMode = EnforcementMode.DRY_RUN
    status: str = "SIMULATED"
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    applied_at: Optional[datetime] = None
    expiration: Optional[datetime] = None
    rollback_reference: Optional[str] = None
    reason: Optional[str] = None


class VerificationEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    subject_id: str
    verification_type: str = "2FA"  # 2FA, BIOMETRIC
    method: str = "TOTP"
    status: str = "SUCCESS"  # SUCCESS, FAILED, TIMEOUT, CANCELLED
    assurance_level: AuthenticationAssuranceLevel = AuthenticationAssuranceLevel.AAL2
    evidence_reference: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PolicyOverride(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    override_id: str
    decision_id: str
    analyst_id: str
    override_type: str  # ALLOW_OVERRIDE, DENY_OVERRIDE, REQUIRE_REVIEW
    previous_decision: str
    new_decision: str
    reason: str
    evidence_ids: List[str] = Field(default_factory=list)
    policy_version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DynamicSecurityContext(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    entity_id: str
    security_tags: List[SecurityTag] = Field(default_factory=list)
    security_groups: List[str] = Field(default_factory=list)
    security_zone: SecurityZoneName = SecurityZoneName.USER_ZONE
    cyber_risk: float = 0.0
    uncertainty: float = 0.0
    evidence_coverage: float = 1.0
    identity_state: Dict[str, Any] = Field(default_factory=dict)
    device_state: Dict[str, Any] = Field(default_factory=dict)
    behavioral_state: Dict[str, Any] = Field(default_factory=dict)
    transaction_state: Dict[str, Any] = Field(default_factory=dict)
    authentication_assurance: AuthenticationAssuranceLevel = AuthenticationAssuranceLevel.AAL1
    active_restrictions: List[str] = Field(default_factory=list)
    version: str = "1.0.0"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
