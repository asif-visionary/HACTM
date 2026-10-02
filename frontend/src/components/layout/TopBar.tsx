import React from 'react';
import { Shield, Activity, RefreshCw, Cpu, AlertTriangle, Layers, Radio } from 'lucide-react';
import { useSystemStatus } from '../../hooks/useSystemStatus';
import { formatRelativeTime } from '../../lib/utils';

export const TopBar: React.FC = () => {
  const { status, isConnected, lastSyncTime, refetch, isLoading } = useSystemStatus();

  return (
    <header className="h-16 border-b border-slate-800/80 bg-[#070B12]/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40 transition-colors">
      {/* Brand & Command Center Title */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-sm shadow-cyan-500/20">
            <Shield size={20} />
          </div>
          <div>
            <div className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              <span>HACTM</span>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/50 uppercase">
                CYBER TRUST MESH
              </span>
            </div>
            <div className="text-[11px] text-slate-400 tracking-wide font-medium flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              <span>Operations Command Center</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top-Level Haulix-Style Operational KPI Pills */}
      <div className="hidden xl:flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0B111A] border border-slate-800/80 text-xs font-mono">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Agents:</span>
          <span className="text-white font-semibold">5 / 5 Active</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0B111A] border border-slate-800/80 text-xs font-mono">
          <Layers className="w-3.5 h-3.5 text-indigo-400" />
          <span className="text-slate-400">Telemetry:</span>
          <span className="text-white font-semibold">Multi-Domain Mesh</span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0B111A] border border-slate-800/80 text-xs font-mono">
          <Radio className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-slate-400">Environment:</span>
          <span className="text-emerald-400 font-semibold">{status?.environment || 'Defensive Enterprise'}</span>
        </div>
      </div>

      {/* System Health & Controls */}
      <div className="flex items-center gap-4 text-xs">
        {/* System Health Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0B111A] border border-slate-800/80 font-mono">
          <span className="text-slate-400 hidden sm:inline">System Health:</span>
          <span className="inline-flex items-center gap-1.5 font-medium">
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-rose-500 shadow-sm shadow-rose-500/50'
              }`}
            />
            <span className={isConnected ? 'text-emerald-400' : 'text-rose-400'}>
              {isConnected ? 'Operational' : 'Offline'}
            </span>
          </span>
        </div>

        {/* Sync & Refresh Button */}
        <div className="flex items-center gap-2">
          <div className="hidden lg:flex items-center gap-1.5 text-slate-400 text-xs font-mono">
            <Activity size={13} className="text-cyan-400" />
            <span>Sync:</span>
            <span className="text-slate-200">
              {formatRelativeTime(lastSyncTime)}
            </span>
          </div>

          <button
            onClick={() => refetch()}
            disabled={isLoading}
            className="p-2 rounded-xl border border-slate-800 bg-[#0B111A] hover:bg-slate-800/80 text-slate-300 hover:text-white transition-all disabled:opacity-50"
            title="Refresh System Status"
            aria-label="Refresh status"
          >
            <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>
    </header>
  );
};
