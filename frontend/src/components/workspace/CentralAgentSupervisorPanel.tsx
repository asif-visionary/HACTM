/**
 * Central Agent Supervisor (CAS) Panel for HACTM Cyber Operations Workspace.
 * Provides unified multi-agent fleet overview, live agent monitoring, supervisory intelligence alerts,
 * governance decisions, defensive controls (restrict, isolate, recover), and watchdog vitals.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  FleetOverview,
  SupervisedAgent,
  AnomalyAlert,
  SupervisorDecision,
  SupervisorIntelligence,
} from '../../types/supervisor';
import { api } from '../../services/api';
import {
  RefreshCw,
  CheckCircle,
  Clock,
  Play,
  Info,
} from 'lucide-react';
import { SuperIcon } from '../common/SuperIcon';

interface CentralAgentSupervisorPanelProps {
  onSelectAgent: (agentId: string) => void;
  onRefreshWorkspace: () => void;
}

export const CentralAgentSupervisorPanel: React.FC<CentralAgentSupervisorPanelProps> = ({
  onSelectAgent,
  onRefreshWorkspace,
}) => {
  const [fleet, setFleet] = useState<FleetOverview | null>(null);
  const [agents, setAgents] = useState<SupervisedAgent[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyAlert[]>([]);
  const [decisions, setDecisions] = useState<SupervisorDecision[]>([]);
  const [intelligence, setIntelligence] = useState<SupervisorIntelligence | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'fleet' | 'alerts' | 'decisions' | 'defense'>('fleet');
  const [selectedAgentForControl, setSelectedAgentForControl] = useState<string>('network-security-agent');
  const [selectedScenario, setSelectedScenario] = useState<string>('UNAUTHORISED_TOOL_REQUEST');
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);

  // Load all supervisor state from authoritative backend
  const refreshSupervisorData = useCallback(async () => {
    try {
      const [fleetData, agentsData, anomData, decData, intelData] = await Promise.all([
        api.getSupervisorStatus(),
        api.getSupervisedAgents(),
        api.getSupervisorAnomalies(undefined, true),
        api.getSupervisorDecisions(30),
        api.getSupervisorIntelligence(),
      ]);

      setFleet(fleetData);
      setAgents(agentsData);
      setAnomalies(anomData);
      setDecisions(decData);
      setIntelligence(intelData);
    } catch (err) {
      console.warn('Could not refresh CAS supervisor data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshSupervisorData();
    const timer = setInterval(refreshSupervisorData, 6000);
    return () => clearInterval(timer);
  }, [refreshSupervisorData]);

  // Execute Anomaly Simulation
  const handleSimulateAnomaly = async () => {
    setSimulating(true);
    setActionSuccessMessage(null);
    try {
      const res = await api.simulateSupervisorAnomaly({
        agent_id: selectedAgentForControl,
        scenario: selectedScenario,
      });
      setActionSuccessMessage(`Simulated ${res.scenario} on ${res.agent_id}. Alert ID: ${res.anomaly_id}`);
      await refreshSupervisorData();
      onRefreshWorkspace();
    } catch (err: any) {
      alert(`Simulation failed: ${err.message || err}`);
    } finally {
      setSimulating(false);
    }
  };

  // Execute Direct Isolation
  const handleIsolateAgent = async (agentId: string) => {
    if (!confirm(`Are you sure you want to ISOLATE agent '${agentId}'? Tool permissions will be revoked.`)) return;
    try {
      await api.isolateAgent(agentId, {
        reason: 'Operator-initiated supervisory isolation from CAS command console.',
        operator_identity: 'SECURITY_ADMIN',
      });
      setActionSuccessMessage(`Agent '${agentId}' has been quarantined in ISOLATED state.`);
      await refreshSupervisorData();
      onRefreshWorkspace();
    } catch (err: any) {
      alert(`Failed to isolate agent: ${err.message || err}`);
    }
  };

  // Execute Reinstatement
  const handleReinstateAgent = async (agentId: string) => {
    try {
      await api.reinstateAgent(agentId, 'SECURITY_ADMIN');
      setActionSuccessMessage(`Agent '${agentId}' has been formally reinstated.`);
      await refreshSupervisorData();
      onRefreshWorkspace();
    } catch (err: any) {
      alert(`Failed to reinstate agent: ${err.message || err}`);
    }
  };

  const watchdogHealth = fleet?.supervisor_health || 'HEALTHY';
  const rawLatency = fleet?.event_ingestion_latency_ms ?? 0.45;
  const formattedLatency = typeof rawLatency === 'number' ? rawLatency.toFixed(2) : String(rawLatency);

  const metricCards = [
    {
      id: 'total-agents',
      label: 'Total Agents',
      value: fleet?.total_registered_agents ?? 5,
      icon: 'multi-agent',
      cardClass: 'bg-slate-900/75 border-cyan-500/25 hover:border-cyan-400/45',
      iconBgClass: 'bg-cyan-500/10 border border-cyan-500/20',
      valueClass: 'text-cyan-200',
    },
    {
      id: 'healthy',
      label: 'Healthy',
      value: fleet?.healthy_agents ?? 5,
      icon: 'evaluation',
      cardClass: 'bg-slate-900/75 border-emerald-500/25 hover:border-emerald-400/45',
      iconBgClass: 'bg-emerald-500/10 border border-emerald-500/20',
      valueClass: 'text-emerald-400',
    },
    {
      id: 'observation',
      label: 'Observation',
      value: fleet?.agents_under_observation ?? 0,
      icon: 'monitoring',
      cardClass: 'bg-slate-900/75 border-amber-500/25 hover:border-amber-400/45',
      iconBgClass: 'bg-amber-500/10 border border-amber-500/20',
      valueClass: 'text-amber-400',
    },
    {
      id: 'anomalies',
      label: 'Anomalies',
      value: fleet?.agents_with_anomalies ?? 0,
      icon: 'monitoring',
      cardClass: 'bg-slate-900/75 border-rose-500/25 hover:border-rose-400/45',
      iconBgClass: 'bg-rose-500/10 border border-rose-500/20',
      valueClass: 'text-rose-400',
    },
    {
      id: 'restricted',
      label: 'Restricted',
      value: fleet?.restricted_agents ?? 0,
      icon: 'permissions',
      cardClass: 'bg-slate-900/75 border-amber-500/25 hover:border-amber-400/45',
      iconBgClass: 'bg-amber-500/10 border border-amber-500/20',
      valueClass: 'text-amber-300',
    },
    {
      id: 'isolated',
      label: 'Isolated',
      value: fleet?.isolated_agents ?? 0,
      icon: 'sandbox',
      cardClass: 'bg-slate-900/75 border-red-500/30 hover:border-red-400/50',
      iconBgClass: 'bg-red-500/10 border border-red-500/25',
      valueClass: 'text-red-400',
    },
    {
      id: 'offline',
      label: 'Offline',
      value: fleet?.offline_agents ?? 0,
      icon: 'agent',
      cardClass: 'bg-slate-900/75 border-slate-700/80 hover:border-slate-600',
      iconBgClass: 'bg-slate-800/80 border border-slate-700/70',
      valueClass: 'text-slate-300',
    },
    {
      id: 'active-alerts',
      label: 'Active Alerts',
      value: fleet?.active_monitoring_alerts ?? 0,
      icon: 'monitoring',
      cardClass: 'bg-slate-900/75 border-cyan-500/30 hover:border-cyan-400/50',
      iconBgClass: 'bg-cyan-500/10 border border-cyan-500/25',
      valueClass: 'text-cyan-300',
    },
  ];

  const supervisorTabs = [
    {
      id: 'fleet' as const,
      label: 'Agent Fleet Monitoring',
      count: agents.length,
      icon: 'multi-agent',
      activeClass: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/45 shadow-sm',
      badgeClass: 'bg-cyan-500/20 text-cyan-200',
    },
    {
      id: 'alerts' as const,
      label: 'Anomaly & Security Alerts',
      count: anomalies.length,
      icon: 'evaluation',
      activeClass: 'bg-rose-500/15 text-rose-300 border-rose-500/45 shadow-sm',
      badgeClass: 'bg-rose-500/20 text-rose-200',
    },
    {
      id: 'decisions' as const,
      label: 'Supervisory Decisions',
      count: decisions.length,
      icon: 'feedback-loop',
      activeClass: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/45 shadow-sm',
      badgeClass: 'bg-emerald-500/20 text-emerald-200',
    },
    {
      id: 'defense' as const,
      label: 'Defensive Simulation & Controls',
      count: null as number | null,
      icon: 'permissions',
      activeClass: 'bg-amber-500/15 text-amber-300 border-amber-500/45 shadow-sm',
      badgeClass: 'bg-amber-500/20 text-amber-200',
    },
  ];

  return (
    <div className="cas-panel-container w-full bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-2xl backdrop-blur-md flex flex-col">
      {/* Supervisor Header */}
      <div className="px-5 py-4 bg-slate-950/85 border-b border-slate-800">
        <div className="flex items-start gap-3.5 min-w-0">
          <div className="w-10 h-10 flex-shrink-0 rounded-lg bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center shadow-sm shadow-cyan-950/50">
            <SuperIcon name="monitoring" style="color" size={22} alt="Central Agent Supervisor" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1">
              <h2 className="text-base sm:text-lg font-bold tracking-wide text-white leading-tight">
                CENTRAL AGENT SUPERVISOR
              </h2>
              <span className="inline-flex items-center px-2 py-0.5 text-[11px] font-semibold tracking-wider rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 flex-shrink-0 whitespace-nowrap">
                ACTIVE
              </span>
            </div>
            <p className="mt-1.5 text-xs text-slate-400 leading-relaxed break-words">
              Continuous Multi-Agent Telemetry, Behavioral Analysis, Trust Evaluation &amp; Autonomous Governance
            </p>
          </div>
        </div>
      </div>

      {/* Watchdog Status Row */}
      <div className="px-5 py-2.5 bg-slate-900/75 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 min-w-0">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-6 h-6 flex-shrink-0 rounded bg-slate-950 border border-slate-800 flex items-center justify-center">
              <SuperIcon name="monitoring" style="color" size={15} alt="Watchdog" />
            </div>
            <span className="text-slate-400 font-semibold tracking-wider text-[11px] uppercase whitespace-nowrap">
              WATCHDOG:
            </span>
            <span
              className={`inline-flex items-center gap-1.5 font-mono font-semibold text-xs whitespace-nowrap ${
                watchdogHealth === 'HEALTHY'
                  ? 'text-emerald-400'
                  : watchdogHealth === 'DEGRADED'
                  ? 'text-amber-400'
                  : 'text-rose-400'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  watchdogHealth === 'HEALTHY'
                    ? 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.65)]'
                    : watchdogHealth === 'DEGRADED'
                    ? 'bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.65)]'
                    : 'bg-rose-400 shadow-[0_0_6px_rgba(251,113,133,0.65)]'
                }`}
              />
              <span>{watchdogHealth}</span>
            </span>
          </div>

          <span className="text-slate-700 select-none" aria-hidden="true">|</span>

          <div className="flex items-center gap-1.5 whitespace-nowrap">
            <span className="text-slate-400 font-semibold tracking-wider text-[11px] uppercase">
              LATENCY:
            </span>
            <span className="text-cyan-300 font-mono font-semibold text-xs">
              {formattedLatency} ms
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={refreshSupervisorData}
          disabled={loading}
          className="ml-auto flex-shrink-0 inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-800/90 hover:bg-slate-700 text-slate-200 rounded-md border border-slate-700 text-[11px] font-medium transition disabled:opacity-60"
          title="Refresh Supervisory Telemetry"
        >
          <RefreshCw className={`w-3.5 h-3.5 flex-shrink-0 ${loading ? 'animate-spin text-cyan-400' : 'text-slate-300'}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* KPI Cards 4x2 Responsive Grid */}
      <div className="p-5 bg-slate-950/40 border-b border-slate-800/80">
        <div className="cas-metrics-grid">
          {metricCards.map((card) => (
            <div key={card.id} className={`metric-card ${card.cardClass}`}>
              <div className={`metric-icon-container ${card.iconBgClass}`}>
                <SuperIcon name={card.icon} style="color" size={18} alt={card.label} />
              </div>
              <div className="metric-label text-slate-300">{card.label}</div>
              <div className={`metric-value font-mono ${card.valueClass}`}>{card.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Supervisory Status Notification */}
      {intelligence && (
        <div
          className={`px-5 py-3.5 border-b flex items-start gap-3.5 ${
            intelligence.supervisory_posture === 'ELEVATED_SUPERVISORY_ALERT'
              ? 'bg-rose-950/25 border-rose-500/30'
              : intelligence.supervisory_posture === 'INCREASED_OBSERVATION'
              ? 'bg-amber-950/25 border-amber-500/30'
              : 'bg-gradient-to-r from-cyan-950/30 to-slate-900/40 border-cyan-900/30'
          }`}
        >
          <div
            className={`w-8 h-8 flex-shrink-0 rounded-lg border flex items-center justify-center ${
              intelligence.supervisory_posture === 'ELEVATED_SUPERVISORY_ALERT'
                ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                : intelligence.supervisory_posture === 'INCREASED_OBSERVATION'
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                : 'bg-cyan-500/10 border-cyan-500/25 text-cyan-400'
            }`}
          >
            <Info className="w-4 h-4 flex-shrink-0" />
          </div>

          <div className="flex-1 min-w-0 flex flex-col gap-1.5">
            <div className="flex items-center flex-wrap gap-2">
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-semibold uppercase tracking-wider border ${
                  intelligence.supervisory_posture === 'ELEVATED_SUPERVISORY_ALERT'
                    ? 'bg-rose-500/15 text-rose-300 border-rose-500/35'
                    : intelligence.supervisory_posture === 'INCREASED_OBSERVATION'
                    ? 'bg-amber-500/15 text-amber-300 border-amber-500/35'
                    : 'bg-cyan-500/15 text-cyan-300 border-cyan-500/35'
                }`}
              >
                {intelligence.supervisory_posture}
              </span>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed break-words">
              {intelligence.executive_narrative}
            </p>

            {intelligence.governance_recommendations.length > 0 && (
              <div className="pt-1.5 mt-0.5 border-t border-slate-800/70 text-xs leading-relaxed break-words">
                <span className="font-semibold text-cyan-400 mr-1.5">Recommendation:</span>
                <span className="text-slate-300">{intelligence.governance_recommendations[0]}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Action Success Toast */}
      {actionSuccessMessage && (
        <div className="px-5 py-2.5 bg-emerald-950/60 border-b border-emerald-500/40 flex items-center justify-between gap-3 text-xs text-emerald-300">
          <div className="flex items-center gap-2 min-w-0">
            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="break-words">{actionSuccessMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setActionSuccessMessage(null)}
            className="text-emerald-400 hover:text-white flex-shrink-0"
            aria-label="Dismiss notification"
          >
            ✕
          </button>
        </div>
      )}

      {/* Navigation Sub-Tabs */}
      <div
        role="tablist"
        aria-label="Central Agent Supervisor Views"
        className="px-5 py-3 bg-slate-950/50 border-b border-slate-800 flex flex-wrap items-center gap-2"
      >
        {supervisorTabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={isActive}
              onClick={() => setActiveTab(tab.id)}
              className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border text-xs font-semibold transition whitespace-nowrap max-w-full ${
                isActive
                  ? tab.activeClass
                  : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 hover:bg-slate-800/70'
              }`}
            >
              <span className="w-5 h-5 flex-shrink-0 flex items-center justify-center">
                <SuperIcon
                  name={tab.icon}
                  style={isActive ? 'color' : 'duotone'}
                  size={15}
                />
              </span>
              <span className="truncate">{tab.label}</span>
              {tab.count !== null && (
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold flex-shrink-0 ${
                    isActive ? tab.badgeClass : 'bg-slate-800 text-slate-300'
                  }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Tab Content */}
      <div className="p-5">
        {/* TAB 1: Agent Fleet Monitoring Table */}
        {activeTab === 'fleet' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 font-mono uppercase text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-3 whitespace-nowrap">Agent Name / ID</th>
                  <th className="py-3 px-3 whitespace-nowrap">Department</th>
                  <th className="py-3 px-3 whitespace-nowrap">Health Vitals</th>
                  <th className="py-3 px-3 whitespace-nowrap">Trust Status</th>
                  <th className="py-3 px-3 whitespace-nowrap">Current Task</th>
                  <th className="py-3 px-3 whitespace-nowrap">Last Heartbeat</th>
                  <th className="py-3 px-3 text-right whitespace-nowrap">Governed Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {agents.map((ag) => (
                  <tr key={ag.agent_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2.5">
                        <div className="w-6 h-6 flex-shrink-0 flex items-center justify-center">
                          <SuperIcon
                            name={ag.agent_id.includes('orchestrator') ? 'orchestration' : 'agent'}
                            style={ag.is_isolated ? 'color' : 'duotone'}
                            size={16}
                          />
                        </div>
                        <div className="min-w-0">
                          <div className="font-semibold text-white flex items-center gap-1.5 whitespace-nowrap">
                            <span>{ag.name}</span>
                            {ag.is_isolated && (
                              <span className="inline-flex items-center gap-1 text-[10px] text-red-400 bg-red-950/80 px-1.5 py-0.5 rounded border border-red-500/40 flex-shrink-0">
                                <SuperIcon name="sandbox" style="color" size={11} />
                                <span>ISOLATED</span>
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-slate-400 font-mono">{ag.agent_id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-slate-300 whitespace-nowrap">{ag.department}</td>
                    <td className="py-3 px-3 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                          ag.health === 'OPERATIONAL'
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30'
                            : ag.health === 'DEGRADED'
                            ? 'bg-amber-950 text-amber-300 border border-amber-500/30'
                            : 'bg-rose-950 text-rose-300 border border-rose-500/30'
                        }`}
                      >
                        {ag.health}
                      </span>
                    </td>
                    <td className="py-3 px-3 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold ${
                            ag.trust_status === 'TRUSTED'
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                              : ag.trust_status === 'NORMAL'
                              ? 'bg-cyan-950 text-cyan-300 border border-cyan-500/40'
                              : ag.trust_status === 'UNDER_OBSERVATION'
                              ? 'bg-amber-950 text-amber-300 border border-amber-500/40'
                              : ag.trust_status === 'ISOLATED'
                              ? 'bg-red-950 text-red-400 border border-red-500/50'
                              : 'bg-rose-950 text-rose-300 border border-rose-500/40'
                          }`}
                        >
                          {ag.trust_status}
                        </span>
                        <span className="font-mono text-slate-300 font-semibold">{ag.trust_score.toFixed(2)}</span>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-slate-300 max-w-[200px]">
                      {ag.current_task ? (
                        <div className="flex items-center gap-1.5 min-w-0">
                          <SuperIcon name="task" style="stroke" size={13} className="text-slate-400 flex-shrink-0" />
                          <span className="truncate">{ag.current_task}</span>
                        </div>
                      ) : (
                        <span className="text-slate-500 italic">Idle</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-slate-400 font-mono text-[11px] whitespace-nowrap">
                      {new Date(ag.last_heartbeat).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-3 text-right whitespace-nowrap">
                      <div className="inline-flex items-center justify-end gap-2">
                        <button
                          type="button"
                          onClick={() => onSelectAgent(ag.agent_id)}
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-300 rounded text-xs transition"
                        >
                          Passport
                        </button>
                        {ag.is_isolated ? (
                          <button
                            type="button"
                            onClick={() => handleReinstateAgent(ag.agent_id)}
                            className="px-2.5 py-1 bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 rounded text-xs transition"
                          >
                            Reinstate
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => handleIsolateAgent(ag.agent_id)}
                            className="px-2.5 py-1 bg-red-950/80 hover:bg-red-900 text-red-300 rounded text-xs transition"
                          >
                            Isolate
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* TAB 2: Anomaly & Security Alerts */}
        {activeTab === 'alerts' && (
          <div className="space-y-3">
            {anomalies.length === 0 ? (
              <div className="py-12 text-center text-slate-400">
                <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2 opacity-80" />
                <p>No active anomalies or policy violations detected across the agent mesh.</p>
              </div>
            ) : (
              anomalies.map((anom) => (
                <div
                  key={anom.anomaly_id}
                  className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg flex flex-wrap items-start justify-between gap-4"
                >
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="flex flex-col items-center gap-1 flex-shrink-0">
                      <SuperIcon name="evaluation" style="color" size={18} />
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider mt-0.5 ${
                          anom.severity === 'CRITICAL'
                            ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                            : anom.severity === 'HIGH'
                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                        }`}
                      >
                        {anom.severity}
                      </span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-semibold text-white">{anom.anomaly_type}</span>
                        <span className="text-slate-400 font-mono text-xs">({anom.agent_id})</span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1 break-words">{anom.description}</p>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-[11px] text-slate-400">
                        <span className="inline-flex items-center gap-1">
                          <SuperIcon name="citations" style="two-tone" size={12} />
                          <span>Source: {anom.source}</span>
                        </span>
                        <span>Recommended: {anom.recommended_action}</span>
                        <span>{new Date(anom.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleIsolateAgent(anom.agent_id)}
                    className="flex-shrink-0 whitespace-nowrap px-3 py-1 bg-rose-950/80 hover:bg-rose-900 text-rose-300 rounded text-xs transition"
                  >
                    Enforce Isolation
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {/* TAB 3: Supervisory Decisions Log */}
        {activeTab === 'decisions' && (
          <div className="space-y-3">
            {decisions.length === 0 ? (
              <div className="py-12 text-center text-slate-400">
                <Clock className="w-8 h-8 text-slate-500 mx-auto mb-2 opacity-50" />
                <p>No supervisory decisions logged yet.</p>
              </div>
            ) : (
              decisions.map((dec) => (
                <div
                  key={dec.decision_id}
                  className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-lg flex flex-wrap items-start justify-between gap-3 text-xs"
                >
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="w-6 h-6 flex-shrink-0 flex items-center justify-center mt-0.5">
                      <SuperIcon
                        name={dec.decision_type === 'ISOLATE' ? 'sandbox' : 'feedback-loop'}
                        style="color"
                        size={18}
                      />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono font-bold">
                          LEVEL {dec.governance_level}: {dec.decision_type}
                        </span>
                        <span className="font-mono text-slate-400">{dec.agent_id}</span>
                      </div>
                      <p className="text-slate-300 mt-1 break-words">{dec.justification}</p>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5 text-[11px] text-slate-500 font-mono">
                        <span>Operator: {dec.operator_identity}</span>
                        <span>Time: {new Date(dec.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                  <span className="flex-shrink-0 whitespace-nowrap px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-900 text-[10px] font-bold">
                    {dec.status}
                  </span>
                </div>
              ))
            )}
          </div>
        )}

        {/* TAB 4: Defensive Simulation & Controls */}
        {activeTab === 'defense' && (
          <div className="space-y-6">
            <div className="p-4 bg-slate-950/80 border border-amber-500/30 rounded-lg">
              <h3 className="text-sm font-bold text-amber-300 flex items-center space-x-2">
                <SuperIcon name="permissions" style="color" size={18} />
                <span>Simulate Agent Anomaly & Test Supervisory Response</span>
              </h3>
              <p className="text-xs text-slate-300 mt-1">
                Trigger real-time adversarial conditions against HACTM agents to observe the Central Agent Supervisor
                detect anomalies, scale epistemic uncertainty, downgrade trust, and initiate governed containment.
              </p>

              <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Target Agent</label>
                  <select
                    value={selectedAgentForControl}
                    onChange={(e) => setSelectedAgentForControl(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-xs text-white"
                  >
                    <option value="network-security-agent">Network Security Agent</option>
                    <option value="phishing-intelligence-agent">Phishing Intelligence Agent</option>
                    <option value="uba-agent">Behaviour Intelligence Agent</option>
                    <option value="identity-authentication-agent">Identity Security Agent</option>
                    <option value="transaction-security-agent">Transaction Security Agent</option>
                    <option value="global-orchestrator">Global Adaptive Orchestrator</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Anomaly Scenario</label>
                  <select
                    value={selectedScenario}
                    onChange={(e) => setSelectedScenario(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-1.5 text-xs text-white"
                  >
                    <option value="UNAUTHORISED_TOOL_REQUEST">Unauthorised Tool Request (Gateway Violation)</option>
                    <option value="MISSING_HEARTBEAT">Missing Heartbeat (Operational Outage)</option>
                    <option value="PROMPT_INJECTION">Adversarial Prompt Injection in Evidence</option>
                    <option value="ORCHESTRATOR_ANOMALY">Orchestrator Assigns Task to Isolated Agent</option>
                  </select>
                </div>
              </div>

              <div className="mt-4 flex justify-end">
                <button
                  onClick={handleSimulateAnomaly}
                  disabled={simulating}
                  className="px-4 py-2 bg-gradient-to-r from-amber-600 to-rose-600 hover:from-amber-500 hover:to-rose-500 text-white font-semibold rounded text-xs transition shadow-lg flex items-center space-x-2"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{simulating ? 'Simulating...' : 'Inject Anomaly Telemetry'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

