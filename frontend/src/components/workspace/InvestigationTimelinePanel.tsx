/**
 * Investigation Timeline Panel for HACTM Cyber Operations.
 * Renders verified chronological investigation steps from incident ingestion to verified response,
 * augmented with official SuperIntelligence AI Agent Loop stages:
 * REASON → PLAN → ACT → OBSERVE → EVALUATE → REPEAT.
 */

import React from 'react';
import { TimelineEntry } from '../../types/workspace';
import {
  CheckCircle2,
  AlertCircle,
  Clock,
  Shield,
  Layers,
  ArrowDown,
  FileCheck,
  Lock,
} from 'lucide-react';
import { SuperIcon } from '../common/SuperIcon';

interface InvestigationTimelinePanelProps {
  timeline: TimelineEntry[];
  currentIncidentId?: string | null;
  onSelectEvidence?: (evidenceId: string) => void;
}

const AGENT_LOOP_STAGES = [
  { id: 'REASON', label: 'REASON', icon: 'reason', desc: 'Hypothesis Formulation' },
  { id: 'PLAN', label: 'PLAN', icon: 'plan', desc: 'Task Decomposition' },
  { id: 'ACT', label: 'ACT', icon: 'act', desc: 'Tool Execution' },
  { id: 'OBSERVE', label: 'OBSERVE', icon: 'observe', desc: 'Evidence Sensing' },
  { id: 'EVALUATE', label: 'EVALUATE', icon: 'evaluate', desc: 'Risk & Calibration' },
  { id: 'REPEAT', label: 'REPEAT', icon: 'repeat', desc: 'Iterate / Contain' },
];

function getLoopStageStatus(stageIndex: number, timeline: TimelineEntry[]) {
  if (timeline.length === 0) return 'PENDING';
  const progressIndex = Math.min(timeline.length - 1, 5);
  const isFinalComplete = timeline.some(
    (e) => e.status === 'COMPLETED' && (e.title.toLowerCase().includes('response') || e.title.toLowerCase().includes('concluded'))
  );

  if (isFinalComplete) return 'COMPLETED';
  if (stageIndex < progressIndex) return 'COMPLETED';
  if (stageIndex === progressIndex) return 'ACTIVE';
  return 'PENDING';
}

function getEntryStageIcon(title: string, index: number): string {
  const t = title.toLowerCase();
  if (t.includes('ingest') || t.includes('phishing') || t.includes('analys')) return 'reason';
  if (t.includes('dispatch') || t.includes('plan') || t.includes('assign')) return 'plan';
  if (t.includes('tool') || t.includes('lookup') || t.includes('scan') || t.includes('query')) return 'act';
  if (t.includes('evidence') || t.includes('observed') || t.includes('telemetry')) return 'observe';
  if (t.includes('fusion') || t.includes('risk') || t.includes('evaluat') || t.includes('approval')) return 'evaluate';
  if (t.includes('response') || t.includes('contain') || t.includes('reassign')) return 'repeat';
  
  // Default to positional stage
  const stages = ['reason', 'plan', 'act', 'observe', 'evaluate', 'repeat'];
  return stages[index % stages.length];
}

export const InvestigationTimelinePanel: React.FC<InvestigationTimelinePanelProps> = ({
  timeline,
  currentIncidentId,
  onSelectEvidence,
}) => {
  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl text-xs">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-950/60">
        <div className="flex items-center space-x-2">
          <SuperIcon name="agent-loop" style="color" size={16} alt="Investigation Loop" />
          <h3 className="font-bold text-white tracking-wide">INVESTIGATION TIMELINE</h3>
          {currentIncidentId && (
            <span className="px-2 py-0.5 bg-cyan-950/60 text-cyan-300 border border-cyan-800/40 rounded-full font-mono text-[10px]">
              {currentIncidentId}
            </span>
          )}
        </div>
      </div>

      {/* SuperIntelligence AI Agent Loop Stage Header */}
      <div className="px-3.5 py-2.5 bg-slate-950/90 border-b border-slate-800/80">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider flex items-center">
            <SuperIcon name="reflection" style="duotone" size={12} className="mr-1" />
            AI Agent Autonomous Loop
          </span>
          <span className="text-[10px] text-cyan-400 font-mono font-semibold">
            {timeline.length > 0 ? `STAGE ${Math.min(timeline.length, 6)} OF 6` : 'STANDBY'}
          </span>
        </div>
        <div className="grid grid-cols-6 gap-1">
          {AGENT_LOOP_STAGES.map((st, idx) => {
            const status = getLoopStageStatus(idx, timeline);
            return (
              <div
                key={st.id}
                className={`flex flex-col items-center p-1 rounded border text-center transition-all ${
                  status === 'COMPLETED'
                    ? 'bg-cyan-950/40 border-cyan-500/50 text-cyan-300'
                    : status === 'ACTIVE'
                    ? 'bg-amber-950/60 border-amber-500 text-amber-300 shadow-sm shadow-amber-500/20'
                    : 'bg-slate-900/40 border-slate-800 text-slate-500'
                }`}
                title={`${st.label}: ${st.desc} (${status})`}
              >
                <SuperIcon
                  name={st.icon}
                  style={status === 'COMPLETED' || status === 'ACTIVE' ? 'color' : 'stroke'}
                  size={15}
                  className={`mb-0.5 ${status === 'ACTIVE' ? 'animate-pulse' : ''}`}
                />
                <span className="text-[9px] font-mono font-bold leading-tight">{st.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Timeline Steps */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {timeline.map((entry, index) => {
          const isLast = index === timeline.length - 1;
          const isComplete = entry.status === 'COMPLETED';
          const isAlert = entry.status === 'ALERT';
          const stageIcon = getEntryStageIcon(entry.title, index);

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
              <div className="flex-1 pb-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-100 flex items-center space-x-1.5">
                    <span>{entry.title}</span>
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {new Date(entry.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-slate-300 mt-0.5 leading-relaxed">{entry.description}</p>

                {entry.evidenceId && (
                  <div className="mt-1.5 flex items-center space-x-2">
                    <button
                      onClick={() => onSelectEvidence && onSelectEvidence(entry.evidenceId!)}
                      className="text-cyan-400 hover:text-cyan-300 text-[10px] font-mono flex items-center space-x-1"
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
            <p className="text-[11px] text-slate-600 mt-1">Trigger demo scenario to view live progression.</p>
          </div>
        )}
      </div>
    </div>
  );
};
