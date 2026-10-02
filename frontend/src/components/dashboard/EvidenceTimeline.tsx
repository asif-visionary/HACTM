import React from 'react';
import { Clock, ShieldAlert } from 'lucide-react';
import { SecurityEvidence } from '../../types/evidence';
import { RiskBadge } from '../common/RiskBadge';
import { formatTimestamp } from '../../lib/utils';

interface EvidenceTimelineProps {
  timeline: SecurityEvidence[];
  isLoading?: boolean;
  onSelectEvent: (event: SecurityEvidence) => void;
}

export const EvidenceTimeline: React.FC<EvidenceTimelineProps> = ({
  timeline,
  isLoading = false,
  onSelectEvent,
}) => {
  return (
    <div className="p-5 rounded-lg bg-hactm-card border border-hactm-border shadow-panel">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-hactm-heading">Evidence Timeline</h3>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-hactm-panel text-hactm-muted border border-hactm-border">
              Temporal Sequence
            </span>
          </div>
          <p className="text-xs text-hactm-muted">
            Chronological ordering of ingested security evidence telemetry (Not attack-chain inference)
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-hactm-muted">
          <Clock size={14} />
          <span>Latest {timeline.length} events</span>
        </div>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-xs text-hactm-muted">Loading timeline...</div>
      ) : timeline.length === 0 ? (
        <div className="py-12 text-center text-xs text-hactm-muted border border-dashed border-hactm-border/60 rounded">
          No evidence ingested yet.
        </div>
      ) : (
        <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-hactm-border">
          {timeline.map((item) => (
            <div
              key={item.event_id}
              onClick={() => onSelectEvent(item)}
              className="relative group cursor-pointer"
            >
              {/* Timeline marker */}
              <div className="absolute -left-[27px] top-1.5 w-3 h-3 rounded-full border-2 border-hactm-card bg-hactm-accent group-hover:scale-125 transition-transform" />

              <div className="p-3 rounded border border-hactm-border bg-hactm-surface/60 group-hover:bg-hactm-panel group-hover:border-hactm-accent/40 transition-colors">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-hactm-heading group-hover:text-hactm-accent transition-colors">
                      {item.event_id}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-hactm-panel text-hactm-muted border border-hactm-border">
                      {item.event_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <RiskBadge score={item.risk_score} />
                    <span className="text-[11px] font-mono text-hactm-muted">
                      {formatTimestamp(item.timestamp)}
                    </span>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between text-xs text-hactm-muted gap-2">
                  <div className="flex items-center gap-1.5">
                    <span className="text-hactm-muted">Entity:</span>
                    <span className="font-mono text-hactm-text">{item.entity_id}</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px]">
                    <span>
                      Confidence: <strong className="font-mono text-hactm-text">{item.confidence.toFixed(2)}</strong>
                    </span>
                    <span>
                      Source: <strong className="font-mono text-hactm-text">{item.source || '—'}</strong>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
