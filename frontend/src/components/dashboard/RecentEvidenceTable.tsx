import React from 'react';
import { SecurityEvidence } from '../../types/evidence';
import { RiskBadge } from '../common/RiskBadge';
import { formatTimestamp } from '../../lib/utils';
import { TableSkeleton } from '../common/Skeleton';

interface RecentEvidenceTableProps {
  events?: SecurityEvidence[];
  evidence?: SecurityEvidence[];
  isLoading?: boolean;
  onSelectEvent: (event: SecurityEvidence) => void;
  onViewAll?: () => void;
}

export const RecentEvidenceTable: React.FC<RecentEvidenceTableProps> = ({
  events,
  evidence,
  isLoading = false,
  onSelectEvent,
  onViewAll,
}) => {
  const dataList = events || evidence || [];

  return (
    <div className="rounded-2xl bg-[#0B111A] border border-slate-800/80 shadow-xl overflow-hidden">
      {isLoading ? (
        <TableSkeleton rows={5} cols={7} />
      ) : dataList.length === 0 ? (
        <div className="p-8 text-center text-xs text-slate-400 font-mono">
          No security evidence has been ingested yet.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800/80 bg-[#101923] text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Event ID</th>
                <th className="py-3 px-4">Event Type</th>
                <th className="py-3 px-4">Entity ID</th>
                <th className="py-3 px-4">Cyber Risk Score</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Uncertainty</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Agent / Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {dataList.map((item) => (
                <tr
                  key={item.event_id}
                  onClick={() => onSelectEvent(item)}
                  className="hover:bg-[#131E2A] cursor-pointer transition-colors group"
                >
                  <td className="py-3 px-4 font-mono font-semibold text-cyan-400 group-hover:text-cyan-300">
                    {item.event_id}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-200">
                    <span className="px-2 py-0.5 rounded-md bg-[#101923] border border-slate-800 text-[10px] text-slate-300">
                      {item.event_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300 truncate max-w-[160px]">
                    {item.entity_id}
                  </td>
                  <td className="py-3 px-4">
                    <RiskBadge score={item.risk_score} />
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-300">
                    {item.confidence.toFixed(2)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400">
                    {item.uncertainty.toFixed(2)}
                  </td>
                  <td className="py-3 px-4 font-mono text-slate-400 whitespace-nowrap">
                    {formatTimestamp(item.timestamp)}
                  </td>
                  <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">
                    {item.agent_id || item.source || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
