import React from 'react';
import { Search, Filter, X } from 'lucide-react';

interface EvidenceFiltersProps {
  search: string;
  onSearchChange: (val: string) => void;
  eventType: string;
  onEventTypeChange: (val: string) => void;
  severity: string;
  onSeverityChange: (val: string) => void;
  minRisk: string;
  onMinRiskChange: (val: string) => void;
  maxRisk: string;
  onMaxRiskChange: (val: string) => void;
  source: string;
  onSourceChange: (val: string) => void;
  onReset: () => void;
}

export const EvidenceFilters: React.FC<EvidenceFiltersProps> = ({
  search,
  onSearchChange,
  eventType,
  onEventTypeChange,
  severity,
  onSeverityChange,
  minRisk,
  onMinRiskChange,
  maxRisk,
  onMaxRiskChange,
  source,
  onSourceChange,
  onReset,
}) => {
  const hasActiveFilters =
    Boolean(search) ||
    Boolean(eventType) ||
    Boolean(severity) ||
    Boolean(minRisk) ||
    Boolean(maxRisk) ||
    Boolean(source);

  return (
    <div className="p-4 rounded-lg bg-hactm-card border border-hactm-border shadow-panel space-y-3">
      {/* Search Bar */}
      <div className="relative">
        <Search
          size={15}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-hactm-muted"
        />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Global evidence search: Event ID, Entity ID, Agent ID, Source..."
          className="w-full pl-9 pr-4 py-2 rounded bg-hactm-surface border border-hactm-border text-xs text-hactm-text placeholder:text-hactm-muted/60 focus:outline-none focus:ring-1 focus:ring-hactm-accent focus:border-hactm-accent font-mono"
        />
      </div>

      {/* Filter Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 text-xs">
        {/* Event Type */}
        <div>
          <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
            Event Type
          </label>
          <select
            value={eventType}
            onChange={(e) => onEventTypeChange(e.target.value)}
            className="w-full px-2 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text focus:outline-none focus:ring-1 focus:ring-hactm-accent font-mono text-[11px]"
          >
            <option value="">All Types</option>
            <option value="NETWORK">Network</option>
            <option value="AUTHENTICATION">Authentication</option>
            <option value="EMAIL">Email</option>
            <option value="UBA">UBA</option>
            <option value="TRANSACTION">Transaction</option>
            <option value="SYSTEM">System</option>
          </select>
        </div>

        {/* Severity */}
        <div>
          <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
            Severity
          </label>
          <select
            value={severity}
            onChange={(e) => onSeverityChange(e.target.value)}
            className="w-full px-2 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text focus:outline-none focus:ring-1 focus:ring-hactm-accent font-mono text-[11px]"
          >
            <option value="">All Severities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>

        {/* Min Risk */}
        <div>
          <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
            Min Risk (0-1)
          </label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.05"
            value={minRisk}
            onChange={(e) => onMinRiskChange(e.target.value)}
            placeholder="e.g. 0.6"
            className="w-full px-2 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text focus:outline-none focus:ring-1 focus:ring-hactm-accent font-mono text-[11px]"
          />
        </div>

        {/* Max Risk */}
        <div>
          <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
            Max Risk (0-1)
          </label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.05"
            value={maxRisk}
            onChange={(e) => onMaxRiskChange(e.target.value)}
            placeholder="e.g. 1.0"
            className="w-full px-2 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text focus:outline-none focus:ring-1 focus:ring-hactm-accent font-mono text-[11px]"
          />
        </div>

        {/* Source */}
        <div>
          <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
            Source
          </label>
          <input
            type="text"
            value={source}
            onChange={(e) => onSourceChange(e.target.value)}
            placeholder="e.g. Suricata"
            className="w-full px-2 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text focus:outline-none focus:ring-1 focus:ring-hactm-accent font-mono text-[11px]"
          />
        </div>

        {/* Reset */}
        <div className="flex items-end">
          <button
            onClick={onReset}
            disabled={!hasActiveFilters}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 rounded border border-hactm-border bg-hactm-panel text-hactm-muted hover:text-hactm-text hover:bg-hactm-panel/80 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-[11px]"
          >
            <X size={13} />
            <span>Reset</span>
          </button>
        </div>
      </div>
    </div>
  );
};
