"""
Pydantic Schemas for Human Approval and Response Gate.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


HIGH_IMPACT_ACTIONS = {
    "ACCOUNT_SUSPENSION",
    "NETWORK_ISOLATION",
    "BLOCK_CRITICAL_RESOURCE",
    "DISRUPTIVE_CHANGE",
    "REVOKE_ALL_TOKENS",
    "CONTAINMENT_LOCKDOWN",
    "QUARANTINE_HOST",
}


class ApprovalRequestCreate(BaseModel):
    incident_id: str = Field(..., description="Parent incident ID")
    entity_id: str = Field(..., description="Affected target entity")
    action_type: str = Field(..., description="Action category/name")
    proposed_action: str = Field(..., description="Detailed action description")
    risk_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    uncertainty: float = Field(..., ge=0.0, le=1.0)
    justification: str = Field(..., description="Rationale for proposed action")
    expected_impact: str = Field(..., description="Expected system/business impact")
    alternatives: List[str] = Field(default_factory=list, description="Alternative options evaluated")
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Supporting evidence details")
    policy_id: Optional[str] = Field(default=None, description="Policy triggering the decision")
    ttl_minutes: int = Field(default=60, ge=1, le=1440, description="Time to live in minutes")


class HumanApprovalDecision(BaseModel):
    request_id: str = Field(..., description="Approval request ID")
    approver_identity: str = Field(..., description="Analyst or Admin user ID")
    approver_role: str = Field(..., description="ANALYST, ADMIN, SECURITY_OPERATOR")
    notes: Optional[str] = Field(default=None, description="Reasoning or notes for decision")


class ApprovalRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    request_id: str
    incident_id: str
    entity_id: str
    policy_id: Optional[str] = None
    action_type: str
    proposed_action: str
    risk_score: float
    confidence: float
    uncertainty: float
    is_high_impact: bool
    justification: str
    expected_impact: str
    alternatives: List[str]
    supporting_evidence: List[Dict[str, Any]]
    status: str
    approver_identity: Optional[str] = None
    approver_role: Optional[str] = None
    approval_notes: Optional[str] = None
    approval_timestamp: Optional[datetime] = None
    execution_status: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    verification_status: Optional[str] = None
    expires_at: datetime
    created_at: datetime
