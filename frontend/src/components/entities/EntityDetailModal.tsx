import React from 'react';
import { X, User, Clock, Layers } from 'lucide-react';
import { useEntityDetail } from '../../hooks/useEntities';
import { formatTimestamp } from '../../lib/utils';
import { RiskBadge } from '../common/RiskBadge';
import { JsonViewer } from '../common/JsonViewer';

interface EntityDetailModalProps {
  entityId: string | null;
  onClose: () => void;
  onSelectEvidence?: (eventId: string) => void;
}

export const EntityDetailModal: React.FC<EntityDetailModalProps> = ({
  entityId,
  onClose,
  onSelectEvidence,
}) => {
  const { data, isLoading } = useEntityDetail(entityId);
  const detail = data?.data;

  if (!entityId) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        className="w-full max-w-3xl max-h-[90vh] bg-hactm-card border border-hactm-border rounded-lg shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-5 py-4 border-b border-hactm-border flex items-center justify-between bg-hactm-panel/50">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded bg-hactm-accent/10 border border-hactm-accent/30 text-hactm-accent">
              <User size={16} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold font-mono text-hactm-heading">
                  {entityId}
                </h3>
                {detail && (
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-hactm-panel text-hactm-muted border border-hactm-border">
                    {detail.entity_type}
                  </span>
                )}
              </div>
              <p className="text-[11px] text-hactm-muted">
                Deterministic Resolved Cyber Entity Profile
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-hactm-muted hover:text-hactm-text hover:bg-hactm-surface transition-colors"
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 overflow-y-auto space-y-5 text-xs">
          {isLoading || !detail ? (
            <div className="py-12 text-center text-hactm-muted">Loading entity details...</div>
          ) : (
            <>
              {/* Overview grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded bg-hactm-surface border border-hactm-border">
                <div>
                  <span className="text-[10px] uppercase text-hactm-muted block font-medium">Canonical Name</span>
                  <span className="font-medium text-hactm-text">{detail.canonical_name}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-hactm-muted block font-medium">Total Events</span>
                  <span className="font-mono text-hactm-text font-bold">{detail.event_count}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-hactm-muted block font-medium">First Seen (UTC)</span>
                  <span className="font-mono text-hactm-text">{formatTimestamp(detail.first_seen)}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-hactm-muted block font-medium">Last Seen (UTC)</span>
                  <span className="font-mono text-hactm-text">{formatTimestamp(detail.last_seen)}</span>
                </div>
              </div>

              {/* Attributes JSON */}
              <div className="space-y-1.5">
                <h4 className="text-[11px] font-semibold uppercase tracking-wider text-hactm-muted">
                  Canonical Attributes
                </h4>
                <JsonViewer data={detail.attributes} title="Resolved Attributes" />
              </div>

              {/* Associated Evidence */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-[11px] font-semibold uppercase tracking-wider text-hactm-muted flex items-center gap-1.5">
                    <Layers size={13} />
                    <span>Associated Evidence Records ({detail.associated_evidence.length})</span>
                  </h4>
                </div>

                {detail.associated_evidence.length === 0 ? (
                  <div className="p-4 text-center text-hactm-muted border border-dashed border-hactm-border/60 rounded">
                    No associated evidence recorded.
                  </div>
                ) : (
                  <div className="rounded border border-hactm-border bg-hactm-surface overflow-hidden">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-hactm-border bg-hactm-panel/50 text-hactm-muted font-medium text-[10px] uppercase">
                          <th className="py-2 px-3">Event ID</th>
                          <th className="py-2 px-3">Type</th>
                          <th className="py-2 px-3">Cyber Risk</th>
                          <th className="py-2 px-3">Confidence</th>
                          <th className="py-2 px-3">Timestamp</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-hactm-border/50 font-mono">
                        {detail.associated_evidence.map((ev) => (
                          <tr
                            key={ev.event_id}
                            onClick={() => onSelectEvidence && onSelectEvidence(ev.event_id)}
                            className="hover:bg-hactm-hover/50 cursor-pointer transition-colors"
                          >
                            <td className="py-2 px-3 text-hactm-accent font-medium">{ev.event_id}</td>
                            <td className="py-2 px-3 text-hactm-text">{ev.event_type}</td>
                            <td className="py-2 px-3">
                              <RiskBadge score={ev.risk_score} />
                            </td>
                            <td className="py-2 px-3 text-hactm-text">{ev.confidence.toFixed(2)}</td>
                            <td className="py-2 px-3 text-hactm-muted">{formatTimestamp(ev.timestamp)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-hactm-border bg-hactm-panel/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded border border-hactm-border bg-hactm-surface hover:bg-hactm-panel text-hactm-text transition-colors text-xs"
          >
            Close Profile
          </button>
        </div>
      </div>
    </div>
  );
};
