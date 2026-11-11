/**
 * Pure utilities for mapping live HACTM workspace events and backend artifacts
 * to the 6 interactive AI Agent Autonomous Loop stages:
 * REASON → PLAN → ACT → OBSERVE → EVALUATE → REPEAT.
 */

import {
  AgentLoopEvent,
  AgentLoopExecutionContext,
  AgentLoopStage,
  AgentLoopStageDetails,
  AgentLoopStageField,
  AgentLoopStageStatus,
  AgentLoopStageToolEntry,
  ApprovalRecord,
  EvidenceDetailRecord,
  TimelineEntry,
  WorkOrderRecord,
  WorkspaceEvent,
} from '../../types/workspace';

export interface LoopStageMetadata {
  stage: AgentLoopStage;
  stageNumber: number;
  title: string;
  shortLabel: string;
  icon: string;
  description: string;
  triggerHint: string;
}

export const AGENT_LOOP_STAGE_ORDER: AgentLoopStage[] = [
  'REASON',
  'PLAN',
  'ACT',
  'OBSERVE',
  'EVALUATE',
  'REPEAT',
];

export const AGENT_LOOP_STAGE_METADATA: Record<AgentLoopStage, LoopStageMetadata> = {
  REASON: {
    stage: 'REASON',
    stageNumber: 1,
    title: 'REASON',
    shortLabel: 'Problem & Context',
    icon: 'reason',
    description: 'The agent analyses incoming information and interprets its objective.',
    triggerHint: 'Driven by incident_created and initial ingestion context.',
  },
  PLAN: {
    stage: 'PLAN',
    stageNumber: 2,
    title: 'PLAN',
    shortLabel: 'Plan & Delegate',
    icon: 'plan',
    description:
      'The agent develops a structured investigation plan based on the task and available evidence.',
    triggerHint: 'Driven by task_assigned, governed Work Orders, and orchestrator selections.',
  },
  ACT: {
    stage: 'ACT',
    stageNumber: 3,
    title: 'ACT',
    shortLabel: 'Execute & Tools',
    icon: 'act',
    description:
      'The agent executes authorised operations and performs its assigned investigation.',
    triggerHint: 'Driven by task_started, tool_access_granted, and tool_access_denied events.',
  },
  OBSERVE: {
    stage: 'OBSERVE',
    stageNumber: 4,
    title: 'OBSERVE',
    shortLabel: 'Evidence & Comms',
    icon: 'observe',
    description:
      'The agent or monitoring system observes execution results and collects feedback.',
    triggerHint: 'Driven by evidence_generated, agent_message, and external intel outputs.',
  },
  EVALUATE: {
    stage: 'EVALUATE',
    stageNumber: 5,
    title: 'EVALUATE',
    shortLabel: 'Policy & Risk Eval',
    icon: 'evaluate',
    description:
      'The system evaluates the results against the assigned objective, evidence quality and applicable policies.',
    triggerHint:
      'Driven by risk_updated, evidence_conflict, and Human Approval Gate decisions.',
  },
  REPEAT: {
    stage: 'REPEAT',
    stageNumber: 6,
    title: 'REPEAT',
    shortLabel: 'Iterate / Conclude',
    icon: 'repeat',
    description:
      'The agent or orchestrator determines whether another investigation cycle is required.',
    triggerHint:
      'Driven by investigation_replanned, reassignments, response_verified, and incident_closed.',
  },
};

const STAGE_INDEX: Record<AgentLoopStage, number> = {
  REASON: 0,
  PLAN: 1,
  ACT: 2,
  OBSERVE: 3,
  EVALUATE: 4,
  REPEAT: 5,
};

/** Maps a HACTM backend SSE event type to its corresponding Autonomous Loop stage. */
export function mapEventTypeToLoopStage(eventType: string): AgentLoopStage | null {
  switch (eventType) {
    case 'incident_created':
      return 'REASON';
    case 'task_assigned':
      return 'PLAN';
    case 'task_started':
    case 'agent_tool_request':
    case 'tool_access_granted':
    case 'tool_access_denied':
    case 'agent_capability_revoked':
    case 'agent_capability_restricted':
      return 'ACT';
    case 'evidence_generated':
    case 'agent_message':
      return 'OBSERVE';
    case 'evidence_conflict':
    case 'agent_evidence_flagged':
    case 'risk_updated':
    case 'approval_requested':
    case 'approval_granted':
    case 'approval_rejected':
      return 'EVALUATE';
    case 'investigation_replanned':
    case 'task_reassigned':
    case 'agent_reassigned':
    case 'response_executed':
    case 'response_verified':
    case 'incident_closed':
      return 'REPEAT';
    default:
      return null;
  }
}

export interface DerivedAgentLoopState {
  stageDetailsByStage: Record<AgentLoopStage, AgentLoopStageDetails>;
  liveStage: AgentLoopStage | null;
  completedCount: number;
  isConcluded: boolean;
  cycleCount: number;
  activeIncidentId?: string;
}

function formatPct(value: number | undefined | null): string {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'Not available';
  return `${(value * 100).toFixed(1)}%`;
}

function formatTimestamp(ts?: string | null): string {
  if (!ts) return 'Not available';
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  return d.toLocaleTimeString();
}

function uniqueStrings(values: Array<string | undefined | null>): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  values.forEach((v) => {
    if (v && v.trim() && !seen.has(v)) {
      seen.add(v);
      out.push(v);
    }
  });
  return out;
}

function filterEventsForActiveIncident(
  workspaceEvents: WorkspaceEvent[],
  currentIncidentId?: string | null
): { events: WorkspaceEvent[]; activeIncidentId?: string } {
  const resolvedIncidentId =
    currentIncidentId ||
    [...workspaceEvents].reverse().find((e) => Boolean(e.incident_id))?.incident_id;

  if (!resolvedIncidentId) {
    return { events: workspaceEvents, activeIncidentId: undefined };
  }

  // Find when the active incident started so global non-incident events (e.g. tool deny during demo) attach cleanly
  const firstIncidentIdx = workspaceEvents.findIndex((e) => e.incident_id === resolvedIncidentId);
  const filtered = workspaceEvents.filter((e, idx) => {
    if (e.incident_id) {
      return e.incident_id === resolvedIncidentId;
    }
    return firstIncidentIdx >= 0 && idx >= firstIncidentIdx;
  });

  return { events: filtered, activeIncidentId: resolvedIncidentId };
}

function normalizeToLoopEvents(scopedEvents: WorkspaceEvent[]): {
  loopEvents: AgentLoopEvent[];
  governanceAlerts: WorkspaceEvent[];
} {
  const loopEvents: AgentLoopEvent[] = [];
  const governanceAlerts: WorkspaceEvent[] = [];

  scopedEvents.forEach((ev, idx) => {
    const stage = mapEventTypeToLoopStage(ev.event_type);
    if (stage) {
      loopEvents.push({
        eventId: ev.event_id || `EVT-${idx}`,
        eventType: ev.event_type,
        stage,
        status: ev.status,
        message: ev.message,
        timestamp: ev.timestamp,
        incidentId: ev.incident_id,
        taskId: ev.task_id,
        agentId: ev.agent_id,
        evidenceId: ev.data?.evidence_id || ev.data?.evidence_ref,
        data: ev.data,
      });
    } else if (
      [
        'agent_isolated',
        'agent_anomaly_detected',
        'agent_behaviour_deviation',
        'agent_warning_issued',
        'orchestrator_anomaly_detected',
      ].includes(ev.event_type)
    ) {
      governanceAlerts.push(ev);
    }
  });

  return { loopEvents, governanceAlerts };
}

function pickPrimaryWorkOrder(
  workOrders: WorkOrderRecord[],
  incidentId?: string
): WorkOrderRecord | undefined {
  if (workOrders.length === 0) return undefined;
  if (incidentId) {
    const match = workOrders.find((w) => w.parent_incident_id === incidentId);
    if (match) return match;
  }
  return undefined;
}

function pickPrimaryApproval(
  approvals: ApprovalRecord[],
  incidentId?: string
): ApprovalRecord | undefined {
  if (approvals.length === 0) return undefined;
  if (incidentId) {
    const match = approvals.find((a) => a.incident_id === incidentId);
    if (match) return match;
  }
  return undefined;
}

function buildReasonFields(
  events: AgentLoopEvent[],
  incidentId: string | undefined,
  workOrder: WorkOrderRecord | undefined,
  evidenceRecords: EvidenceDetailRecord[],
  primaryEvidenceData: Record<string, any> | undefined
): { fields: AgentLoopStageField[]; uncertainties: string[] } {
  const createdEv = events.find((e) => e.eventType === 'incident_created');
  const firstEv = createdEv || events[0];
  const agentId = firstEv?.agentId || workOrder?.assigned_agent_id || 'Not available';

  const observations = uniqueStrings([
    createdEv?.data?.scenario ? `Scenario: ${createdEv.data.scenario}` : undefined,
    createdEv?.data?.sender ? `Sender: ${createdEv.data.sender}` : undefined,
    createdEv?.data?.subject ? `Subject: ${createdEv.data.subject}` : undefined,
    createdEv?.data?.target_user ? `Target User: ${createdEv.data.target_user}` : undefined,
    firstEv?.message,
  ]);

  const contextItems = uniqueStrings([
    ...(workOrder?.data_sources || []).map((ds) => `Source: ${ds}`),
    ...(workOrder?.scope
      ? Object.entries(workOrder.scope).map(([k, v]) => `${k}: ${String(v)}`)
      : []),
    ...evidenceRecords.map((er) => `Entity: ${er.entity_id} (${er.event_type})`),
  ]);

  const uncertainties = uniqueStrings([
    ...(workOrder?.required_questions || []),
    ...(workOrder?.evidence_pack?.assumptions || []),
    typeof primaryEvidenceData?.uncertainty === 'number'
      ? `Initial predictive uncertainty: ${formatPct(primaryEvidenceData.uncertainty)}`
      : undefined,
  ]);

  const reasoningSummary =
    workOrder?.objective ||
    (createdEv?.data?.scenario
      ? `Interpreted ${createdEv.data.scenario} against entity ${createdEv.data.target_user || 'unknown'}.`
      : firstEv?.message) ||
    'Not available';

  const evidenceRefs = uniqueStrings([
    ...events.map((e) => e.evidenceId),
    ...evidenceRecords.map((e) => e.event_id),
  ]);

  const fields: AgentLoopStageField[] = [
    { label: 'Agent ID', value: agentId, tone: 'cyan' },
    { label: 'Current Incident', value: incidentId || 'Not available', tone: 'mono' },
    {
      label: 'Input Observations',
      value: observations.length > 0 ? observations : ['Not available'],
    },
    {
      label: 'Retrieved Context',
      value: contextItems.length > 0 ? contextItems : ['Not available'],
    },
    {
      label: 'Relevant Evidence References',
      value: evidenceRefs.length > 0 ? evidenceRefs : ['Not available'],
      tone: 'cyan',
    },
    { label: 'Reasoning Summary', value: reasoningSummary },
    {
      label: 'Identified Uncertainties',
      value: uncertainties.length > 0 ? uncertainties : ['None flagged in initial ingestion'],
      tone: uncertainties.length > 0 ? 'amber' : 'slate',
    },
    { label: 'Reasoning Timestamp', value: formatTimestamp(firstEv?.timestamp), tone: 'mono' },
  ];

  return { fields, uncertainties };
}

function buildPlanFields(
  events: AgentLoopEvent[],
  incidentId: string | undefined,
  workOrder: WorkOrderRecord | undefined
): AgentLoopStageField[] {
  const latestPlanEv = events[events.length - 1];
  const selectedAgents = uniqueStrings([
    workOrder?.assigned_agent_id,
    ...events.map((e) => e.agentId),
  ]);

  const steps = uniqueStrings([
    ...(workOrder?.required_questions || []).map((q, i) => `Q${i + 1}: ${q}`),
    ...(workOrder?.success_criteria || []).map((c) => `Success Criterion: ${c}`),
    ...events.map((e) => `${e.taskId ? `[${e.taskId}] ` : ''}${e.message}`),
  ]);

  const dependencies = uniqueStrings([
    incidentId ? `Parent Incident: ${incidentId}` : undefined,
    workOrder?.investigation_id ? `Investigation ID: ${workOrder.investigation_id}` : undefined,
    workOrder?.data_sources?.length
      ? `Data Sources: ${workOrder.data_sources.join(', ')}`
      : undefined,
  ]);

  const budgetEntries = workOrder?.resource_limits
    ? Object.entries(workOrder.resource_limits).map(([k, v]) => `${k}: ${String(v)}`)
    : [];

  return [
    {
      label: 'Assigned Objective',
      value: workOrder?.objective || latestPlanEv?.message || 'Not available',
    },
    {
      label: 'Investigation Steps & Orchestrator Plan',
      value: steps.length > 0 ? steps : ['Not available'],
    },
    {
      label: 'Selected Specialist Agents',
      value: selectedAgents.length > 0 ? selectedAgents : ['Not available'],
      tone: 'cyan',
    },
    {
      label: 'Task Dependencies',
      value: dependencies.length > 0 ? dependencies : ['Not available'],
      tone: 'mono',
    },
    {
      label: 'Tool Requirements',
      value:
        workOrder?.permitted_tools && workOrder.permitted_tools.length > 0
          ? workOrder.permitted_tools
          : ['Not available'],
      tone: 'mono',
    },
    {
      label: 'Execution Budget',
      value: budgetEntries.length > 0 ? budgetEntries : ['Not available'],
      tone: 'mono',
    },
    {
      label: 'Expected Evidence',
      value:
        workOrder?.required_evidence && workOrder.required_evidence.length > 0
          ? workOrder.required_evidence
          : ['Not available'],
    },
    {
      label: 'Plan Status',
      value: workOrder?.status || latestPlanEv?.status || 'Not available',
      tone: 'emerald',
    },
    {
      label: 'Planning Timestamp',
      value: formatTimestamp(latestPlanEv?.timestamp || workOrder?.created_at),
      tone: 'mono',
    },
  ];
}

function buildActFields(
  events: AgentLoopEvent[],
  governanceAlerts: WorkspaceEvent[],
  workOrder: WorkOrderRecord | undefined,
  context: AgentLoopExecutionContext
): {
  fields: AgentLoopStageField[];
  toolHistory: AgentLoopStageToolEntry[];
  restrictionsOrDenials: string[];
} {
  const latestActEv = events[events.length - 1];
  const executingAgentId =
    events.find((e) => e.agentId)?.agentId || workOrder?.assigned_agent_id || 'Not available';
  const agentObj = context.agents.find((a) => a.agent_id === executingAgentId);

  const toolHistory: AgentLoopStageToolEntry[] = [];
  if (workOrder?.evidence_pack?.tool_use_log) {
    workOrder.evidence_pack.tool_use_log.forEach((entry) => {
      toolHistory.push({
        toolName: String(entry.tool_name || 'unknown_tool'),
        status: String(entry.status || 'EXECUTED'),
        detail: workOrder.work_order_id ? `Work Order ${workOrder.work_order_id}` : undefined,
      });
    });
  }

  events.forEach((ev) => {
    if (
      ev.eventType === 'tool_access_granted' ||
      ev.eventType === 'tool_access_denied' ||
      ev.eventType === 'agent_tool_request'
    ) {
      toolHistory.push({
        toolName: String(ev.data?.tool || ev.data?.tool_name || 'tool_request'),
        status: ev.eventType === 'tool_access_denied' ? 'DENIED' : 'AUTHORIZED',
        timestamp: ev.timestamp,
        detail: ev.data?.error || ev.message,
      });
    }
  });

  const restrictionsOrDenials = uniqueStrings([
    ...events
      .filter((e) =>
        ['tool_access_denied', 'agent_capability_revoked', 'agent_capability_restricted'].includes(
          e.eventType
        )
      )
      .map((e) => e.message),
    ...governanceAlerts.map((a) => `${a.event_type.toUpperCase()}: ${a.message}`),
    ...(workOrder?.forbidden_actions?.length
      ? [`Forbidden Operations: ${workOrder.forbidden_actions.join(', ')}`]
      : []),
  ]);

  const authorisedOps = uniqueStrings([
    ...(workOrder?.permitted_tools || []),
    ...(agentObj?.toolPermissions || []),
  ]);

  const completedResults = uniqueStrings([
    ...(workOrder?.evidence_pack?.claims || []).map((c) => String(c.claim || '')),
    workOrder?.evidence_pack?.completion_status
      ? `Evidence Pack Status: ${workOrder.evidence_pack.completion_status}`
      : undefined,
    latestActEv?.message,
  ]);

  const currentTaskRef =
    events.find((e) => e.taskId)?.taskId || workOrder?.work_order_id || 'Not available';

  const fields: AgentLoopStageField[] = [
    { label: 'Executing Agent', value: executingAgentId, tone: 'cyan' },
    { label: 'Current Task', value: latestActEv?.message || 'Not available' },
    { label: 'Work-Order Reference', value: currentTaskRef, tone: 'mono' },
    {
      label: 'Authorised Operations',
      value: authorisedOps.length > 0 ? authorisedOps : ['Not available'],
      tone: 'mono',
    },
    {
      label: 'Results of Completed Actions',
      value: completedResults.length > 0 ? completedResults : ['Not available'],
    },
    {
      label: 'Action Timestamp',
      value: formatTimestamp(latestActEv?.timestamp),
      tone: 'mono',
    },
  ];

  return { fields, toolHistory, restrictionsOrDenials };
}

function buildObserveFields(
  events: AgentLoopEvent[],
  workOrder: WorkOrderRecord | undefined,
  context: AgentLoopExecutionContext
): {
  fields: AgentLoopStageField[];
  contradictions: string[];
  agentMessages: AgentLoopExecutionContext['messages'];
  evidenceRefs: string[];
} {
  const latestObsEv = events[events.length - 1];
  const evidenceEvents = events.filter((e) => e.eventType === 'evidence_generated');
  const messageEvents = events.filter((e) => e.eventType === 'agent_message');

  const evidenceRefs = uniqueStrings([
    ...events.map((e) => e.evidenceId),
    ...context.evidenceRecords.map((r) => r.event_id),
  ]);

  const generatedEvidenceSummaries = uniqueStrings([
    ...evidenceEvents.map(
      (e) =>
        `${e.evidenceId || 'Evidence'}: ${e.message}${
          typeof e.data?.risk_score === 'number'
            ? ` (Risk ${(e.data.risk_score * 100).toFixed(0)}%)`
            : ''
        }`
    ),
    ...context.evidenceRecords.map(
      (r) =>
        `${r.event_id} [${r.severity}] Risk ${(r.risk_score * 100).toFixed(0)}% | Confidence ${(
          r.confidence * 100
        ).toFixed(0)}%`
    ),
  ]);

  const toolResponses = uniqueStrings([
    ...(workOrder?.evidence_pack?.tool_use_log || []).map(
      (t) => `${String(t.tool_name)}: ${String(t.status)}`
    ),
    ...(workOrder?.evidence_pack?.supporting_evidence || []).map(
      (s) => `${String(s.evidence_id || s.type || 'Support')} (Risk: ${String(s.risk_score ?? 'N/A')})`
    ),
  ]);

  const externalIntel = uniqueStrings([
    ...messageEvents
      .filter(
        (m) =>
          m.agentId?.includes('threat-intel') ||
          m.data?.sender?.includes('threat-intel') ||
          m.data?.recipient?.includes('threat-intel')
      )
      .map((m) => m.message),
  ]);

  const contradictions = uniqueStrings([
    ...(workOrder?.evidence_pack?.contradicting_evidence || []).map((c) => JSON.stringify(c)),
    ...context.evidenceRecords.flatMap((r) =>
      Array.isArray(r.evidence?.contradictory_findings)
        ? r.evidence.contradictory_findings.map((item: unknown) => String(item))
        : []
    ),
  ]);

  const provenanceItems = uniqueStrings([
    ...context.evidenceRecords.map((r) =>
      r.evidence?.forensic_provenance ? String(r.evidence.forensic_provenance) : undefined
    ),
    ...context.auditTrail
      .filter((a) => a.record_hash)
      .slice(0, 3)
      .map((a) => `Audit ${a.event_type}: ${String(a.record_hash).slice(0, 18)}…`),
    ...evidenceEvents.map((e) => (e.agentId ? `Producer Agent: ${e.agentId}` : undefined)),
  ]);

  const incidentMessages = context.messages.filter(
    (m) => !context.incidentId || m.incidentId === context.incidentId
  );

  const taskCompletions = uniqueStrings([
    workOrder?.status ? `Work Order ${workOrder.work_order_id}: ${workOrder.status}` : undefined,
    ...evidenceEvents.map((e) => `Observation recorded at ${formatTimestamp(e.timestamp)}`),
  ]);

  const fields: AgentLoopStageField[] = [
    {
      label: 'SecurityEvidence Generated',
      value: generatedEvidenceSummaries.length > 0 ? generatedEvidenceSummaries : ['Not available'],
      tone: 'cyan',
    },
    {
      label: 'Tool Responses',
      value: toolResponses.length > 0 ? toolResponses : ['Not available'],
      tone: 'mono',
    },
    {
      label: 'External Intelligence Observations',
      value: externalIntel.length > 0 ? externalIntel : ['No external intel messages recorded'],
    },
    {
      label: 'Task Completion Events',
      value: taskCompletions.length > 0 ? taskCompletions : ['Not available'],
    },
    {
      label: 'Contradictory Findings',
      value: contradictions.length > 0 ? contradictions : ['0 contradictions detected'],
      tone: contradictions.length > 0 ? 'amber' : 'emerald',
    },
    {
      label: 'Evidence Provenance',
      value: provenanceItems.length > 0 ? provenanceItems : ['Not available'],
      tone: 'mono',
    },
    {
      label: 'Latest Observation Timestamp',
      value: formatTimestamp(latestObsEv?.timestamp),
      tone: 'mono',
    },
  ];

  return { fields, contradictions, agentMessages: incidentMessages, evidenceRefs };
}

function buildEvaluateFields(
  events: AgentLoopEvent[],
  observeEvents: AgentLoopEvent[],
  workOrder: WorkOrderRecord | undefined,
  approval: ApprovalRecord | undefined,
  context: AgentLoopExecutionContext,
  hasReplanAfterEval: boolean
): { fields: AgentLoopStageField[]; contradictions: string[] } {
  const riskEv = [...events].reverse().find((e) => e.eventType === 'risk_updated');
  const approvalEv = [...events]
    .reverse()
    .find((e) =>
      ['approval_granted', 'approval_rejected', 'approval_requested'].includes(e.eventType)
    );
  const conflictEvents = events.filter(
    (e) => e.eventType === 'evidence_conflict' || e.eventType === 'agent_evidence_flagged'
  );
  const obsEvidenceEv = [...observeEvents]
    .reverse()
    .find((e) => e.eventType === 'evidence_generated');
  const primaryEvidence = context.evidenceRecords[0];

  const confidenceVal =
    approval?.confidence ??
    workOrder?.evidence_pack?.confidence ??
    obsEvidenceEv?.data?.confidence ??
    primaryEvidence?.confidence;

  const uncertaintyVal =
    riskEv?.data?.uncertainty ??
    approval?.uncertainty ??
    workOrder?.evidence_pack?.uncertainty ??
    obsEvidenceEv?.data?.uncertainty ??
    primaryEvidence?.uncertainty;

  const fusedRiskVal =
    riskEv?.data?.fused_risk ??
    riskEv?.data?.risk_score ??
    approval?.risk_score ??
    obsEvidenceEv?.data?.risk_score ??
    primaryEvidence?.risk_score;

  const severityVal =
    riskEv?.data?.severity ?? primaryEvidence?.severity ?? undefined;

  const primaryAgent = context.agents.find(
    (a) =>
      a.agent_id ===
      (workOrder?.assigned_agent_id || obsEvidenceEv?.agentId || primaryEvidence?.agent_id)
  );

  const requiredEvCount = workOrder?.required_evidence?.length ?? 0;
  const supportCount = workOrder?.evidence_pack?.supporting_evidence?.length ?? context.evidenceRecords.length;
  const completenessLabel =
    workOrder?.evidence_pack || supportCount > 0
      ? `${supportCount} supporting item(s)${
          requiredEvCount > 0 ? ` against ${requiredEvCount} required types (${workOrder?.required_evidence?.join(', ')})` : ''
        }`
      : 'Not available';

  const contradictions = uniqueStrings([
    ...conflictEvents.map((e) => e.message),
    ...(workOrder?.evidence_pack?.contradicting_evidence || []).map((c) => JSON.stringify(c)),
  ]);

  const policyText = approval
    ? `${approval.policy_id || 'Policy'} — ${approval.action_type} [${approval.status}]${
        approval.justification ? `: ${approval.justification}` : ''
      }`
    : approvalEv?.message || 'Not available';

  const decisionText = approvalEv
    ? approvalEv.eventType === 'approval_granted'
      ? `APPROVED by ${approvalEv.data?.approver || approval?.approver_identity || 'Human Approver'}`
      : approvalEv.eventType === 'approval_rejected'
      ? `REJECTED by ${approvalEv.data?.approver || approval?.approver_identity || 'Human Approver'}`
      : `WAITING_FOR_APPROVAL (${approval?.request_id || approvalEv.data?.request_id || 'Pending'})`
    : workOrder?.evidence_pack?.completion_status || 'Not available';

  let additionalNeeded = 'Not available';
  if (hasReplanAfterEval || approval?.status === 'MORE_EVIDENCE_REQUESTED') {
    additionalNeeded = 'YES — Additional evidence requested / investigation replanned';
  } else if (approvalEv?.eventType === 'approval_granted' && contradictions.length === 0) {
    additionalNeeded = 'NO — Evidence & policy threshold satisfied';
  } else if (approvalEv?.eventType === 'approval_rejected') {
    additionalNeeded = 'YES — Proposed action rejected; manual review required';
  } else if (approvalEv?.eventType === 'approval_requested') {
    additionalNeeded = 'PENDING — Awaiting Human Approval Gate decision';
  } else if (contradictions.length > 0) {
    additionalNeeded = 'YES — Contradictions detected in evidence stream';
  }

  const fields: AgentLoopStageField[] = [
    { label: 'Evidence Completeness', value: completenessLabel },
    {
      label: 'Evidence Reliability',
      value: primaryAgent
        ? `${primaryAgent.name}: ${(primaryAgent.reliabilityScore * 100).toFixed(1)}%`
        : 'Not available',
      tone: 'cyan',
    },
    {
      label: 'Confidence & Uncertainty',
      value:
        confidenceVal !== undefined || uncertaintyVal !== undefined
          ? `Confidence: ${formatPct(confidenceVal)} | Uncertainty: ${formatPct(uncertaintyVal)}`
          : 'Not available',
      tone: 'mono',
    },
    {
      label: 'Detected Contradictions',
      value: contradictions.length > 0 ? contradictions : ['0 contradicting findings'],
      tone: contradictions.length > 0 ? 'amber' : 'emerald',
    },
    { label: 'Policy Evaluation', value: policyText },
    {
      label: 'Risk Assessment',
      value:
        fusedRiskVal !== undefined
          ? `Score: ${formatPct(fusedRiskVal)}${severityVal ? ` [${severityVal}]` : ''}`
          : 'Not available',
      tone: typeof fusedRiskVal === 'number' && fusedRiskVal >= 0.7 ? 'red' : 'amber',
    },
    { label: 'Task Completion Decision', value: decisionText, tone: 'cyan' },
    { label: 'Additional Investigation Required', value: additionalNeeded },
  ];

  return { fields, contradictions };
}

function buildRepeatFields(
  events: AgentLoopEvent[],
  workOrder: WorkOrderRecord | undefined,
  approval: ApprovalRecord | undefined,
  cycleCount: number,
  isConcluded: boolean,
  hasStarted: boolean,
  pendingEvalWait: boolean,
  evalFailed: boolean
): AgentLoopStageField[] {
  const latestRepeatEv = events[events.length - 1];
  const replanEvents = events.filter((e) => e.eventType === 'investigation_replanned');
  const reassignEvents = events.filter(
    (e) => e.eventType === 'agent_reassigned' || e.eventType === 'task_reassigned'
  );
  const verifyEv = events.find(
    (e) => e.eventType === 'response_verified' || e.eventType === 'incident_closed'
  );
  const execEv = events.find((e) => e.eventType === 'response_executed');

  const gaps = uniqueStrings([
    ...(workOrder?.evidence_pack?.assumptions || []),
    workOrder?.evidence_pack?.reason_for_incomplete_work || undefined,
    approval?.approval_notes || undefined,
    ...replanEvents.map((e) => e.data?.notes || e.message),
  ]);

  const remainingSteps = !hasStarted
    ? ['Not available']
    : isConcluded
    ? ['0 remaining — Response verified and cycle concluded']
    : pendingEvalWait
    ? ['Execute & verify gated response after Human Approval']
    : evalFailed
    ? ['Determine alternative remediation after rejection']
    : replanEvents.length > 0
    ? ['Execute follow-up evidence collection round']
    : ['Complete active evaluation cycle'];

  const nextAction =
    workOrder?.evidence_pack?.recommended_next_step ||
    (isConcluded
      ? 'Monitor post-containment telemetry'
      : pendingEvalWait
      ? approval?.proposed_action || 'Await Human Approval decision'
      : latestRepeatEv?.message || 'Not available');

  const stopOrContinueReason = isConcluded
    ? verifyEv?.message || 'Containment executed and verified in immutable audit trail.'
    : replanEvents.length > 0
    ? replanEvents[replanEvents.length - 1].message
    : execEv
    ? execEv.message
    : evalFailed
    ? 'Halted automated response following rejection at Human Approval Gate.'
    : pendingEvalWait
    ? 'Paused before final cycle closure pending Human Approval Gate.'
    : 'Not available';

  const completionStatus = isConcluded
    ? 'COMPLETED'
    : replanEvents.length > 0
    ? 'CONTINUING (NEXT CYCLE REQUESTED)'
    : evalFailed
    ? 'STOPPED (REJECTED)'
    : pendingEvalWait
    ? 'AWAITING_HUMAN_GATE'
    : 'Not available';

  return [
    {
      label: 'Previous Cycle',
      value: !hasStarted
        ? 'Not available'
        : cycleCount > 1
        ? `Cycle #${cycleCount - 1}`
        : 'None (Initial Cycle)',
      tone: 'mono',
    },
    {
      label: 'Current Cycle',
      value: hasStarted ? `Cycle #${cycleCount}` : 'Not available',
      tone: 'mono',
    },
    { label: 'Remaining Investigation Steps', value: remainingSteps },
    {
      label: 'Newly Discovered Evidence Gaps',
      value: gaps.length > 0 ? gaps : ['None reported'],
      tone: gaps.length > 0 ? 'amber' : 'slate',
    },
    { label: 'Next Requested Action', value: nextAction, tone: 'cyan' },
    {
      label: 'Agent Reassignment',
      value:
        reassignEvents.length > 0
          ? reassignEvents.map((r) => r.message)
          : ['No reassignment recorded'],
    },
    { label: 'Reason for Continuing or Stopping', value: stopOrContinueReason },
    {
      label: 'Investigation Completion Status',
      value: completionStatus,
      tone: isConcluded ? 'emerald' : evalFailed ? 'red' : 'amber',
    },
  ];
}

/**
 * Derives per-stage status, active backend loop stage, and strictly real details
 * from actual HACTM workspace SSE events and optional read-only backend records.
 */
export function deriveAgentLoopState(
  workspaceEvents: WorkspaceEvent[],
  timeline: TimelineEntry[],
  context: AgentLoopExecutionContext
): DerivedAgentLoopState {
  const { events: scopedEvents, activeIncidentId } = filterEventsForActiveIncident(
    workspaceEvents,
    context.incidentId
  );
  const { loopEvents: rawLoopEvents, governanceAlerts } = normalizeToLoopEvents(scopedEvents);

  // Fallback compatibility if component is driven solely via timeline entries (exclude stream_connected)
  const nonStreamTimeline = timeline.filter((t) => t.step !== 'stream_connected');
  const loopEvents: AgentLoopEvent[] =
    rawLoopEvents.length > 0
      ? rawLoopEvents
      : [...nonStreamTimeline]
          .reverse()
          .map((entry) => {
            const mapped = mapEventTypeToLoopStage(entry.step);
            if (!mapped) return null;
            return {
              eventId: entry.id,
              eventType: entry.step,
              stage: mapped,
              status: entry.status,
              message: entry.description,
              timestamp: entry.timestamp,
              incidentId: entry.incidentId,
              agentId: entry.agentId,
              evidenceId: entry.evidenceId,
            } as AgentLoopEvent;
          })
          .filter((item): item is AgentLoopEvent => item !== null);

  const statuses: Record<AgentLoopStage, AgentLoopStageStatus> = {
    REASON: 'NOT_STARTED',
    PLAN: 'NOT_STARTED',
    ACT: 'NOT_STARTED',
    OBSERVE: 'NOT_STARTED',
    EVALUATE: 'NOT_STARTED',
    REPEAT: 'NOT_STARTED',
  };

  const eventsByStage: Record<AgentLoopStage, AgentLoopEvent[]> = {
    REASON: [],
    PLAN: [],
    ACT: [],
    OBSERVE: [],
    EVALUATE: [],
    REPEAT: [],
  };

  let highestStageIdx = -1;
  let liveStage: AgentLoopStage | null = null;
  let isConcluded = false;
  let cycleCount = 1;
  let hasReplanAfterEval = false;

  loopEvents.forEach((ev) => {
    eventsByStage[ev.stage].push(ev);
    const idx = STAGE_INDEX[ev.stage];

    if (ev.eventType === 'incident_closed' || ev.eventType === 'response_verified') {
      AGENT_LOOP_STAGE_ORDER.slice(0, 5).forEach((s) => {
        if (statuses[s] !== 'FAILED' && statuses[s] !== 'BLOCKED') {
          statuses[s] = 'COMPLETED';
        }
      });
      statuses.REPEAT = 'COMPLETED';
      highestStageIdx = 5;
      liveStage = 'REPEAT';
      isConcluded = true;
      return;
    }

    if (ev.eventType === 'approval_rejected') {
      AGENT_LOOP_STAGE_ORDER.slice(0, 4).forEach((s) => {
        if (statuses[s] !== 'FAILED' && statuses[s] !== 'BLOCKED') {
          statuses[s] = 'COMPLETED';
        }
      });
      statuses.EVALUATE = 'FAILED';
      highestStageIdx = Math.max(highestStageIdx, 4);
      liveStage = 'EVALUATE';
      return;
    }

    if (ev.eventType === 'approval_requested') {
      AGENT_LOOP_STAGE_ORDER.slice(0, 4).forEach((s) => {
        if (statuses[s] !== 'FAILED' && statuses[s] !== 'BLOCKED') {
          statuses[s] = 'COMPLETED';
        }
      });
      statuses.EVALUATE = 'WAITING';
      highestStageIdx = Math.max(highestStageIdx, 4);
      liveStage = 'EVALUATE';
      return;
    }

    if (ev.eventType === 'approval_granted') {
      statuses.EVALUATE = 'COMPLETED';
      highestStageIdx = Math.max(highestStageIdx, 4);
      liveStage = 'EVALUATE';
      return;
    }

    if (
      ev.eventType === 'investigation_replanned' ||
      ev.eventType === 'task_reassigned' ||
      ev.eventType === 'agent_reassigned'
    ) {
      cycleCount += 1;
      hasReplanAfterEval = true;
      AGENT_LOOP_STAGE_ORDER.slice(0, 5).forEach((s) => {
        if (statuses[s] !== 'FAILED' && statuses[s] !== 'BLOCKED') {
          statuses[s] = 'COMPLETED';
        }
      });
      statuses.REPEAT = 'IN_PROGRESS';
      highestStageIdx = 5;
      liveStage = 'REPEAT';
      isConcluded = false;
      return;
    }

    if (ev.eventType === 'response_executed') {
      AGENT_LOOP_STAGE_ORDER.slice(0, 5).forEach((s) => {
        if (statuses[s] !== 'FAILED' && statuses[s] !== 'BLOCKED') {
          statuses[s] = 'COMPLETED';
        }
      });
      statuses.REPEAT = 'IN_PROGRESS';
      highestStageIdx = 5;
      liveStage = 'REPEAT';
      return;
    }

    if (
      ev.eventType === 'tool_access_denied' ||
      ev.eventType === 'agent_capability_revoked' ||
      ev.eventType === 'agent_capability_restricted'
    ) {
      AGENT_LOOP_STAGE_ORDER.slice(0, idx).forEach((s) => {
        if (statuses[s] === 'NOT_STARTED' || statuses[s] === 'IN_PROGRESS') {
          statuses[s] = 'COMPLETED';
        }
      });
      statuses[ev.stage] = 'BLOCKED';
      highestStageIdx = Math.max(highestStageIdx, idx);
      liveStage = ev.stage;
      return;
    }

    if (ev.status === 'FAILED') {
      statuses[ev.stage] = 'FAILED';
      highestStageIdx = Math.max(highestStageIdx, idx);
      liveStage = ev.stage;
      return;
    }

    if (idx > highestStageIdx) {
      AGENT_LOOP_STAGE_ORDER.slice(0, idx).forEach((s) => {
        if (statuses[s] === 'NOT_STARTED' || statuses[s] === 'IN_PROGRESS') {
          statuses[s] = 'COMPLETED';
        }
      });
      statuses[ev.stage] = 'IN_PROGRESS';
      highestStageIdx = idx;
      liveStage = ev.stage;
    } else if (statuses[ev.stage] === 'BLOCKED' && ev.eventType === 'tool_access_granted') {
      statuses[ev.stage] = 'IN_PROGRESS';
    } else if (statuses[ev.stage] === 'NOT_STARTED') {
      statuses[ev.stage] = 'IN_PROGRESS';
    }
  });

  // Apply live isolation blocks only when an active investigation is underway
  if (loopEvents.length > 0 && !isConcluded) {
    const latestGov = governanceAlerts[governanceAlerts.length - 1];
    if (latestGov && (latestGov.event_type === 'agent_isolated' || latestGov.status === 'ISOLATED')) {
      const targetStage = liveStage || 'ACT';
      if (statuses[targetStage] === 'IN_PROGRESS' || statuses[targetStage] === 'WAITING') {
        statuses[targetStage] = 'BLOCKED';
      }
    }
  }

  const workOrder = pickPrimaryWorkOrder(context.workOrders, activeIncidentId);
  const approval = pickPrimaryApproval(context.approvals, activeIncidentId);

  const stageDetailsByStage = {} as Record<AgentLoopStage, AgentLoopStageDetails>;
  const hasStarted = loopEvents.length > 0;

  AGENT_LOOP_STAGE_ORDER.forEach((stage) => {
    const meta = AGENT_LOOP_STAGE_METADATA[stage];
    const stageEvents = eventsByStage[stage];
    const status = statuses[stage];
    const lastStageEv = stageEvents[stageEvents.length - 1];

    let fields: AgentLoopStageField[] = [];
    let toolHistory: AgentLoopStageToolEntry[] | undefined;
    let restrictionsOrDenials: string[] | undefined;
    let contradictions: string[] | undefined;
    let uncertainties: string[] | undefined;
    let agentMessages: AgentLoopExecutionContext['messages'] | undefined;
    let extraEvidenceRefs: string[] = [];

    const stageHasData =
      stageEvents.length > 0 ||
      status !== 'NOT_STARTED' ||
      (stage === 'ACT' && governanceAlerts.length > 0 && hasStarted);

    if (stageHasData) {
      if (stage === 'REASON') {
        const built = buildReasonFields(
          stageEvents,
          activeIncidentId,
          workOrder,
          context.evidenceRecords,
          eventsByStage.OBSERVE[0]?.data
        );
        fields = built.fields;
        uncertainties = built.uncertainties;
      } else if (stage === 'PLAN') {
        fields = buildPlanFields(stageEvents, activeIncidentId, workOrder);
      } else if (stage === 'ACT') {
        const built = buildActFields(stageEvents, governanceAlerts, workOrder, context);
        fields = built.fields;
        toolHistory = built.toolHistory;
        restrictionsOrDenials = built.restrictionsOrDenials;
      } else if (stage === 'OBSERVE') {
        const built = buildObserveFields(stageEvents, workOrder, context);
        fields = built.fields;
        contradictions = built.contradictions;
        agentMessages = built.agentMessages;
        extraEvidenceRefs = built.evidenceRefs;
      } else if (stage === 'EVALUATE') {
        const built = buildEvaluateFields(
          stageEvents,
          eventsByStage.OBSERVE,
          workOrder,
          approval,
          context,
          hasReplanAfterEval
        );
        fields = built.fields;
        contradictions = built.contradictions;
      } else if (stage === 'REPEAT') {
        fields = buildRepeatFields(
          stageEvents,
          workOrder,
          approval,
          cycleCount,
          isConcluded,
          hasStarted,
          statuses.EVALUATE === 'WAITING',
          statuses.EVALUATE === 'FAILED'
        );
      }
    }

    const evidenceRefs = uniqueStrings([
      ...stageEvents.map((e) => e.evidenceId),
      ...extraEvidenceRefs,
    ]);

    stageDetailsByStage[stage] = {
      stage,
      stageNumber: meta.stageNumber,
      title: meta.title,
      shortLabel: meta.shortLabel,
      icon: meta.icon,
      description: meta.description,
      status,
      hasExecutionData: stageHasData,
      incidentId: activeIncidentId,
      taskId: lastStageEv?.taskId || workOrder?.work_order_id,
      agentId: lastStageEv?.agentId || workOrder?.assigned_agent_id,
      timestamp: lastStageEv?.timestamp,
      summary: lastStageEv?.message,
      events: stageEvents,
      evidenceRefs,
      fields,
      highlights: {
        restrictionsOrDenials,
        contradictions,
        uncertainties,
        toolHistory,
        agentMessages,
      },
    };
  });

  const completedCount = AGENT_LOOP_STAGE_ORDER.filter((s) => statuses[s] === 'COMPLETED').length;

  return {
    stageDetailsByStage,
    liveStage,
    completedCount,
    isConcluded,
    cycleCount,
    activeIncidentId,
  };
}
