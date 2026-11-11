/**
 * Interactive Investigation Timeline & AI Agent Autonomous Loop Panel for HACTM.
 * Renders the interactive 6-stage loop (REASON → PLAN → ACT → OBSERVE → EVALUATE → REPEAT),
 * live SSE-driven stage progression, per-stage execution inspection, and the real-time event timeline.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  ArrowLeft,
  Ban,
  CheckCircle2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  CircleDashed,
  Clock,
  Loader2,
  Terminal,
  XCircle,
} from 'lucide-react';
import {
  AgentLoopStage,
  AgentLoopStageField,
  AgentLoopStageStatus,
  AgentMessageItem,
  ApprovalRecord,
  AuditTrailRecord,
  EvidenceDetailRecord,
  TimelineEntry,
  WorkOrderRecord,
  WorkspaceAgentState,
  WorkspaceEvent,
} from '../../types/workspace';
import { StreamConnectionStatus } from '../../services/workspaceEventService';
import { api } from '../../services/api';
import { SuperIcon, SuperIconStyle } from '../common/SuperIcon';
import {
  AGENT_LOOP_STAGE_METADATA,
  AGENT_LOOP_STAGE_ORDER,
  deriveAgentLoopState,
  mapEventTypeToLoopStage,
} from './agentLoopUtils';

interface InvestigationTimelinePanelProps {
  timeline: TimelineEntry[];
  workspaceEvents?: WorkspaceEvent[];
  streamStatus?: StreamConnectionStatus;
  currentIncidentId?: string | null;
  agents?: WorkspaceAgentState[];
  messages?: AgentMessageItem[];
  onSelectEvidence?: (evidenceId: string) => void;
}

interface StatusVisualConfig {
  label: string;
  cardClass: string;
  badgeClass: string;
  iconStyle: SuperIconStyle;
  renderIcon: () => React.ReactNode;
}

function getStageStatusVisuals(status: AgentLoopStageStatus): StatusVisualConfig {
  switch (status) {
    case 'COMPLETED':
      return {
        label: 'COMPLETED',
        cardClass:
          'bg-emerald-950/35 border-emerald-500/55 text-emerald-200 hover:border-emerald-400 hover:bg-emerald-950/50',
        badgeClass: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40',
        iconStyle: 'color',
        renderIcon: () => <CheckCircle2 size={10} className="text-emerald-400" />,
      };
    case 'IN_PROGRESS':
      return {
        label: 'IN_PROGRESS',
        cardClass:
          'bg-cyan-950/60 border-cyan-400/80 text-cyan-100 hover:border-cyan-300 shadow-sm shadow-cyan-500/20',
        badgeClass: 'bg-cyan-500/20 text-cyan-200 border-cyan-400/50 animate-pulse',
        iconStyle: 'color',
        renderIcon: () => <Loader2 size={10} className="text-cyan-300 animate-spin" />,
      };
    case 'WAITING':
      return {
        label: 'WAITING',
        cardClass:
          'bg-amber-950/45 border-amber-500/75 text-amber-200 hover:border-amber-400 shadow-sm shadow-amber-500/15',
        badgeClass: 'bg-amber-500/20 text-amber-300 border-amber-500/50',
        iconStyle: 'color',
        renderIcon: () => <Clock size={10} className="text-amber-400" />,
      };
    case 'FAILED':
      return {
        label: 'FAILED',
        cardClass: 'bg-red-950/45 border-red-500/75 text-red-200 hover:border-red-400',
        badgeClass: 'bg-red-500/20 text-red-300 border-red-500/50',
        iconStyle: 'color',
        renderIcon: () => <XCircle size={10} className="text-red-400" />,
      };
    case 'BLOCKED':
      return {
        label: 'BLOCKED',
        cardClass: 'bg-slate-900/90 border-rose-700/75 text-rose-300 hover:border-rose-500',
        badgeClass: 'bg-rose-950/70 text-rose-300 border-rose-700/60',
        iconStyle: 'two-tone',
        renderIcon: () => <Ban size={10} className="text-rose-400" />,
      };
    case 'NOT_STARTED':
    default:
      return {
        label: 'NOT_STARTED',
        cardClass:
          'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-600 hover:text-slate-200',
        badgeClass: 'bg-slate-800/80 text-slate-400 border-slate-700',
        iconStyle: 'stroke',
        renderIcon: () => <CircleDashed size={10} className="text-slate-500" />,
      };
  }
}

function getEntryStageIcon(step: string, title: string, index: number): string {
  const mappedStage = mapEventTypeToLoopStage(step);
  if (mappedStage) {
    return AGENT_LOOP_STAGE_METADATA[mappedStage].icon;
  }

  const t = title.toLowerCase();
  if (t.includes('ingest') || t.includes('phishing') || t.includes('analys')) return 'reason';
  if (t.includes('dispatch') || t.includes('plan') || t.includes('assign')) return 'plan';
  if (t.includes('tool') || t.includes('lookup') || t.includes('scan') || t.includes('query')) {
    return 'act';
  }
  if (t.includes('evidence') || t.includes('observed') || t.includes('telemetry')) return 'observe';
  if (t.includes('fusion') || t.includes('risk') || t.includes('evaluat') || t.includes('approval')) {
    return 'evaluate';
  }
  if (t.includes('response') || t.includes('contain') || t.includes('reassign')) return 'repeat';

  const stages = ['reason', 'plan', 'act', 'observe', 'evaluate', 'repeat'];
  return stages[index % stages.length];
}

function getFieldToneClass(tone?: AgentLoopStageField['tone']): string {
  switch (tone) {
    case 'cyan':
      return 'text-cyan-300';
    case 'emerald':
      return 'text-emerald-300';
    case 'amber':
      return 'text-amber-300';
    case 'red':
      return 'text-red-300';
    case 'slate':
      return 'text-slate-400';
    case 'mono':
      return 'text-slate-200 font-mono';
    default:
      return 'text-slate-200';
  }
}

export const InvestigationTimelinePanel: React.FC<InvestigationTimelinePanelProps> = ({
  timeline,
  workspaceEvents = [],
  streamStatus,
  currentIncidentId,
  agents = [],
  messages = [],
  onSelectEvidence,
}) => {
  // Independent UI navigation state: selecting/navigating stages never modifies backend execution.
  const [selectedStage, setSelectedStage] = useState<AgentLoopStage | null>(null);
  const [hoveredStage, setHoveredStage] = useState<AgentLoopStage | null>(null);
  const [showLiveEventsDrawer, setShowLiveEventsDrawer] = useState<boolean>(false);

  // Read-only enrichment state synced from authoritative HACTM endpoints when active incident events change
  const [workOrders, setWorkOrders] = useState<WorkOrderRecord[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRecord[]>([]);
  const [evidenceRecords, setEvidenceRecords] = useState<EvidenceDetailRecord[]>([]);
  const [auditTrail, setAuditTrail] = useState<AuditTrailRecord[]>([]);

  const stageButtonRefs = useRef<Array<HTMLButtonElement | null>>([]);

  const resolvedIncidentId = useMemo(() => {
    if (currentIncidentId) return currentIncidentId;
    return [...workspaceEvents].reverse().find((e) => Boolean(e.incident_id))?.incident_id || null;
  }, [currentIncidentId, workspaceEvents]);

  const observedEvidenceIdsKey = useMemo(() => {
    const ids = new Set<string>();
    workspaceEvents.forEach((ev) => {
      if (resolvedIncidentId && ev.incident_id && ev.incident_id !== resolvedIncidentId) return;
      const evId = ev.data?.evidence_id || ev.data?.evidence_ref;
      if (typeof evId === 'string' && evId) ids.add(evId);
    });
    return Array.from(ids).join(',');
  }, [workspaceEvents, resolvedIncidentId]);

  const incidentEventCount = useMemo(() => {
    if (!resolvedIncidentId) return workspaceEvents.length;
    return workspaceEvents.filter((e) => !e.incident_id || e.incident_id === resolvedIncidentId)
      .length;
  }, [workspaceEvents, resolvedIncidentId]);

  // Fetch authoritative WorkOrder / Approval / Evidence / Audit records for the active incident
  useEffect(() => {
    let cancelled = false;
    if (!resolvedIncidentId) {
      return;
    }

    const fetchContextRecords = async () => {
      try {
        const evidenceIds = observedEvidenceIdsKey ? observedEvidenceIdsKey.split(',') : [];
        const [woRes, appRes, auditRes, evResults] = await Promise.allSettled([
          api.getWorkOrders(),
          api.getApprovalRequests(),
          api.getAuditTrail(resolvedIncidentId, 30),
          Promise.all(evidenceIds.map((id) => api.getEvidenceById(id))),
        ]);

        if (cancelled) return;

        if (woRes.status === 'fulfilled' && Array.isArray(woRes.value?.data)) {
          setWorkOrders(
            woRes.value.data.filter(
              (wo: WorkOrderRecord) => wo.parent_incident_id === resolvedIncidentId
            )
          );
        }
        if (appRes.status === 'fulfilled' && Array.isArray(appRes.value?.data)) {
          setApprovals(
            appRes.value.data.filter((ap: ApprovalRecord) => ap.incident_id === resolvedIncidentId)
          );
        }
        if (auditRes.status === 'fulfilled' && Array.isArray(auditRes.value?.data)) {
          setAuditTrail(auditRes.value.data);
        }
        if (evResults.status === 'fulfilled' && Array.isArray(evResults.value)) {
          const validRecords = evResults.value
            .map((r: any) => r?.data)
            .filter((item): item is EvidenceDetailRecord => Boolean(item?.event_id));
          setEvidenceRecords(validRecords);
        }
      } catch (err) {
        console.warn('Could not refresh stage enrichment context:', err);
      }
    };

    fetchContextRecords();
    return () => {
      cancelled = true;
    };
  }, [resolvedIncidentId, observedEvidenceIdsKey, incidentEventCount]);

  const loopState = useMemo(
    () =>
      deriveAgentLoopState(workspaceEvents, timeline, {
        incidentId: resolvedIncidentId,
        agents,
        messages,
        workOrders: resolvedIncidentId ? workOrders : [],
        approvals: resolvedIncidentId ? approvals : [],
        evidenceRecords: resolvedIncidentId ? evidenceRecords : [],
        auditTrail: resolvedIncidentId ? auditTrail : [],
      }),
    [
      workspaceEvents,
      timeline,
      resolvedIncidentId,
      agents,
      messages,
      workOrders,
      approvals,
      evidenceRecords,
      auditTrail,
    ]
  );

  const selectedStageIndex = selectedStage ? AGENT_LOOP_STAGE_ORDER.indexOf(selectedStage) : -1;
  const selectedDetails = selectedStage ? loopState.stageDetailsByStage[selectedStage] : null;
  const selectedStatusVisual = selectedDetails
    ? getStageStatusVisuals(selectedDetails.status)
    : null;

  const effectiveStreamStatus: StreamConnectionStatus =
    streamStatus ||
    (timeline.some((entry) => entry.step === 'stream_connected') ? 'CONNECTED' : 'DISCONNECTED');

  const handleStageKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>, idx: number) => {
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const nextIdx = (idx + 1) % AGENT_LOOP_STAGE_ORDER.length;
      stageButtonRefs.current[nextIdx]?.focus();
      setSelectedStage(AGENT_LOOP_STAGE_ORDER[nextIdx]);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prevIdx = (idx - 1 + AGENT_LOOP_STAGE_ORDER.length) % AGENT_LOOP_STAGE_ORDER.length;
      stageButtonRefs.current[prevIdx]?.focus();
      setSelectedStage(AGENT_LOOP_STAGE_ORDER[prevIdx]);
    } else if (e.key === 'Home') {
      e.preventDefault();
      stageButtonRefs.current[0]?.focus();
      setSelectedStage(AGENT_LOOP_STAGE_ORDER[0]);
    } else if (e.key === 'End') {
      e.preventDefault();
      const lastIdx = AGENT_LOOP_STAGE_ORDER.length - 1;
      stageButtonRefs.current[lastIdx]?.focus();
      setSelectedStage(AGENT_LOOP_STAGE_ORDER[lastIdx]);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setSelectedStage(null);
    }
  };

  const handlePrevStage = () => {
    if (selectedStageIndex > 0) {
      setSelectedStage(AGENT_LOOP_STAGE_ORDER[selectedStageIndex - 1]);
    }
  };

  const handleNextStage = () => {
    if (selectedStageIndex >= 0 && selectedStageIndex < AGENT_LOOP_STAGE_ORDER.length - 1) {
      setSelectedStage(AGENT_LOOP_STAGE_ORDER[selectedStageIndex + 1]);
    }
  };

  const renderLiveStatusSummary = () => {
    if (loopState.isConcluded) {
      return (
        <span className="text-[10px] text-emerald-400 font-mono font-semibold whitespace-nowrap">
          CYCLE #{loopState.cycleCount} · COMPLETED (6/6)
        </span>
      );
    }
    if (loopState.liveStage) {
      const activeStatus = loopState.stageDetailsByStage[loopState.liveStage].status;
      const stageNum = AGENT_LOOP_STAGE_METADATA[loopState.liveStage].stageNumber;
      const toneClass =
        activeStatus === 'WAITING'
          ? 'text-amber-300'
          : activeStatus === 'BLOCKED' || activeStatus === 'FAILED'
          ? 'text-red-400'
          : 'text-cyan-400';
      return (
        <span className={`text-[10px] font-mono font-semibold whitespace-nowrap ${toneClass}`}>
          STAGE {stageNum}/6 · {loopState.liveStage}
        </span>
      );
    }
    return (
      <span className="text-[10px] text-slate-500 font-mono font-semibold whitespace-nowrap">
        STANDBY · NOT STARTED
      </span>
    );
  };

  return (
    <div
      className="flex flex-col h-full min-h-0 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl text-xs"
      onKeyDown={(e) => {
        if (e.key === 'Escape' && selectedStage) {
          setSelectedStage(null);
        }
      }}
    >
      {/* Panel Header with Preserved Stream Status */}
      <div className="flex-shrink-0 flex items-center justify-between gap-2 px-3.5 py-2.5 border-b border-slate-800 bg-slate-950/70">
        <div className="flex items-center space-x-2 min-w-0">
          <SuperIcon name="agent-loop" style="color" size={16} alt="Investigation Loop" />
          <h3 className="font-bold text-white tracking-wide truncate">INVESTIGATION TIMELINE</h3>
          {resolvedIncidentId && (
            <span className="px-2 py-0.5 bg-cyan-950/60 text-cyan-300 border border-cyan-800/40 rounded-full font-mono text-[10px] flex-shrink-0">
              {resolvedIncidentId}
            </span>
          )}
        </div>

        <div
          className="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800 text-[9.5px] font-mono flex-shrink-0"
          title={`SSE Event Stream Status: ${effectiveStreamStatus}`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              effectiveStreamStatus === 'CONNECTED'
                ? 'bg-emerald-400'
                : effectiveStreamStatus === 'CONNECTING' || effectiveStreamStatus === 'RECONNECTING'
                ? 'bg-amber-400 animate-pulse'
                : 'bg-red-400'
            }`}
          />
          <span className="text-slate-300">STREAM {effectiveStreamStatus}</span>
        </div>
      </div>

      {/* SuperIntelligence AI Agent Autonomous Loop Interactive Selector */}
      <div className="flex-shrink-0 px-3.5 py-2.5 bg-slate-950/90 border-b border-slate-800/80">
        <div className="flex items-center justify-between gap-2 mb-2">
          <span className="text-[10px] text-slate-300 font-mono uppercase tracking-wider flex items-center min-w-0 truncate">
            <SuperIcon name="reflection" style="duotone" size={12} className="mr-1.5" />
            <span className="truncate">AI Agent Autonomous Loop</span>
          </span>
          {renderLiveStatusSummary()}
        </div>

        <div
          className="grid grid-cols-6 gap-1"
          role="group"
          aria-label="AI Agent Autonomous Loop Stages"
        >
          {AGENT_LOOP_STAGE_ORDER.map((stageKey, idx) => {
            const meta = AGENT_LOOP_STAGE_METADATA[stageKey];
            const details = loopState.stageDetailsByStage[stageKey];
            const visual = getStageStatusVisuals(details.status);
            const isSelected = selectedStage === stageKey;

            return (
              <button
                key={stageKey}
                ref={(el) => {
                  stageButtonRefs.current[idx] = el;
                }}
                type="button"
                aria-pressed={isSelected}
                aria-label={`Stage ${meta.stageNumber}: ${meta.stage} (${visual.label}). ${meta.description}`}
                title={`${meta.stage} (${visual.label}) — ${meta.description} Click to inspect stage details.`}
                onClick={() => setSelectedStage(stageKey)}
                onMouseEnter={() => setHoveredStage(stageKey)}
                onMouseLeave={() => setHoveredStage((prev) => (prev === stageKey ? null : prev))}
                onKeyDown={(e) => handleStageKeyDown(e, idx)}
                className={`group h-[62px] w-full min-w-0 flex flex-col items-center justify-between px-1 py-1.5 rounded-lg border text-center cursor-pointer transition-all duration-150 hover:-translate-y-0.5 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 ${
                  visual.cardClass
                } ${
                  isSelected
                    ? 'ring-2 ring-cyan-300 ring-offset-1 ring-offset-slate-950 -translate-y-0.5 shadow-lg shadow-cyan-500/25'
                    : ''
                }`}
              >
                <div className="flex items-center justify-between w-full px-0.5 h-3 flex-shrink-0">
                  <span className="text-[8px] font-mono opacity-65 leading-none">
                    {meta.stageNumber}
                  </span>
                  <span className="flex-shrink-0">{visual.renderIcon()}</span>
                </div>

                <div className="w-5 h-5 flex items-center justify-center flex-shrink-0">
                  <SuperIcon
                    name={meta.icon}
                    style={isSelected ? 'color' : visual.iconStyle}
                    size={15}
                    className="transition-transform duration-150 group-hover:scale-110"
                  />
                </div>

                <span className="w-full text-[8.5px] font-mono font-bold leading-none tracking-tight whitespace-nowrap truncate">
                  {meta.stage}
                </span>
              </button>
            );
          })}
        </div>

        {/* View Mode Switcher & Hover/Keyboard Context Strip */}
        <div className="flex items-center justify-between gap-2 mt-2 pt-2 border-t border-slate-800/80">
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              type="button"
              onClick={() => setSelectedStage(null)}
              className={`px-2 py-1 rounded text-[10px] font-mono transition cursor-pointer ${
                selectedStage === null
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                  : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              Timeline ({timeline.length})
            </button>
            <button
              type="button"
              onClick={() => setSelectedStage(selectedStage ?? loopState.liveStage ?? 'REASON')}
              className={`px-2 py-1 rounded text-[10px] font-mono transition cursor-pointer ${
                selectedStage !== null
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                  : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200 hover:border-slate-700'
              }`}
            >
              Stage Details{selectedStage ? ` · ${selectedStage}` : ''}
            </button>
          </div>

          <span className="text-[9.5px] font-mono text-slate-500 truncate text-right">
            {hoveredStage
              ? `${hoveredStage}: ${AGENT_LOOP_STAGE_METADATA[hoveredStage].shortLabel} [${
                  loopState.stageDetailsByStage[hoveredStage].status
                }]`
              : selectedStage
              ? '←/→ stages · Esc timeline'
              : 'Click a stage to inspect'}
          </span>
        </div>
      </div>

      {/* Mode A: Selected Stage Details Panel */}
      {selectedDetails && selectedStatusVisual ? (
        <div className="flex-1 min-h-0 flex flex-col overflow-hidden bg-slate-950/35">
          {/* Detail View Navigation & Stage Header */}
          <div className="flex-shrink-0 px-3.5 py-2.5 border-b border-slate-800 bg-slate-950/80 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <button
                type="button"
                onClick={() => setSelectedStage(null)}
                className="inline-flex items-center space-x-1 px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-700/80 text-[10px] font-mono transition cursor-pointer"
              >
                <ArrowLeft size={11} />
                <span>Back to Timeline</span>
              </button>

              <div className="flex items-center space-x-1">
                <button
                  type="button"
                  onClick={handlePrevStage}
                  disabled={selectedStageIndex <= 0}
                  aria-label="Previous Stage"
                  title={
                    selectedStageIndex > 0
                      ? `Previous: ${AGENT_LOOP_STAGE_ORDER[selectedStageIndex - 1]}`
                      : 'At first stage'
                  }
                  className="inline-flex items-center px-1.5 py-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 border border-slate-700/80 text-[10px] font-mono transition cursor-pointer"
                >
                  <ChevronLeft size={12} />
                  <span>Prev</span>
                </button>
                <span className="px-1.5 text-[10px] font-mono text-slate-400">
                  {selectedStageIndex + 1}/6
                </span>
                <button
                  type="button"
                  onClick={handleNextStage}
                  disabled={selectedStageIndex >= AGENT_LOOP_STAGE_ORDER.length - 1}
                  aria-label="Next Stage"
                  title={
                    selectedStageIndex < AGENT_LOOP_STAGE_ORDER.length - 1
                      ? `Next: ${AGENT_LOOP_STAGE_ORDER[selectedStageIndex + 1]}`
                      : 'At final stage'
                  }
                  className="inline-flex items-center px-1.5 py-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300 border border-slate-700/80 text-[10px] font-mono transition cursor-pointer"
                >
                  <span>Next</span>
                  <ChevronRight size={12} />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center space-x-2 min-w-0">
                <div className="w-7 h-7 rounded-lg bg-slate-900 border border-slate-700/80 flex items-center justify-center flex-shrink-0">
                  <SuperIcon name={selectedDetails.icon} style="color" size={18} />
                </div>
                <div className="min-w-0">
                  <h4 className="font-bold text-white text-xs tracking-wide truncate">
                    AI AGENT LOOP — {selectedDetails.title}
                  </h4>
                  <p className="text-[10px] text-slate-400 font-mono truncate">
                    Stage {selectedDetails.stageNumber} · {selectedDetails.shortLabel}
                  </p>
                </div>
              </div>

              <span
                className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded border text-[9.5px] font-mono font-semibold flex-shrink-0 ${selectedStatusVisual.badgeClass}`}
              >
                {selectedStatusVisual.renderIcon()}
                <span>{selectedStatusVisual.label}</span>
              </span>
            </div>

            {loopState.liveStage && loopState.liveStage !== selectedDetails.stage && (
              <div className="flex items-center justify-between px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800 text-[10px] font-mono text-slate-400">
                <span>Read-only inspection view</span>
                <button
                  type="button"
                  onClick={() => setSelectedStage(loopState.liveStage)}
                  className="text-cyan-400 hover:text-cyan-300 underline cursor-pointer"
                >
                  Live Stage: {loopState.liveStage}
                </button>
              </div>
            )}
          </div>

          {/* Scrollable Stage Execution Details */}
          <div className="flex-1 min-h-0 overflow-y-auto p-3.5 space-y-3">
            {/* Stage Overview Card */}
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
              <p className="text-slate-300 leading-relaxed">{selectedDetails.description}</p>
              <div className="grid grid-cols-2 gap-1.5 pt-2 border-t border-slate-800/80 text-[10px] font-mono">
                <div className="min-w-0">
                  <span className="text-slate-500 block">INCIDENT</span>
                  <span className="text-slate-200 truncate block">
                    {selectedDetails.incidentId || 'Not available'}
                  </span>
                </div>
                <div className="min-w-0">
                  <span className="text-slate-500 block">AGENT / ACTOR</span>
                  <span className="text-cyan-300 truncate block">
                    {selectedDetails.agentId || 'Not available'}
                  </span>
                </div>
                <div className="min-w-0">
                  <span className="text-slate-500 block">TASK / WORK ORDER</span>
                  <span className="text-slate-200 truncate block">
                    {selectedDetails.taskId || 'Not available'}
                  </span>
                </div>
                <div className="min-w-0">
                  <span className="text-slate-500 block">LAST UPDATE</span>
                  <span className="text-slate-200 truncate block">
                    {selectedDetails.timestamp
                      ? new Date(selectedDetails.timestamp).toLocaleTimeString()
                      : 'Not available'}
                  </span>
                </div>
              </div>
            </div>

            {!selectedDetails.hasExecutionData ? (
              <div className="p-5 rounded-lg bg-slate-900/50 border border-dashed border-slate-700/80 text-center space-y-2">
                <SuperIcon
                  name={selectedDetails.icon}
                  style="duotone"
                  size={28}
                  className="mx-auto opacity-60"
                />
                <p className="text-slate-200 font-semibold">
                  No execution data available for this stage yet.
                </p>
                <p className="text-[11px] text-slate-400">
                  {AGENT_LOOP_STAGE_METADATA[selectedDetails.stage].triggerHint}
                </p>
              </div>
            ) : (
              <>
                {/* Governance Restrictions / Denied Tool Warnings (ACT / Execution) */}
                {selectedDetails.highlights?.restrictionsOrDenials &&
                  selectedDetails.highlights.restrictionsOrDenials.length > 0 && (
                    <div className="p-3 rounded-lg bg-red-950/30 border border-red-500/40 space-y-1.5">
                      <div className="flex items-center space-x-1.5 text-red-300 font-semibold text-[11px]">
                        <AlertTriangle size={13} className="flex-shrink-0" />
                        <span>Governance Restrictions & Denied Requests</span>
                      </div>
                      <ul className="space-y-1 text-[11px] text-red-200/90 list-disc pl-4 break-words">
                        {selectedDetails.highlights.restrictionsOrDenials.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                {/* Stage-Specific Structured Execution Details */}
                <div className="space-y-2">
                  <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400 px-0.5">
                    Execution Details
                  </div>
                  <div className="space-y-2">
                    {selectedDetails.fields.map((field) => (
                      <div
                        key={field.label}
                        className="p-2.5 rounded-lg bg-slate-900/75 border border-slate-800/90 min-w-0"
                      >
                        <div className="text-[10px] font-mono uppercase text-slate-400 mb-1">
                          {field.label}
                        </div>
                        {Array.isArray(field.value) ? (
                          <ul
                            className={`space-y-1 text-[11px] break-words ${getFieldToneClass(
                              field.tone
                            )}`}
                          >
                            {field.value.map((entry, idx) => (
                              <li key={idx} className="leading-snug flex items-start space-x-1.5">
                                <span className="text-slate-500 mt-0.5 flex-shrink-0">•</span>
                                <span className="min-w-0 break-words">{entry}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p
                            className={`text-[11px] leading-relaxed break-words ${getFieldToneClass(
                              field.tone
                            )}`}
                          >
                            {field.value}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Tool Invocation History (ACT) */}
                {selectedDetails.highlights?.toolHistory &&
                  selectedDetails.highlights.toolHistory.length > 0 && (
                    <div className="p-3 rounded-lg bg-slate-900/75 border border-slate-800 space-y-2">
                      <div className="flex items-center space-x-1.5 text-[10px] font-mono uppercase tracking-wider text-slate-400">
                        <Terminal size={12} className="text-cyan-400" />
                        <span>Tool Invocation History</span>
                      </div>
                      <div className="space-y-1.5">
                        {selectedDetails.highlights.toolHistory.map((tool, i) => (
                          <div
                            key={`${tool.toolName}-${i}`}
                            className="flex items-start justify-between gap-2 p-2 rounded bg-slate-950/70 border border-slate-800/80"
                          >
                            <div className="min-w-0">
                              <div className="font-mono text-[11px] text-cyan-300 truncate">
                                {tool.toolName}
                              </div>
                              {tool.detail && (
                                <p className="text-[10px] text-slate-400 mt-0.5 break-words">
                                  {tool.detail}
                                </p>
                              )}
                            </div>
                            <span
                              className={`px-1.5 py-0.5 rounded text-[9px] font-mono flex-shrink-0 ${
                                tool.status === 'DENIED'
                                  ? 'bg-red-500/20 text-red-300 border border-red-500/40'
                                  : 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                              }`}
                            >
                              {tool.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                {/* Agent Messages (OBSERVE) */}
                {selectedDetails.highlights?.agentMessages &&
                  selectedDetails.highlights.agentMessages.length > 0 && (
                    <div className="p-3 rounded-lg bg-slate-900/75 border border-slate-800 space-y-2">
                      <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                        Observed Agent Messages ({selectedDetails.highlights.agentMessages.length})
                      </div>
                      <div className="space-y-2">
                        {selectedDetails.highlights.agentMessages.map((msg) => (
                          <div
                            key={msg.id}
                            className="p-2 rounded bg-slate-950/70 border border-slate-800/80 space-y-1"
                          >
                            <div className="flex items-center justify-between text-[10px] font-mono">
                              <span className="text-cyan-300 truncate">
                                {msg.sender} → {msg.recipient}
                              </span>
                              <span className="text-slate-500 flex-shrink-0">
                                {new Date(msg.timestamp).toLocaleTimeString()}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-300 break-words">{msg.message}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                {/* Clickable Evidence References */}
                {selectedDetails.evidenceRefs.length > 0 && (
                  <div className="p-3 rounded-lg bg-slate-900/75 border border-slate-800 space-y-1.5">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                      Evidence References
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedDetails.evidenceRefs.map((evId) => (
                        <button
                          key={evId}
                          type="button"
                          onClick={() => onSelectEvidence && onSelectEvidence(evId)}
                          className="inline-flex items-center space-x-1 px-2 py-1 rounded bg-cyan-950/60 hover:bg-cyan-900/60 text-cyan-300 border border-cyan-800/50 text-[10px] font-mono transition cursor-pointer"
                        >
                          <SuperIcon name="citations" style="two-tone" size={11} />
                          <span>{evId}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Stage-Mapped Investigation Events */}
                {selectedDetails.events.length > 0 && (
                  <div className="space-y-1.5">
                    <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400 px-0.5">
                      Stage Investigation Events ({selectedDetails.events.length})
                    </div>
                    <div className="space-y-1.5">
                      {selectedDetails.events.map((ev) => (
                        <div
                          key={ev.eventId}
                          className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1"
                        >
                          <div className="flex items-center justify-between gap-2 text-[10px] font-mono">
                            <span className="text-cyan-400 uppercase">{ev.eventType}</span>
                            <span className="text-slate-500">
                              {new Date(ev.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-200 break-words">{ev.message}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Coexisting Live Stream Drawer so live events remain inspectable inside stage view */}
            <div className="pt-2 border-t border-slate-800/80 space-y-2">
              <button
                type="button"
                onClick={() => setShowLiveEventsDrawer((prev) => !prev)}
                className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-slate-900/90 hover:bg-slate-800/90 border border-slate-800 text-slate-300 text-[10px] font-mono transition cursor-pointer"
              >
                <span>LIVE INVESTIGATION STREAM ({timeline.length} EVENTS)</span>
                {showLiveEventsDrawer ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
              </button>

              {showLiveEventsDrawer && (
                <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                  {timeline.length === 0 ? (
                    <p className="text-[11px] text-slate-500 font-mono px-1">
                      No stream events recorded yet.
                    </p>
                  ) : (
                    timeline.map((entry) => (
                      <div
                        key={entry.id}
                        className="p-2 rounded bg-slate-900/70 border border-slate-800 text-[10px]"
                      >
                        <div className="flex items-center justify-between font-mono text-slate-400">
                          <span className="text-slate-200 font-semibold">{entry.title}</span>
                          <span>{new Date(entry.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <p className="text-slate-400 mt-0.5 break-words">{entry.description}</p>
                      </div>
                    ))
                  )}
                </div>
              )}

              <button
                type="button"
                onClick={() => setSelectedStage(null)}
                className="w-full py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 hover:text-cyan-300 text-[11px] font-mono font-semibold flex items-center justify-center space-x-1.5 transition cursor-pointer"
              >
                <ArrowLeft size={12} />
                <span>Back to Timeline</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Mode B: Original Chronological Investigation Event Timeline */
        <div className="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
          {timeline.map((entry, index) => {
            const isLast = index === timeline.length - 1;
            const isComplete = entry.status === 'COMPLETED';
            const isAlert = entry.status === 'ALERT';
            const stageIcon = getEntryStageIcon(entry.step, entry.title, index);
            const entryLoopStage = mapEventTypeToLoopStage(entry.step);

            return (
              <div key={entry.id} className="relative flex items-start space-x-3">
                {/* Connecting vertical line */}
                {!isLast && (
                  <div
                    className={`absolute left-3 top-6 bottom-0 w-0.5 ${
                      isComplete ? 'bg-cyan-500/50' : 'bg-slate-700'
                    }`}
                    style={{ transform: 'translateX(-50%)' }}
                  />
                )}

                {/* Status & Stage Icon */}
                <div
                  className={`relative z-10 flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center p-0.5 ${
                    isComplete
                      ? 'bg-cyan-950 border border-cyan-400 text-cyan-300 shadow-md shadow-cyan-500/20'
                      : isAlert
                      ? 'bg-amber-950 border border-amber-500 text-amber-300 shadow-md shadow-amber-500/20'
                      : 'bg-slate-800 text-slate-400 border border-slate-700'
                  }`}
                >
                  <SuperIcon name={stageIcon} style={isComplete ? 'color' : 'duotone'} size={14} />
                </div>

                {/* Step Card Content */}
                <div className="flex-1 min-w-0 pb-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold text-slate-100 flex items-center space-x-1.5 min-w-0 truncate">
                      <span className="truncate">{entry.title}</span>
                    </span>
                    <div className="flex items-center space-x-1.5 flex-shrink-0">
                      {entryLoopStage && (
                        <button
                          type="button"
                          onClick={() => setSelectedStage(entryLoopStage)}
                          title={`Inspect ${entryLoopStage} loop stage`}
                          className="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-cyan-950 text-cyan-400 border border-slate-700 hover:border-cyan-500/50 text-[9px] font-mono transition cursor-pointer"
                        >
                          {entryLoopStage}
                        </button>
                      )}
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(entry.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                  <p className="text-slate-300 mt-0.5 leading-relaxed break-words">
                    {entry.description}
                  </p>

                  {entry.evidenceId && (
                    <div className="mt-1.5 flex items-center space-x-2">
                      <button
                        type="button"
                        onClick={() => onSelectEvidence && onSelectEvidence(entry.evidenceId!)}
                        className="text-cyan-400 hover:text-cyan-300 text-[10px] font-mono flex items-center space-x-1 cursor-pointer"
                      >
                        <SuperIcon name="citations" style="two-tone" size={12} className="mr-0.5" />
                        <span>EVIDENCE: {entry.evidenceId}</span>
                      </button>
                      {entry.riskScore !== undefined && (
                        <span className="text-[10px] font-mono text-amber-400">
                          [RISK: {(entry.riskScore * 100).toFixed(0)}%]
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {timeline.length === 0 && (
            <div className="py-12 text-center text-slate-500 font-mono">
              <SuperIcon name="task" style="stroke" size={24} className="mx-auto mb-2 opacity-40" />
              <p>No active investigation running.</p>
              <p className="text-[11px] text-slate-600 mt-1">
                Trigger demo scenario to view live progression.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
