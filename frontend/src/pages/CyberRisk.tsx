import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Shield, Clock, TrendingUp, AlertTriangle, CheckCircle2, User, Layers, Search } from 'lucide-react';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export const CyberRisk: React.FC = () => {
  const [searchEntity, setSearchEntity] = useState<string>('USER-103');
  const [activeEntity, setActiveEntity] = useState<string>('USER-103');

  const { data: riskData, isLoading, refetch } = useQuery({
    queryKey: ['entity-risk', activeEntity],
    queryFn: () => api.getEntityRisk(activeEntity),
  });

  const riskInfo = riskData?.data;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchEntity.trim()) {
      setActiveEntity(searchEntity.trim());
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Header & Search */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-hactm-heading tracking-tight flex items-center gap-2">
            <span>Unified Cyber Risk Telemetry</span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 font-normal">
              Entity Risk Evolution
            </span>
          </h1>
          <p className="text-xs text-hactm-muted mt-1">
            Tracks historical cyber-risk score trajectories for deterministically resolved actors.
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-hactm-muted" />
            <input
              type="text"
              value={searchEntity}
              onChange={(e) => setSearchEntity(e.target.value)}
              placeholder="Search Entity ID..."
              className="pl-8 pr-3 py-1.5 rounded bg-hactm-card border border-hactm-border text-xs text-hactm-text focus:outline-none focus:border-hactm-accent w-48 font-mono"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 rounded bg-hactm-accent text-black font-semibold text-xs hover:bg-hactm-accent/90 transition-colors"
          >
            Inspect
          </button>
        </form>
      </div>

      {isLoading ? (
        <LoadingSpinner message="Retrieving entity cyber risk telemetry..." />
      ) : (
        <div className="space-y-6">
          {/* Main Risk Overview */}
          <div className="p-5 rounded-lg bg-hactm-card border border-hactm-border space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="p-2.5 rounded-lg bg-hactm-panel border border-hactm-border text-hactm-accent">
                  <User size={22} />
                </span>
                <div>
                  <h2 className="text-sm font-bold text-hactm-heading font-mono">
                    {riskInfo?.entity_id || activeEntity}
                  </h2>
                  <span className="text-xs text-hactm-muted block">
                    Last Assessed: {riskInfo?.last_assessed_at ? new Date(riskInfo.last_assessed_at).toLocaleTimeString() : 'N/A'}
                  </span>
                </div>
              </div>

              <div className="text-right">
                <span className="text-xs text-hactm-muted block">Current Unified Cyber Risk</span>
                <span className="text-3xl font-mono font-bold text-amber-400">
                  {riskInfo?.current_risk_score?.toFixed(2) || '0.00'}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-hactm-border text-xs">
              <div className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border">
                <span className="text-hactm-muted text-[10px] block">Risk Category</span>
                <span className="font-mono font-semibold text-hactm-text">
                  {riskInfo?.current_risk_category || 'LOW'}
                </span>
              </div>
              <div className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border">
                <span className="text-hactm-muted text-[10px] block">Confidence</span>
                <span className="font-mono font-semibold text-emerald-400">
                  {((riskInfo?.confidence || 1.0) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border">
                <span className="text-hactm-muted text-[10px] block">Uncertainty</span>
                <span className="font-mono font-semibold text-amber-400">
                  {((riskInfo?.uncertainty || 0.0) * 100).toFixed(1)}%
                </span>
              </div>
              <div className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border">
                <span className="text-hactm-muted text-[10px] block">Domain Coverage</span>
                <span className="font-mono font-semibold text-hactm-accent">
                  {((riskInfo?.coverage || 0.2) * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>

          {/* Historical Risk Trajectory Timeline */}
          <div className="p-5 rounded-lg bg-hactm-card border border-hactm-border space-y-4">
            <h2 className="text-xs font-semibold text-hactm-text tracking-wide flex items-center gap-2">
              <TrendingUp size={16} className="text-hactm-accent" />
              <span>Historical Risk Trajectory Timeline ({riskInfo?.history?.length || 0} evaluations)</span>
            </h2>

            {!riskInfo?.history || riskInfo.history.length === 0 ? (
              <p className="text-xs text-hactm-muted italic p-4 text-center">
                No historical risk evaluations recorded yet. Run evidence fusion to generate risk trajectory points.
              </p>
            ) : (
              <div className="space-y-2 text-xs">
                {riskInfo.history.map((h: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3 rounded bg-hactm-panel/70 border border-hactm-border flex items-center justify-between font-mono text-[11px]"
                  >
                    <div className="flex items-center gap-3">
                      <Clock size={14} className="text-hactm-muted" />
                      <span>{new Date(h.timestamp).toLocaleTimeString()}</span>
                    </div>

                    <div className="flex items-center gap-4">
                      <span className="text-hactm-muted">
                        Coverage: {(h.coverage * 100).toFixed(0)}%
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded border text-[10px] ${
                          h.risk_score >= 0.75
                            ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                            : h.risk_score >= 0.5
                            ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                            : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                        }`}
                      >
                        {h.risk_category} ({h.risk_score.toFixed(2)})
                      </span>
                      <span className="text-hactm-muted text-[10px]">
                        Fusion: {h.fusion_id}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
