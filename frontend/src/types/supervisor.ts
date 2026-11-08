/**
 * Central Agent Supervisor (CAS) TypeScript Interfaces.
 * Authoritative types for centralized agent fleet monitoring, behavioral profiles,
 * anomaly alerts, supervisory decisions, intelligence briefs, and defensive controls.
 */

export interface FleetOverview {
  total_registered_agents: number;
  healthy_agents: number;
  agents_under_observation: number;
  agents_with_anomalies: number;
  restricted_agents: number;
  isolated_agents: number;
  offline_agents: number;
  active_monitoring_alerts: number;
  supervisor_health: 'HEALTHY' | 'DEGRADED' | 'FAILING';
  event_ingestion_latency_ms: number;
  processing_queue_length: number;
  watchdog_status: string;
  last_updated_at: string;
}

export interface SupervisedAgent {
  agent_id: string;
  name: string;
  department: string;
  agent_type: string;
  health: string;
  trust_status: 'TRUSTED' | 'NORMAL' | 'UNDER_OBSERVATION' | 'SUSPICIOUS' | 'RESTRICTED' | 'ISOLATED' | 'REVOKED';
  trust_score: number;
  current_task?: string;
  last_heartbeat: string;
  status: string;
  recent_anomalies_count: number;
  is_isolated: boolean;
  revoked_capabilities_count: number;
}

export interface AgentHealthDetails {
  agent_id: string;
  status: string;
  is_online: boolean;
  last_heartbeat: string;
  heartbeat_interval_sec: number;
  time_since_heartbeat_sec: number;
  active_task?: string;
  consecutive_failures: number;
  is_stuck: boolean;
  cpu_load: number;
  memory_mb: number;
  queue_length: number;
  health_score: number;
}

export interface AgentBehaviourDetails {
  agent_id: string;
  task_frequency_per_min: number;
  avg_execution_ms: number;
  tool_request_count: number;
  handoff_count: number;
  communication_volume: number;
  anomaly_score: number;
  active_flags: string[];
  baseline_deviation_ratio: number;
}

export interface AgentTrustDetails {
  agent_id: string;
  trust_status: string;
  trust_score: number;
  reliability_score: number;
  compliance_score: number;
  uncertainty: number;
  recent_anomalies_count: number;
  violation_history: string[];
  revoked_capabilities: string[];
  is_isolated: boolean;
  reasoning_summary: string;
  last_assessed_at: string;
}

export interface AnomalyAlert {
  anomaly_id: string;
  agent_id: string;
  incident_id?: string;
  task_id?: string;
  timestamp: string;
  anomaly_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  source: string;
  description: string;
  evidence_references: string[];
  recommended_action: string;
  status: 'ACTIVE' | 'MITIGATED' | 'DISMISSED' | 'INVESTIGATING';
}

export interface SupervisorDecision {
  decision_id: string;
  agent_id: string;
  incident_id?: string;
  timestamp: string;
  governance_level: number;
  decision_type: string;
  justification: string;
  action_payload: Record<string, any>;
  work_orders_affected: string[];
  operator_identity: string;
  status: string;
}

export interface SupervisorIntelligence {
  timestamp: string;
  supervisory_posture: string;
  executive_narrative: string;
  fleet_health_ratio: string;
  critical_anomalies_count: number;
  high_anomalies_count: number;
  isolated_agents_count: number;
  governance_recommendations: string[];
}

export interface IsolationRecord {
  isolation_id: string;
  agent_id: string;
  incident_id?: string;
  isolated_at: string;
  reason: string;
  trigger_anomaly_id?: string;
  revoked_capabilities: string[];
  reassigned_tasks: string[];
  is_active: boolean;
  reinstated_at?: string;
  authorized_by: string;
}

