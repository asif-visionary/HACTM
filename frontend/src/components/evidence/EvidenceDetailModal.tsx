import React from 'react';
import { X, Shield, FileText, Database, Tag } from 'lucide-react';
import { SecurityEvidence } from '../../types/evidence';
import { RiskBadge } from '../common/RiskBadge';
import { Badge } from '../common/Badge';
import { JsonViewer } from '../common/JsonViewer';
import { formatTimestamp } from '../../lib/utils';

interface EvidenceDetailModalProps {
  evidence: SecurityEvidence | null;
  onClose: () => void;
}

export const EvidenceDetailModal: React.FC<EvidenceDetailModalProps> = ({
  evidence,
  onClose,
}) => {
  if (!evidence) return null;

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
              <Shield size={16} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold font-mono text-hactm-heading">
                  {evidence.event_id}
                </h3>
                <RiskBadge score={evidence.risk_score} />
              </div>
              <p className="text-[11px] text-hactm-muted">
                Observed Cyber Evidence Telemetry Inspector
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

        {/* Modal Body */}
        <div className="p-5 overflow-y-auto space-y-5 text-xs">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded bg-hactm-surface border border-hactm-border">
            <div>
              <span className="text-[10px] uppercase text-hactm-muted block font-medium">Event Type</span>
              <span className="font-mono text-hactm-text font-semibold">{evidence.event_type}</span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-hactm-muted block font-medium">Cyber Risk Score</span>
              <span className="font-mono text-hactm-text font-semibold">{evidence.risk_score.toFixed(4)}</span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-hactm-muted block font-medium">Confidence</span>
              <span className="font-mono text-hactm-text font-semibold">{evidence.confidence.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-[10px] uppercase text-hactm-muted block font-medium">Uncertainty</span>
              <span className="font-mono text-hactm-muted font-semibold">{evidence.uncertainty.toFixed(2)}</span>
            </div>
          </div>

          {/* Identifiers & Attribution */}
          <div className="space-y-2">
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-hactm-muted flex items-center gap-1.5">
              <FileText size={13} />
              <span>Attribution & Deterministic Resolution</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-3 rounded bg-hactm-surface/60 border border-hactm-border">
              <div>
                <span className="text-hactm-muted text-[10px] block">Entity ID</span>
                <span className="font-mono text-hactm-accent font-medium">{evidence.entity_id}</span>
              </div>
              <div>
                <span className="text-hactm-muted text-[10px] block">Agent ID</span>
                <span className="font-mono text-hactm-text">{evidence.agent_id}</span>
              </div>
              <div>
                <span className="text-hactm-muted text-[10px] block">Event Timestamp (UTC)</span>
                <span className="font-mono text-hactm-text">{formatTimestamp(evidence.timestamp)}</span>
              </div>
              <div>
                <span className="text-hactm-muted text-[10px] block">Source & Dataset</span>
                <span className="text-hactm-text">
                  {evidence.source || '—'} {evidence.dataset ? `(${evidence.dataset})` : ''}
                </span>
              </div>
            </div>
          </div>

          {/* Security Context */}
          <div className="space-y-2">
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-hactm-muted flex items-center gap-1.5">
              <Tag size={13} />
              <span>Security Context</span>
            </h4>
            <div className="p-3 rounded bg-hactm-surface/60 border border-hactm-border flex flex-wrap gap-2 items-center">
              {evidence.security_tags && evidence.security_tags.length > 0 ? (
                evidence.security_tags.map((tag, idx) => (
                  <Badge key={idx} variant="accent">
                    #{tag}
                  </Badge>
                ))
              ) : (
                <span className="text-hactm-muted italic text-[11px]">No security tags attached</span>
              )}
              {evidence.security_zone && (
                <Badge variant="default">Zone: {evidence.security_zone}</Badge>
              )}
              {evidence.security_group && (
                <Badge variant="muted">Group: {evidence.security_group}</Badge>
              )}
            </div>
          </div>

          {/* Evidentiary Telemetry Payload */}
          <div className="space-y-2">
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-hactm-muted">
              Structured Evidence Data
            </h4>
            <JsonViewer data={evidence.evidence} />
          </div>

          {/* Lineage & Research Reproducibility */}
          <div className="space-y-2">
            <h4 className="text-[11px] font-semibold uppercase tracking-wider text-hactm-muted flex items-center gap-1.5">
              <Database size={13} />
              <span>Research Lineage & Traceability</span>
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 p-3 rounded bg-hactm-panel/40 border border-hactm-border font-mono text-[11px]">
              <div>
                <span className="text-[9px] uppercase text-hactm-muted block">Schema Ver</span>
                <span>{evidence.schema_version || '1.0.0'}</span>
              </div>
              <div>
                <span className="text-[9px] uppercase text-hactm-muted block">Preproc Ver</span>
                <span>{evidence.preprocessing_version || '1.0.0'}</span>
              </div>
              <div>
                <span className="text-[9px] uppercase text-hactm-muted block">Source Row</span>
                <span>{evidence.source_record_id || '—'}</span>
              </div>
              <div>
                <span className="text-[9px] uppercase text-hactm-muted block">Ingestion Run</span>
                <span className="truncate block">{evidence.ingestion_run_id || 'manual'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-hactm-border bg-hactm-panel/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded border border-hactm-border bg-hactm-surface hover:bg-hactm-panel text-hactm-text transition-colors text-xs"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
