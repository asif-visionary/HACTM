import React from 'react';
import { Entity } from '../../types/entity';
import { formatTimestamp } from '../../lib/utils';
import { Pagination } from '../common/Pagination';
import { TableSkeleton } from '../common/Skeleton';

interface EntityTableProps {
  entities: Entity[];
  total: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  onPageChange: (newPage: number) => void;
  onSelectEntity: (entity: Entity) => void;
}

export const EntityTable: React.FC<EntityTableProps> = ({
  entities,
  total,
  page,
  pageSize,
  isLoading,
  onPageChange,
  onSelectEntity,
}) => {
  return (
    <div className="rounded-lg bg-hactm-card border border-hactm-border shadow-panel overflow-hidden">
      {isLoading ? (
        <TableSkeleton rows={6} cols={6} />
      ) : entities.length === 0 ? (
        <div className="p-12 text-center text-xs text-hactm-muted">
          No entities found in storage.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-hactm-border bg-hactm-panel/60 text-hactm-muted font-medium uppercase tracking-wider text-[10px]">
                <th className="py-2.5 px-3">Entity ID</th>
                <th className="py-2.5 px-3">Entity Type</th>
                <th className="py-2.5 px-3">Canonical Name</th>
                <th className="py-2.5 px-3">Event Count</th>
                <th className="py-2.5 px-3">First Seen (UTC)</th>
                <th className="py-2.5 px-3">Last Seen (UTC)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-hactm-border/60">
              {entities.map((ent) => (
                <tr
                  key={ent.entity_id}
                  onClick={() => onSelectEntity(ent)}
                  className="hover:bg-hactm-hover/50 cursor-pointer transition-colors"
                >
                  <td className="py-2.5 px-3 font-mono font-medium text-hactm-accent">
                    {ent.entity_id}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className="px-1.5 py-0.5 rounded bg-hactm-panel border border-hactm-border/60 font-mono text-[10px]">
                      {ent.entity_type}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-medium text-hactm-text">
                    {ent.canonical_name}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-hactm-text font-semibold">
                    {ent.event_count.toLocaleString()}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-hactm-muted whitespace-nowrap">
                    {formatTimestamp(ent.first_seen)}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-hactm-muted whitespace-nowrap">
                    {formatTimestamp(ent.last_seen)}
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
