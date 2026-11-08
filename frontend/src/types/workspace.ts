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

