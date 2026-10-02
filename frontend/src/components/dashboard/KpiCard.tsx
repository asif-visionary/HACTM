import React from 'react';
import { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Skeleton } from '../common/Skeleton';

interface KpiCardProps {
  title: string;
  value: string | number | undefined;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'default' | 'accent' | 'warning' | 'danger';
  isLoading?: boolean;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default',
  isLoading = false,
}) => {
  const variantStyles = {
    default: 'border-slate-800/80 text-slate-300 bg-[#0B111A]',
    accent: 'border-cyan-500/30 text-cyan-400 bg-cyan-950/20',
    warning: 'border-amber-500/30 text-amber-400 bg-amber-950/20',
    danger: 'border-rose-500/30 text-rose-400 bg-rose-950/20',
  };

  return (
    <div className="p-5 rounded-2xl bg-[#101923] border border-slate-800/80 shadow-xl flex flex-col justify-between hover:border-slate-700/80 transition-all group">
      <div className="flex items-center justify-between text-xs text-slate-400 mb-3">
        <span className="font-semibold tracking-wider uppercase text-[11px]">{title}</span>
        <div className={cn('p-2.5 rounded-xl border transition-colors', variantStyles[variant])}>
          <Icon size={18} />
        </div>
      </div>

      <div className="my-1">
        {isLoading ? (
          <Skeleton className="h-9 w-28 my-1" />
        ) : (
          <div className="text-3xl font-bold font-mono text-white tracking-tight group-hover:text-cyan-400 transition-colors">
            {value !== undefined ? value : '—'}
          </div>
        )}
      </div>

      {subtitle && (
        <div className="text-xs text-slate-400 font-sans mt-2 flex items-center gap-1">
          <span>{subtitle}</span>
        </div>
      )}
    </div>
  );
};
