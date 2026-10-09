import { PaginatedResponse, SingleResponse, SystemHealth, OverviewMetrics } from '../types/api';
import { SecurityEvidence, IngestionRunResult } from '../types/evidence';
import { Entity, EntityDetail } from '../types/entity';

const API_BASE = '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorData;
    try {
      errorData = await res.json();
    } catch {
      throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
    }
    const message = errorData?.error?.message || `API request failed with status ${res.status}`;
    throw new Error(message);
  }
  return res.json();
}

export const api = {
  // System Health
  async getHealth(): Promise<SystemHealth> {
    const res = await fetch('/health');
    return handleResponse<SystemHealth>(res);
  },

  // Metrics & Timeline
  async getMetricsOverview(): Promise<SingleResponse<OverviewMetrics>> {
    const res = await fetch(`${API_BASE}/metrics/overview`);
    return handleResponse<SingleResponse<OverviewMetrics>>(res);
  },

  async getEvidenceTimeline(limit: number = 20): Promise<SingleResponse<SecurityEvidence[]>> {
    const res = await fetch(`${API_BASE}/metrics/timeline?limit=${limit}`);
    return handleResponse<SingleResponse<SecurityEvidence[]>>(res);
  },

  // Evidence
  async getEvidence(params: {
    page?: number;
    page_size?: number;
    search?: string;
    event_type?: string;
    entity_id?: string;
    agent_id?: string;
    source?: string;
    dataset?: string;
    severity?: string;
    min_risk?: number;
    max_risk?: number;
    start_time?: string;
    end_time?: string;
  }): Promise<PaginatedResponse<SecurityEvidence>> {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page.toString());
    if (params.page_size) query.append('page_size', params.page_size.toString());
    if (params.search) query.append('search', params.search);
    if (params.event_type) query.append('event_type', params.event_type);
    if (params.entity_id) query.append('entity_id', params.entity_id);
    if (params.agent_id) query.append('agent_id', params.agent_id);
    if (params.source) query.append('source', params.source);
    if (params.dataset) query.append('dataset', params.dataset);
    if (params.severity) query.append('severity', params.severity);
    if (params.min_risk !== undefined) query.append('min_risk', params.min_risk.toString());
    if (params.max_risk !== undefined) query.append('max_risk', params.max_risk.toString());
    if (params.start_time) query.append('start_time', params.start_time);
    if (params.end_time) query.append('end_time', params.end_time);

    const res = await fetch(`${API_BASE}/evidence?${query.toString()}`);
    return handleResponse<PaginatedResponse<SecurityEvidence>>(res);
  },

  async getEvidenceById(eventId: string): Promise<SingleResponse<SecurityEvidence>> {
    const res = await fetch(`${API_BASE}/evidence/${encodeURIComponent(eventId)}`);
    return handleResponse<SingleResponse<SecurityEvidence>>(res);
  },

  // Entities
  async getEntities(params: {
    page?: number;
    page_size?: number;
    query?: string;
    entity_type?: string;
  }): Promise<PaginatedResponse<Entity>> {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page.toString());
    if (params.page_size) query.append('page_size', params.page_size.toString());
    if (params.query) query.append('query', params.query);
    if (params.entity_type) query.append('entity_type', params.entity_type);

    const res = await fetch(`${API_BASE}/entities?${query.toString()}`);
    return handleResponse<PaginatedResponse<Entity>>(res);
  },

  async getEntityById(entityId: string): Promise<SingleResponse<EntityDetail>> {
    const res = await fetch(`${API_BASE}/entities/${encodeURIComponent(entityId)}`);
    return handleResponse<SingleResponse<EntityDetail>>(res);
  },

  // Ingestion
  async triggerIngestion(payload: {
    file_path?: string;
    records?: Record<string, any>[];
    source_name?: string;
    policy?: string;
    batch_size?: number;
    dataset_name?: string;
  }): Promise<SingleResponse<IngestionRunResult>> {
    const res = await fetch(`${API_BASE}/ingestion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<SingleResponse<IngestionRunResult>>(res);
  },

  // Reports
  async generateEvidenceReport(payload: {
    entity_id?: string;
    event_type?: string;
    source?: string;
    start_time?: string;
    end_time?: string;
    min_risk?: number;
  }): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/reports/evidence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<SingleResponse<any>>(res);
  },

  async downloadEvidenceReportPdf(payload: {
    entity_id?: string;
    event_type?: string;
    source?: string;
    start_time?: string;
    end_time?: string;
    min_risk?: number;
  }): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/evidence/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to download PDF' }));
      throw new Error(err.detail || 'Failed to generate PDF report');
    }
    return res.blob();
  },

  // Network Security Agent API
  async getNetworkEvents(params: {
    page?: number;
    page_size?: number;
    src_ip?: string;
    dst_ip?: string;
    protocol?: string;
  }): Promise<PaginatedResponse<any>> {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page.toString());
    if (params.page_size) query.append('page_size', params.page_size.toString());
    if (params.src_ip) query.append('src_ip', params.src_ip);
    if (params.dst_ip) query.append('dst_ip', params.dst_ip);
    if (params.protocol) query.append('protocol', params.protocol);

    const res = await fetch(`${API_BASE}/network/events?${query.toString()}`);
    return handleResponse<PaginatedResponse<any>>(res);
  },

  async getNetworkDetections(params: {
    page?: number;
    page_size?: number;
    detector_type?: string;
    category?: string;
    severity?: string;
    min_risk?: number;
    event_id?: string;
  }): Promise<PaginatedResponse<any>> {
    const query = new URLSearchParams();
    if (params.page) query.append('page', params.page.toString());
    if (params.page_size) query.append('page_size', params.page_size.toString());
    if (params.detector_type) query.append('detector_type', params.detector_type);
    if (params.category) query.append('category', params.category);
    if (params.severity) query.append('severity', params.severity);
    if (params.min_risk !== undefined) query.append('min_risk', params.min_risk.toString());
    if (params.event_id) query.append('event_id', params.event_id);

    const res = await fetch(`${API_BASE}/network/detections?${query.toString()}`);
    return handleResponse<PaginatedResponse<any>>(res);
  },

  async getNetworkDetectionById(detectionId: string): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/network/detections/${encodeURIComponent(detectionId)}`);
    return handleResponse<SingleResponse<any>>(res);
  },

  async runNetworkDetection(events: any[]): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/network/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(events),
    });
    return handleResponse<SingleResponse<any>>(res);
  },

  async getNetworkModels(): Promise<SingleResponse<any[]>> {
    const res = await fetch(`${API_BASE}/network/models`);
    return handleResponse<SingleResponse<any[]>>(res);
  },

  async activateNetworkModel(modelId: string): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/network/models/${encodeURIComponent(modelId)}/activate`, {
      method: 'POST',
    });
    return handleResponse<SingleResponse<any>>(res);
  },

  async getNetworkMetrics(): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/network/metrics`);
    return handleResponse<SingleResponse<any>>(res);
  },

  async getNetworkHealth(): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/network/health`);
    return handleResponse<SingleResponse<any>>(res);
  },

  async getNetworkConfig(): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/network/config`);
    return handleResponse<SingleResponse<any>>(res);
  },

  async evaluateNetworkModel(payload: { test_file: string }): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/network/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<SingleResponse<any>>(res);
  },

  async submitDetectionFeedback(payload: {
    detection_id: string;
    label: string;
    analyst_note?: string;
  }): Promise<SingleResponse<any>> {
    const res = await fetch(`${API_BASE}/network/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<SingleResponse<any>>(res);
  },
  // Specialized Security Agents Multi-Domain Security Agents API
  async getPhishingEvents(page: number = 1, limit: number = 50): Promise<any> {
    const res = await fetch(`${API_BASE}/phishing/events?page=${page}&limit=${limit}`);
    return handleResponse<any>(res);
  },

  async getPhishingDetections(page: number = 1, limit: number = 50, minRisk?: number): Promise<any> {
    const query = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (minRisk !== undefined) query.append('min_risk', minRisk.toString());
    const res = await fetch(`${API_BASE}/phishing/detections?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async getPhishingMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/phishing/metrics`);
    return handleResponse<any>(res);
  },

  async getPhishingModels(): Promise<any> {
    const res = await fetch(`${API_BASE}/phishing/models`);
    return handleResponse<any>(res);
  },

  // UBA API
  async getUbaEvents(page: number = 1, limit: number = 50): Promise<any> {
    const res = await fetch(`${API_BASE}/uba/events?page=${page}&limit=${limit}`);
    return handleResponse<any>(res);
  },

  async getUbaDetections(page: number = 1, limit: number = 50, minRisk?: number): Promise<any> {
    const query = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (minRisk !== undefined) query.append('min_risk', minRisk.toString());
    const res = await fetch(`${API_BASE}/uba/detections?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async getUbaProfiles(): Promise<any> {
    const res = await fetch(`${API_BASE}/uba/profiles`);
    return handleResponse<any>(res);
  },

  async getUbaMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/uba/metrics`);
    return handleResponse<any>(res);
  },

  // Identity API
  async getIdentityEvents(page: number = 1, limit: number = 50): Promise<any> {
    const res = await fetch(`${API_BASE}/identity/events?page=${page}&limit=${limit}`);
    return handleResponse<any>(res);
  },

  async getIdentityDetections(page: number = 1, limit: number = 50, minRisk?: number): Promise<any> {
    const query = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (minRisk !== undefined) query.append('min_risk', minRisk.toString());
    const res = await fetch(`${API_BASE}/identity/detections?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async getIdentityMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/identity/metrics`);
    return handleResponse<any>(res);
  },

  // Transaction API
  async getTransactionEvents(page: number = 1, limit: number = 50): Promise<any> {
    const res = await fetch(`${API_BASE}/transactions/events?page=${page}&limit=${limit}`);
    return handleResponse<any>(res);
  },

  async getTransactionDetections(page: number = 1, limit: number = 50, minRisk?: number): Promise<any> {
    const query = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (minRisk !== undefined) query.append('min_risk', minRisk.toString());
    const res = await fetch(`${API_BASE}/transactions/detections?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async getTransactionMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/transactions/metrics`);
    return handleResponse<any>(res);
  },

  // Common Agents API
  async getAllAgents(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/agents`);
    return handleResponse<any[]>(res);
  },

  async getAgentDetail(agentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/agents/${encodeURIComponent(agentId)}`);
    return handleResponse<any>(res);
  },

  async getAgentHealth(agentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/agents/${encodeURIComponent(agentId)}/health`);
    return handleResponse<any>(res);
  },

  // Evidence Fusion Engine & Unified Cyber Risk API
  async getFusionResults(page: number = 1, limit: number = 50, entityId?: string, minRisk?: number): Promise<any> {
    const query = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (entityId) query.append('entity_id', entityId);
    if (minRisk !== undefined) query.append('min_risk', minRisk.toString());
    const res = await fetch(`${API_BASE}/fusion/results?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async getFusionById(fusionId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/fusion/results/${encodeURIComponent(fusionId)}`);
    return handleResponse<any>(res);
  },

  async runFusion(entityId: string, windowSeconds: number = 1800): Promise<any> {
    const res = await fetch(`${API_BASE}/fusion/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ entity_id: entityId, window_seconds: windowSeconds }),
    });
    return handleResponse<any>(res);
  },

  async evaluateFusion(): Promise<any> {
    const res = await fetch(`${API_BASE}/fusion/evaluate`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  async getFusionConflicts(): Promise<any> {
    const res = await fetch(`${API_BASE}/fusion/conflicts`);
    return handleResponse<any>(res);
  },

  async getFusionCoverage(): Promise<any> {
    const res = await fetch(`${API_BASE}/fusion/coverage`);
    return handleResponse<any>(res);
  },

  async getEntityRisk(entityId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/risk/entities/${encodeURIComponent(entityId)}`);
    return handleResponse<any>(res);
  },

  async getFusionMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/fusion/metrics`);
    return handleResponse<any>(res);
  },

  async getFusionConfig(): Promise<any> {
    const res = await fetch(`${API_BASE}/fusion/config`);
    return handleResponse<any>(res);
  },

  // Adaptive Memory & Graph Adaptive Memory, Graph & Temporal API
  async getMemoryHealth(): Promise<any> {
    const res = await fetch(`${API_BASE}/memory/health`);
    return handleResponse<any>(res);
  },

  async getMemoryEvidence(params?: { entity_id?: string; domain?: string; tier?: string; limit?: number }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.entity_id) query.append('entity_id', params.entity_id);
    if (params?.domain) query.append('domain', params.domain);
    if (params?.tier) query.append('tier', params.tier);
    if (params?.limit) query.append('limit', params.limit.toString());
    const res = await fetch(`${API_BASE}/memory/evidence?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async getMemoryContext(entityId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/memory/context/${encodeURIComponent(entityId)}`);
    return handleResponse<any>(res);
  },

  async getMemoryTransitions(): Promise<any> {
    const res = await fetch(`${API_BASE}/memory/transitions`);
    return handleResponse<any>(res);
  },

  async getMemoryAccessLog(): Promise<any> {
    const res = await fetch(`${API_BASE}/memory/access-log`);
    return handleResponse<any>(res);
  },

  async getGraphNode(nodeId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/graph/nodes/${encodeURIComponent(nodeId)}`);
    return handleResponse<any>(res);
  },

  async getGraphSubgraph(nodeId: string, kHop: number = 2, maxNodes: number = 200): Promise<any> {
    const res = await fetch(`${API_BASE}/graph/subgraph/${encodeURIComponent(nodeId)}?k_hop=${kHop}&max_nodes=${maxNodes}`);
    return handleResponse<any>(res);
  },

  async getAttackChains(entityId?: string): Promise<any> {
    const query = entityId ? `?entity_id=${encodeURIComponent(entityId)}` : '';
    const res = await fetch(`${API_BASE}/graph/attack-chains${query}`);
    return handleResponse<any>(res);
  },

  async getTemporalTimeline(entityId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/temporal/timeline/${encodeURIComponent(entityId)}`);
    return handleResponse<any>(res);
  },

  async getTemporalPatterns(): Promise<any> {
    const res = await fetch(`${API_BASE}/temporal/patterns`);
    return handleResponse<any>(res);
  },

  async evaluateAdaptiveMemory(): Promise<any> {
    const res = await fetch(`${API_BASE}/adaptive_memory/evaluate`);
    return handleResponse<any>(res);
  },

  // ============================================================
  // RELIABILITY & TRUST: RELIABILITY, UNCERTAINTY, CALIBRATION, DRIFT & REPUTATION
  // ============================================================
  async getReliabilityHealth(): Promise<any> {
    const res = await fetch(`${API_BASE}/reliability/health`);
    return handleResponse<any>(res);
  },

  async getReliabilityConfig(): Promise<any> {
    const res = await fetch(`${API_BASE}/reliability/config`);
    return handleResponse<any>(res);
  },

  async listAgentReliabilities(params?: { page?: number; page_size?: number; agent_id?: string; domain?: string; status?: string }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.page_size) query.append('page_size', params.page_size.toString());
    if (params?.agent_id) query.append('agent_id', params.agent_id);
    if (params?.domain) query.append('domain', params.domain);
    if (params?.status) query.append('status', params.status);
    const res = await fetch(`${API_BASE}/reliability/agents?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async getAgentReliability(agentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/reliability/agents/${encodeURIComponent(agentId)}`);
    return handleResponse<any>(res);
  },

  async getReliabilityHistory(agentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/reliability/history/${encodeURIComponent(agentId)}`);
    return handleResponse<any>(res);
  },

  async listCalibrationRecords(params?: { page?: number; page_size?: number; agent_id?: string }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.page_size) query.append('page_size', params.page_size.toString());
    if (params?.agent_id) query.append('agent_id', params.agent_id);
    const res = await fetch(`${API_BASE}/reliability/calibration?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async evaluateCalibration(payload: { agent_id: string; predicted_confidences: number[]; observed_outcomes: number[]; calibration_method?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/reliability/calibration/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async listDriftRecords(params?: { page?: number; page_size?: number; agent_id?: string; drift_detected?: boolean }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.page_size) query.append('page_size', params.page_size.toString());
    if (params?.agent_id) query.append('agent_id', params.agent_id);
    if (params?.drift_detected !== undefined) query.append('drift_detected', params.drift_detected.toString());
    const res = await fetch(`${API_BASE}/reliability/drift?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async evaluateDrift(payload: { agent_id: string; feature_or_signal: string; reference_values: number[]; current_values: number[]; drift_method?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/reliability/drift/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async listReliabilityConflicts(params?: { page?: number; page_size?: number; entity_id?: string }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.page_size) query.append('page_size', params.page_size.toString());
    if (params?.entity_id) query.append('entity_id', params.entity_id);
    const res = await fetch(`${API_BASE}/reliability/conflicts?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async listUncertaintyRecords(params?: { page?: number; page_size?: number; agent_id?: string }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.page_size) query.append('page_size', params.page_size.toString());
    if (params?.agent_id) query.append('agent_id', params.agent_id);
    const res = await fetch(`${API_BASE}/reliability/uncertainty?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async listEvidenceQuality(params?: { page?: number; page_size?: number; evidence_id?: string }): Promise<any> {
    const query = new URLSearchParams();
    if (params?.page) query.append('page', params.page.toString());
    if (params?.page_size) query.append('page_size', params.page_size.toString());
    if (params?.evidence_id) query.append('evidence_id', params.evidence_id);
    const res = await fetch(`${API_BASE}/reliability/quality?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async evaluateReliability(payload: { agent_id: string; true_positives: number; false_positives: number; true_negatives: number; false_negatives: number; detector_id?: string; domain?: string; model_version?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/reliability/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async runResearchEvaluation(): Promise<any> {
    const res = await fetch(`${API_BASE}/reliability/research/evaluate`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  // Orchestration Engine APIs
  async getOrchestrationAgents(domain?: string): Promise<any[]> {
    const query = domain ? `?domain=${encodeURIComponent(domain)}` : '';
    const res = await fetch(`${API_BASE}/orchestration/agents${query}`);
    return handleResponse<any[]>(res);
  },

  async getOrchestrationCandidates(params: { context_id: string; event_type: string; domain?: string }): Promise<any> {
    const query = new URLSearchParams({ context_id: params.context_id, event_type: params.event_type });
    if (params.domain) query.append('domain', params.domain);
    const res = await fetch(`${API_BASE}/orchestration/candidates?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async selectOrchestrationAgents(context: any, config?: any): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context, config }),
    });
    return handleResponse<any>(res);
  },

  async invokeOrchestrationAgents(decision_id: string, selected_agent_ids: string[], context: any): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/invoke`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision_id, selected_agent_ids, context }),
    });
    return handleResponse<any>(res);
  },

  async listOrchestrationDecisions(limit: number = 50): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/decisions?limit=${limit}`);
    return handleResponse<any>(res);
  },

  async getOrchestrationDecision(decision_id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/decisions/${encodeURIComponent(decision_id)}`);
    return handleResponse<any>(res);
  },

  async listOrchestrationInvocations(limit: number = 50): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/invocations?limit=${limit}`);
    return handleResponse<any>(res);
  },

  async getOrchestrationMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/metrics`);
    return handleResponse<any>(res);
  },

  async getOrchestrationEvaluation(num_events: number = 10): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/evaluation?num_events=${num_events}`);
    return handleResponse<any>(res);
  },

  async getOrchestrationConfig(): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/config`);
    return handleResponse<any>(res);
  },

  async getOrchestrationHealth(): Promise<any> {
    const res = await fetch(`${API_BASE}/orchestration/health`);
    return handleResponse<any>(res);
  },

  // Zero-Trust Engine Zero-Trust Policy APIs
  async getPolicyHealth(): Promise<any> {
    const res = await fetch(`${API_BASE}/policy-health`);
    return handleResponse<any>(res);
  },

  async listPolicies(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/policies`);
    return handleResponse<any[]>(res);
  },

  async createPolicy(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/policies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async simulatePolicyDecision(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/policies/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async evaluateZeroTrustDecision(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/zero-trust/decide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async listZeroTrustDecisions(limit: number = 50): Promise<any> {
    const res = await fetch(`${API_BASE}/zero-trust/decisions?limit=${limit}`);
    return handleResponse<any>(res);
  },

  async getZeroTrustSecurityContext(entity_id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/security-context/${encodeURIComponent(entity_id)}`);
    return handleResponse<any>(res);
  },

  async getSecurityTags(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/security-tags`);
    return handleResponse<any[]>(res);
  },

  async getSecurityGroups(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/security-groups`);
    return handleResponse<any[]>(res);
  },

  async getSecurityZones(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/security-zones`);
    return handleResponse<any[]>(res);
  },

  async listMicroSegments(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/micro-segmentation/segments`);
    return handleResponse<any[]>(res);
  },

  async simulateMicroSegmentation(subject_zone: string, target_zone: string, action: string): Promise<any> {
    const res = await fetch(`${API_BASE}/micro-segmentation/simulate?subject_zone=${subject_zone}&target_zone=${target_zone}&action=${action}`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  async listEnforcementActions(limit: number = 50): Promise<any[]> {
    const res = await fetch(`${API_BASE}/enforcement/actions?limit=${limit}`);
    return handleResponse<any[]>(res);
  },

  async record2FAEvent(payload: { subject_id: string; status: string; method?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/verification/2fa/event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async listPolicyAuditLogs(limit: number = 50): Promise<any[]> {
    const res = await fetch(`${API_BASE}/policy-audit?limit=${limit}`);
    return handleResponse<any[]>(res);
  },

  // Closed-Loop Adaptation: Closed-Loop Feedback & Adaptation
  async submitFeedback(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async listFeedback(limit: number = 100): Promise<any> {
    const res = await fetch(`${API_BASE}/feedback?limit=${limit}`);
    return handleResponse<any>(res);
  },

  async listOutcomes(limit: number = 100): Promise<any> {
    const res = await fetch(`${API_BASE}/outcomes?limit=${limit}`);
    return handleResponse<any>(res);
  },

  async recordOutcome(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/outcomes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async getAdaptationStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/adaptation`);
    return handleResponse<any>(res);
  },

  async listAdaptationProposals(status?: string): Promise<any> {
    const query = status ? `?status=${status}` : '';
    const res = await fetch(`${API_BASE}/adaptation/proposals${query}`);
    return handleResponse<any>(res);
  },

  async approveAdaptationProposal(proposal_id: string, reviewer: string = 'analyst_admin', reason: string = 'Approved'): Promise<any> {
    const res = await fetch(`${API_BASE}/adaptation/proposals/${proposal_id}/approve?reviewer=${reviewer}&reason=${encodeURIComponent(reason)}`, {
      method: 'POST',
    });
    return handleResponse<any>(res);
  },

  async rejectAdaptationProposal(proposal_id: string, reviewer: string = 'analyst_admin', reason: string = 'Rejected'): Promise<any> {
    const res = await fetch(`${API_BASE}/adaptation/proposals/${proposal_id}/reject?reviewer=${reviewer}&reason=${encodeURIComponent(reason)}`, {
      method: 'POST',
    });
    return handleResponse<any>(res);
  },

  async shadowEvaluateProposal(proposal_id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/adaptation/shadow-evaluate?proposal_id=${proposal_id}`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  async getAdaptationHistory(): Promise<any> {
    const res = await fetch(`${API_BASE}/adaptation/history`);
    return handleResponse<any>(res);
  },

  async getAdaptationStability(): Promise<any> {
    const res = await fetch(`${API_BASE}/adaptation/stability`);
    return handleResponse<any>(res);
  },

  async getChampionModels(): Promise<any> {
    const res = await fetch(`${API_BASE}/models/champion`);
    return handleResponse<any>(res);
  },

  async getChallengerModels(): Promise<any> {
    const res = await fetch(`${API_BASE}/models/challengers`);
    return handleResponse<any>(res);
  },

  async evaluateModels(champion_id: string, challenger_id: string): Promise<any> {
    const res = await fetch(`${API_BASE}/models/evaluate?champion_id=${champion_id}&challenger_id=${challenger_id}`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  async promoteModel(model_id: string, version_id: string, operator: string = 'mlops_admin', reason: string = 'Approved'): Promise<any> {
    const res = await fetch(`${API_BASE}/models/promote?model_id=${model_id}&version_id=${version_id}&operator=${operator}&reason=${encodeURIComponent(reason)}`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  async getPolicyEffectiveness(): Promise<any> {
    const res = await fetch(`${API_BASE}/policy-effectiveness`);
    return handleResponse<any>(res);
  },

  async runDecisionReplay(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/decision-replay/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async runCounterfactual(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/counterfactual/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async getClosedLoopAdaptationHealth(): Promise<any> {
    const res = await fetch(`${API_BASE}/closed_loop_adaptation/health`);
    return handleResponse<any>(res);
  },

  async runEvalBaselines(): Promise<any> {
    const res = await fetch(`${API_BASE}/eval/baselines`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  // Evaluation: Evaluation & Research Reports
  async listEvaluationDatasets(domain?: string): Promise<any> {
    const query = domain ? `?domain=${domain}` : '';
    const res = await fetch(`${API_BASE}/evaluation/datasets${query}`);
    return handleResponse<any>(res);
  },

  async listEvaluationExperiments(): Promise<any> {
    const res = await fetch(`${API_BASE}/evaluation/experiments`);
    return handleResponse<any>(res);
  },

  async runEvaluationExperiment(experiment_id: string = 'EXP_14_END_TO_END', workload_size: number = 10000): Promise<any> {
    const res = await fetch(`${API_BASE}/evaluation/experiments/run?experiment_id=${experiment_id}&workload_size=${workload_size}`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  async getEvaluationMetrics(): Promise<any> {
    const res = await fetch(`${API_BASE}/evaluation/metrics`);
    return handleResponse<any>(res);
  },

  async getScalabilityMatrix(): Promise<any> {
    const res = await fetch(`${API_BASE}/evaluation/scalability`);
    return handleResponse<any>(res);
  },

  async getAblationsMatrix(): Promise<any> {
    const res = await fetch(`${API_BASE}/evaluation/ablations`);
    return handleResponse<any>(res);
  },

  async getBaselinesComparison(): Promise<any> {
    const res = await fetch(`${API_BASE}/evaluation/baselines`);
    return handleResponse<any>(res);
  },

  async listResearchReports(): Promise<any> {
    const res = await fetch(`${API_BASE}/reports`);
    return handleResponse<any>(res);
  },

  async generateResearchReport(experiment_id: string = 'EXP_14_END_TO_END', title: string = 'HACTM Final Report', format: string = 'PDF'): Promise<any> {
    const res = await fetch(`${API_BASE}/reports/generate?experiment_id=${experiment_id}&title=${encodeURIComponent(title)}&format=${format}`, { method: 'POST' });
    return handleResponse<any>(res);
  },

  // Research Validation Validation & Publication Readiness API
  async getResearchValidationSummary(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/validation`);
    return handleResponse<any>(res);
  },

  async validateResearchResult(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/research/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async getResearchStatistics(experiment_id: string = 'EXP-001'): Promise<any> {
    const res = await fetch(`${API_BASE}/research/statistics?experiment_id=${experiment_id}`);
    return handleResponse<any>(res);
  },

  async getResearchSensitivity(experiment_id: string = 'EXP-001'): Promise<any> {
    const res = await fetch(`${API_BASE}/research/sensitivity?experiment_id=${experiment_id}`);
    return handleResponse<any>(res);
  },

  async getResearchRobustness(experiment_id: string = 'EXP-001'): Promise<any> {
    const res = await fetch(`${API_BASE}/research/robustness?experiment_id=${experiment_id}`);
    return handleResponse<any>(res);
  },

  async getResearchCrossDataset(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/cross-dataset`);
    return handleResponse<any>(res);
  },

  async getResearchCrossSession(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/cross-session`);
    return handleResponse<any>(res);
  },

  async getResearchTemporal(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/temporal`);
    return handleResponse<any>(res);
  },

  async getResearchHypotheses(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/hypotheses`);
    return handleResponse<any>(res);
  },

  async getResearchClaims(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/claims`);
    return handleResponse<any>(res);
  },

  async validateResearchClaims(claims: string[]): Promise<any> {
    const res = await fetch(`${API_BASE}/research/claims/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ claims }),
    });
    return handleResponse<any>(res);
  },

  async getResearchReproducibility(experiment_id: string = 'EXP-001'): Promise<any> {
    const res = await fetch(`${API_BASE}/research/reproducibility?experiment_id=${experiment_id}`);
    return handleResponse<any>(res);
  },

  async getResearchProvenance(experiment_id: string = 'EXP-001'): Promise<any> {
    const res = await fetch(`${API_BASE}/research/provenance?experiment_id=${experiment_id}`);
    return handleResponse<any>(res);
  },

  async getResearchThreats(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/threats-validity`);
    return handleResponse<any>(res);
  },

  async getResearchAudit(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/audit`);
    return handleResponse<any>(res);
  },

  async getResearchPublicationStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/publication`);
    return handleResponse<any>(res);
  },

  async generatePublicationPackage(payload: any = {}): Promise<any> {
    const res = await fetch(`${API_BASE}/research/publication/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async getResearchTraceabilityMatrix(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/traceability`);
    return handleResponse<any>(res);
  },

  async getResearchProjectCompletion(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/completion`);
    return handleResponse<any>(res);
  },

  // Zero-Day Detection & Evaluation API
  async getZeroDaySummary(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/zero-day/summary`);
    return handleResponse<any>(res);
  },

  async getZeroDayCandidates(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/zero-day/candidates`);
    return handleResponse<any>(res);
  },

  async runZeroDayEvaluation(payload: { experiment_id?: string; protocol_type?: string; dataset_name?: string; model_name?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/research/zero-day/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async getZeroDayTemporal(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/zero-day/temporal`);
    return handleResponse<any>(res);
  },

  async getZeroDayCrossDataset(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/zero-day/cross-dataset`);
    return handleResponse<any>(res);
  },

  async getZeroDayCalibration(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/zero-day/calibration`);
    return handleResponse<any>(res);
  },

  async getZeroDayFixedFPR(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/zero-day/fixed-fpr`);
    return handleResponse<any>(res);
  },

  async getZeroDayResources(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/zero-day/resources`);
    return handleResponse<any>(res);
  },

  // Threat Intelligence API (AbuseIPDB Integration)
  async getThreatIntelStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/threat-intelligence/status`);
    return handleResponse<any>(res);
  },

  async getThreatIntelIp(ip: string): Promise<any> {
    const res = await fetch(`${API_BASE}/threat-intelligence/ip/${encodeURIComponent(ip)}`);
    return handleResponse<any>(res);
  },
  async getResearchDatasets(): Promise<any> {
    const res = await fetch(`${API_BASE}/research/datasets`);
    return handleResponse<any>(res);
  },

  // Governed Investigation & Work Orders
  async getWorkOrders(agentId?: string, statusFilter?: string): Promise<any> {
    const query = new URLSearchParams();
    if (agentId) query.append('assigned_agent_id', agentId);
    if (statusFilter) query.append('status_filter', statusFilter);
    const res = await fetch(`${API_BASE}/governance/work-orders?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async createWorkOrder(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/governance/work-orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async validateEvidencePack(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/governance/evidence-packs/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  // Human Response Approvals
  async getApprovalRequests(statusFilter?: string): Promise<any> {
    const query = new URLSearchParams();
    if (statusFilter) query.append('status_filter', statusFilter);
    const res = await fetch(`${API_BASE}/governance/approvals?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async proposePolicyAction(payload: any): Promise<any> {
    const res = await fetch(`${API_BASE}/governance/approvals/propose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<any>(res);
  },

  async approveAction(decision: { request_id: string; approver_identity: string; approver_role: string; notes?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/governance/approvals/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(decision),
    });
    return handleResponse<any>(res);
  },

  async rejectAction(decision: { request_id: string; approver_identity: string; approver_role: string; notes?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/governance/approvals/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(decision),
    });
    return handleResponse<any>(res);
  },

  async requestMoreEvidence(decision: { request_id: string; approver_identity: string; approver_role: string; notes?: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/governance/approvals/request-evidence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(decision),
    });
    return handleResponse<any>(res);
  },

  // Audit Trail & Hash-Chain Verification
  async getAuditTrail(incidentId?: string, limit: number = 50): Promise<any> {
    const query = new URLSearchParams();
    if (incidentId) query.append('incident_id', incidentId);
    query.append('limit', limit.toString());
    const res = await fetch(`${API_BASE}/governance/audit-trail?${query.toString()}`);
    return handleResponse<any>(res);
  },

  async verifyAuditTrail(): Promise<any> {
    const res = await fetch(`${API_BASE}/governance/audit-trail/verify`);
    return handleResponse<any>(res);
  },

  // Incident Explanations
  async getIncidentExplanation(incidentId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/incidents/${encodeURIComponent(incidentId)}/explanation`);
    return handleResponse<any>(res);
  },

  // Resilience Evaluation Harness
  async getResilienceScenarios(): Promise<any> {
    const res = await fetch(`${API_BASE}/resilience-evaluation/scenarios`);
    return handleResponse<any>(res);
  },

  async runResilienceEvaluation(): Promise<any> {
    const res = await fetch(`${API_BASE}/resilience-evaluation/run`, { method: 'POST' });
    return handleResponse<any>(res);
  },
};





