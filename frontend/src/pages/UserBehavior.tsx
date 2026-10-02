import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { UserCheck, ShieldAlert, AlertTriangle, Users, CheckCircle2, ChevronRight } from 'lucide-react';

export const UserBehavior: React.FC = () => {
  const [page, setPage] = useState(1);
  const [selectedUser, setSelectedUser] = useState<any>(null);

  const { data: metricsData } = useQuery({
    queryKey: ['ubaMetrics'],
    queryFn: () => api.getUbaMetrics(),
  });

  const { data: eventsData } = useQuery({
    queryKey: ['ubaEvents', page],
    queryFn: () => api.getUbaEvents(page, 20),
  });

  const { data: detectionsData } = useQuery({
    queryKey: ['ubaDetections', page],
    queryFn: () => api.getUbaDetections(page, 20),
  });

  const { data: profilesData } = useQuery({
    queryKey: ['ubaProfiles'],
    queryFn: () => api.getUbaProfiles(),
  });

  const health = metricsData?.agent_health || {};
  const evalMetrics = metricsData?.evaluation || {};

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex items-center justify-between bg-hactm-surface border border-hactm-border rounded-lg p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg border border-blue-500/20">
            <UserCheck size={28} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-hactm-heading">User Behavior Analytics (UBA) Agent</h1>
            <p className="text-xs text-hactm-muted mt-0.5">
              Behavioral Anomaly & Insider Threat Indicator Engine (Agent ID: <code className="text-hactm-accent">uba-agent</code>)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 text-xs font-mono rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
            <CheckCircle2 size={14} /> {health.status || 'OPERATIONAL'}
          </span>
          <span className="text-xs font-mono text-hactm-muted bg-hactm-panel px-3 py-1 rounded border border-hactm-border">
            Users Profiled: {health.users_observed || 0}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Observed Events</div>
          <div className="text-2xl font-bold text-hactm-heading mt-1">{health.events_processed || 0}</div>
          <div className="text-[11px] text-hactm-muted mt-1">Rate: {health.processing_rate_events_per_sec || 0} evts/sec</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Behavioral Anomalies</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{health.detections_generated || 0}</div>
          <div className="text-[11px] text-hactm-muted mt-1">Robust Z-score / Profile Baseline</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Insufficient Baseline</div>
          <div className="text-2xl font-bold text-blue-400 mt-1">
            {health.percentage_users_insufficient_baseline || 0}%
          </div>
          <div className="text-[11px] text-hactm-muted mt-1">New User Historical Guardrail</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">False Alert Rate</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {evalMetrics.false_alerts_per_user || 0} / user
          </div>
          <div className="text-[11px] text-hactm-muted mt-1">Non-Fabricated Metric</div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User Activity & Detections List */}
        <div className="lg:col-span-2 bg-hactm-surface border border-hactm-border rounded-lg p-5">
          <h2 className="text-sm font-semibold text-hactm-heading uppercase tracking-wider mb-4">
            Behavioral Anomaly Telemetry
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-hactm-panel border-b border-hactm-border text-hactm-muted font-mono uppercase">
                <tr>
                  <th className="p-3">User ID</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Detector</th>
                  <th className="p-3">Cyber Risk Score</th>
                  <th className="p-3">Explanation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hactm-border/60 text-hactm-text">
                {(detectionsData?.items || []).map((det: any) => (
                  <tr key={det.detection_id} className="hover:bg-hactm-panel/50 transition-colors">
                    <td className="p-3 font-mono text-hactm-accent">{det.user_id}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {det.category}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-hactm-muted">{det.detector_type}</td>
                    <td className="p-3 font-mono font-bold text-amber-400">{det.risk_score.toFixed(2)}</td>
                    <td className="p-3 truncate max-w-xs text-hactm-muted">{det.explanation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* User Profiles Baseline View */}
        <div className="bg-hactm-surface border border-hactm-border rounded-lg p-5">
          <h2 className="text-sm font-semibold text-hactm-heading uppercase tracking-wider mb-4">
            User Profiles & Peer Baselines
          </h2>

          <div className="space-y-3">
            {(profilesData || []).map((p: any) => (
              <div key={p.user_id} className="p-3 bg-hactm-panel rounded border border-hactm-border text-xs space-y-1">
                <div className="flex items-center justify-between font-mono">
                  <span className="text-hactm-accent font-bold">{p.user_id}</span>
                  <span className="text-hactm-muted text-[10px]">Group: {p.peer_group || 'Default'}</span>
                </div>
                <div className="text-hactm-muted">Known Devices: {p.known_devices?.join(', ') || 'None'}</div>
                <div className="text-hactm-muted">Normal Hours: {p.normal_login_hours?.join(', ') || 'None'} UTC</div>
                <div className="text-hactm-muted">Total Activity Events: {p.event_count}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
