"""
Pydantic Schemas for Governed Investigation Controller.
Enforces strict schemas for Work Orders and Validated Evidence Packs.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class WorkOrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    investigation_id: str = Field(..., description="Unique investigation identifier")
    parent_incident_id: str = Field(..., description="Parent incident identifier")
    objective: str = Field(..., description="Formal investigation objective")
    scope: Dict[str, Any] = Field(default_factory=dict, description="Scope boundaries and target entities")
    required_questions: List[str] = Field(default_factory=list, description="Questions agent must answer")
    success_criteria: List[str] = Field(default_factory=list, description="Criteria for completion")
    permitted_tools: List[str] = Field(default_factory=list, description="Whitelist of allowed tools")
    data_sources: List[str] = Field(default_factory=list, description="Permitted data sources")
    forbidden_actions: List[str] = Field(default_factory=list, description="Forbidden agent operations")
    resource_limits: Dict[str, Any] = Field(default_factory=lambda: {"max_execution_time_ms": 30000, "max_tool_calls": 10}, description="Execution budget")
    required_evidence: List[str] = Field(default_factory=list, description="Mandatory evidence types")
    deadline: Optional[datetime] = Field(default=None, description="Stopping deadline")
    assigned_agent_id: str = Field(..., description="Agent assigned to work order")


class WorkOrderResponse(WorkOrderCreate):
    model_config = ConfigDict(from_attributes=True)

    work_order_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    evidence_pack: Optional[Dict[str, Any]] = None


class ValidatedEvidencePack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claims: List[Dict[str, Any]] = Field(..., description="Claims and findings made by agent")
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Supporting evidence items")
    contradicting_evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Contradicting evidence or alternative explanations")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions and missing information")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    uncertainty: float = Field(..., ge=0.0, le=1.0, description="Predictive uncertainty score")
    tool_use_log: List[Dict[str, Any]] = Field(default_factory=list, description="Log of executed tool calls")
    completion_status: str = Field(..., description="COMPLETED, PARTIAL, FAILED, TIMED_OUT")
    reason_for_incomplete_work: Optional[str] = Field(default=None, description="Reason if work is incomplete")
    recommended_next_step: Optional[str] = Field(default=None, description="Recommended next action")


class ValidatePackRequest(BaseModel):
    work_order_id: str
    agent_id: str
    evidence_pack: ValidatedEvidencePack
