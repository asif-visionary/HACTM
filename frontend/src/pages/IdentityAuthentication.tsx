import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { KeyRound, ShieldAlert, AlertTriangle, CheckCircle2, Lock } from 'lucide-react';

export const IdentityAuthentication: React.FC = () => {
  const [page, setPage] = useState(1);

  const { data: metricsData } = useQuery({
    queryKey: ['identityMetrics'],
    queryFn: () => api.getIdentityMetrics(),
  });

  const { data: eventsData } = useQuery({
    queryKey: ['identityEvents', page],
    queryFn: () => api.getIdentityEvents(page, 20),
  });

  const { data: detectionsData } = useQuery({
    queryKey: ['identityDetections', page],
    queryFn: () => api.getIdentityDetections(page, 20),
  });

  const health = metricsData?.agent_health || {};
  const evalMetrics = metricsData?.evaluation || {};

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex items-center justify-between bg-hactm-surface border border-hactm-border rounded-lg p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-red-500/10 text-red-400 rounded-lg border border-red-500/20">
            <KeyRound size={28} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-hactm-heading">Identity & Authentication Agent</h1>
            <p className="text-xs text-hactm-muted mt-0.5">
              Account Takeover, Credential Abuse & 2FA Anomaly Engine (Agent ID: <code className="text-hactm-accent">identity-authentication-agent</code>)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 text-xs font-mono rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
            <CheckCircle2 size={14} /> {health.status || 'OPERATIONAL'}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Auth Events</div>
          <div className="text-2xl font-bold text-hactm-heading mt-1">{health.events_processed || 0}</div>
          <div className="text-[11px] text-hactm-muted mt-1">Rate: {health.processing_rate_events_per_sec || 0} evts/sec</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Identity Detections</div>
          <div className="text-2xl font-bold text-red-400 mt-1">{health.detections_generated || 0}</div>
          <div className="text-[11px] text-hactm-muted mt-1">Brute-Force & ATO Indicators</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">F1 Classification Score</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">{evalMetrics.f1_score || 0}</div>
          <div className="text-[11px] text-hactm-muted mt-1">Precision: {evalMetrics.precision || 0}</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Privacy Invariant</div>
          <div className="text-sm font-bold text-emerald-400 mt-1 flex items-center gap-1">
            <Lock size={14} /> ZERO SECRETS STORED
          </div>
          <div className="text-[11px] text-hactm-muted mt-1">No Passwords or OTP Tokens Saved</div>
        </div>
      </div>

      {/* Detections Stream */}
      <div className="bg-hactm-surface border border-hactm-border rounded-lg p-5">
        <h2 className="text-sm font-semibold text-hactm-heading uppercase tracking-wider mb-4">
          Identity Security Detections
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-hactm-panel border-b border-hactm-border text-hactm-muted font-mono uppercase">
              <tr>
                <th className="p-3">Event ID</th>
                <th className="p-3">User / Account</th>
                <th className="p-3">Category</th>
                <th className="p-3">Cyber Risk</th>
                <th className="p-3">Explanation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-hactm-border/60 text-hactm-text">
              {(detectionsData?.items || []).map((det: any) => (
                <tr key={det.detection_id} className="hover:bg-hactm-panel/50 transition-colors">
                  <td className="p-3 font-mono text-hactm-accent">{det.event_id}</td>
                  <td className="p-3 font-mono">{det.user_id}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-red-500/10 text-red-400 border border-red-500/20">
                      {det.category}
                    </span>
                  </td>
                  <td className="p-3 font-mono font-bold text-red-400">{det.risk_score.toFixed(2)}</td>
                  <td className="p-3 text-hactm-muted">{det.explanation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
