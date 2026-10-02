import React from 'react';
import { cn, getRiskSeverity } from '../../lib/utils';

interface RiskBadgeProps {
  score: number;
  showScore?: boolean;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  score,
  showScore = true,
  className,
}) => {
  const severity = getRiskSeverity(score);

  const config = {
    LOW: {
      bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
      dot: 'bg-emerald-500',
      label: 'LOW',
    },
    MEDIUM: {
      bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
      dot: 'bg-amber-500',
      label: 'MEDIUM',
    },
    HIGH: {
      bg: 'bg-orange-500/10 border-orange-500/30 text-orange-400',
      dot: 'bg-orange-500',
      label: 'HIGH',
    },
    CRITICAL: {
      bg: 'bg-red-500/10 border-red-500/30 text-red-400',
      dot: 'bg-red-500',
      label: 'CRITICAL',
    },
  }[severity];

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono font-medium border tracking-wider',
        config.bg,
        className
      )}
      aria-label={`Risk Level ${config.label}, Score ${score.toFixed(2)}`}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full', config.dot)} aria-hidden="true" />
      <span>{config.label}</span>
      {showScore && <span className="opacity-75 font-mono">({score.toFixed(2)})</span>}
    </span>
  );
};
