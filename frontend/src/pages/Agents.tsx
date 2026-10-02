import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Network, Mail, UserCheck, Shield, CreditCard, Info, Activity, Clock, CheckCircle2, AlertTriangle, Layers, ChevronRight, X } from 'lucide-react';
import { api } from '../services/api';
import { NavigationTab } from '../components/layout/Sidebar';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

interface AgentsProps {
  onNavigateToDomain?: (domain: NavigationTab) => void;
}

export const Agents: React.FC<AgentsProps> = ({ onNavigateToDomain }) => {
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  const { data: agentsData, isLoading, refetch } = useQuery({
    queryKey: ['agents-all'],
    queryFn: () => api.getAllAgents(),
    refetchInterval: 10000,
  });

  const { data: agentDetail } = useQuery({
    queryKey: ['agent-detail', selectedAgentId],
    queryFn: () => (selectedAgentId ? api.getAgentDetail(selectedAgentId) : null),
    enabled: !!selectedAgentId,
  });

  const agentsList = Array.isArray(agentsData) ? agentsData : ((agentsData as any)?.data || []);

  const agentMeta: Record<string, {
    tab: NavigationTab;
    icon: any;
    color: string;
    detectionMethod: string;
    limitations: string;
  }> = {
    'network-security-agent': {
      tab: 'network',
      icon: Network,
      color: 'text-blue-400 border-blue-500/30 bg-blue-500/10',
      detectionMethod: 'Flow statistical anomaly analysis (Isolation Forest), protocol signature rules, port scanning heuristic.',
      limitations: 'Evaluates headers and flow metadata; does not inspect encrypted TLS payload content directly.',
    },
    'phishing-intelligence-agent': {
      tab: 'phishing',
      icon: Mail,
      color: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
      detectionMethod: 'Header authentication rules (SPF/DKIM/DMARC mismatch), lexical URL analysis, attachment double-extension metadata check, TF-IDF + Logistic Regression NLP classifier.',
      limitations: 'Offline metadata and static text evaluation only. Does not click URLs, resolve external DNS, or execute attachment binaries.',
    },
    'uba-agent': {
      tab: 'uba',
      icon: UserCheck,
      color: 'text-purple-400 border-purple-500/30 bg-purple-500/10',
      detectionMethod: 'Profile baseline deviation (z-score/MAD), temporal off-hours activity, rare resource/app access heuristics, potential data movement indicators.',
      limitations: 'Requires minimum historical event threshold per user; new users yield INSUFFICIENT_BASELINE status to avoid false alerts.',
    },
    'identity-authentication-agent': {
      tab: 'identity',
      icon: Shield,
      color: 'text-amber-400 border-amber-500/30 bg-amber-500/10',
      detectionMethod: 'Brute-force login velocity checks, 2FA failure/bypass anomaly analysis, novel IP/device heuristic, Haversine impossible-travel velocity calculation.',
      limitations: 'Impossible-travel calculation requires explicit geocoordinate pairs. Does not perform IP geolocation or store raw auth secrets.',
    },
    'transaction-security-agent': {
      tab: 'transaction',
      icon: CreditCard,
      color: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
      detectionMethod: 'Transaction velocity windowing, historical amount robust z-score, new recipient / novel merchant correlation.',
      limitations: 'Evidence generation only. Does not execute payments, modify bank balances, or freeze consumer accounts.',
    } as any,
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      <div>
        <h1 className="text-xl font-bold text-hactm-heading tracking-tight flex items-center gap-2">
          <span>Heterogeneous Security Agents</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-hactm-accent/10 text-hactm-accent border border-hactm-accent/30 font-normal">
            Specialized Security Agents Active Multi-Agent Topology
          </span>
        </h1>
        <p className="text-xs text-hactm-muted mt-1">
          Autonomous multi-domain security evidence generators running independent detection pipelines.
        </p>
      </div>

      {/* Notice Callout */}
      <div className="p-4 rounded-lg bg-hactm-panel/80 border border-hactm-border flex items-start gap-3 text-xs leading-relaxed text-hactm-muted">
        <Info size={16} className="text-hactm-accent shrink-0 mt-0.5" />
        <div>
          <strong className="text-hactm-text font-semibold block mb-0.5">
            Specialized Security Agents Cross-Agent Isolation Architecture
          </strong>
          Each agent operates independently to validate input, extract features, execute domain detectors, calculate Cyber Risk & Confidence scores, and emit canonical <code className="text-hactm-accent">SecurityEvidence</code>. Cross-agent evidence fusion is intentionally strictly reserved for Evidence Fusion.
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner message="Fetching security agent health telemetry..." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agentsList.map((agent: any) => {
            const meta = agentMeta[agent.agent_id] || {
              tab: 'overview',
              icon: Activity,
              color: 'text-gray-400 border-gray-500/30 bg-gray-500/10',
              detectionMethod: 'Standard domain detector pipeline.',
              limitations: 'Standard operational boundaries.',
            };
            const Icon = meta.icon;

            return (
              <div
                key={agent.agent_id}
                className="p-5 rounded-lg bg-hactm-card border border-hactm-border hover:border-hactm-accent/40 transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className={`p-2 rounded-md border ${meta.color}`}>
                        <Icon size={18} />
                      </span>
                      <div>
                        <h3 className="text-xs font-semibold text-hactm-text">
                          {agent.agent_name}
                        </h3>
                        <p className="text-[10px] font-mono text-hactm-muted">
                          v{agent.version} • {agent.agent_id}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                        agent.status === 'active' || agent.status === 'healthy'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {agent.status.toUpperCase()}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 p-2.5 rounded bg-hactm-panel/60 border border-hactm-border text-[11px]">
                    <div>
                      <span className="text-hactm-muted block text-[10px]">Events Processed</span>
                      <span className="font-mono font-semibold text-hactm-text">
                        {agent.events_processed?.toLocaleString() || 0}
                      </span>
                    </div>
                    <div>
                      <span className="text-hactm-muted block text-[10px]">Detections</span>
                      <span className="font-mono font-semibold text-hactm-accent">
                        {agent.detections_generated?.toLocaleString() || 0}
                      </span>
                    </div>
                    <div>
                      <span className="text-hactm-muted block text-[10px]">Avg Latency</span>
                      <span className="font-mono text-hactm-text">
                        {agent.average_latency_ms?.toFixed(2) || '0.00'} ms
                      </span>
                    </div>
                    <div>
                      <span className="text-hactm-muted block text-[10px]">Active Model</span>
                      <span className="font-mono text-hactm-muted truncate block">
                        {agent.model_version || 'v1.0.0'}
                      </span>
                    </div>
                  </div>

                  <div className="space-y-1 text-[11px]">
                    <span className="text-hactm-text font-semibold block text-[10px]">Detection Method:</span>
                    <p className="text-hactm-muted leading-tight text-[11px]">
                      {meta.detectionMethod}
                    </p>
                  </div>

                  <div className="space-y-1 text-[11px]">
                    <span className="text-amber-400/90 font-semibold block text-[10px]">Current Limitations:</span>
                    <p className="text-hactm-muted leading-tight text-[11px]">
                      {meta.limitations}
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-hactm-border flex items-center justify-between">
                  <button
                    onClick={() => setSelectedAgentId(agent.agent_id)}
                    className="text-[11px] text-hactm-accent hover:underline flex items-center gap-1 font-semibold"
                  >
                    View Details <ChevronRight size={12} />
                  </button>
                  {onNavigateToDomain && (
                    <button
                      onClick={() => onNavigateToDomain(meta.tab)}
                      className="px-2.5 py-1 rounded bg-hactm-panel text-hactm-text hover:bg-hactm-border text-[11px] font-medium border border-hactm-border transition-colors"
                    >
                      Open Telemetry
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Agent Detail Inspector Modal */}
      {selectedAgentId && agentDetail && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-hactm-card border border-hactm-border rounded-xl max-w-xl w-full p-6 space-y-4 shadow-2xl animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-hactm-border">
              <div>
                <h2 className="text-base font-bold text-hactm-heading">
                  {agentDetail.data?.agent_name || selectedAgentId}
                </h2>
                <p className="text-xs font-mono text-hactm-muted">
                  ID: {selectedAgentId}
                </p>
              </div>
              <button
                onClick={() => setSelectedAgentId(null)}
                className="p-1 rounded text-hactm-muted hover:text-hactm-text hover:bg-hactm-panel"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded bg-hactm-panel border border-hactm-border space-y-1">
                  <span className="text-hactm-muted text-[10px]">Status</span>
                  <p className="font-mono text-emerald-400 font-semibold">
                    {agentDetail.data?.status || 'HEALTHY'}
                  </p>
                </div>
                <div className="p-3 rounded bg-hactm-panel border border-hactm-border space-y-1">
                  <span className="text-hactm-muted text-[10px]">Model Version</span>
                  <p className="font-mono text-hactm-text font-semibold">
                    {agentDetail.data?.model_version || 'v1.0.0'}
                  </p>
                </div>
              </div>

              <div className="p-3 rounded bg-hactm-panel border border-hactm-border space-y-2">
                <span className="text-hactm-muted text-[10px] font-semibold block">Detector Modules Loaded</span>
                <div className="flex flex-wrap gap-1.5 font-mono text-[11px]">
                  {agentDetail.data?.detector_types?.map((dt: string) => (
                    <span key={dt} className="px-2 py-0.5 rounded bg-hactm-card border border-hactm-border text-hactm-accent">
                      {dt}
                    </span>
                  )) || <span className="text-hactm-muted">Standard modules</span>}
                </div>
              </div>

              <div className="p-3 rounded bg-hactm-panel border border-hactm-border space-y-1 font-mono text-[11px]">
                <span className="text-hactm-muted text-[10px] block">Performance Metrics</span>
                <p>Total Events Processed: {agentDetail.data?.events_processed}</p>
                <p>Detections Generated: {agentDetail.data?.detections_generated}</p>
                <p>Processing Errors: {agentDetail.data?.errors}</p>
                <p>Average Latency: {agentDetail.data?.average_latency_ms?.toFixed(2)} ms</p>
              </div>
            </div>

            <div className="pt-3 border-t border-hactm-border flex justify-end">
              <button
                onClick={() => setSelectedAgentId(null)}
                className="px-4 py-1.5 rounded bg-hactm-panel border border-hactm-border text-xs font-semibold text-hactm-text hover:bg-hactm-border transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

