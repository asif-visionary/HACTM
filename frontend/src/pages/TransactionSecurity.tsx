import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { CreditCard, ShieldAlert, AlertTriangle, CheckCircle2, ShieldCheck } from 'lucide-react';

export const TransactionSecurity: React.FC = () => {
  const [page, setPage] = useState(1);

  const { data: metricsData } = useQuery({
    queryKey: ['transactionMetrics'],
    queryFn: () => api.getTransactionMetrics(),
  });

  const { data: eventsData } = useQuery({
    queryKey: ['transactionEvents', page],
    queryFn: () => api.getTransactionEvents(page, 20),
  });

  const { data: detectionsData } = useQuery({
    queryKey: ['transactionDetections', page],
    queryFn: () => api.getTransactionDetections(page, 20),
  });

  const health = metricsData?.agent_health || {};
  const evalMetrics = metricsData?.evaluation || {};

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex items-center justify-between bg-hactm-surface border border-hactm-border rounded-lg p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg border border-emerald-500/20">
            <CreditCard size={28} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-hactm-heading">Transaction Security Agent</h1>
            <p className="text-xs text-hactm-muted mt-0.5">
              Financial Transaction Anomaly & Fraud Indicator Engine (Agent ID: <code className="text-hactm-accent">transaction-security-agent</code>)
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
          <div className="text-xs font-mono text-hactm-muted uppercase">Transactions Processed</div>
          <div className="text-2xl font-bold text-hactm-heading mt-1">{health.events_processed || 0}</div>
          <div className="text-[11px] text-hactm-muted mt-1">Rate: {health.processing_rate_events_per_sec || 0} evts/sec</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Anomalous Transactions</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{health.detections_generated || 0}</div>
          <div className="text-[11px] text-hactm-muted mt-1">Velocity & Amount Deviations</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">False Alerts</div>
          <div className="text-2xl font-bold text-blue-400 mt-1">
            {evalMetrics.false_alerts_per_1000_transactions || 0} / 1K
          </div>
          <div className="text-[11px] text-hactm-muted mt-1">Per 1,000 Transactions</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Safety Invariant</div>
          <div className="text-sm font-bold text-emerald-400 mt-1 flex items-center gap-1">
            <ShieldCheck size={14} /> DETECTION ONLY
          </div>
          <div className="text-[11px] text-hactm-muted mt-1">NO Execution / Fund Transfers</div>
        </div>
      </div>

      {/* Detections Table */}
      <div className="bg-hactm-surface border border-hactm-border rounded-lg p-5">
        <h2 className="text-sm font-semibold text-hactm-heading uppercase tracking-wider mb-4">
          Financial Anomaly Detections Stream
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-hactm-panel border-b border-hactm-border text-hactm-muted font-mono uppercase">
              <tr>
                <th className="p-3">Transaction ID</th>
                <th className="p-3">Account ID</th>
                <th className="p-3">Category</th>
                <th className="p-3">Cyber Risk</th>
                <th className="p-3">Explanation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-hactm-border/60 text-hactm-text">
              {(detectionsData?.items || []).map((det: any) => (
                <tr key={det.detection_id} className="hover:bg-hactm-panel/50 transition-colors">
                  <td className="p-3 font-mono text-hactm-accent">{det.event_id}</td>
                  <td className="p-3 font-mono">{det.account_id}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {det.category}
                    </span>
                  </td>
                  <td className="p-3 font-mono font-bold text-amber-400">{det.risk_score.toFixed(2)}</td>
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
