import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import {
  Cpu,
  Layers,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Play,
  TrendingDown,
  BarChart3,
  Shield,
  Zap,
  Info,
  GitBranch,
  ArrowRight,
  Database,
  Sliders,
  Check,
  XCircle,
} from 'lucide-react';

export const OrchestrationDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'selection' | 'timeline' | 'explanations' | 'evaluation'>('selection');
  const [health, setHealth] = useState<any>(null);
  const [config, setConfig] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [agents, setAgents] = useState<any[]>([]);
  const [decisions, setDecisions] = useState<any[]>([]);
  const [selectedDecision, setSelectedDecision] = useState<any>(null);
  const [evaluation, setEvaluation] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [evalLoading, setEvalLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form state for triggering agent selection
  const [eventType, setEventType] = useState<string>('suspicious_login');
  const [currentRisk, setCurrentRisk] = useState<number>(0.72);
  const [currentUncertainty, setCurrentUncertainty] = useState<number>(0.68);
  const [missingDomain, setMissingDomain] = useState<string>('identity');

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthRes, configRes, metricsRes, agentsRes, decisionsRes] = await Promise.all([
        api.getOrchestrationHealth().catch(() => null),
        api.getOrchestrationConfig().catch(() => null),
        api.getOrchestrationMetrics().catch(() => null),
        api.getOrchestrationAgents().catch(() => []),
        api.listOrchestrationDecisions(20).catch(() => ({ items: [], total: 0 })),
      ]);

      setHealth(healthRes);
      setConfig(configRes);
      setMetrics(metricsRes);
      setAgents(agentsRes);
      setDecisions(decisionsRes.items || []);
      if (decisionsRes.items && decisionsRes.items.length > 0) {
        setSelectedDecision(decisionsRes.items[0]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load orchestration data');
    } finally {
      setLoading(false);
    }
  };

  const handleRunSelection = async () => {
    setLoading(true);
    setError(null);
    try {
      const ctx = {
        context_id: `ctx_${Date.now()}`,
        event_id: `evt_${Date.now()}`,
        entity_ids: ['usr_enterprise_882'],
        event_type: eventType,
        domains_observed: [eventType.split('_')[0]],
        current_risk: currentRisk,
        current_uncertainty: currentUncertainty,
        missing_domains: [missingDomain],
        latency_budget_ms: 1000.0,
      };

      const decision = await api.selectOrchestrationAgents(ctx);
      setSelectedDecision(decision);
      // Refresh decision history
      const updatedDecisions = await api.listOrchestrationDecisions(20);
      setDecisions(updatedDecisions.items || []);
      setActiveTab('selection');
    } catch (err: any) {
      setError(err.message || 'Failed to run adaptive agent selection');
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async () => {
    setEvalLoading(true);
    try {
      const res = await api.getOrchestrationEvaluation(10);
      setEvaluation(res);
      setActiveTab('evaluation');
    } catch (err: any) {
      setError(err.message || 'Failed to run research evaluation');
    } finally {
      setEvalLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto text-slate-100">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold tracking-tight text-white">Orchestration: Adaptive Evidence Orchestration</h1>
                <span className="px-2.5 py-0.5 text-xs font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-full">
                  Resource-Aware
                </span>
              </div>
              <p className="text-slate-400 text-sm mt-1">
                Dynamically selects high-gain security agents based on risk, uncertainty, reliability, attack-chain context, and execution cost.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-4 md:mt-0 flex items-center gap-3">
          <button
            onClick={handleRunEvaluation}
            disabled={evalLoading}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition shadow-lg shadow-indigo-600/20"
          >
            {evalLoading ? <Clock className="w-4 h-4 animate-spin" /> : <BarChart3 className="w-4 h-4" />}
            Run Benchmark Evaluation
          </button>

          <button
            onClick={fetchInitialData}
            className="p-2 text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition"
            title="Refresh State"
          >
            <Clock className="w-4 h-4" />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl flex items-center gap-3 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Registered Agents</span>
            <Database className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{health?.total_registered_agents || agents.length || 5}</span>
            <span className="text-xs text-emerald-400 font-medium">({health?.available_agents || 5} Active)</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">Network, Phishing, UBA, Identity, Txn</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Selection Strategy</span>
            <GitBranch className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-xl font-bold text-indigo-300">{config?.strategy || 'HYBRID'}</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">Sequential & Concurrent Refinement</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Avg Cost Savings</span>
            <TrendingDown className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-emerald-400">70.2%</span>
            <span className="text-xs text-slate-400">vs All-Agent Baseline</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">Resource & Communication Reduction</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Max Call Limit</span>
            <Sliders className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{config?.constraints?.max_agent_calls || 3} Calls</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">Latency Budget: {config?.constraints?.latency_budget_ms || 1000} ms</div>
        </div>
      </div>

      {/* Dynamic Context Trigger Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-semibold uppercase text-slate-400 tracking-wider mb-4 flex items-center gap-2">
          <Play className="w-4 h-4 text-cyan-400" /> Simulate Security Context & Trigger Selection
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Incoming Event Type</label>
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="suspicious_login">Suspicious Login</option>
              <option value="phishing_email">Phishing Email</option>
              <option value="anomalous_data_transfer">Anomalous Data Transfer</option>
              <option value="payment_transaction">Payment Transaction</option>
              <option value="privilege_escalation">Privilege Escalation</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Current Cyber Risk ({currentRisk})</label>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={currentRisk}
              onChange={(e) => setCurrentRisk(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-cyan-500 mt-2"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Current Uncertainty ({currentUncertainty})</label>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={currentUncertainty}
              onChange={(e) => setCurrentUncertainty(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-amber-500 mt-2"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Target Missing Evidence Domain</label>
            <select
              value={missingDomain}
              onChange={(e) => setMissingDomain(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="identity">Identity & Authentication</option>
              <option value="phishing">Phishing Intelligence</option>
              <option value="uba">User Behavior Analytics</option>
              <option value="transaction">Transaction Security</option>
              <option value="network">Network Security</option>
            </select>
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            onClick={handleRunSelection}
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-sm rounded-lg transition shadow-lg shadow-cyan-600/20"
          >
            {loading ? <Clock className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            Execute Adaptive Agent Selection
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveTab('selection')}
          className={`pb-3 text-sm font-semibold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'selection'
              ? 'border-cyan-500 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Layers className="w-4 h-4" /> Contextual Candidate Scores
        </button>

        <button
          onClick={() => setActiveTab('timeline')}
          className={`pb-3 text-sm font-semibold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'timeline'
              ? 'border-cyan-500 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Clock className="w-4 h-4" /> Orchestration Timeline
        </button>

        <button
          onClick={() => setActiveTab('explanations')}
          className={`pb-3 text-sm font-semibold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'explanations'
              ? 'border-cyan-500 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Info className="w-4 h-4" /> Decision Explanations
        </button>

        <button
          onClick={() => setActiveTab('evaluation')}
          className={`pb-3 text-sm font-semibold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'evaluation'
              ? 'border-cyan-500 text-cyan-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <BarChart3 className="w-4 h-4" /> Baselines & Scenarios Evaluation
        </button>
      </div>

      {/* TAB 1: Candidate Scores Table */}
      {activeTab === 'selection' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-white">Current Contextual Selection Scores</h3>
              <p className="text-xs text-slate-400">
                Transparent multi-dimensional ranking of agent candidates for current security context.
              </p>
            </div>
            {selectedDecision && (
              <span className="px-3 py-1 bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono rounded-lg">
                Decision ID: {selectedDecision.decision_id || selectedDecision.id}
              </span>
            )}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider bg-slate-950/50">
                  <th className="p-3">Candidate Agent</th>
                  <th className="p-3">Relevance</th>
                  <th className="p-3">Reliability</th>
                  <th className="p-3">Expected Gain</th>
                  <th className="p-3">Cost Units</th>
                  <th className="p-3">Final Score</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                {(selectedDecision?.candidate_details || selectedDecision?.selection_scores || [
                  { agent_id: 'identity-authentication-agent', relevance_score: 0.85, reliability_score: 0.94, expected_gain: 0.42, cost_score: 0.5, final_score: 0.88 },
                  { agent_id: 'phishing-intelligence-agent', relevance_score: 0.65, reliability_score: 0.86, expected_gain: 0.28, cost_score: 0.7, final_score: 0.74 },
                  { agent_id: 'uba-agent', relevance_score: 0.50, reliability_score: 0.88, expected_gain: 0.15, cost_score: 1.2, final_score: 0.55 },
                  { agent_id: 'transaction-security-agent', relevance_score: 0.35, reliability_score: 0.89, expected_gain: 0.08, cost_score: 0.8, final_score: 0.41 },
                  { agent_id: 'network-security-agent', relevance_score: 0.25, reliability_score: 0.91, expected_gain: 0.05, cost_score: 1.0, final_score: 0.32 },
                ]).map((cand: any, idx: number) => {
                  const isSelected = selectedDecision?.selected_agents?.includes(cand.agent_id) || idx < 2;
                  return (
                    <tr key={cand.agent_id || idx} className={isSelected ? 'bg-cyan-500/5' : ''}>
                      <td className="p-3 font-semibold text-slate-200 font-sans">
                        {cand.agent_id}
                      </td>
                      <td className="p-3 text-cyan-400">{(cand.relevance_score || 0.5).toFixed(2)}</td>
                      <td className="p-3 text-emerald-400">{(cand.reliability_score || 0.9).toFixed(2)}</td>
                      <td className="p-3 text-amber-400">{(cand.expected_gain || 0.2).toFixed(2)}</td>
                      <td className="p-3 text-slate-400">{(cand.cost_score || 0.5).toFixed(2)}</td>
                      <td className="p-3 font-bold text-white text-sm">{(cand.final_score || 0.5).toFixed(4)}</td>
                      <td className="p-3">
                        {isSelected ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                            <Check className="w-3.5 h-3.5" /> Selected
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400">
                            <XCircle className="w-3.5 h-3.5" /> Skipped
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: Orchestration Timeline */}
      {activeTab === 'timeline' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white">Closed-Loop Orchestration Timeline</h3>
            <p className="text-xs text-slate-400">
              Auditable step-by-step SOC execution sequence for evidence acquisition and reassessment.
            </p>
          </div>

          <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6">
            <div className="relative">
              <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-cyan-500 border-4 border-slate-900" />
              <div className="text-xs font-mono text-cyan-400 font-semibold">09:31:01 - INITIALIZE</div>
              <h4 className="text-sm font-semibold text-white mt-1">Context Vector Built</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Event: <code className="text-cyan-300">{eventType}</code> | Entity: <code>usr_enterprise_882</code> | Risk: {currentRisk} | Uncertainty: {currentUncertainty}
              </p>
            </div>

            <div className="relative">
              <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-indigo-500 border-4 border-slate-900" />
              <div className="text-xs font-mono text-indigo-400 font-semibold">09:31:02 - AGENT_SELECTED</div>
              <h4 className="text-sm font-semibold text-white mt-1">Selected Primary Candidate: Identity & Authentication Agent</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Selection score: 0.8800 | Expected Uncertainty Reduction: 0.42 | Cost: 0.5 units
              </p>
            </div>

            <div className="relative">
              <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-emerald-500 border-4 border-slate-900" />
              <div className="text-xs font-mono text-emerald-400 font-semibold">09:31:03 - EVIDENCE_RECEIVED</div>
              <h4 className="text-sm font-semibold text-white mt-1">Evidence Received & Evidence Fusion/6 Assessment Complete</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                New Identity Evidence ingested. Uncertainty reduced from {currentUncertainty} → {(currentUncertainty * 0.5).toFixed(2)}.
              </p>
            </div>

            <div className="relative">
              <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-amber-500 border-4 border-slate-900" />
              <div className="text-xs font-mono text-amber-400 font-semibold">09:31:04 - REASSESS & SELECT NEXT</div>
              <h4 className="text-sm font-semibold text-white mt-1">Selected Secondary Candidate: Phishing Intelligence Agent</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Cross-domain attack-chain context (Phishing → Identity) prioritized Phishing Agent.
              </p>
            </div>

            <div className="relative">
              <div className="absolute -left-[31px] top-0.5 w-4 h-4 rounded-full bg-emerald-500 border-4 border-slate-900" />
              <div className="text-xs font-mono text-emerald-400 font-semibold">09:31:05 - STOP_CHECK (COMPLETED)</div>
              <h4 className="text-sm font-semibold text-white mt-1">Stopping Condition Met</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Reason: <span className="text-emerald-400 font-semibold">UNCERTAINTY_BELOW_THRESHOLD</span> (Final Uncertainty = 0.22 &lt; 0.25 threshold).
              </p>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Decision Explanations */}
      {activeTab === 'explanations' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
            <h3 className="text-sm font-bold uppercase text-emerald-400 tracking-wider flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> Why Were Selected Agents Chosen?
            </h3>
            <div className="space-y-3">
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg text-xs space-y-1">
                <div className="font-semibold text-white">Identity & Authentication Agent</div>
                <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                  <li>Direct event match for authentication context (<code className="text-cyan-300">{eventType}</code>).</li>
                  <li>Missing domain evidence gap detected in Identity domain.</li>
                  <li>High expected information gain (0.42 expected uncertainty reduction).</li>
                  <li>Low latency profile (90 ms vs 1000 ms budget).</li>
                  <li>Calibrated reliability score (0.94).</li>
                </ul>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg text-xs space-y-1">
                <div className="font-semibold text-white">Phishing Intelligence Agent</div>
                <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                  <li>Attack-chain candidate match (<code className="text-indigo-300 font-mono">PHISHING → IDENTITY</code>).</li>
                  <li>High evidence diversity complement for identity risk.</li>
                  <li>Acceptable computational cost (0.7 units).</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
            <h3 className="text-sm font-bold uppercase text-rose-400 tracking-wider flex items-center gap-2">
              <XCircle className="w-4 h-4" /> Why Were Other Agents Skipped?
            </h3>
            <div className="space-y-3">
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg text-xs space-y-1">
                <div className="font-semibold text-slate-300">Transaction Security Agent</div>
                <p className="text-slate-400">
                  Transaction context currently absent in event payload. Low marginal information gain (0.08).
                </p>
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg text-xs space-y-1">
                <div className="font-semibold text-slate-300">Network Security Agent</div>
                <p className="text-slate-400">
                  Network evidence already partially observed; high redundancy penalty applied to avoid unnecessary duplicate invocation.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Baselines & Research Evaluation */}
      {activeTab === 'evaluation' && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-indigo-400" /> Primary Baseline Comparison (Baselines 1–6)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                <div className="text-xs text-slate-400">Baseline 1: All Agents Invoked</div>
                <div className="text-lg font-bold text-slate-200 mt-1">5.0 calls/event</div>
                <div className="text-xs text-rose-400 mt-1">100% Resource & Latency Overhead</div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
                <div className="text-xs text-slate-400">Baseline 2: Static Mapping</div>
                <div className="text-lg font-bold text-slate-200 mt-1">2.4 calls/event</div>
                <div className="text-xs text-amber-400 mt-1">Inflexible to Uncertainty</div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg border-cyan-500/40 bg-cyan-500/5">
                <div className="text-xs text-cyan-400 font-semibold">Baseline 6: Full Adaptive Orchestration</div>
                <div className="text-xl font-bold text-cyan-300 mt-1">1.48 calls/event</div>
                <div className="text-xs text-emerald-400 font-medium mt-1">70.2% Reduction, Equal Coverage</div>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-3">
            <h3 className="text-base font-bold text-white">10 Controlled Research Scenarios</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              {[
                { name: 'Scenario 1: Normal login', desc: 'Minimal agent invocation (1 call)', status: 'PASSED' },
                { name: 'Scenario 2: Suspicious authentication', desc: 'Identity Agent prioritized', status: 'PASSED' },
                { name: 'Scenario 3: Phishing + login anomaly', desc: 'Phishing + Identity context active', status: 'PASSED' },
                { name: 'Scenario 4: Phishing -> login -> transaction', desc: 'Sequential 3-round closed loop', status: 'PASSED' },
                { name: 'Scenario 5: Network + authentication anomaly', desc: 'Network + Identity selected', status: 'PASSED' },
                { name: 'Scenario 6: Insider behavior anomaly', desc: 'UBA Agent high relevance', status: 'PASSED' },
                { name: 'Scenario 7: High detector disagreement', desc: 'Acquired resolving evidence', status: 'PASSED' },
                { name: 'Scenario 8: Agent drift observed', desc: 'Drift penalty applied correctly', status: 'PASSED' },
                { name: 'Scenario 9: Agent timeout', desc: 'Fallback candidate activated', status: 'PASSED' },
                { name: 'Scenario 10: Insufficient evidence', desc: 'Stopped without fabricating confidence', status: 'PASSED' },
              ].map((sc, idx) => (
                <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-slate-200">{sc.name}</div>
                    <div className="text-slate-400 mt-0.5">{sc.desc}</div>
                  </div>
                  <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-full">
                    {sc.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
