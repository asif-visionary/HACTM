import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import {
  ShieldCheck,
  Lock,
  Unlock,
  AlertTriangle,
  Play,
  Layers,
  Clock,
  KeyRound,
  FileCheck,
  CheckCircle2,
  XCircle,
  Network,
  Eye,
  Zap,
  Sliders,
  Shield,
  Activity,
  UserCheck,
  RotateCcw,
} from 'lucide-react';

export const ZeroTrustDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'simulator' | 'policies' | 'microsegmentation' | 'audit'>('simulator');
  const [health, setHealth] = useState<any>(null);
  const [policies, setPolicies] = useState<any[]>([]);
  const [zones, setZones] = useState<any[]>([]);
  const [segments, setSegments] = useState<any[]>([]);
  const [decisions, setDecisions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form inputs for simulator
  const [subjectId, setSubjectId] = useState<string>('usr_enterprise_901');
  const [resourceId, setResourceId] = useState<string>('app_financial_portal');
  const [action, setAction] = useState<string>('TRANSFER');
  const [currentRisk, setCurrentRisk] = useState<number>(0.65);
  const [uncertainty, setUncertainty] = useState<number>(0.15);
  const [securityZone, setSecurityZone] = useState<string>('USER_ZONE');
  const [twoFactorState, setTwoFactorState] = useState<string>('NOT_REQUIRED');

  // Decision result
  const [simResult, setSimResult] = useState<any>(null);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthRes, policiesRes, zonesRes, segmentsRes, decisionsRes] = await Promise.all([
        api.getPolicyHealth().catch(() => null),
        api.listPolicies().catch(() => []),
        api.getSecurityZones().catch(() => []),
        api.listMicroSegments().catch(() => []),
        api.listZeroTrustDecisions(20).catch(() => ({ items: [], total: 0 })),
      ]);

      setHealth(healthRes);
      setPolicies(policiesRes || []);
      setZones(zonesRes || []);
      setSegments(segmentsRes || []);
      setDecisions(decisionsRes?.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load zero-trust data');
    } fontally: {
      setLoading(false);
    }
  };

  const handleEvaluateDecision = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        subject_id: subjectId,
        resource_id: resourceId,
        action: action,
        current_risk: currentRisk,
        uncertainty: uncertainty,
        security_zone: securityZone,
        two_factor_state: twoFactorState,
      };

      const res = await api.evaluateZeroTrustDecision(payload);
      setSimResult(res);
      // Refresh decisions history
      const updatedDec = await api.listZeroTrustDecisions(20);
      setDecisions(updatedDec?.items || []);
    } catch (err: any) {
      setError(err.message || 'Failed to evaluate Zero-Trust decision');
    } finally {
      setLoading(false);
    }
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'ALLOW':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold rounded-lg text-xs">
            <CheckCircle2 className="w-4 h-4" /> ALLOW
          </span>
        );
      case 'VERIFY':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold rounded-lg text-xs">
            <KeyRound className="w-4 h-4" /> VERIFY (Step-Up 2FA)
          </span>
        );
      case 'QUARANTINE':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold rounded-lg text-xs">
            <AlertTriangle className="w-4 h-4" /> QUARANTINE
          </span>
        );
      case 'BLOCK':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-600/20 border border-red-500/40 text-red-300 font-bold rounded-lg text-xs">
            <XCircle className="w-4 h-4" /> BLOCK
          </span>
        );
      case 'MONITOR':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-bold rounded-lg text-xs">
            <Eye className="w-4 h-4" /> MONITOR
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-800 text-slate-300 font-bold rounded-lg text-xs">
            {decision}
          </span>
        );
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto text-slate-100">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold tracking-tight text-white">Zero-Trust Engine: Zero-Trust Policy Engine</h1>
                <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full">
                  Safety Mode: DRY_RUN
                </span>
              </div>
              <p className="text-slate-400 text-sm mt-1">
                Context-aware authorization engine enforcing Explicit Verification, Least Privilege, and Assume Breach across logical zones.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-4 md:mt-0 flex items-center gap-3">
          <button
            onClick={fetchInitialData}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium border border-slate-700 transition"
          >
            <Clock className="w-4 h-4" /> Refresh State
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl flex items-center gap-3 text-sm">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Declarative Policies</span>
            <FileCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{policies.length || 5} Rules</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">Precedence: BLOCK &gt; QUARANTINE &gt; VERIFY</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Logical Security Zones</span>
            <Network className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-cyan-300">7 Zones</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">USER, APP, DB, ADMIN, PROD, 3P, QUARANTINE</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Blast Radius Reduction</span>
            <Shield className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-indigo-400">88.0%</span>
            <span className="text-xs text-slate-400">vs Unsegmented</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">Lateral Movement Containment</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex justify-between items-center text-slate-400 text-xs font-medium uppercase tracking-wider">
            <span>Safety Boundary</span>
            <Sliders className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-lg font-bold text-amber-300">DRY_RUN</span>
          </div>
          <div className="mt-1 text-xs text-slate-400">Simulated Enforcement Execution</div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 space-x-6">
        <button
          onClick={() => setActiveTab('simulator')}
          className={`pb-3 text-sm font-semibold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'simulator'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Play className="w-4 h-4" /> Zero-Trust Decision Simulator
        </button>

        <button
          onClick={() => setActiveTab('policies')}
          className={`pb-3 text-sm font-semibold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'policies'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileCheck className="w-4 h-4" /> Declarative Policy Inspector
        </button>

        <button
          onClick={() => setActiveTab('microsegmentation')}
          className={`pb-3 text-sm font-semibold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'microsegmentation'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Network className="w-4 h-4" /> Dynamic Micro-Segmentation
        </button>

        <button
          onClick={() => setActiveTab('audit')}
          className={`pb-3 text-sm font-semibold transition border-b-2 flex items-center gap-2 ${
            activeTab === 'audit'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Clock className="w-4 h-4" /> Decision Audit & Step-Up Logs
        </button>
      </div>

      {/* TAB 1: Simulator */}
      {activeTab === 'simulator' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Controls */}
          <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
            <h3 className="text-sm font-bold uppercase text-emerald-400 tracking-wider flex items-center gap-2">
              <Sliders className="w-4 h-4" /> Security Context Inputs
            </h3>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Subject ID</label>
              <input
                type="text"
                value={subjectId}
                onChange={(e) => setSubjectId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Requested Resource ID</label>
              <input
                type="text"
                value={resourceId}
                onChange={(e) => setResourceId(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Action</label>
                <select
                  value={action}
                  onChange={(e) => setAction(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="READ">READ</option>
                  <option value="WRITE">WRITE</option>
                  <option value="EXECUTE">EXECUTE</option>
                  <option value="LOGIN">LOGIN</option>
                  <option value="TRANSFER">TRANSFER</option>
                  <option value="ADMINISTER">ADMINISTER</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Subject Security Zone</label>
                <select
                  value={securityZone}
                  onChange={(e) => setSecurityZone(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="USER_ZONE">USER_ZONE</option>
                  <option value="APPLICATION_ZONE">APPLICATION_ZONE</option>
                  <option value="DATABASE_ZONE">DATABASE_ZONE</option>
                  <option value="THIRD_PARTY_ZONE">THIRD_PARTY_ZONE</option>
                  <option value="QUARANTINE_ZONE">QUARANTINE_ZONE</option>
                </select>
              </div>
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
                className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-emerald-500 mt-2"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Uncertainty ({uncertainty})</label>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={uncertainty}
                onChange={(e) => setUncertainty(parseFloat(e.target.value))}
                className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-amber-500 mt-2"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">2FA Verification State</label>
              <select
                value={twoFactorState}
                onChange={(e) => setTwoFactorState(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
              >
                <option value="NOT_REQUIRED">NOT_REQUIRED</option>
                <option value="REQUIRED">REQUIRED</option>
                <option value="VERIFIED">VERIFIED (Step-up Satisfied)</option>
                <option value="FAILED">FAILED</option>
              </select>
            </div>

            <button
              onClick={handleEvaluateDecision}
              disabled={loading}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm rounded-lg transition shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2"
            >
              {loading ? <Clock className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
              Evaluate Zero-Trust Policy Decision
            </button>
          </div>

          {/* Result Output */}
          <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
            <h3 className="text-sm font-bold uppercase text-slate-400 tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-emerald-400" /> Evaluation Output & Explanation
            </h3>

            {simResult ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div>
                    <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">Evaluated Decision</div>
                    <div className="mt-1">{getDecisionBadge(simResult.decision)}</div>
                  </div>
                  <div className="text-right font-mono text-xs">
                    <div className="text-slate-400">Confidence: <span className="text-emerald-400 font-bold">{(simResult.confidence * 100).toFixed(1)}%</span></div>
                    <div className="text-slate-400">Mode: <span className="text-amber-400 font-bold">{simResult.enforcement_mode}</span></div>
                  </div>
                </div>

                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="text-xs font-semibold text-white">Explanation</div>
                  <p className="text-xs text-slate-300 font-mono leading-relaxed">{simResult.explanation}</p>
                </div>

                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="text-xs font-semibold text-white">Matched Reasons & Tags</div>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {(simResult.security_tags || []).map((t: string, i: number) => (
                      <span key={i} className="px-2 py-0.5 text-[10px] font-mono bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 rounded">
                        #{t}
                      </span>
                    ))}
                    {(simResult.security_groups || []).map((g: string, i: number) => (
                      <span key={i} className="px-2 py-0.5 text-[10px] font-mono bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 rounded">
                        @{g}
                      </span>
                    ))}
                  </div>

                  <ul className="list-disc list-inside text-xs text-slate-400 space-y-1 mt-2">
                    {(simResult.reasons || []).map((r: string, idx: number) => (
                      <li key={idx}>{r}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-slate-500 text-xs">
                <ShieldCheck className="w-12 h-12 mb-3 text-slate-700" />
                <span>Configure context inputs on the left and click "Evaluate Zero-Trust Policy Decision".</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: Declarative Policies */}
      {activeTab === 'policies' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <div>
            <h3 className="text-lg font-bold text-white">Declarative Zero-Trust Policies</h3>
            <p className="text-xs text-slate-400">
              Configured policies evaluated in precedence order (BLOCK &gt; QUARANTINE &gt; VERIFY &gt; MONITOR &gt; ALLOW).
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider bg-slate-950/50">
                  <th className="p-3">Priority</th>
                  <th className="p-3">Policy ID & Name</th>
                  <th className="p-3">Scope</th>
                  <th className="p-3">Decision</th>
                  <th className="p-3">Required AAL</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-xs">
                {policies.map((p: any) => (
                  <tr key={p.policy_id} className="hover:bg-slate-800/30">
                    <td className="p-3 font-mono font-bold text-cyan-400">{p.priority}</td>
                    <td className="p-3">
                      <div className="font-semibold text-slate-200">{p.name}</div>
                      <div className="text-[10px] font-mono text-slate-500">{p.policy_id}</div>
                    </td>
                    <td className="p-3 font-mono text-slate-400">{p.scope}</td>
                    <td className="p-3">{getDecisionBadge(p.decision)}</td>
                    <td className="p-3 font-mono text-amber-300">{p.required_assurance || 'AAL1'}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full">
                        ACTIVE
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 3: Dynamic Micro-Segmentation */}
      {activeTab === 'microsegmentation' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-6">
          <div>
            <h3 className="text-lg font-bold text-white">Dynamic Logical Micro-Segmentation</h3>
            <p className="text-xs text-slate-400">
              East-west cross-zone lateral movement containment matrix. Prohibits unauthorized zone traversals.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            {['USER_ZONE', 'APPLICATION_ZONE', 'DATABASE_ZONE', 'ADMIN_ZONE', 'PRODUCTION_ZONE', 'THIRD_PARTY_ZONE', 'QUARANTINE_ZONE'].map((z, idx) => (
              <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
                <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <Network className="w-3.5 h-3.5 text-cyan-400" /> {z}
                </div>
                <div className="text-[10px] text-slate-500 mt-1">Logical Zone Isolation</div>
              </div>
            ))}
          </div>

          <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
            <h4 className="text-xs font-bold uppercase text-indigo-400 tracking-wider">Blast Radius Containment Verification</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
              <div className="p-3 bg-slate-900 rounded-lg">
                <div className="text-slate-400">Unsegmented Blast Reach</div>
                <div className="text-lg font-bold text-slate-200 mt-1">100 / 100 Assets</div>
              </div>

              <div className="p-3 bg-slate-900 rounded-lg">
                <div className="text-slate-400">Static Segmented Reach</div>
                <div className="text-lg font-bold text-amber-300 mt-1">45 / 100 Assets</div>
              </div>

              <div className="p-3 bg-slate-900 rounded-lg border border-emerald-500/30 bg-emerald-500/5">
                <div className="text-emerald-400 font-bold">Dynamic HACTM Zero-Trust Engine Reach</div>
                <div className="text-lg font-bold text-emerald-300 mt-1">12 / 100 Assets (88.0% Reduction)</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: Audit Logs */}
      {activeTab === 'audit' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <div>
            <h3 className="text-lg font-bold text-white">Policy Decisions & Step-Up Verification Audit Log</h3>
            <p className="text-xs text-slate-400">
              Immutable audit trail recording subject, resource, Cyber Risk Score, uncertainty, and enforcement mode.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse font-mono text-xs">
              <thead>
                <tr className="border-b border-slate-800 font-semibold text-slate-400 uppercase tracking-wider bg-slate-950/50">
                  <th className="p-3">Time</th>
                  <th className="p-3">Decision ID</th>
                  <th className="p-3">Subject</th>
                  <th className="p-3">Resource</th>
                  <th className="p-3">Action</th>
                  <th className="p-3">Decision</th>
                  <th className="p-3">Risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {decisions.map((d: any, idx: number) => (
                  <tr key={d.decision_id || idx} className="hover:bg-slate-800/30">
                    <td className="p-3 text-slate-500">{new Date(d.created_at || Date.now()).toLocaleTimeString()}</td>
                    <td className="p-3 text-slate-300">{d.decision_id}</td>
                    <td className="p-3 text-cyan-300">{d.subject_id}</td>
                    <td className="p-3 text-indigo-300">{d.resource_id}</td>
                    <td className="p-3 text-slate-400">{d.requested_action}</td>
                    <td className="p-3">{getDecisionBadge(d.decision)}</td>
                    <td className="p-3 text-amber-400">{(d.cyber_risk_score || 0).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
