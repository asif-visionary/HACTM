import React from 'react';
import { LucideIcon, Lock, CheckCircle2, ArrowRight } from 'lucide-react';

interface AgentPlaceholderProps {
  name: string;
  plannedPhase: string;
  domain: string;
  icon: LucideIcon;
  description: string;
  isActive?: boolean;
  onSelect?: () => void;
}

export const AgentStatusCard: React.FC<AgentPlaceholderProps> = ({
  name,
  plannedPhase,
  domain,
  icon: Icon,
  description,
  isActive = false,
  onSelect,
}) => {
  return (
    <div
      onClick={isActive ? onSelect : undefined}
      className={`p-5 rounded-lg bg-hactm-card border ${
        isActive
          ? 'border-emerald-500/40 hover:border-emerald-500/80 cursor-pointer shadow-lg shadow-emerald-500/5'
          : 'border-hactm-border hover:border-hactm-border/80'
      } shadow-panel flex flex-col justify-between relative overflow-hidden group transition-all`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div
            className={`p-2 rounded bg-hactm-panel border ${
              isActive
                ? 'border-emerald-500/30 text-emerald-400'
                : 'border-hactm-border text-hactm-muted group-hover:text-hactm-accent'
            } transition-colors`}
          >
            <Icon size={18} />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-hactm-heading">{name}</h4>
            <span className="text-[10px] font-mono text-hactm-muted uppercase">{domain}</span>
          </div>
        </div>

        {isActive ? (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <CheckCircle2 size={10} />
            <span>Active</span>
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-hactm-panel border border-hactm-border text-hactm-muted">
            <Lock size={10} />
            <span>{plannedPhase}</span>
          </span>
        )}
      </div>

      <p className="text-xs text-hactm-muted leading-relaxed mb-4">{description}</p>

      <div className="pt-3 border-t border-hactm-border/60 flex items-center justify-between text-[11px] font-mono">
        <span className="text-hactm-muted">Runtime Status:</span>
        {isActive ? (
          <span className="text-emerald-400 font-medium inline-flex items-center gap-1">
            <span>Online &bull; Open Console</span>
            <ArrowRight size={12} />
          </span>
        ) : (
          <span className="text-amber-400/90 font-medium">Not enabled &mdash; {plannedPhase}</span>
        )}
      </div>
    </div>
  );
};

