import React, { useState } from 'react';
import { useEvidence } from '../hooks/useEvidence';
import { EvidenceFilters } from '../components/evidence/EvidenceFilters';
import { EvidenceTable } from '../components/evidence/EvidenceTable';
import { EvidenceDetailModal } from '../components/evidence/EvidenceDetailModal';
import { SecurityEvidence } from '../types/evidence';
import { ErrorState } from '../components/common/ErrorState';

export const Evidence: React.FC = () => {
  const [page, setPage] = useState(1);
  const pageSize = 50;
  const [search, setSearch] = useState('');
  const [eventType, setEventType] = useState('');
  const [severity, setSeverity] = useState('');
  const [minRisk, setMinRisk] = useState('');
  const [maxRisk, setMaxRisk] = useState('');
  const [source, setSource] = useState('');

  const [selectedEvent, setSelectedEvent] = useState<SecurityEvidence | null>(null);

  const queryParams = {
    page,
    page_size: pageSize,
    search: search.trim() || undefined,
    event_type: eventType || undefined,
    severity: severity || undefined,
    min_risk: minRisk ? parseFloat(minRisk) : undefined,
    max_risk: maxRisk ? parseFloat(maxRisk) : undefined,
    source: source.trim() || undefined,
  };

  const { data, isLoading, isError, refetch } = useEvidence(queryParams);

  const handleReset = () => {
    setSearch('');
    setEventType('');
    setSeverity('');
    setMinRisk('');
    setMaxRisk('');
    setSource('');
    setPage(1);
  };

  if (isError) {
    return (
      <ErrorState
        title="Failed to Load Evidence"
        message="An error occurred while fetching security evidence from the repository."
        onRetry={() => refetch()}
      />
    );
  }

  const items = data?.data || [];
  const total = data?.pagination?.total || 0;

  return (
    <div className="space-y-5 animate-in fade-in duration-150">
      <div>
        <h1 className="text-xl font-bold text-hactm-heading tracking-tight flex items-center gap-2">
          <span>Evidence Explorer</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-hactm-panel text-hactm-muted border border-hactm-border font-normal">
            Canonical SecurityEvidence
          </span>
        </h1>
        <p className="text-xs text-hactm-muted mt-1">
          Query, filter, and inspect common security telemetry records stored in the Foundation persistent repository.
        </p>
      </div>

      <EvidenceFilters
        search={search}
        onSearchChange={(val) => {
          setSearch(val);
          setPage(1);
        }}
        eventType={eventType}
        onEventTypeChange={(val) => {
          setEventType(val);
          setPage(1);
        }}
        severity={severity}
        onSeverityChange={(val) => {
          setSeverity(val);
          setPage(1);
        }}
        minRisk={minRisk}
        onMinRiskChange={(val) => {
          setMinRisk(val);
          setPage(1);
        }}
        maxRisk={maxRisk}
        onMaxRiskChange={(val) => {
          setMaxRisk(val);
          setPage(1);
        }}
        source={source}
        onSourceChange={(val) => {
          setSource(val);
          setPage(1);
        }}
        onReset={handleReset}
      />

      <EvidenceTable
        evidence={items}
        total={total}
        page={page}
        pageSize={pageSize}
        isLoading={isLoading}
        onPageChange={(newPage) => setPage(newPage)}
        onSelectEvent={(ev) => setSelectedEvent(ev)}
      />

      <EvidenceDetailModal
        evidence={selectedEvent}
        onClose={() => setSelectedEvent(null)}
      />
    </div>
  );
};
