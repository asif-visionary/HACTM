/**
 * Core Domain & Workspace Types for HACTM Cyber Operations Workspace.
 * Authoritative types for isometric office, agents, events, governance, and trust passports.
 */

export type AgentOfficeStatus =
  | 'IDLE'
  | 'QUEUED'
  | 'ASSIGNED'
  | 'ANALYSING'
  | 'GENERATING_EVIDENCE'
  | 'COMMUNICATING'
  | 'HANDOFF'
  | 'WAITING_FOR_APPROVAL'
  | 'COMPLETED'
  | 'DEGRADED'
  | 'ISOLATED'
  | 'FAILED';

export type OfficeDepartmentId =
  | 'command_center'
  | 'network_ops'
  | 'phishing_intel'
  | 'identity_sec'
  | 'behaviour_intel'
  | 'transaction_sec'
  | 'governance_trust';

export interface OfficeDepartment {
  id: OfficeDepartmentId;
  name: string;
  code: string;
  description: string;
  color: string;
  gridX: number;
  gridY: number;
  width: number;
  height: number;
  activeAgentsCount: number;
  totalAlerts: number;
}

export interface WorkspaceAgentState {
  agent_id: string;
  name: string;
  shortName: string;
  departmentId: OfficeDepartmentId;
  status: AgentOfficeStatus;
  currentTask?: string;
  currentIncidentId?: string;
  activeEvidenceId?: string;
  deskPosition: {
    gridX: number;
    gridY: number;
  };
  facing: 'SE' | 'SW' | 'NE' | 'NW';
  avatarColor: string;
  accentColor: string;
  reliabilityScore: number;
  isIsolated: boolean;
  isolationReason?: string;
  lastMessage?: string;
  lastActiveTimestamp: string;
  eventsProcessed: number;
  detectionsCount: number;
  toolPermissions: string[];
}

export type WorkspaceEventType =
  | 'incident_created'
  | 'agent_registered'
  | 'agent_status'
  | 'task_assigned'
  | 'task_started'
  | 'agent_tool_request'
  | 'agent_message'
  | 'evidence_generated'
  | 'evidence_conflict'
  | 'investigation_replanned'
  | 'risk_updated'
  | 'approval_requested'
  | 'approval_granted'
  | 'approval_rejected'
  | 'tool_access_denied'
  | 'tool_access_granted'
  | 'agent_capability_revoked'
  | 'agent_isolated'
  | 'agent_reassigned'
  | 'task_reassigned'
  | 'response_executed'
  | 'response_verified'
  | 'incident_closed'
  | 'stream_connected'
  | 'heartbeat'
  | 'agent_heartbeat_received'
  | 'agent_health_changed'
  | 'agent_anomaly_detected'
  | 'agent_behaviour_deviation'
  | 'agent_evidence_flagged'
  | 'agent_trust_updated'
  | 'agent_warning_issued'
  | 'agent_capability_restricted'
  | 'agent_recovery_requested'
  | 'agent_reinstated'
  | 'orchestrator_anomaly_detected'
  | 'supervisor_health_changed';

export interface WorkspaceEvent {
  event_id: string;
  event_type: WorkspaceEventType;
  tenant_id?: string;
  incident_id?: string;
  task_id?: string;
  agent_id?: string;
  status?: AgentOfficeStatus;
  message: string;
  timestamp: string;
  data?: Record<string, any>;
}

export interface AgentTrustPassport {
  agent_id: string;
  agent_name: string;
  department: string;
  agent_type: string;
  model_and_version: string;
  current_status: string;
  allowed_capabilities: string[];
  tool_permissions: string[];
  tenant_scope: string;
  reliability_score?: number;
  reliability_lower_bound?: number;
  reliability_upper_bound?: number;
  drift_status: string;
  calibration_status: string;
  health_status: string;
  average_latency_ms: number;
  events_processed: number;
  detections_generated: number;
  active_detectors: string[];
  violation_history: string[];
  last_activity: string;
  is_isolated: boolean;
  isolation_reason?: string;
  revoked_capabilities: string[];
}

export interface AgentMessageItem {
  id: string;
  sender: string;
  recipient: string;
  incidentId?: string;
  taskId?: string;
  message: string;
  evidenceRef?: string;
  timestamp: string;
  status: AgentOfficeStatus;
}

export interface TimelineEntry {
  id: string;
  step: string;
  title: string;
  description: string;
  timestamp: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'ALERT' | 'BLOCKED';
  incidentId?: string;
  agentId?: string;
  evidenceId?: string;
  riskScore?: number;
}

export type AgentLoopStage =
  | 'REASON'
  | 'PLAN'
  | 'ACT'
  | 'OBSERVE'
  | 'EVALUATE'
  | 'REPEAT';

export type AgentLoopStageStatus =
  | 'NOT_STARTED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'WAITING'
  | 'FAILED'
  | 'BLOCKED';

export interface AgentLoopEvent {
  eventId: string;
  eventType: WorkspaceEventType | string;
  stage: AgentLoopStage;
  status?: string;
  message: string;
  timestamp: string;
  incidentId?: string;
  taskId?: string;
  agentId?: string;
  evidenceId?: string;
  data?: Record<string, any>;
}

export interface AgentLoopStageField {
  label: string;
  value: string | string[];
  tone?: 'default' | 'cyan' | 'emerald' | 'amber' | 'red' | 'slate' | 'mono';
  evidenceId?: string;
}

export interface AgentLoopStageToolEntry {
  toolName: string;
  status: string;
  timestamp?: string;
  detail?: string;
}

export interface WorkOrderRecord {
  work_order_id: string;
  investigation_id: string;
  parent_incident_id: string;
  objective: string;
  scope?: Record<string, any>;
  required_questions?: string[];
  success_criteria?: string[];
  permitted_tools?: string[];
  data_sources?: string[];
  forbidden_actions?: string[];
  resource_limits?: Record<string, any>;
  required_evidence?: string[];
  assigned_agent_id: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  evidence_pack?: {
    claims?: Array<Record<string, any>>;
    supporting_evidence?: Array<Record<string, any>>;
    contradicting_evidence?: Array<Record<string, any>>;
    assumptions?: string[];
    confidence?: number;
    uncertainty?: number;
    tool_use_log?: Array<Record<string, any>>;
    completion_status?: string;
    reason_for_incomplete_work?: string | null;
    recommended_next_step?: string | null;
  } | null;
}

export interface ApprovalRecord {
  request_id: string;
  incident_id: string;
  entity_id: string;
  policy_id?: string | null;
  action_type: string;
  proposed_action: string;
  risk_score: number;
  confidence: number;
  uncertainty: number;
  justification?: string;
  expected_impact?: string;
  alternatives?: string[];
  status: string;
  approver_identity?: string | null;
  approver_role?: string | null;
  approval_notes?: string | null;
  execution_status?: string | null;
  execution_result?: Record<string, any> | null;
  verification_status?: string | null;
  created_at?: string;
}

export interface EvidenceDetailRecord {
  event_id: string;
  agent_id: string;
  entity_id: string;
  event_type: string;
  timestamp: string;
  risk_score: number;
  confidence: number;
  uncertainty: number;
  severity: string;
  evidence?: Record<string, any>;
  dataset?: string;
  security_tags?: string[];
}

export interface AuditTrailRecord {
  event_id: string;
  incident_id?: string | null;
  timestamp: string;
  actor_id: string;
  actor_type: string;
  event_type: string;
  evidence_references?: string[];
  work_order_references?: string[];
  decision_rationale?: string;
  proposed_or_executed_action?: string;
  approver_identity?: string | null;
  execution_status?: string | null;
  record_hash?: string | null;
}

export interface AgentLoopExecutionContext {
  incidentId?: string | null;
  agents: WorkspaceAgentState[];
  messages: AgentMessageItem[];
  workOrders: WorkOrderRecord[];
  approvals: ApprovalRecord[];
  evidenceRecords: EvidenceDetailRecord[];
  auditTrail: AuditTrailRecord[];
}

export interface AgentLoopStageDetails {
  stage: AgentLoopStage;
  stageNumber: number;
  title: string;
  shortLabel: string;
  icon: string;
  description: string;
  status: AgentLoopStageStatus;
  hasExecutionData: boolean;
  incidentId?: string;
  taskId?: string;
  agentId?: string;
  timestamp?: string;
  summary?: string;
  events: AgentLoopEvent[];
  evidenceRefs: string[];
  fields: AgentLoopStageField[];
  highlights?: {
    restrictionsOrDenials?: string[];
    contradictions?: string[];
    uncertainties?: string[];
    toolHistory?: AgentLoopStageToolEntry[];
    agentMessages?: AgentMessageItem[];
  };
}


