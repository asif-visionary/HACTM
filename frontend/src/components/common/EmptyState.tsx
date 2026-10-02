import React from 'react';
import { Database, AlertCircle, RefreshCw } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No security evidence has been ingested yet.',
  description = 'Ingest a dataset via CLI or Settings to view telemetry and security evidence.',
  icon,
  action,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-hactm-border rounded-lg bg-hactm-surface/40 my-4">
      <div className="w-12 h-12 rounded-full bg-hactm-panel flex items-center justify-center text-hactm-muted mb-3 border border-hactm-border">
        {icon || <Database size={22} />}
      </div>
      <h3 className="text-sm font-medium text-hactm-heading mb-1">{title}</h3>
      <p className="text-xs text-hactm-muted max-w-md mb-4">{description}</p>
      {action && <div>{action}</div>}
    </div>
  );
};

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  title?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Backend unavailable',
  message = 'Unable to establish connection with the HACTM core services. Ensure the backend server is running.',
  onRetry,
}) => {
  return (
    <div className="p-6 rounded-lg border border-red-500/30 bg-red-950/20 text-center my-4 max-w-lg mx-auto">
      <div className="w-10 h-10 rounded-full bg-red-500/10 text-red-400 mx-auto flex items-center justify-center mb-3 border border-red-500/20">
        <AlertCircle size={20} />
      </div>
      <h3 className="text-sm font-semibold text-red-200 mb-1">{title}</h3>
      <p className="text-xs text-red-300/80 mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-red-500/20 text-red-200 hover:bg-red-500/30 border border-red-500/30 transition-colors focus:outline-none focus:ring-1 focus:ring-red-400"
        >
          <RefreshCw size={13} />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};
