import React from 'react';
import { AlertTriangle, ArrowUpRight, ShieldAlert, ShieldCheck, Clock, ExternalLink } from 'lucide-react';
import { SecurityEvidence } from '../../types/evidence';
import { formatRelativeTime } from '../../lib/utils';
import { Badge } from '../common/Badge';

interface PriorityQueueProps {
  evidenceList: SecurityEvidence[];
  onSelectEvidence: (evidence: SecurityEvidence) => void;
}

export const PriorityQueue: React.FC<PriorityQueueProps> = ({
  evidenceList,
  onSelectEvidence,
}) => {
  // Sort high risk first
  const sorted = [...evidenceList].sort((a, b) => b.risk_score - a.risk_score).slice(0, 5);

  const getSeverityBadge = (severity: string, risk: number) => {
    const sev = severity ? severity.toUpperCase() : risk >= 0.8 ? 'CRITICAL' : risk >= 0.6 ? 'HIGH' : risk >= 0.3 ? 'MEDIUM' : 'LOW';
    switch (sev) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-rose-950/80 text-rose-400 border border-rose-800/60 flex items-center gap-1"><ShieldAlert className="w-3 h-3" /> CRITICAL</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-950/80 text-amber-400 border border-amber-800/60 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> HIGH</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-yellow-950/80 text-yellow-400 border border-yellow-800/60 flex items-center gap-1">MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 flex items-center gap-1">LOW</span>;
    }
  };

  return (
    <div className="bg-[#101923] border border-slate-800/80 rounded-2xl p-5 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-xl">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">Security Priority Queue</h3>
            <p className="text-[11px] text-slate-400">High-risk evidence requires real-time analyst action</p>
          </div>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-900 border border-slate-800 text-slate-300">
          {sorted.length} Pending
        </span>
      </div>

      <div className="space-y-2.5">
        {sorted.length === 0 ? (
          <div className="p-6 text-center text-slate-400 text-xs font-mono">
            No high-priority threats queued. System nominal.
          </div>
        ) : (
          sorted.map((item) => (
            <div
              key={item.event_id}
              onClick={() => onSelectEvidence(item)}
              className="p-3.5 bg-[#0B111A]/80 hover:bg-[#131E2A] border border-slate-800/80 hover:border-slate-700 rounded-xl transition-all cursor-pointer group flex items-start justify-between gap-3"
            >
              <div className="space-y-1.5 min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  {getSeverityBadge(item.severity, item.risk_score)}
                  <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-400 transition-colors truncate">
                    {item.event_type}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono">
                  <span>Entity: <strong className="text-slate-300">{item.entity_id}</strong></span>
                  <span>Agent: <strong className="text-slate-300">{item.agent_id}</strong></span>
                </div>
              </div>

              <div className="flex flex-col items-end justify-between self-stretch flex-shrink-0">
                <span className="text-xs font-mono font-bold text-rose-400">
                  Risk {(item.risk_score * 100).toFixed(0)}%
                </span>
                <span className="text-[10px] text-slate-400 font-mono flex items-center gap-1 mt-1">
                  <Clock className="w-3 h-3" />
                  {formatRelativeTime(item.timestamp)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
