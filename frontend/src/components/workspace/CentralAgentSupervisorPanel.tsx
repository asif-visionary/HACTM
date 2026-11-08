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
  ShieldAlert,
  ShieldCheck,
  Activity,
  AlertTriangle,
  Radio,
  RefreshCw,
  Users,
  Eye,
  Lock,
  Unlock,
  Sliders,
  CheckCircle,
  Clock,
  Play,
  Cpu,
  Zap,
  Terminal,
  FileText,
  ChevronRight,
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

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-2xl backdrop-blur-md flex flex-col">
      {/* Supervisor Header */}
      <div className="px-6 py-4 bg-slate-950/80 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-950/50">
            <SuperIcon name="monitoring" style="color" size={26} alt="Central Agent Supervisor" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold tracking-wide text-white">CENTRAL AGENT SUPERVISOR</h2>
              <span className="px-2 py-0.5 text-xs font-semibold rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                ACTIVE
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Continuous Multi-Agent Telemetry, Behavioral Analysis, Trust Evaluation & Autonomous Governance
            </p>
          </div>
        </div>

        {/* Watchdog status & Refresh */}
        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
            <SuperIcon name="feedback-loop" style="duotone" size={14} className="mr-0.5" />
            <span className="text-slate-400">Watchdog:</span>
            <span className="text-emerald-400 font-mono font-semibold flex items-center">
              <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5 animate-ping" />
              {fleet?.supervisor_health || 'HEALTHY'}
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">Latency:</span>
            <span className="text-cyan-400 font-mono">{fleet?.event_ingestion_latency_ms || 0.45} ms</span>
          </div>

          <button
            onClick={refreshSupervisorData}
            disabled={loading}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
            title="Refresh Supervisory Telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="p-6 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3 bg-slate-950/40 border-b border-slate-800/80">
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-medium">Total Agents</span>
            <SuperIcon name="multi-agent" style="duotone" size={15} />
          </div>
          <span className="text-xl font-bold text-white font-mono mt-1">{fleet?.total_registered_agents ?? 5}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-emerald-950/40 border-l-2 border-l-emerald-500 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-medium">Healthy</span>
            <SuperIcon name="alignment" style="color" size={15} />
          </div>
          <span className="text-xl font-bold text-emerald-400 font-mono mt-1">{fleet?.healthy_agents ?? 5}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-amber-950/40 border-l-2 border-l-amber-500 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-medium">Observation</span>
            <SuperIcon name="reflection" style="color" size={15} />
          </div>
          <span className="text-xl font-bold text-amber-400 font-mono mt-1">{fleet?.agents_under_observation ?? 0}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-rose-950/40 border-l-2 border-l-rose-500 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-medium">Anomalies</span>
            <SuperIcon name="evaluation" style="color" size={15} />
          </div>
          <span className="text-xl font-bold text-rose-400 font-mono mt-1">{fleet?.agents_with_anomalies ?? 0}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-yellow-950/40 border-l-2 border-l-yellow-500 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-medium">Restricted</span>
            <SuperIcon name="permissions" style="color" size={15} />
          </div>
          <span className="text-xl font-bold text-yellow-400 font-mono mt-1">{fleet?.restricted_agents ?? 0}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-red-950/40 border-l-2 border-l-red-600 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-medium">Isolated</span>
            <SuperIcon name="sandbox" style="color" size={15} />
          </div>
          <span className="text-xl font-bold text-red-500 font-mono mt-1">{fleet?.isolated_agents ?? 0}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800 border-l-2 border-l-slate-600 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-medium">Offline</span>
            <SuperIcon name="sandbox" style="stroke" size={15} />
          </div>
          <span className="text-xl font-bold text-slate-400 font-mono mt-1">{fleet?.offline_agents ?? 0}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-lg border border-cyan-950/40 border-l-2 border-l-cyan-400 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-400 font-medium">Active Alerts</span>
            <SuperIcon name="monitoring" style="color" size={15} />
          </div>
          <span className="text-xl font-bold text-cyan-300 font-mono mt-1">{fleet?.active_monitoring_alerts ?? 0}</span>
        </div>
      </div>

      {/* Intelligence Banner */}
      {intelligence && (
        <div className="px-6 py-3 bg-gradient-to-r from-cyan-950/30 to-slate-900/40 border-b border-cyan-900/30 flex items-start space-x-3 text-xs">
          <Info className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <span className="font-semibold text-cyan-300 uppercase tracking-wider mr-2">
              [{intelligence.supervisory_posture}]
            </span>
            <span className="text-slate-300">{intelligence.executive_narrative}</span>
            {intelligence.governance_recommendations.length > 0 && (
              <span className="ml-2 text-cyan-400/90 font-medium">
                Recommendation: {intelligence.governance_recommendations[0]}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Action Success Toast */}
      {actionSuccessMessage && (
        <div className="px-6 py-2.5 bg-emerald-950/60 border-b border-emerald-500/40 flex items-center justify-between text-xs text-emerald-300">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>{actionSuccessMessage}</span>
          </div>
          <button onClick={() => setActionSuccessMessage(null)} className="text-emerald-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Navigation Sub-Tabs */}
      <div className="px-6 pt-4 border-b border-slate-800 flex space-x-2">
        <button
          onClick={() => setActiveTab('fleet')}
          className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition border-b-2 flex items-center space-x-2 ${
            activeTab === 'fleet'
              ? 'border-cyan-400 text-cyan-400 bg-slate-800/60'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <SuperIcon name="multi-agent" style="duotone" size={15} />
          <span>Agent Fleet Monitoring ({agents.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('alerts')}
          className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition border-b-2 flex items-center space-x-2 ${
            activeTab === 'alerts'
              ? 'border-rose-400 text-rose-400 bg-slate-800/60'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <SuperIcon name="evaluation" style="duotone" size={15} />
          <span>Anomaly & Security Alerts ({anomalies.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('decisions')}
          className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition border-b-2 flex items-center space-x-2 ${
            activeTab === 'decisions'
              ? 'border-emerald-400 text-emerald-400 bg-slate-800/60'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <SuperIcon name="feedback-loop" style="duotone" size={15} />
          <span>Supervisory Decisions ({decisions.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('defense')}
          className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition border-b-2 flex items-center space-x-2 ${
            activeTab === 'defense'
              ? 'border-amber-400 text-amber-400 bg-slate-800/60'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <SuperIcon name="permissions" style="duotone" size={15} />
          <span>Defensive Simulation & Controls</span>
        </button>
      </div>

      {/* Main Tab Content */}
      <div className="p-6">
        {/* TAB 1: Agent Fleet Monitoring Table */}
        {activeTab === 'fleet' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 font-mono uppercase text-[11px] border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Agent Name / ID</th>
                  <th className="py-3 px-4">Department</th>
                  <th className="py-3 px-4">Health Vitals</th>
                  <th className="py-3 px-4">Trust Status</th>
                  <th className="py-3 px-4">Current Task</th>
                  <th className="py-3 px-4">Last Heartbeat</th>
                  <th className="py-3 px-4 text-right">Governed Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {agents.map((ag) => (
                  <tr key={ag.agent_id} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <SuperIcon
                          name={ag.agent_id.includes('orchestrator') ? 'orchestration' : 'agent'}
                          style={ag.is_isolated ? 'color' : 'duotone'}
                          size={16}
                          className="flex-shrink-0"
                        />
                        <div>
                          <div className="font-semibold text-white flex items-center space-x-1.5">
                            <span>{ag.name}</span>
                            {ag.is_isolated && (
                              <span className="flex items-center text-[10px] text-red-400 bg-red-950/80 px-1.5 py-0.2 rounded border border-red-500/40">
                                <SuperIcon name="sandbox" style="color" size={11} className="mr-0.5" />
                                ISOLATED
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-slate-400 font-mono">{ag.agent_id}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-300">{ag.department}</td>
                    <td className="py-3 px-4">
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
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
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
                    <td className="py-3 px-4 text-slate-300 truncate max-w-xs">
                      {ag.current_task ? (
                        <div className="flex items-center space-x-1.5">
                          <SuperIcon name="task" style="stroke" size={13} className="text-slate-400 flex-shrink-0" />
                          <span className="truncate">{ag.current_task}</span>
                        </div>
                      ) : (
                        <span className="text-slate-500 italic">Idle</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(ag.last_heartbeat).toLocaleTimeString()}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => onSelectAgent(ag.agent_id)}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-300 rounded text-xs transition"
                      >
                        Passport
                      </button>
                      {ag.is_isolated ? (
                        <button
                          onClick={() => handleReinstateAgent(ag.agent_id)}
                          className="px-2.5 py-1 bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 rounded text-xs transition"
                        >
                          Reinstate
                        </button>
                      ) : (
                        <button
                          onClick={() => handleIsolateAgent(ag.agent_id)}
                          className="px-2.5 py-1 bg-red-950/80 hover:bg-red-900 text-red-300 rounded text-xs transition"
                        >
                          Isolate
                        </button>
                      )}
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
                  className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg flex items-start justify-between gap-4"
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex flex-col items-center space-y-1">
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
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-white">{anom.anomaly_type}</span>
                        <span className="text-slate-400 font-mono text-xs">({anom.agent_id})</span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1">{anom.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-[11px] text-slate-400">
                        <span className="flex items-center">
                          <SuperIcon name="citations" style="two-tone" size={12} className="mr-1" />
                          Source: {anom.source}
                        </span>
                        <span>Recommended: {anom.recommended_action}</span>
                        <span>{new Date(anom.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => handleIsolateAgent(anom.agent_id)}
                    className="px-3 py-1 bg-rose-950/80 hover:bg-rose-900 text-rose-300 rounded text-xs transition"
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
                  className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-lg flex items-start justify-between text-xs"
                >
                  <div className="flex items-start space-x-3">
                    <SuperIcon
                      name={dec.decision_type === 'ISOLATE' ? 'sandbox' : 'feedback-loop'}
                      style="color"
                      size={18}
                      className="mt-0.5 flex-shrink-0"
                    />
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono font-bold">
                          LEVEL {dec.governance_level}: {dec.decision_type}
                        </span>
                        <span className="font-mono text-slate-400">{dec.agent_id}</span>
                      </div>
                      <p className="text-slate-300 mt-1">{dec.justification}</p>
                      <div className="flex items-center space-x-4 mt-1.5 text-[11px] text-slate-500 font-mono">
                        <span>Operator: {dec.operator_identity}</span>
                        <span>Time: {new Date(dec.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-900 text-[10px] font-bold">
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

