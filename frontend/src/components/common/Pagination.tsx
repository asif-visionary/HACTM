import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (newPage: number) => void;
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  page,
  pageSize,
  total,
  onPageChange,
  className,
}) => {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const startItem = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(total, page * pageSize);

  const isFirst = page <= 1;
  const isLast = page >= totalPages;

  return (
    <div className={`flex flex-wrap items-center justify-between gap-3 text-xs text-hactm-muted ${className || ''}`}>
      <div>
        Showing <span className="font-mono text-hactm-text">{startItem}</span> to{' '}
        <span className="font-mono text-hactm-text">{endItem}</span> of{' '}
        <span className="font-mono text-hactm-text">{total.toLocaleString()}</span> records
      </div>

      <div className="flex items-center gap-2">
        <span className="mr-2">
          Page <span className="font-mono text-hactm-text">{page}</span> of{' '}
          <span className="font-mono text-hactm-text">{totalPages}</span>
        </span>

        <button
          onClick={() => onPageChange(page - 1)}
          disabled={isFirst}
          className="flex items-center justify-center p-1.5 rounded border border-hactm-border bg-hactm-surface hover:bg-hactm-panel disabled:opacity-40 disabled:cursor-not-allowed text-hactm-text transition-colors focus:ring-1 focus:ring-hactm-accent"
          aria-label="Previous page"
        >
          <ChevronLeft size={14} />
        </button>

        <button
          onClick={() => onPageChange(page + 1)}
          disabled={isLast}
          className="flex items-center justify-center p-1.5 rounded border border-hactm-border bg-hactm-surface hover:bg-hactm-panel disabled:opacity-40 disabled:cursor-not-allowed text-hactm-text transition-colors focus:ring-1 focus:ring-hactm-accent"
          aria-label="Next page"
        >
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
};
