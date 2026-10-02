import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
  size?: number;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = 'Loading...', size = 24 }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-3 text-hactm-muted animate-in fade-in duration-150">
      <Loader2 size={size} className="animate-spin text-hactm-accent" />
      {message && <p className="text-xs font-mono">{message}</p>}
    </div>
  );
};
