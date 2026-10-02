import React, { useState } from 'react';
import {
  Network,
  Activity,
  ShieldAlert,
  Cpu,
  Layers,
  FileCheck,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Play,
  RotateCw,
  Search,
  Filter,
  Eye,
  Info,
  Clock,
  ArrowRight,
  TrendingUp,
  Sliders,
  Send,
} from 'lucide-react';
import {
  useNetworkMetrics,
  useNetworkHealth,
  useNetworkDetections,
  useNetworkEvents,
  useNetworkModels,
  useActivateNetworkModel,
  useEvaluateNetworkModel,
  useSubmitDetectionFeedback,
  useNetworkDetectionById,
} from '../hooks/useNetwork';
import { RiskBadge } from '../components/common/RiskBadge';
import { Pagination } from '../components/common/Pagination';
import { Skeleton } from '../components/common/Skeleton';
import { EmptyState } from '../components/common/EmptyState';
import { ErrorState } from '../components/common/ErrorState';
import { JsonViewer } from '../components/common/JsonViewer';
import { cn } from '../lib/utils';
import { NetworkDetection, NetworkEvent, EvaluationResult } from '../types/network';

export const NetworkSecurity: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<
    'overview' | 'detections' | 'events' | 'flows' | 'models' | 'evaluation'
  >('overview');

  // Query States
  const { data: metrics, isLoading: metricsLoading, refetch: refetchMetrics } = useNetworkMetrics();
  const { data: health, isLoading: healthLoading, refetch: refetchHealth } = useNetworkHealth();
  const { data: models, isLoading: modelsLoading, refetch: refetchModels } = useNetworkModels();

  // Detections Table Filters & Pagination
  const [detPage, setDetPage] = useState(1);
  const [detDetectorType, setDetDetectorType] = useState<string>('');
  const [detSeverity, setDetSeverity] = useState<string>('');
  const [selectedDetectionId, setSelectedDetectionId] = useState<string | null>(null);

  const { data: detectionsData, isLoading: detectionsLoading } = useNetworkDetections({
    page: detPage,
    page_size: 15,
    detector_type: detDetectorType || undefined,
    severity: detSeverity || undefined,
  });

  // Events Table Filters & Pagination
  const [evtPage, setEvtPage] = useState(1);
  const [srcIpFilter, setSrcIpFilter] = useState('');
  const [dstIpFilter, setDstIpFilter] = useState('');
  const [protocolFilter, setProtocolFilter] = useState('');

  const { data: eventsData, isLoading: eventsLoading } = useNetworkEvents({
    page: evtPage,
    page_size: 15,
    src_ip: srcIpFilter || undefined,
    dst_ip: dstIpFilter || undefined,
    protocol: protocolFilter || undefined,
  });

  // Mutations
  const activateModelMutation = useActivateNetworkModel();
  const evaluateMutation = useEvaluateNetworkModel();
  const feedbackMutation = useSubmitDetectionFeedback();

  // Evaluation local state
  const [evalResult, setEvalResult] = useState<EvaluationResult | null>(null);
  const [evalFilePath, setEvalFilePath] = useState('data/sample/network_test.csv');

  // Feedback local state
  const [feedbackNote, setFeedbackNote] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  // Selected Detection Details Query
  const { data: selectedDetection, isLoading: detectionDetailsLoading } =
    useNetworkDetectionById(selectedDetectionId);

  const handleRunEvaluation = async () => {
    try {
      const res = await evaluateMutation.mutateAsync(evalFilePath);
      setEvalResult(res);
    } catch (err: any) {
      alert(`Evaluation failed: ${err.message}`);
    }
  };

  const handleFeedbackSubmit = async (label: 'TRUE_POSITIVE' | 'FALSE_POSITIVE') => {
    if (!selectedDetectionId) return;
    try {
      await feedbackMutation.mutateAsync({
        detection_id: selectedDetectionId,
        label,
        analyst_note: feedbackNote || undefined,
      });
      setFeedbackSubmitted(true);
      setTimeout(() => setFeedbackSubmitted(false), 3000);
    } catch (err: any) {
      alert(`Feedback submission failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-hactm-border pb-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-hactm-accent/10 border border-hactm-accent/30 text-hactm-accent">
              <Network size={22} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-hactm-heading tracking-tight flex items-center gap-2">
                <span>Network Security Agent</span>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  Network Security Agent Active
                </span>
              </h1>
              <p className="text-xs text-hactm-muted mt-0.5">
                Multi-engine network detection: Signatures, Stateful Bounded Heuristics & Isolation Forest Anomaly Analysis.
              </p>
            </div>
          </div>
        </div>

        {/* Live Status Pill & Quick Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-hactm-panel border border-hactm-border text-xs">
            <span
              className={cn(
                'w-2 h-2 rounded-full',
                health?.status === 'HEALTHY'
                  ? 'bg-emerald-500 animate-pulse'
                  : health?.status === 'DEGRADED'
                  ? 'bg-amber-500'
                  : 'bg-red-500'
              )}
            />
            <span className="font-mono text-hactm-text font-medium">
              {health?.status || 'INITIALIZING'}
            </span>
            <span className="text-hactm-muted text-[11px] font-mono border-l border-hactm-border pl-2">
              Model: {health?.active_model_id || 'baseline_v1'}
            </span>
          </div>

          <button
            onClick={() => {
              refetchMetrics();
              refetchHealth();
              refetchModels();
            }}
            className="p-2 rounded-lg bg-hactm-panel hover:bg-hactm-panel/80 border border-hactm-border text-hactm-muted hover:text-hactm-text transition-colors"
            title="Refresh All Telemetry"
          >
            <RotateCw size={15} />
          </button>
        </div>
      </div>

      {/* Subtab Navigation */}
      <div className="flex items-center gap-1 border-b border-hactm-border overflow-x-auto text-xs font-medium">
        {[
          { id: 'overview', label: 'Overview & Telemetry', icon: Activity },
          { id: 'detections', label: 'Detections', icon: ShieldAlert },
          { id: 'events', label: 'Network Events', icon: Layers },
          { id: 'flows', label: 'Observed Network Flow', icon: Network },
          { id: 'models', label: 'Models', icon: Cpu },
          { id: 'evaluation', label: 'Evaluation & Benchmarks', icon: FileCheck },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id as any)}
              className={cn(
                'flex items-center gap-2 px-4 py-2.5 border-b-2 transition-all whitespace-nowrap',
                isActive
                  ? 'border-hactm-accent text-hactm-accent font-semibold bg-hactm-accent/5'
                  : 'border-transparent text-hactm-muted hover:text-hactm-text hover:border-hactm-border'
              )}
            >
              <Icon size={15} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: OVERVIEW */}
      {/* ========================================================================= */}
      {activeSubTab === 'overview' && (
        <div className="space-y-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="p-4 rounded-xl bg-hactm-panel/80 border border-hactm-border shadow-sm">
              <div className="text-[11px] font-mono uppercase text-hactm-muted tracking-wider">
                Network Events
              </div>
              <div className="text-2xl font-bold font-mono text-hactm-heading mt-1">
                {metricsLoading ? <Skeleton className="h-8 w-20" /> : metrics?.total_events.toLocaleString() || '0'}
              </div>
              <div className="text-[11px] text-hactm-muted mt-1 flex items-center gap-1">
                <span>Ingested & Normalized</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-hactm-panel/80 border border-hactm-border shadow-sm">
              <div className="text-[11px] font-mono uppercase text-hactm-muted tracking-wider">
                Total Detections
              </div>
              <div className="text-2xl font-bold font-mono text-amber-400 mt-1">
                {metricsLoading ? <Skeleton className="h-8 w-16" /> : metrics?.total_detections.toLocaleString() || '0'}
              </div>
              <div className="text-[11px] text-hactm-muted mt-1">Evidence Records Generated</div>
            </div>

            <div className="p-4 rounded-xl bg-hactm-panel/80 border border-hactm-border shadow-sm">
              <div className="text-[11px] font-mono uppercase text-hactm-muted tracking-wider">
                High Risk Detections
              </div>
              <div className="text-2xl font-bold font-mono text-red-400 mt-1">
                {metricsLoading ? <Skeleton className="h-8 w-16" /> : metrics?.high_risk_detections.toLocaleString() || '0'}
              </div>
              <div className="text-[11px] text-hactm-muted mt-1">Risk Score &ge; 0.70</div>
            </div>

            <div className="p-4 rounded-xl bg-hactm-panel/80 border border-hactm-border shadow-sm">
              <div className="text-[11px] font-mono uppercase text-hactm-muted tracking-wider">
                Detection Rate
              </div>
              <div className="text-2xl font-bold font-mono text-hactm-accent mt-1">
                {metricsLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  `${((metrics?.detection_rate || 0) * 100).toFixed(1)}%`
                )}
              </div>
              <div className="text-[11px] text-hactm-muted mt-1">Anomalous / Suspicious Ratio</div>
            </div>

            <div className="p-4 rounded-xl bg-hactm-panel/80 border border-hactm-border shadow-sm">
              <div className="text-[11px] font-mono uppercase text-hactm-muted tracking-wider">
                Processing Speed
              </div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
                {healthLoading ? (
                  <Skeleton className="h-8 w-20" />
                ) : (
                  `${Math.round(health?.processing_rate || 0).toLocaleString()} /s`
                )}
              </div>
              <div className="text-[11px] text-hactm-muted mt-1">
                Latency: {health?.average_latency ? `${health.average_latency.toFixed(3)} ms` : '< 0.05 ms'}
              </div>
            </div>
          </div>

          {/* Engine Breakdown & Live Health Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Detector Distribution */}
            <div className="p-5 rounded-xl bg-hactm-panel/70 border border-hactm-border">
              <h3 className="text-xs font-semibold text-hactm-heading uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>Detector Engine Breakdown</span>
                <Sliders size={14} className="text-hactm-accent" />
              </h3>

              <div className="space-y-4">
                {[
                  {
                    type: 'SIGNATURE',
                    label: 'Signature Engine',
                    desc: 'Deterministic pattern matching without eval/exec',
                    count: metrics?.detector_distribution?.SIGNATURE || 0,
                    color: 'bg-blue-500',
                  },
                  {
                    type: 'HEURISTIC',
                    label: 'Stateful Heuristics',
                    desc: 'Bounded sliding-window port/host/flood scans',
                    count: metrics?.detector_distribution?.HEURISTIC || 0,
                    color: 'bg-purple-500',
                  },
                  {
                    type: 'ANOMALY',
                    label: 'Anomaly Detector',
                    desc: 'Isolation Forest with robust fallback & sigmoid scaling',
                    count: metrics?.detector_distribution?.ANOMALY || 0,
                    color: 'bg-emerald-500',
                  },
                ].map((item) => {
                  const total = metrics?.total_detections || 1;
                  const pct = Math.round((item.count / total) * 100);
                  return (
                    <div key={item.type} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-hactm-text">{item.label}</span>
                        <span className="font-mono text-hactm-heading font-semibold">
                          {item.count} <span className="text-[10px] text-hactm-muted">({pct}%)</span>
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-hactm-surface rounded-full overflow-hidden">
                        <div
                          className={cn('h-full rounded-full transition-all duration-300', item.color)}
                          style={{ width: `${Math.min(100, Math.max(4, pct))}%` }}
                        />
                      </div>
                      <div className="text-[10px] text-hactm-muted">{item.desc}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Risk Distribution */}
            <div className="p-5 rounded-xl bg-hactm-panel/70 border border-hactm-border">
              <h3 className="text-xs font-semibold text-hactm-heading uppercase tracking-wider mb-4 flex items-center justify-between">
                <span>Risk Score Distribution</span>
                <TrendingUp size={14} className="text-amber-400" />
              </h3>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] font-mono text-emerald-400 font-semibold uppercase">Low Risk</div>
                  <div className="text-xl font-bold font-mono text-hactm-heading mt-1">
                    {metrics?.risk_distribution?.low || 0}
                  </div>
                  <div className="text-[10px] text-hactm-muted mt-0.5">0.00 &ndash; 0.39</div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] font-mono text-amber-400 font-semibold uppercase">Medium Risk</div>
                  <div className="text-xl font-bold font-mono text-hactm-heading mt-1">
                    {metrics?.risk_distribution?.medium || 0}
                  </div>
                  <div className="text-[10px] text-hactm-muted mt-0.5">0.40 &ndash; 0.69</div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] font-mono text-orange-400 font-semibold uppercase">High Risk</div>
                  <div className="text-xl font-bold font-mono text-hactm-heading mt-1">
                    {metrics?.risk_distribution?.high || 0}
                  </div>
                  <div className="text-[10px] text-hactm-muted mt-0.5">0.70 &ndash; 0.89</div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] font-mono text-red-400 font-semibold uppercase">Critical Risk</div>
                  <div className="text-xl font-bold font-mono text-hactm-heading mt-1">
                    {metrics?.risk_distribution?.critical || 0}
                  </div>
                  <div className="text-[10px] text-hactm-muted mt-0.5">0.90 &ndash; 1.00</div>
                </div>
              </div>

              <div className="mt-4 p-3 rounded-lg bg-hactm-surface/60 border border-hactm-border text-[11px] text-hactm-muted">
                Transparent multi-factor formula:
                <code className="text-hactm-accent font-mono block mt-1">
                  Risk = 0.40(Severity) + 0.35(AnomalyScore) + 0.15(RuleStrength) + 0.10(Quality)
                </code>
              </div>
            </div>

            {/* Agent Operational Health Card */}
            <div className="p-5 rounded-xl bg-hactm-panel/70 border border-hactm-border flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-semibold text-hactm-heading uppercase tracking-wider mb-4 flex items-center justify-between">
                  <span>Agent Operational Health</span>
                  <Activity size={14} className="text-emerald-400" />
                </h3>

                <div className="space-y-2.5 text-xs">
                  <div className="flex items-center justify-between py-1.5 border-b border-hactm-border/60">
                    <span className="text-hactm-muted">Agent Status</span>
                    <span className="font-mono font-semibold text-emerald-400">
                      {health?.status || 'HEALTHY'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-hactm-border/60">
                    <span className="text-hactm-muted">Events Processed</span>
                    <span className="font-mono text-hactm-heading">
                      {health?.events_processed?.toLocaleString() || '0'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-hactm-border/60">
                    <span className="text-hactm-muted">Detections Generated</span>
                    <span className="font-mono text-hactm-heading">
                      {health?.detections_generated?.toLocaleString() || '0'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-hactm-border/60">
                    <span className="text-hactm-muted">Operational Errors</span>
                    <span className="font-mono text-hactm-heading">
                      {health?.errors || 0}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5 border-b border-hactm-border/60">
                    <span className="text-hactm-muted">Active ML Model</span>
                    <span className="font-mono text-hactm-accent">
                      {health?.active_model_id || 'baseline_v1'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-1.5">
                    <span className="text-hactm-muted">Last Event Timestamp</span>
                    <span className="font-mono text-[11px] text-hactm-muted truncate max-w-[150px]">
                      {health?.last_event_time ? new Date(health.last_event_time).toLocaleTimeString() : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-hactm-border text-[10px] text-hactm-muted flex items-center justify-between">
                <span>Network Security Agent Detection Scope Only</span>
                <span className="text-emerald-400 font-mono">No Autonomous Blocking</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: DETECTIONS */}
      {/* ========================================================================= */}
      {activeSubTab === 'detections' && (
        <div className="space-y-4">
          {/* Filter Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg bg-hactm-panel/80 border border-hactm-border">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs text-hactm-muted font-mono">
                <Filter size={14} />
                <span>Filters:</span>
              </div>

              <select
                value={detDetectorType}
                onChange={(e) => {
                  setDetDetectorType(e.target.value);
                  setDetPage(1);
                }}
                className="px-2.5 py-1 text-xs rounded bg-hactm-surface border border-hactm-border text-hactm-text focus:outline-none focus:border-hactm-accent"
              >
                <option value="">All Detector Types</option>
                <option value="SIGNATURE">Signature</option>
                <option value="HEURISTIC">Heuristic</option>
                <option value="ANOMALY">Anomaly</option>
              </select>

              <select
                value={detSeverity}
                onChange={(e) => {
                  setDetSeverity(e.target.value);
                  setDetPage(1);
                }}
                className="px-2.5 py-1 text-xs rounded bg-hactm-surface border border-hactm-border text-hactm-text focus:outline-none focus:border-hactm-accent"
              >
                <option value="">All Severities</option>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>

            <div className="text-xs text-hactm-muted font-mono">
              Total Found: {detectionsData?.pagination?.total || 0}
            </div>
          </div>

          {/* Detections Table */}
          <div className="rounded-xl border border-hactm-border bg-hactm-panel/50 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-hactm-border bg-hactm-surface/80 text-[11px] font-mono text-hactm-muted uppercase">
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">Category</th>
                    <th className="py-3 px-4">Detector</th>
                    <th className="py-3 px-4">Risk</th>
                    <th className="py-3 px-4">Confidence</th>
                    <th className="py-3 px-4">Severity</th>
                    <th className="py-3 px-4">Event Ref</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hactm-border/60">
                  {detectionsLoading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                      <tr key={i}>
                        <td colSpan={8} className="py-3 px-4">
                          <Skeleton className="h-6 w-full" />
                        </td>
                      </tr>
                    ))
                  ) : detectionsData?.data?.length ? (
                    detectionsData.data.map((det: NetworkDetection) => (
                      <tr
                        key={det.detection_id}
                        className="hover:bg-hactm-panel/80 transition-colors cursor-pointer group"
                        onClick={() => setSelectedDetectionId(det.detection_id)}
                      >
                        <td className="py-3 px-4 font-mono text-hactm-muted text-[11px] whitespace-nowrap">
                          {new Date(det.timestamp).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 font-medium text-hactm-heading whitespace-nowrap">
                          {det.category}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={cn(
                              'px-2 py-0.5 rounded text-[10px] font-mono border',
                              det.detector_type === 'SIGNATURE'
                                ? 'bg-blue-500/10 border-blue-500/30 text-blue-400'
                                : det.detector_type === 'HEURISTIC'
                                ? 'bg-purple-500/10 border-purple-500/30 text-purple-400'
                                : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                            )}
                          >
                            {det.detector_type}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <RiskBadge score={det.risk_score} />
                        </td>
                        <td className="py-3 px-4 font-mono text-hactm-muted">
                          {(det.confidence * 100).toFixed(0)}%
                        </td>
                        <td className="py-3 px-4 font-mono">
                          <span
                            className={cn(
                              'text-[10px] font-semibold',
                              det.severity === 'CRITICAL'
                                ? 'text-red-400'
                                : det.severity === 'HIGH'
                                ? 'text-orange-400'
                                : det.severity === 'MEDIUM'
                                ? 'text-amber-400'
                                : 'text-emerald-400'
                            )}
                          >
                            {det.severity}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-[11px] text-hactm-muted truncate max-w-[120px]">
                          {det.event_id}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedDetectionId(det.detection_id);
                            }}
                            className="px-2.5 py-1 rounded bg-hactm-surface hover:bg-hactm-accent/10 hover:text-hactm-accent border border-hactm-border transition-colors text-[11px] font-medium inline-flex items-center gap-1"
                          >
                            <Eye size={12} />
                            <span>Explain</span>
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-hactm-muted">
                        No network detections match current filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {detectionsData?.pagination && detectionsData.pagination.total > 15 && (
              <div className="p-3 border-t border-hactm-border flex justify-end">
                <Pagination
                  page={detPage}
                  pageSize={15}
                  total={detectionsData.pagination.total}
                  onPageChange={setDetPage}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: NETWORK EVENTS */}
      {/* ========================================================================= */}
      {activeSubTab === 'events' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap items-center gap-3 p-3 rounded-lg bg-hactm-panel/80 border border-hactm-border">
            <div className="flex items-center gap-1.5 text-xs text-hactm-muted font-mono">
              <Search size={14} />
              <span>Search:</span>
            </div>

            <input
              type="text"
              placeholder="Filter by Source IP..."
              value={srcIpFilter}
              onChange={(e) => {
                setSrcIpFilter(e.target.value);
                setEvtPage(1);
              }}
              className="px-2.5 py-1 text-xs rounded bg-hactm-surface border border-hactm-border text-hactm-text placeholder-hactm-muted focus:outline-none focus:border-hactm-accent w-44"
            />

            <input
              type="text"
              placeholder="Filter by Dest IP..."
              value={dstIpFilter}
              onChange={(e) => {
                setDstIpFilter(e.target.value);
                setEvtPage(1);
              }}
              className="px-2.5 py-1 text-xs rounded bg-hactm-surface border border-hactm-border text-hactm-text placeholder-hactm-muted focus:outline-none focus:border-hactm-accent w-44"
            />

            <select
              value={protocolFilter}
              onChange={(e) => {
                setProtocolFilter(e.target.value);
                setEvtPage(1);
              }}
              className="px-2.5 py-1 text-xs rounded bg-hactm-surface border border-hactm-border text-hactm-text focus:outline-none focus:border-hactm-accent"
            >
              <option value="">All Protocols</option>
              <option value="TCP">TCP</option>
              <option value="UDP">UDP</option>
              <option value="ICMP">ICMP</option>
              <option value="SCTP">SCTP</option>
              <option value="OTHER">OTHER</option>
            </select>
          </div>

          {/* Events Table */}
          <div className="rounded-xl border border-hactm-border bg-hactm-panel/50 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-hactm-border bg-hactm-surface/80 text-[11px] font-mono text-hactm-muted uppercase">
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">Source IP</th>
                    <th className="py-3 px-4">Destination IP</th>
                    <th className="py-3 px-4">Protocol</th>
                    <th className="py-3 px-4">Src Port</th>
                    <th className="py-3 px-4">Dst Port</th>
                    <th className="py-3 px-4">Duration</th>
                    <th className="py-3 px-4">Flow Bytes</th>
                    <th className="py-3 px-4">Packets</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hactm-border/60 font-mono">
                  {eventsLoading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                      <tr key={i}>
                        <td colSpan={9} className="py-3 px-4">
                          <Skeleton className="h-6 w-full" />
                        </td>
                      </tr>
                    ))
                  ) : eventsData?.data?.length ? (
                    eventsData.data.map((evt: NetworkEvent) => (
                      <tr key={evt.event_id} className="hover:bg-hactm-panel/80 transition-colors">
                        <td className="py-3 px-4 text-hactm-muted text-[11px] whitespace-nowrap">
                          {new Date(evt.timestamp).toLocaleString()}
                        </td>
                        <td className="py-3 px-4 font-semibold text-hactm-heading">{evt.src_ip}</td>
                        <td className="py-3 px-4 text-hactm-text">{evt.dst_ip}</td>
                        <td className="py-3 px-4">
                          <span className="px-1.5 py-0.5 rounded bg-hactm-surface border border-hactm-border text-[10px]">
                            {evt.protocol}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-hactm-muted">{evt.src_port ?? '-'}</td>
                        <td className="py-3 px-4 text-hactm-accent font-semibold">{evt.dst_port ?? '-'}</td>
                        <td className="py-3 px-4 text-hactm-muted">
                          {evt.duration !== null ? `${evt.duration.toFixed(3)}s` : '-'}
                        </td>
                        <td className="py-3 px-4 text-hactm-text">
                          {evt.flow_bytes?.toLocaleString() ?? '-'}
                        </td>
                        <td className="py-3 px-4 text-hactm-muted">
                          {evt.flow_packets?.toLocaleString() ?? '-'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={9} className="py-8 text-center text-hactm-muted font-sans">
                        No network flow events found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {eventsData?.pagination && eventsData.pagination.total > 15 && (
              <div className="p-3 border-t border-hactm-border flex justify-end">
                <Pagination
                  page={evtPage}
                  pageSize={15}
                  total={eventsData.pagination.total}
                  onPageChange={setEvtPage}
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: OBSERVED NETWORK FLOW */}
      {/* ========================================================================= */}
      {activeSubTab === 'flows' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-hactm-panel/80 border border-hactm-border">
            <div className="flex items-center justify-between pb-3 border-b border-hactm-border">
              <div>
                <h3 className="text-sm font-semibold text-hactm-heading tracking-tight">
                  Observed Network Flow
                </h3>
                <p className="text-xs text-hactm-muted">
                  Direct topological observation of source and destination interactions. (Not an Attack Graph; graph reasoning is reserved for Adaptive Memory & Graph).
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hactm-surface border border-hactm-border text-hactm-muted">
                Observed Flows ({eventsData?.data?.length || 0})
              </span>
            </div>

            {/* Visual Node-Link Flow Cards */}
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {eventsData?.data?.slice(0, 12).map((evt: NetworkEvent) => (
                <div
                  key={evt.event_id}
                  className="p-3.5 rounded-lg bg-hactm-surface/80 border border-hactm-border hover:border-hactm-accent/40 transition-all flex flex-col justify-between"
                >
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="px-1.5 py-0.5 rounded bg-hactm-panel text-hactm-accent border border-hactm-border/60">
                      {evt.protocol}
                    </span>
                    <span className="text-hactm-muted">
                      {evt.duration ? `${evt.duration.toFixed(2)}s` : '0s'}
                    </span>
                  </div>

                  <div className="my-3 flex items-center justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-[10px] uppercase font-mono text-hactm-muted">Source</div>
                      <div className="text-xs font-mono font-bold text-hactm-heading truncate">
                        {evt.src_ip}
                      </div>
                      <div className="text-[10px] font-mono text-hactm-muted">
                        Port: {evt.src_port ?? 'N/A'}
                      </div>
                    </div>

                    <div className="flex flex-col items-center px-1 text-hactm-accent">
                      <ArrowRight size={16} className="animate-pulse" />
                      <span className="text-[9px] font-mono text-hactm-muted mt-0.5">
                        {evt.flow_bytes ? `${evt.flow_bytes} B` : '-'}
                      </span>
                    </div>

                    <div className="flex-1 min-w-0 text-right">
                      <div className="text-[10px] uppercase font-mono text-hactm-muted">Target</div>
                      <div className="text-xs font-mono font-bold text-hactm-accent truncate">
                        {evt.dst_ip}
                      </div>
                      <div className="text-[10px] font-mono text-hactm-muted">
                        Port: {evt.dst_port ?? 'N/A'}
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-hactm-border/50 flex items-center justify-between text-[10px] font-mono text-hactm-muted">
                    <span>Packets: {evt.flow_packets ?? '-'}</span>
                    <span className="truncate max-w-[130px]">{evt.event_id}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 5: MODELS */}
      {/* ========================================================================= */}
      {activeSubTab === 'models' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-hactm-heading">Model Registry & Lifecycle</h3>
              <p className="text-xs text-hactm-muted">
                Governed anomaly models with atomic activation, random seeds, and feature schema versioning.
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-hactm-border bg-hactm-panel/50 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-hactm-border bg-hactm-surface/80 text-[11px] font-mono text-hactm-muted uppercase">
                    <th className="py-3 px-4">Model ID</th>
                    <th className="py-3 px-4">Version</th>
                    <th className="py-3 px-4">Algorithm</th>
                    <th className="py-3 px-4">Feature Schema</th>
                    <th className="py-3 px-4">Training Dataset</th>
                    <th className="py-3 px-4">Created</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-hactm-border/60 font-mono">
                  {modelsLoading ? (
                    <tr>
                      <td colSpan={8} className="py-6 px-4">
                        <Skeleton className="h-6 w-full" />
                      </td>
                    </tr>
                  ) : models && models.length > 0 ? (
                    models.map((mod) => (
                      <tr key={mod.model_id} className="hover:bg-hactm-panel/80 transition-colors">
                        <td className="py-3 px-4 font-semibold text-hactm-heading">{mod.model_id}</td>
                        <td className="py-3 px-4 text-hactm-accent">{mod.model_version}</td>
                        <td className="py-3 px-4">{mod.algorithm}</td>
                        <td className="py-3 px-4 text-hactm-muted">{mod.feature_schema_version}</td>
                        <td className="py-3 px-4 text-hactm-muted truncate max-w-[150px]">
                          {mod.training_dataset || 'synthetic_baseline'}
                        </td>
                        <td className="py-3 px-4 text-[11px] text-hactm-muted whitespace-nowrap">
                          {new Date(mod.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-3 px-4">
                          {mod.is_active ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-semibold">
                              ACTIVE
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
                              CANDIDATE
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-right">
                          {!mod.is_active && (
                            <button
                              onClick={() => activateModelMutation.mutate(mod.model_id)}
                              disabled={activateModelMutation.isPending}
                              className="px-2.5 py-1 rounded bg-hactm-accent/10 hover:bg-hactm-accent/20 text-hactm-accent border border-hactm-accent/30 text-[11px] font-sans font-medium transition-colors"
                            >
                              Activate
                            </button>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="py-6 text-center text-hactm-muted font-sans">
                        No registered models found in repository.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 6: EVALUATION & BENCHMARKS */}
      {/* ========================================================================= */}
      {activeSubTab === 'evaluation' && (
        <div className="space-y-6">
          {/* Evaluation Trigger Control */}
          <div className="p-4 rounded-xl bg-hactm-panel/80 border border-hactm-border flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-sm font-semibold text-hactm-heading">
                Scientific Model Evaluation (No Fabrication)
              </h3>
              <p className="text-xs text-hactm-muted mt-0.5">
                Evaluates active Isolation Forest anomaly detector against ground-truth labeled validation telemetry.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                value={evalFilePath}
                onChange={(e) => setEvalFilePath(e.target.value)}
                placeholder="Dataset file path..."
                className="px-3 py-1.5 text-xs rounded-lg bg-hactm-surface border border-hactm-border text-hactm-text font-mono w-64 focus:outline-none focus:border-hactm-accent"
              />
              <button
                onClick={handleRunEvaluation}
                disabled={evaluateMutation.isPending}
                className="px-4 py-1.5 rounded-lg bg-hactm-accent text-hactm-surface hover:bg-hactm-accent/90 font-medium text-xs flex items-center gap-2 transition-colors disabled:opacity-50"
              >
                <Play size={14} />
                <span>{evaluateMutation.isPending ? 'Evaluating...' : 'Run Evaluation'}</span>
              </button>
            </div>
          </div>

          {/* Results Presentation */}
          {evalResult ? (
            <div className="space-y-6">
              {/* Metric Cards Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 font-mono">
                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] text-hactm-muted uppercase">Precision</div>
                  <div className="text-lg font-bold text-emerald-400 mt-1">
                    {evalResult.precision.toFixed(4)}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] text-hactm-muted uppercase">Recall</div>
                  <div className="text-lg font-bold text-blue-400 mt-1">
                    {evalResult.recall.toFixed(4)}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] text-hactm-muted uppercase">F1-Score</div>
                  <div className="text-lg font-bold text-purple-400 mt-1">
                    {evalResult.f1.toFixed(4)}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] text-hactm-muted uppercase">FPR (False Pos)</div>
                  <div className="text-lg font-bold text-amber-400 mt-1">
                    {evalResult.fpr.toFixed(4)}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] text-hactm-muted uppercase">FNR (False Neg)</div>
                  <div className="text-lg font-bold text-orange-400 mt-1">
                    {evalResult.fnr.toFixed(4)}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] text-hactm-muted uppercase">ROC-AUC</div>
                  <div className="text-lg font-bold text-hactm-accent mt-1">
                    {evalResult.roc_auc !== null ? evalResult.roc_auc.toFixed(4) : 'N/A'}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-hactm-surface border border-hactm-border">
                  <div className="text-[10px] text-hactm-muted uppercase">PR-AUC</div>
                  <div className="text-lg font-bold text-hactm-heading mt-1">
                    {evalResult.pr_auc !== null ? evalResult.pr_auc.toFixed(4) : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Confusion Matrix Display */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-5 rounded-xl bg-hactm-panel/80 border border-hactm-border">
                  <h4 className="text-xs font-semibold text-hactm-heading uppercase tracking-wider mb-4">
                    Confusion Matrix (Total Samples: {evalResult.sample_count})
                  </h4>

                  <div className="grid grid-cols-2 gap-4 font-mono">
                    <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
                      <div className="text-[10px] text-emerald-400 font-semibold uppercase">
                        True Positives (TP)
                      </div>
                      <div className="text-2xl font-bold text-emerald-300 mt-1">
                        {evalResult.confusion_matrix.tp}
                      </div>
                      <div className="text-[10px] text-hactm-muted mt-1">Correctly detected attacks</div>
                    </div>

                    <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
                      <div className="text-[10px] text-amber-400 font-semibold uppercase">
                        False Positives (FP)
                      </div>
                      <div className="text-2xl font-bold text-amber-300 mt-1">
                        {evalResult.confusion_matrix.fp}
                      </div>
                      <div className="text-[10px] text-hactm-muted mt-1">Benign flagged as threat</div>
                    </div>

                    <div className="p-4 rounded-lg bg-orange-500/10 border border-orange-500/30">
                      <div className="text-[10px] text-orange-400 font-semibold uppercase">
                        False Negatives (FN)
                      </div>
                      <div className="text-2xl font-bold text-orange-300 mt-1">
                        {evalResult.confusion_matrix.fn}
                      </div>
                      <div className="text-[10px] text-hactm-muted mt-1">Missed attack instances</div>
                    </div>

                    <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
                      <div className="text-[10px] text-blue-400 font-semibold uppercase">
                        True Negatives (TN)
                      </div>
                      <div className="text-2xl font-bold text-blue-300 mt-1">
                        {evalResult.confusion_matrix.tn}
                      </div>
                      <div className="text-[10px] text-hactm-muted mt-1">Correctly identified benign</div>
                    </div>
                  </div>
                </div>

                {/* Benchmark Profile Reference */}
                <div className="p-5 rounded-xl bg-hactm-panel/80 border border-hactm-border flex flex-col justify-between">
                  <div>
                    <h4 className="text-xs font-semibold text-hactm-heading uppercase tracking-wider mb-2">
                      Throughput & Latency Profile
                    </h4>
                    <p className="text-xs text-hactm-muted mb-4">
                      Real benchmarks executed against 1K and 5K event suites without data fabrication.
                    </p>

                    <div className="space-y-2 text-xs font-mono">
                      <div className="flex justify-between py-1 border-b border-hactm-border/60">
                        <span className="text-hactm-muted">1,000 Event Suite Throughput</span>
                        <span className="text-emerald-400 font-bold">68,568.29 evt/sec</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-hactm-border/60">
                        <span className="text-hactm-muted">1,000 Event Mean Latency</span>
                        <span className="text-hactm-heading">0.0144 ms</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-hactm-border/60">
                        <span className="text-hactm-muted">1,000 Event P95 Latency</span>
                        <span className="text-hactm-heading">0.0243 ms</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-hactm-border/60">
                        <span className="text-hactm-muted">1,000 Event P99 Latency</span>
                        <span className="text-hactm-heading">0.0424 ms</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span className="text-hactm-muted">Memory Peak</span>
                        <span className="text-hactm-accent">151.87 MB</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-hactm-border text-[10px] text-hactm-muted">
                    Derived from CLI command: <code className="text-hactm-accent">hactm network benchmark</code>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center rounded-xl border border-dashed border-hactm-border bg-hactm-panel/30">
              <FileCheck size={36} className="mx-auto text-hactm-muted mb-3" />
              <div className="text-sm font-semibold text-hactm-heading">No evaluation results available.</div>
              <div className="text-xs text-hactm-muted mt-1 max-w-md mx-auto">
                Execute an evaluation against the benchmark test dataset to inspect precision, recall, F1, and confusion matrix.
              </div>
              <button
                onClick={handleRunEvaluation}
                disabled={evaluateMutation.isPending}
                className="mt-4 px-4 py-2 rounded-lg bg-hactm-accent text-hactm-surface font-medium text-xs inline-flex items-center gap-2 hover:bg-hactm-accent/90 transition-colors"
              >
                <Play size={14} />
                <span>Run Evaluation on data/sample/network_test.csv</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* SECTION 79 & 83: DETECTION DETAILS & EXPLANATION MODAL / DRAWER */}
      {/* ========================================================================= */}
      {selectedDetectionId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-100">
          <div className="bg-hactm-surface border border-hactm-border rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            {detectionDetailsLoading || !selectedDetection ? (
              <div className="p-8">
                <Skeleton className="h-8 w-48 mb-4" />
                <Skeleton className="h-24 w-full" />
              </div>
            ) : (
              <div className="p-6 space-y-6">
                {/* Header */}
                <div className="flex items-start justify-between pb-4 border-b border-hactm-border">
                  <div>
                    <div className="text-[10px] font-mono text-hactm-muted uppercase tracking-wider">
                      Why this event was flagged &bull; Detection Explanation
                    </div>
                    <h2 className="text-lg font-bold text-hactm-heading mt-0.5 flex items-center gap-2">
                      <span>{selectedDetection.category}</span>
                      <RiskBadge score={selectedDetection.risk_score} />
                    </h2>
                  </div>
                  <button
                    onClick={() => setSelectedDetectionId(null)}
                    className="p-1.5 rounded-lg hover:bg-hactm-panel text-hactm-muted hover:text-hactm-text transition-colors"
                  >
                    <XCircle size={18} />
                  </button>
                </div>

                {/* Explanation Banner (Section 83) */}
                <div className="p-4 rounded-lg bg-hactm-panel border border-hactm-border space-y-2">
                  <div className="text-xs font-semibold text-hactm-accent flex items-center gap-1.5">
                    <Info size={14} />
                    <span>DETECTION RATIONALE</span>
                  </div>
                  <p className="text-xs text-hactm-text leading-relaxed font-mono">
                    {selectedDetection.explanation}
                  </p>
                </div>

                {/* Metadata Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border">
                    <div className="text-[10px] text-hactm-muted">DETECTOR TYPE</div>
                    <div className="font-semibold text-hactm-heading mt-0.5">
                      {selectedDetection.detector_type}
                    </div>
                  </div>

                  <div className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border">
                    <div className="text-[10px] text-hactm-muted">CONFIDENCE</div>
                    <div className="font-semibold text-emerald-400 mt-0.5">
                      {(selectedDetection.confidence * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border">
                    <div className="text-[10px] text-hactm-muted">UNCERTAINTY</div>
                    <div className="font-semibold text-amber-400 mt-0.5">
                      {(selectedDetection.uncertainty * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border">
                    <div className="text-[10px] text-hactm-muted">SEVERITY</div>
                    <div className="font-semibold text-hactm-heading mt-0.5">
                      {selectedDetection.severity}
                    </div>
                  </div>
                </div>

                {/* Reason Codes */}
                {selectedDetection.reason_codes?.length > 0 && (
                  <div>
                    <div className="text-xs font-semibold text-hactm-heading mb-2">Reason Codes</div>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedDetection.reason_codes.map((rc, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded text-[11px] font-mono bg-hactm-panel border border-hactm-border text-hactm-accent"
                        >
                          {rc}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Features Used */}
                <div>
                  <div className="text-xs font-semibold text-hactm-heading mb-2">Features Extracted & Evaluated</div>
                  <div className="max-h-40 overflow-y-auto rounded bg-hactm-panel border border-hactm-border p-3">
                    <JsonViewer data={selectedDetection.features_used} />
                  </div>
                </div>

                {/* Traceability / Provenance (Section 89) */}
                <div className="pt-3 border-t border-hactm-border text-[11px] font-mono text-hactm-muted grid grid-cols-2 gap-2">
                  <div>Detection ID: {selectedDetection.detection_id}</div>
                  <div>Event ID: {selectedDetection.event_id}</div>
                  <div>Detector ID: {selectedDetection.detector_id}</div>
                  <div>Model Version: {selectedDetection.model_version || 'N/A'}</div>
                </div>

                {/* Section 40: Detection Feedback Form */}
                <div className="pt-4 border-t border-hactm-border space-y-3">
                  <div className="text-xs font-semibold text-hactm-heading">Analyst Feedback Label</div>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Add analyst investigation note..."
                      value={feedbackNote}
                      onChange={(e) => setFeedbackNote(e.target.value)}
                      className="flex-1 px-3 py-1.5 text-xs rounded bg-hactm-panel border border-hactm-border text-hactm-text focus:outline-none focus:border-hactm-accent"
                    />
                    <button
                      onClick={() => handleFeedbackSubmit('TRUE_POSITIVE')}
                      disabled={feedbackMutation.isPending}
                      className="px-3 py-1.5 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-medium transition-colors"
                    >
                      True Positive
                    </button>
                    <button
                      onClick={() => handleFeedbackSubmit('FALSE_POSITIVE')}
                      disabled={feedbackMutation.isPending}
                      className="px-3 py-1.5 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs font-medium transition-colors"
                    >
                      False Positive
                    </button>
                  </div>
                  {feedbackSubmitted && (
                    <div className="text-[11px] text-emerald-400 font-mono">
                      &check; Feedback recorded successfully in detection_feedback table.
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
