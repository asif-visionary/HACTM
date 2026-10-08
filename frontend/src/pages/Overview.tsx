import React, { useState } from 'react';
import { Layers, Users, AlertTriangle, ShieldCheck, Database, Network, Mail, UserCheck, Shield, CreditCard, ArrowRight, Activity, Radio, Cpu, Sparkles, Laptop } from 'lucide-react';
import { useMetricsOverview, useEvidenceTimeline } from '../hooks/useEvidence';
import { KpiCard } from '../components/dashboard/KpiCard';
import { RiskDistribution } from '../components/dashboard/RiskDistribution';
import { EvidenceTimeline } from '../components/dashboard/EvidenceTimeline';
import { RecentEvidenceTable } from '../components/dashboard/RecentEvidenceTable';
import { PriorityQueue } from '../components/dashboard/PriorityQueue';
import { EvidenceDetailModal } from '../components/evidence/EvidenceDetailModal';
import { SecurityEvidence } from '../types/evidence';
import { ErrorState } from '../components/common/ErrorState';
import { NavigationTab } from '../components/layout/Sidebar';

interface OverviewProps {
  onNavigateToEvidence: () => void;
  onNavigateToSettings: () => void;
  onNavigateToDomain?: (domain: NavigationTab) => void;
}

export const Overview: React.FC<OverviewProps> = ({
  onNavigateToEvidence,
  onNavigateToSettings,
  onNavigateToDomain,
}) => {
  const { data: metricsData, isLoading: metricsLoading, isError: metricsError, refetch: refetchMetrics } = useMetricsOverview();
  const { data: timelineData, isLoading: timelineLoading, isError: timelineError, refetch: refetchTimeline } = useEvidenceTimeline(10);

  const [selectedEvent, setSelectedEvent] = useState<SecurityEvidence | null>(null);

  const metrics = metricsData?.data;
  const timeline = timelineData?.data || [];

  if (metricsError || timelineError) {
    return (
      <ErrorState
        title="Command Center Offline"
        message="Unable to communicate with the HACTM core services. Please verify that the backend FastAPI server is running."
        onRetry={() => {
          refetchMetrics();
          refetchTimeline();
        }}
      />
    );
  }

  const isEmpty = metrics && metrics.total_events === 0;

  // Domain-level evidence agents
  const domainAgents: Array<{
    id: NavigationTab;
    name: string;
    icon: any;
    color: string;
    agentId: string;
    description: string;
  }> = [
    {
      id: 'network',
      name: 'Network Security',
      icon: Network,
      color: 'text-cyan-400 border-cyan-500/30 bg-cyan-950/30',
      agentId: 'network-security-agent',
      description: 'Network flow anomalies & intrusion telemetry',
    },
    {
      id: 'phishing',
      name: 'Phishing Intelligence',
      icon: Mail,
      color: 'text-emerald-400 border-emerald-500/30 bg-emerald-950/30',
      agentId: 'phishing-intelligence-agent',
      description: 'Email headers, URLs, BEC & NLP indicators',
    },
    {
      id: 'device',
      name: 'Device & Endpoint',
      icon: Laptop,
      color: 'text-teal-400 border-teal-500/30 bg-teal-950/30',
      agentId: 'device-security-agent',
      description: 'Endpoint posture, MAC fingerprinting & process execution',
    },
    {
      id: 'uba',
      name: 'User Behavior (UBA)',
      icon: UserCheck,
      color: 'text-indigo-400 border-indigo-500/30 bg-indigo-950/30',
      agentId: 'uba-agent',
      description: 'Temporal, resource & data exfiltration anomalies',
    },
    {
      id: 'identity',
      name: 'Identity & Auth',
      icon: Shield,
      color: 'text-amber-400 border-amber-500/30 bg-amber-950/30',
      agentId: 'identity-authentication-agent',
      description: 'Brute-force, 2FA, ATO & impossible travel',
    },
    {
      id: 'transaction',
      name: 'Transaction Security',
      icon: CreditCard,
      color: 'text-rose-400 border-rose-500/30 bg-rose-950/30',
      agentId: 'transaction-security-agent',
      description: 'Payment velocity & amount anomaly detection',
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-200 text-slate-100">
      {/* Page Header & Operational Status Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/30">
              <Activity className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                <span>Cyber Trust Command Center</span>
                <span className="text-xs font-mono font-semibold px-2.5 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 uppercase">
                  Live Operations
                </span>
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                Hierarchical Adaptive Cyber Trust Mesh — Multi-Domain Security Telemetry
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigateToDomain && onNavigateToDomain('3d-mesh')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-extrabold text-sm transition-all shadow-lg shadow-cyan-500/20"
          >
            <Sparkles size={16} />
            <span>Launch 3D AI Orchestrator SOC</span>
          </button>

          {isEmpty && (
            <button
              onClick={onNavigateToSettings}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-all border border-slate-700"
            >
              <Database size={16} />
              <span>Load Sample Dataset</span>
            </button>
          )}
        </div>
      </div>

      {/* Primary KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiCard
          title="Total Security Evidence"
          value={metrics?.total_events.toLocaleString()}
          subtitle="Normalized telemetry records"
          icon={Layers}
          variant="default"
          isLoading={metricsLoading}
        />

        <KpiCard
          title="Monitored Entities"
          value={metrics?.total_entities.toLocaleString()}
          subtitle="Tracked users, devices & IPs"
          icon={Users}
          variant="accent"
          isLoading={metricsLoading}
        />

        <KpiCard
          title="High Risk Threat Events"
          value={metrics?.high_risk_events.toLocaleString()}
          subtitle="Risk Score ≥ 0.70 threshold"
          icon={AlertTriangle}
          variant="danger"
          isLoading={metricsLoading}
        />

        <KpiCard
          title="Ingestion Health Score"
          value={metrics ? `${metrics.ingestion_health_pct.toFixed(0)}%` : undefined}
          subtitle="Data model validation rate"
          icon={ShieldCheck}
          variant="warning"
          isLoading={metricsLoading}
        />
      </div>

      {/* Main Grid: Left Timeline/Agents, Right Priority Queue/Risk */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns */}
        <div className="lg:col-span-2 space-y-6">
          {/* Security Activity Timeline */}
          <div className="bg-[#101923] border border-slate-800/80 rounded-2xl p-6 shadow-xl">
            <h3 className="text-base font-bold text-white mb-4 flex items-center justify-between">
              <span>Security Activity & Risk Timeline</span>
              <span className="text-xs font-mono text-slate-400 font-normal">Recent Telemetry Ingestion</span>
            </h3>
            <EvidenceTimeline
              timeline={timeline}
              isLoading={timelineLoading}
              onSelectEvent={setSelectedEvent}
            />
          </div>


          {/* Domain Specialized Agents Panel */}
          <div className="bg-[#101923] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">Specialized Security Agents</h3>
                <p className="text-xs text-slate-400">Independent multi-domain telemetry & anomaly evaluation</p>
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-[#0B111A] text-cyan-400 border border-slate-800 font-semibold">
                6 / 6 Operational
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {domainAgents.map((agent) => {
                const Icon = agent.icon;
                return (
                  <div
                    key={agent.id}
                    onClick={() => onNavigateToDomain && onNavigateToDomain(agent.id)}
                    className="p-4 bg-[#0B111A] hover:bg-[#131E2A] border border-slate-800/80 hover:border-slate-700 rounded-xl transition-all cursor-pointer group flex flex-col justify-between"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`p-2.5 rounded-xl border ${agent.color}`}>
                          <Icon size={18} />
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-slate-200 group-hover:text-cyan-400 transition-colors">
                            {agent.name}
                          </h4>
                          <span className="text-[10px] font-mono text-slate-400">● Operational</span>
                        </div>
                      </div>
                      <ArrowRight size={16} className="text-slate-500 group-hover:text-cyan-400 transition-colors" />
                    </div>
                    <p className="text-xs text-slate-400 mt-3">{agent.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right 1 Column */}
        <div className="space-y-6">
          {/* Priority Queue */}
          <PriorityQueue
            evidenceList={timeline}
            onSelectEvidence={setSelectedEvent}
          />

          {/* Cyber Risk Distribution */}
          <div className="bg-[#101923] border border-slate-800/80 rounded-2xl p-6 shadow-xl">
            <h3 className="text-base font-bold text-white mb-4">Risk Severity Distribution</h3>
            <RiskDistribution
              distribution={metrics?.risk_distribution}
              isLoading={metricsLoading}
            />
          </div>
        </div>
      </div>

      {/* Bottom Section: Recent Evidence Table */}
      <div className="bg-[#101923] border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Recent Security Evidence Telemetry</h3>
            <p className="text-xs text-slate-400">Real-time normalized security evidence ingested across mesh domains</p>
          </div>
          <button
            onClick={onNavigateToEvidence}
            className="flex items-center gap-1.5 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            <span>View All Evidence</span>
            <ArrowRight size={14} />
          </button>
        </div>

        <RecentEvidenceTable
          events={timeline}
          isLoading={timelineLoading}
          onSelectEvent={setSelectedEvent}
        />
      </div>

      {/* Detail Modal */}
      {selectedEvent && (
        <EvidenceDetailModal
          evidence={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </div>
  );
};
