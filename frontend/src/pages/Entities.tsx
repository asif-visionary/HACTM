import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { useEntities } from '../hooks/useEntities';
import { EntityTable } from '../components/entities/EntityTable';
import { EntityDetailModal } from '../components/entities/EntityDetailModal';
import { Entity } from '../types/entity';
import { ErrorState } from '../components/common/ErrorState';

export const Entities: React.FC = () => {
  const [page, setPage] = useState(1);
  const pageSize = 50;
  const [query, setQuery] = useState('');
  const [entityType, setEntityType] = useState('');
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);

  const queryParams = {
    page,
    page_size: pageSize,
    query: query.trim() || undefined,
    entity_type: entityType || undefined,
  };

  const { data, isLoading, isError, refetch } = useEntities(queryParams);

  if (isError) {
    return (
      <ErrorState
        title="Failed to Load Entities"
        message="An error occurred while fetching resolved cyber entities."
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
          <span>Entities</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-hactm-panel text-hactm-muted border border-hactm-border font-normal">
            Deterministic Identity Resolution
          </span>
        </h1>
        <p className="text-xs text-hactm-muted mt-1">
          Catalog of resolved entities derived from normalized telemetry (IPs, accounts, users, hosts, devices).
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-lg bg-hactm-card border border-hactm-border shadow-panel flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-hactm-muted" />
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setPage(1);
            }}
            placeholder="Search entities by ID or canonical name..."
            className="w-full pl-9 pr-4 py-2 rounded bg-hactm-surface border border-hactm-border text-xs text-hactm-text font-mono focus:ring-1 focus:ring-hactm-accent focus:outline-none"
          />
        </div>

        <select
          value={entityType}
          onChange={(e) => {
            setEntityType(e.target.value);
            setPage(1);
          }}
          className="px-3 py-2 rounded bg-hactm-surface border border-hactm-border text-xs text-hactm-text font-mono focus:ring-1 focus:ring-hactm-accent focus:outline-none"
        >
          <option value="">All Entity Types</option>
          <option value="IP">IP Addresses</option>
          <option value="EMAIL">Emails</option>
          <option value="USER">Users</option>
          <option value="HOST">Hosts</option>
          <option value="DEVICE">Devices</option>
          <option value="ACCOUNT">Accounts</option>
        </select>
      </div>

      {/* Table */}
      <EntityTable
        entities={items}
        total={total}
        page={page}
        pageSize={pageSize}
        isLoading={isLoading}
        onPageChange={(newPage) => setPage(newPage)}
        onSelectEntity={(ent) => setSelectedEntityId(ent.entity_id)}
      />

      {/* Detail Modal */}
      <EntityDetailModal
        entityId={selectedEntityId}
        onClose={() => setSelectedEntityId(null)}
      />
    </div>
  );
};
