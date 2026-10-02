import React from 'react';
import { SecurityEvidence } from '../../types/evidence';
import { RiskBadge } from '../common/RiskBadge';
import { Pagination } from '../common/Pagination';
import { TableSkeleton } from '../common/Skeleton';
import { formatTimestamp } from '../../lib/utils';

interface EvidenceTableProps {
  evidence: SecurityEvidence[];
  total: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  onPageChange: (newPage: number) => void;
  onSelectEvent: (event: SecurityEvidence) => void;
}

export const EvidenceTable: React.FC<EvidenceTableProps> = ({
  evidence,
  total,
  page,
  pageSize,
  isLoading,
  onPageChange,
  onSelectEvent,
}) => {
  return (
    <div className="rounded-lg bg-hactm-card border border-hactm-border shadow-panel overflow-hidden">
      {isLoading ? (
        <TableSkeleton rows={8} cols={7} />
      ) : evidence.length === 0 ? (
        <div className="p-12 text-center text-xs text-hactm-muted">
          No security evidence records match the selected query and filters.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-hactm-border bg-hactm-panel/60 text-hactm-muted font-medium uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Event ID</th>
                <th className="py-2.5 px-3">Agent ID</th>
                <th className="py-2.5 px-3">Entity ID</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Cyber Risk</th>
                <th className="py-2.5 px-3">Confidence</th>
                <th className="py-2.5 px-3">Uncertainty</th>
                <th className="py-2.5 px-3">Timestamp (UTC)</th>
                <th className="py-2.5 px-3">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-hactm-border/60">
              {evidence.map((item) => (
                <tr
                  key={item.event_id}
                  onClick={() => onSelectEvent(item)}
                  className="hover:bg-hactm-hover/50 cursor-pointer transition-colors"
                >
                  <td className="py-2.5 px-3 font-mono font-medium text-hactm-accent">
                    {item.event_id}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-hactm-text">
                    {item.agent_id}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-hactm-text truncate max-w-[150px]">
                    {item.entity_id}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="px-1.5 py-0.5 rounded bg-hactm-panel border border-hactm-border/60 font-mono text-[10px]">
                      {item.event_type}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <RiskBadge score={item.risk_score} />
                  </td>
                  <td className="py-2.5 px-3 font-mono text-hactm-text">
                    {item.confidence.toFixed(2)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-hactm-muted">
                    {item.uncertainty.toFixed(2)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-hactm-muted whitespace-nowrap">
                    {formatTimestamp(item.timestamp)}
                  </td>
                  <td className="py-2.5 px-3 text-hactm-muted">
                    {item.source || '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination Footer */}
      <div className="p-3 border-t border-hactm-border bg-hactm-surface/40">
        <Pagination
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={onPageChange}
        />
      </div>
    </div>
  );
};
