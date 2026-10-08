import React, { useState, useEffect } from 'react';
import {
  Shield,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Radio,
  Cpu,
  Layers,
  Filter,
  Eye,
  Maximize2,
  Minimize2,
  Play,
  Pause,
  ArrowRight,
  TrendingUp,
  RefreshCw,
  GitBranch,
  Database,
  Lock,
  Zap,
  Sliders,
  ChevronRight,
  Info,
  X,
  FileText,
} from 'lucide-react';
import { Isometric3DScene, Agent3DData, INITIAL_AGENTS_DATA } from './Isometric3DScene';
import {
  evaluateTrustDecision,
  DEMO_SCENARIOS,
  TrustDecisionResult,
  TrustEvaluationInput,
} from '../../lib/policyEngine';
import { div } from 'three/tsl';

export interface SecurityEvent {
  id: string;
  timestamp: string;
  title: string;
  domain: 'NETWORK' | 'IDENTITY' | 'DEVICE' | 'BEHAVIOUR' | 'TRANSACTION' | 'THREAT_INTEL';
  agentId: string;
  evaluation: TrustDecisionResult;
  details: string;
  entityId: string;
}

// Initial events generated with the authoritative Policy Engine
const INITIAL_EVENTS: SecurityEvent[] = [
  {
    id: 'EV-9021',
    timestamp: '19:48:09',
    title: 'Suspicious login detected',
    domain: 'IDENTITY',
    agentId: 'agent-identity',
    evaluation: evaluateTrustDecision({
      riskScore: 72,
      confidence: 91,
      uncertainty: 9,
      contextualFlags: { identityAnomaly: true },
    }),
    details: 'Unrecognized IP (Frankfurt, DE) vs expected baseline (Tokyo, JP)',
    entityId: 'usr_enterprise_882',
  },
  {
    id: 'EV-9020',
    timestamp: '19:48:06',
    title: 'Device posture anomaly detected',
    domain: 'DEVICE',
    agentId: 'agent-device',
    evaluation: evaluateTrustDecision({
      riskScore: 58,
      confidence: 94,
      uncertainty: 6,
      contextualFlags: { newDevice: true },
    }),
    details: 'Hardware fingerprint mismatch on macOS endpoint',
    entityId: 'dev_mac_4091',
  },
  {
    id: 'EV-9019',
    timestamp: '19:48:03',
    title: 'Routine high-value transaction',
    domain: 'TRANSACTION',
    agentId: 'agent-transaction',
    evaluation: evaluateTrustDecision({
      riskScore: 18,
      confidence: 98,
      uncertainty: 2,
    }),
    details: 'Wire transfer $4,250 within normal monthly payload range',
    entityId: 'txn_9921',
  },
  {
    id: 'EV-9018',
    timestamp: '19:47:58',
    title: 'Critical intrusion payload correlated',
    domain: 'NETWORK',
    agentId: 'agent-network',
    evaluation: evaluateTrustDecision({
      riskScore: 94,
      confidence: 98,
      uncertainty: 2,
      contextualFlags: { criticalNetworkAttack: true, criticalThreatIntel: true },
    }),
    details: 'Syn flood payload matching known CVE-2026-1082 signature',
    entityId: 'gw_edge_01',
  },
  {
    id: 'EV-9017',
    timestamp: '19:47:50',
    title: 'Identity MFA verified',
    domain: 'IDENTITY',
    agentId: 'agent-identity',
    evaluation: evaluateTrustDecision({
      riskScore: 12,
      confidence: 99,
      uncertainty: 1,
    }),
    details: '2FA push prompt successfully acknowledged by owner',
    entityId: 'usr_enterprise_882',
  },
  {
    id: 'EV-9016',
    timestamp: '19:47:42',
    title: 'User behaviour anomaly flagged',
    domain: 'BEHAVIOUR',
    agentId: 'agent-uba',
    evaluation: evaluateTrustDecision({
      riskScore: 81,
      confidence: 92,
      uncertainty: 8,
    }),
    details: '+38% burst in sensitive file read operations outside business hours',
    entityId: 'usr_admin_04',
  },
];

export const CyberTrustOrchestratorDashboard: React.FC = () => {
  const [agents, setAgents] = useState<Agent3DData[]>(INITIAL_AGENTS_DATA);
  const [selectedAgent, setSelectedAgent] = useState<Agent3DData | null>(INITIAL_AGENTS_DATA[1]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('SCENARIO_2');

  // Authoritative Policy Result State
  const [trustResult, setTrustResult] = useState<TrustDecisionResult>(() =>
    evaluateTrustDecision(DEMO_SCENARIOS[1].input)
  );

  // Inspection Modal State
  const [isInspectModalOpen, setIsInspectModalOpen] = useState<boolean>(false);

  // Live Security Events Stream State
  const [events, setEvents] = useState<SecurityEvent[]>(INITIAL_EVENTS);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent>(INITIAL_EVENTS[0]);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [isStreamLive, setIsStreamLive] = useState<boolean>(true);

  // 3D Scene Settings
  const [cameraPreset, setCameraPreset] = useState<'ISO_45' | 'TOP_DOWN' | 'FRONT' | 'FREE'>('ISO_45');
  const [showDataStreams, setShowDataStreams] = useState<boolean>(true);
  const [showGrid, setShowGrid] = useState<boolean>(true);

  // Handle Scenario Switching with the Central Policy Engine
  const handleSelectScenario = (scenarioId: string) => {
    setSelectedScenarioId(scenarioId);
    const scenario = DEMO_SCENARIOS.find((s) => s.id === scenarioId);
    if (scenario) {
      const evaluation = evaluateTrustDecision(scenario.input);
      setTrustResult(evaluation);

      // Construct matching live event for scenario
      const scenarioEv: SecurityEvent = {
        id: `EV-${scenario.id}`,
        timestamp: new Date().toLocaleTimeString(),
        title: scenario.name,
        domain: scenario.input.contextualFlags?.newDevice ? 'DEVICE' : 'IDENTITY',
        agentId: scenario.input.contextualFlags?.newDevice ? 'agent-device' : 'agent-identity',
        evaluation,
        details: evaluation.reason,
        entityId: 'ent_demo_eval',
      };
      setSelectedEvent(scenarioEv);
    }
  };

  // Dynamic Event Stream Simulator using the Policy Engine
  useEffect(() => {
    if (!isStreamLive) return;

    const interval = setInterval(() => {
      const agentList = INITIAL_AGENTS_DATA;
      const randomAgent = agentList[Math.floor(Math.random() * agentList.length)];
      const now = new Date();
      const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

      // Pick a risk score logically
      const simulatedRisk = Math.floor(10 + Math.random() * 85);
      const isOverride = Math.random() > 0.75;
      const flags = isOverride
        ? { newDevice: Math.random() > 0.5, identityAnomaly: Math.random() > 0.5 }
        : {};

      const evaluation = evaluateTrustDecision({
        riskScore: simulatedRisk,
        confidence: Math.floor(88 + Math.random() * 10),
        contextualFlags: flags,
      });

      const newEv: SecurityEvent = {
        id: `EV-${Math.floor(1000 + Math.random() * 9000)}`,
        timestamp: timeStr,
        title: `${randomAgent.name} telemetry evaluated`,
        domain: randomAgent.type,
        agentId: randomAgent.id,
        evaluation,
        details: `Telemetry evaluated by Policy Engine: ${evaluation.reason}`,
        entityId: `ent_${Math.floor(100 + Math.random() * 900)}`,
      };

      setEvents((prev) => [newEv, ...prev.slice(0, 24)]);
    }, 3500);

    return () => clearInterval(interval);
  }, [isStreamLive]);

  // Handle Clicking a Live Event -> Pass through Policy Engine & focus camera
  const handleSelectEvent = (ev: SecurityEvent) => {
    setSelectedEvent(ev);
    setTrustResult(ev.evaluation);

    const matchingAgent = agents.find((a) => a.id === ev.agentId || a.type === ev.domain);
    if (matchingAgent) {
      setSelectedAgent(matchingAgent);
    }
  };

  const filteredEvents = events.filter((e) => severityFilter === 'ALL' || e.evaluation.severity === severityFilter);

  const getSeverityBadgeClass = (sev: TrustDecisionResult['severity']) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      case 'HIGH':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40';
      case 'LOW':
        return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
    }
  };

  return (
    <div className="w-full min-h-full bg-[#050811] text-slate-100 font-sans flex flex-col select-none overflow-x-hidden flex-1">
      {/* ============================================================ */}
      {/* HEADER BANNER */}
      {/* ============================================================ */}
      <header className="bg-[#090e1a]/90 border-b border-slate-800/80 px-6 py-2.5 flex-shrink-0 flex flex-col lg:flex-row items-center justify-between gap-4 backdrop-blur-md z-30">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-gradient-to-br from-cyan-500/20 to-indigo-500/20 border border-cyan-500/40 rounded-xl text-cyan-400 shadow-lg shadow-cyan-500/10 flex items-center justify-center">
            <Shield className="w-7 h-7 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-black tracking-wider text-white uppercase bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-cyan-400">
                HACTM — AI TRUST ORCHESTRATOR
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 uppercase tracking-widest flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                Agents: 6 / 6 Active
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Hierarchical Adaptive Multi-Domain Evidence Fusion & Autonomous Trust Decisioning Engine
            </p>
          </div>
        </div>

        {/* Quick Demo Scenario Selector */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="bg-[#050914] p-1.5 rounded-xl border border-slate-800 flex items-center gap-2">
            <span className="text-[10px] font-mono text-cyan-400 px-2 uppercase font-bold flex items-center gap-1">
              <Sliders size={12} /> POLICY SCENARIO:
            </span>
            <select
              value={selectedScenarioId}
              onChange={(e) => handleSelectScenario(e.target.value)}
              className="bg-[#090e1a] text-slate-200 border border-slate-700 text-xs font-mono rounded-lg px-2.5 py-1 focus:outline-none focus:border-cyan-500 cursor-pointer"
            >
              {DEMO_SCENARIOS.map((sc) => (
                <option key={sc.id} value={sc.id}>
                  {sc.label} — {sc.name}
                </option>
              ))}
            </select>
          </div>

          {/* 3D Camera Controls */}
          <div className="bg-[#050914] p-1 rounded-xl border border-slate-800 flex items-center gap-1">
            <button
              onClick={() => setCameraPreset('ISO_45')}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-mono transition-all ${cameraPreset === 'ISO_45' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400'
                }`}
              title="Isometric 45° View"
            >
              3D ISO 45°
            </button>
            <button
              onClick={() => setCameraPreset('TOP_DOWN')}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-mono transition-all ${cameraPreset === 'TOP_DOWN' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400'
                }`}
              title="Top-Down Tactical Map View"
            >
              Tactical
            </button>
          </div>
        </div>
      </header>

      {/* ============================================================ */}
      {/* SECTION 1: FULL-SCREEN OPERATIONAL COMMAND CENTER */}
      {/* ============================================================ */}
      <section className="operational-section h-[calc(100vh-140px)] min-h-[550px] w-full max-w-full flex-shrink-0 grid grid-cols-1 lg:grid-cols-[minmax(240px,0.72fr)_minmax(0,2.5fr)_minmax(260px,0.78fr)] gap-3 p-4 box-border min-w-0 overflow-hidden">
        {/* ---------------------------------------------------------- */}
        {/* LEFT PANEL: LIVE SECURITY EVENTS */}
        {/* ---------------------------------------------------------- */}
        <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-3 flex flex-col h-full min-h-0 shadow-2xl backdrop-blur-md min-w-0 overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-3">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
              <h2 className="text-xs font-mono font-bold text-white uppercase tracking-wider">LIVE SECURITY EVENTS</h2>
            </div>
            <button
              onClick={() => setIsStreamLive(!isStreamLive)}
              className={`p-1.5 rounded-lg border text-xs font-mono flex items-center gap-1 transition-all ${isStreamLive ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' : 'bg-slate-800 border-slate-700 text-slate-400'
                }`}
            >
              {isStreamLive ? <Pause size={12} /> : <Play size={12} />}
              <span>{isStreamLive ? 'LIVE' : 'PAUSED'}</span>
            </button>
          </div>

          {/* Severity Filter Tabs */}
          <div className="flex items-center justify-between gap-1 mb-3 text-[10px] font-mono">
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-2 py-1 rounded-md font-semibold transition-all ${severityFilter === sev
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
              >
                {sev}
              </button>
            ))}
          </div>

          {/* Event Stream List */}
          <div className="flex-1 overflow-y-auto space-y-2 pr-1 hactm-sidebar-scroll">
            {filteredEvents.map((ev) => {
              const isSelected = selectedEvent.id === ev.id;
              return (
                <div
                  key={ev.id}
                  onClick={() => handleSelectEvent(ev)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer group ${isSelected
                    ? 'bg-[#101b2d] border-cyan-500/50 shadow-md shadow-cyan-500/10'
                    : 'bg-[#050914]/80 border-slate-800/80 hover:border-slate-700 hover:bg-[#0c1322]'
                    }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-mono text-slate-400">{ev.timestamp}</span>
                    <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold border ${getSeverityBadgeClass(ev.evaluation.severity)}`}>
                      {ev.evaluation.severity}
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-slate-200 group-hover:text-cyan-400 transition-colors line-clamp-1">
                    {ev.title}
                  </h3>

                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-tight">{ev.details}</p>

                  <div className="mt-2 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono">
                    <span className="text-slate-400">
                      Domain: <strong className="text-slate-200">{ev.domain}</strong>
                    </span>
                    <span className="text-cyan-400 font-bold">
                      Risk: {ev.evaluation.riskScore}/100 → <strong className={ev.evaluation.decision === 'ALLOW' ? 'text-emerald-400' : ev.evaluation.decision === 'VERIFY' ? 'text-amber-400' : 'text-rose-400'}>{ev.evaluation.decision}</strong>
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* ---------------------------------------------------------- */}
        {/* CENTER PANEL: ISOMETRIC 3D ENVIRONMENT & CORE (Col span 6) */}
        {/* ---------------------------------------------------------- */}
        <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl relative overflow-hidden h-full min-h-0 shadow-2xl flex flex-col min-w-0">
          {/* Top HUD Core Info Display Bar */}
          <div className="absolute top-4 left-4 right-4 z-10 flex items-center justify-between gap-4 pointer-events-none">
            {/* Orchestrator Metrics Badge */}
            <div className="bg-[#050914]/90 border border-cyan-500/40 p-3 rounded-2xl backdrop-blur-md shadow-2xl flex items-center gap-5 pointer-events-auto">
              <div>
                <span className="text-[9px] font-mono text-slate-400 uppercase tracking-widest block">RISK SCORE</span>
                <span className="text-2xl font-black text-white font-mono">{trustResult.riskScore}</span>
              </div>
              <div className="h-8 w-px bg-slate-800" />
              <div>
                <span className="text-[9px] font-mono text-slate-400 uppercase tracking-widest block">CONFIDENCE</span>
                <span className="text-xl font-bold text-emerald-400 font-mono">{trustResult.confidence}%</span>
              </div>
              <div className="h-8 w-px bg-slate-800" />
              <div>
                <span className="text-[9px] font-mono text-slate-400 uppercase tracking-widest block">UNCERTAINTY</span>
                <span className="text-xl font-bold text-amber-400 font-mono">{trustResult.uncertainty}%</span>
              </div>
            </div>

            {/* Current Decision Pill */}
            <div className="bg-[#050914]/90 border border-slate-800 p-3 rounded-2xl backdrop-blur-md shadow-2xl flex items-center gap-3 pointer-events-auto">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">POLICY DECISION:</span>
              <span
                className={`px-4 py-1.5 rounded-xl font-mono font-black text-sm tracking-wider uppercase shadow-lg border transition-all ${trustResult.decision === 'ALLOW'
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/60 shadow-emerald-500/20 animate-pulse'
                  : trustResult.decision === 'VERIFY'
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/60 shadow-amber-500/20 animate-pulse'
                    : 'bg-rose-500/20 text-rose-300 border-rose-500/60 shadow-rose-500/20 animate-pulse'
                  }`}
              >
                {trustResult.decision === 'ALLOW' && '🟢 ALLOW'}
                {trustResult.decision === 'VERIFY' && '🟡 VERIFY'}
                {trustResult.decision === 'BLOCK' && '🔴 BLOCK'}
              </span>
            </div>
          </div>

          {/* 3D Scene Viewport */}
          <div className="flex-1 w-full h-full min-w-0 min-h-0 relative">
            <Isometric3DScene
              agentsData={agents}
              selectedAgentId={selectedAgent?.id}
              selectedDecision={trustResult.decision}
              onSelectAgent={(agent) => {
                setSelectedAgent(agent);
                setIsInspectModalOpen(true);
              }}
              cameraPreset={cameraPreset}
              showDataStreams={showDataStreams}
              showGrid={showGrid}
            />
          </div>

          {/* Bottom Evidence Fusion Pipeline Indicator Overlay */}
          <div className="absolute bottom-3 left-3 right-3 z-10 bg-[#050914]/90 border border-slate-800/80 p-2.5 rounded-xl backdrop-blur-md shadow-2xl pointer-events-auto max-w-[calc(100%-24px)] box-border">
            <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              <div className="flex items-center gap-1.5">
                <GitBranch className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                <span className="font-bold text-slate-200 truncate">EVIDENCE FUSION & CONTEXTUAL REASONING PIPELINE</span>
              </div>
              <span className="text-cyan-400 font-semibold flex-shrink-0">6 / 6 AGENTS CONVERGING</span>
            </div>

            <div className="flex items-center justify-between gap-1 text-[9px] font-mono overflow-x-auto hactm-sidebar-scroll pb-0.5">
              <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-400 font-bold whitespace-nowrap">Network</span>
              <span className="text-slate-600 flex-shrink-0">+</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-purple-400 font-bold whitespace-nowrap">Identity</span>
              <span className="text-slate-600 flex-shrink-0">+</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-emerald-400 font-bold whitespace-nowrap">Device</span>
              <span className="text-slate-600 flex-shrink-0">+</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-amber-400 font-bold whitespace-nowrap">Behaviour</span>
              <span className="text-slate-600 flex-shrink-0">+</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-rose-400 font-bold whitespace-nowrap">Transaction</span>
              <span className="text-slate-600 flex-shrink-0">+</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-sky-400 font-bold whitespace-nowrap">Threat Intel</span>
              <span className="text-slate-600 flex-shrink-0">→</span>
              <span className="px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800 font-bold whitespace-nowrap">
                EVIDENCE FUSION
              </span>
              <span className="text-slate-600 flex-shrink-0">→</span>
              <span className="px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800 font-bold whitespace-nowrap">
                CONTEXT REASONING
              </span>
            </div>
          </div>
        </div>

        {/* ---------------------------------------------------------- */}
        {/* RIGHT PANEL: SYSTEM STATUS & CONTROL PANEL (Col span 3) */}
        {/* ---------------------------------------------------------- */}
        <div className="bg-[#090e1a]/90 border border-slate-800/80 rounded-2xl p-4 flex flex-col h-full min-h-0 shadow-2xl backdrop-blur-md min-w-0 overflow-hidden system-status-panel">
          {/* Fixed System Status Header */}
          <div className="border-b border-slate-800/80 pb-3 flex-shrink-0 mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <h2 className="text-xs font-mono font-bold text-white uppercase tracking-wider">SYSTEM STATUS</h2>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-bold">
              REALTIME
            </span>
          </div>

          {/* Internal Scrollable Content Container */}
          <div className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden space-y-4 pr-1.5 system-status-scroll">
            {/* AGENT METRICS HUD GRID */}
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-[#050914] p-2.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-colors">
                <span className="text-slate-400 text-[10px] block">AGENTS ONLINE</span>
                <span className="text-emerald-400 font-bold text-sm">6 / 6 Operational</span>
              </div>
              <div className="bg-[#050914] p-2.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-colors">
                <span className="text-slate-400 text-[10px] block">EVENTS / SEC</span>
                <span className="text-cyan-400 font-bold text-sm">1,284 ev/s</span>
              </div>
              <div className="bg-[#050914] p-2.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-colors">
                <span className="text-slate-400 text-[10px] block">THREATS DETECTED</span>
                <span className="text-amber-400 font-bold text-sm">17 Active</span>
              </div>
              <div className="bg-[#050914] p-2.5 rounded-xl border border-slate-800 hover:border-slate-700 transition-colors">
                <span className="text-slate-400 text-[10px] block">ACTIVE INCIDENTS</span>
                <span className="text-rose-400 font-bold text-sm">3 High Priority</span>
              </div>
            </div>

            {/* RISK DISTRIBUTION */}
            <div className="border-b border-slate-800/80 pb-3">
              <h3 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-2.5">
                RISK DISTRIBUTION
              </h3>

              {/* Progress Bar */}
              <div className="w-full h-3 bg-[#050914] rounded-full overflow-hidden flex border border-slate-800 mb-2">
                <div style={{ width: '72%' }} className="bg-emerald-500 h-full" title="Low: 72%" />
                <div style={{ width: '19%' }} className="bg-amber-500 h-full" title="Medium: 19%" />
                <div style={{ width: '7%' }} className="bg-rose-500 h-full" title="High: 7%" />
                <div style={{ width: '2%' }} className="bg-purple-500 h-full" title="Critical: 2%" />
              </div>

              <div className="grid grid-cols-4 gap-1 text-[10px] font-mono text-center">
                <div className="bg-[#050914] p-1.5 rounded border border-slate-800">
                  <span className="text-emerald-400 block font-bold">72%</span>
                  <span className="text-slate-400">Low</span>
                </div>
                <div className="bg-[#050914] p-1.5 rounded border border-slate-800">
                  <span className="text-amber-400 block font-bold">19%</span>
                  <span className="text-slate-400">Medium</span>
                </div>
                <div className="bg-[#050914] p-1.5 rounded border border-slate-800">
                  <span className="text-rose-400 block font-bold">7%</span>
                  <span className="text-slate-400">High</span>
                </div>
                <div className="bg-[#050914] p-1.5 rounded border border-slate-800">
                  <span className="text-purple-400 block font-bold">2%</span>
                  <span className="text-slate-400">Critical</span>
                </div>
              </div>
            </div>

            {/* RECENT POLICY DECISIONS */}
            <div className="border-b border-slate-800/80 pb-3">
              <h3 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-2">
                RECENT POLICY DECISIONS
              </h3>

              <div className="space-y-1.5 text-xs font-mono">
                <div className="p-2 rounded-lg bg-[#050914] border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-300">Transaction #TX-8291</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                    ALLOW
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-[#050914] border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-300">Login #ID-4921</span>
                  <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-bold">
                    VERIFY
                  </span>
                </div>
                <div className="p-2 rounded-lg bg-[#050914] border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-300">Device #DV-1029</span>
                  <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px] font-bold">
                    BLOCK
                  </span>
                </div>
              </div>
            </div>

            {/* SELECTED AGENT INSPECTION CALLOUT CARD */}
            <div>
              <h3 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-2">
                AGENT INSPECTION DETAILS
              </h3>
              {selectedAgent ? (
                <div
                  onClick={() => setIsInspectModalOpen(true)}
                  className="p-3 bg-[#050914] border border-cyan-500/40 hover:border-cyan-400 rounded-xl space-y-2 text-xs cursor-pointer transition-all group"
                >
                  <div className="flex items-center justify-between border-b border-slate-800 pb-1.5">
                    <span className="font-bold text-white flex items-center gap-1.5 group-hover:text-cyan-400 transition-colors">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: selectedAgent.color }} />
                      {selectedAgent.name}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 font-bold">
                      INSPECT DETAILED
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-2">{selectedAgent.description}</p>
                  <div className="flex justify-between text-[10px] font-mono text-slate-300 pt-1">
                    <span>Model: {selectedAgent.modelVersion}</span>
                    <span className="text-cyan-400 font-bold">Conf: {selectedAgent.confidence}%</span>
                  </div>
                </div>
              ) : (
                <div className="text-center p-3 text-xs text-slate-400 font-mono bg-[#050914] rounded-xl border border-slate-800">
                  Click any agent building in 3D scene to inspect details
                </div>
              )}
            </div>

            {/* ADDITIONAL SYSTEM INFORMATION */}
            <div className="pt-1">
              <h3 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider mb-2">
                ADDITIONAL SYSTEM INFORMATION
              </h3>
              <div className="space-y-2 text-[11px] font-mono">
                <div className="bg-[#050914] p-2.5 rounded-xl border border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Policy Engine Rule Version</span>
                    <span className="text-cyan-400 font-bold">v3.4.1-hybrid</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Mesh Telemetry Latency</span>
                    <span className="text-emerald-400 font-bold">4.2 ms</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Zero-Trust Encryption</span>
                    <span className="text-emerald-400 font-bold">mTLS Active</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Node Sync Status</span>
                    <span className="text-cyan-400 font-bold">100% Synced</span>
                  </div>
                </div>

                <div className="bg-[#050914] p-2.5 rounded-xl border border-slate-800 flex items-center justify-between">
                  <span className="text-slate-400">Consensus Engine</span>
                  <span className="text-purple-400 font-bold">Byzantine Fault Tolerant</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* SECTION 2: POLICY DECISION & CONTEXTUAL REASONING (BELOW SCROLL) */}
      {/* ============================================================ */}
      <section className="policy-decision-section w-full min-h-[320px] bg-[#090e1a]/95 border-t border-slate-800/80 p-5 mx-4 my-6 rounded-2xl shadow-2xl backdrop-blur-md flex-shrink-0 box-border max-w-[calc(100%-32px)]">
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(300px,0.8fr)_minmax(600px,1.7fr)] gap-5 items-start">
          {/* Decision Status Title & Action */}
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div
                className={`p-2.5 rounded-xl border ${trustResult.decision === 'ALLOW'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : trustResult.decision === 'VERIFY'
                    ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  }`}
              >
                {trustResult.decision === 'ALLOW' && <CheckCircle2 className="w-7 h-7" />}
                {trustResult.decision === 'VERIFY' && <AlertTriangle className="w-7 h-7" />}
                {trustResult.decision === 'BLOCK' && <XCircle className="w-7 h-7" />}
              </div>

              <div>
                <span className="text-[10px] font-mono text-slate-400 block uppercase tracking-wider">HACTM POLICY DECISION</span>
                <h2
                  className={`text-xl font-black font-mono tracking-wide ${trustResult.decision === 'ALLOW'
                    ? 'text-emerald-400'
                    : trustResult.decision === 'VERIFY'
                      ? 'text-amber-400'
                      : 'text-rose-400'
                    }`}
                >
                  DECISION: {trustResult.decision}
                </h2>
              </div>
            </div>

            {/* Contextual Override Indicator if present */}
            {trustResult.hasOverride && (
              <div className="p-2.5 bg-amber-500/10 border border-amber-500/40 rounded-xl text-xs font-mono text-amber-300 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <span>
                  <strong>OVERRIDE:</strong> {trustResult.overrideReason}
                </span>
              </div>
            )}

            <div className="p-3 bg-[#050914] border border-slate-800 rounded-xl space-y-1">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block">
                RECOMMENDED ACTION
              </span>
              <p className="text-xs font-bold text-white flex items-center gap-2">
                <ArrowRight className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                {trustResult.recommendedAction}
              </p>
            </div>
          </div>

          {/* Contextual Reasoning WHY Breakdown */}
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
                <Info className="w-4 h-4" /> WHY WAS THIS DECISION REACHED? (CONTEXTUAL REASONING EVIDENCE)
              </h3>
              <span className="text-[10px] font-mono text-slate-400">Evaluated event: {selectedEvent.id}</span>
            </div>

            {/* Dynamic Reason Text from Policy Engine */}
            <p className="text-xs text-slate-300 font-mono bg-[#050914] p-3 rounded-xl border border-slate-800/80 leading-relaxed">
              <strong className="text-cyan-400">POLICY REASONING:</strong> {trustResult.reason}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 text-xs font-mono">
              {trustResult.whyBreakdown.map((item, idx) => (
                <div key={idx} className="p-2.5 bg-[#050914] border border-slate-800 rounded-xl space-y-1">
                  <span className="text-slate-400 text-[10px] block">{item.title}</span>
                  <span
                    className={`font-bold block text-xs ${item.badgeColor === 'emerald'
                      ? 'text-emerald-400'
                      : item.badgeColor === 'amber'
                        ? 'text-amber-400'
                        : item.badgeColor === 'rose'
                          ? 'text-rose-400'
                          : 'text-cyan-400'
                      }`}
                  >
                    {item.badge}
                  </span>
                  <span className="text-slate-400 text-[10px] block truncate">{item.subtitle}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* AGENT DETAILED INSPECTION MODAL */}
      {/* ============================================================ */}
      {isInspectModalOpen && selectedAgent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200">
          <div className="bg-[#090e1a] border border-cyan-500/40 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl relative">
            <button
              onClick={() => setIsInspectModalOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            >
              <X size={16} />
            </button>

            <div className="flex items-center gap-3 border-b border-slate-800 pb-3">
              <span className="w-3.5 h-3.5 rounded-full animate-pulse" style={{ backgroundColor: selectedAgent.color }} />
              <div>
                <h3 className="text-lg font-bold text-white uppercase tracking-wider">{selectedAgent.name}</h3>
                <span className="text-xs font-mono text-cyan-400">{selectedAgent.modelVersion} ● Status: ONLINE</span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">{selectedAgent.description}</p>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 bg-[#050914] border border-slate-800 rounded-xl">
                <span className="text-slate-400 text-[10px] block">THROUGHPUT</span>
                <span className="text-cyan-400 font-bold text-base">{selectedAgent.eventsPerSec} ev/sec</span>
              </div>
              <div className="p-3 bg-[#050914] border border-slate-800 rounded-xl">
                <span className="text-slate-400 text-[10px] block">RISK SCORE</span>
                <span className={selectedAgent.riskScore > 60 ? 'text-amber-400 font-bold text-base' : 'text-emerald-400 font-bold text-base'}>
                  {selectedAgent.riskScore}/100 ({selectedAgent.riskScore > 60 ? 'HIGH' : 'LOW'})
                </span>
              </div>
              <div className="p-3 bg-[#050914] border border-slate-800 rounded-xl">
                <span className="text-slate-400 text-[10px] block">CONFIDENCE</span>
                <span className="text-white font-bold text-base">{selectedAgent.confidence}%</span>
              </div>
              <div className="p-3 bg-[#050914] border border-slate-800 rounded-xl">
                <span className="text-slate-400 text-[10px] block">LAST EVENT</span>
                <span className="text-purple-400 font-bold text-base">{selectedAgent.lastEvent}</span>
              </div>
            </div>

            {/* Evidence List */}
            <div className="space-y-2">
              <h4 className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <FileText size={14} className="text-cyan-400" /> Correlated Evidence Telemetry
              </h4>
              <div className="space-y-1.5">
                {selectedAgent.evidenceList.map((item, idx) => (
                  <div key={idx} className="p-2.5 bg-[#050914] border border-slate-800/80 rounded-lg text-xs font-mono text-slate-300 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 flex-shrink-0" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Decision Recommendation */}
            <div className="p-3 bg-[#050914] border border-slate-800 rounded-xl flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400">Agent Decision State:</span>
              <span className="px-3 py-1 rounded bg-amber-500/10 text-amber-300 border border-amber-500/40 font-bold uppercase">
                {trustResult.decision}
              </span>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setIsInspectModalOpen(false)}
                className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs rounded-xl transition-all"
              >
                Close Inspection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
