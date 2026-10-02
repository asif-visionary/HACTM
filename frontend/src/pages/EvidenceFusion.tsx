import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layers, ShieldAlert, Cpu, GitMerge, AlertTriangle, CheckCircle2, Clock, Info, Play, BarChart3, HelpCircle } from 'lucide-react';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorState } from '../components/common/ErrorState';

export const EvidenceFusion: React.FC = () => {
  const [selectedEntityId, setSelectedEntityId] = useState<string>('USER-103');
  const [windowSeconds, setWindowSeconds] = useState<number>(1800);
  const [evalResults, setEvalResults] = useState<any | null>(null);
  const [isEvaluating, setIsEvaluating] = useState<boolean>(false);

  const { data: fusionData, isLoading, isError, refetch } = useQuery({
    queryKey: ['fusion-results', selectedEntityId, windowSeconds],
    queryFn: () => api.runFusion(selectedEntityId, windowSeconds),
  });

  const { data: conflictsData } = useQuery({
    queryKey: ['fusion-conflicts'],
    queryFn: () => api.getFusionConflicts(),
  });

  const { data: metricsData } = useQuery({
    queryKey: ['fusion-metrics'],
    queryFn: () => api.getFusionMetrics(),
  });

  const fusion = fusionData?.data?.fusion;
  const conflictsList = conflictsData?.data || [];
  const metrics = metricsData?.data;

  const handleRunEvaluation = async () => {
    setIsEvaluating(true);
    try {
      const res = await api.evaluateFusion();
      setEvalResults(res.data);
    } catch (err) {
      console.error('Failed to run fusion evaluation:', err);
    } finally {
      setIsEvaluating(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Correlating cross-domain evidence streams and calculating Unified Cyber Risk..." />;
  }

  if (isError) {
    return (
      <ErrorState
        title="Evidence Fusion Engine Offline"
        message="Unable to communicate with the Evidence Fusion Engine Service."
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-hactm-heading tracking-tight flex items-center gap-2">
            <span>Cross-Domain Evidence Fusion</span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-hactm-accent/10 text-hactm-accent border border-hactm-accent/30 font-normal">
              Evidence Fusion Unified Cyber Risk
            </span>
          </h1>
          <p className="text-xs text-hactm-muted mt-1">
            Correlates heterogeneous evidence across Network, Phishing, UBA, Identity, and Transaction domains.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-hactm-panel px-3 py-1.5 rounded border border-hactm-border text-xs">
            <span className="text-hactm-muted">Entity:</span>
            <input
              type="text"
              value={selectedEntityId}
              onChange={(e) => setSelectedEntityId(e.target.value)}
              className="bg-hactm-card border border-hactm-border rounded px-2 py-0.5 text-hactm-text font-mono text-xs focus:outline-none focus:border-hactm-accent"
              placeholder="e.g. USER-103"
            />
          </div>

          <button
            onClick={handleRunEvaluation}
            disabled={isEvaluating}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-hactm-accent text-black font-semibold text-xs hover:bg-hactm-accent/90 transition-colors shadow-accent-subtle disabled:opacity-50"
          >
            {isEvaluating ? <LoadingSpinner message="" /> : <Play size={14} />}
            <span>Run Research Evaluation</span>
          </button>
        </div>
      </div>

      {/* Overview Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg bg-hactm-card border border-hactm-border space-y-1">
          <span className="text-xs text-hactm-muted block">Unified Cyber Risk</span>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-mono font-bold text-amber-400">
              {fusion?.unified_risk_score?.toFixed(2) || '0.00'}
            </span>
            <span
              className={`text-xs font-mono px-2 py-0.5 rounded border ${
                fusion?.risk_category === 'CRITICAL' || fusion?.risk_category === 'HIGH'
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  : fusion?.risk_category === 'MODERATE'
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
              }`}
            >
              {fusion?.risk_category || 'LOW'}
            </span>
          </div>
          <span className="text-[11px] text-hactm-muted block">Bounded probabilistic aggregation</span>
        </div>

        <div className="p-4 rounded-lg bg-hactm-card border border-hactm-border space-y-1">
          <span className="text-xs text-hactm-muted block">Fusion Confidence & Uncertainty</span>
          <div className="flex items-center justify-between font-mono text-sm">
            <span className="text-emerald-400 font-semibold">
              Conf: {fusion ? (fusion.confidence * 100).toFixed(1) : '0'}%
            </span>
            <span className="text-amber-400 font-semibold">
              Uncert: {fusion ? (fusion.uncertainty * 100).toFixed(1) : '0'}%
            </span>
          </div>
          <span className="text-[11px] text-hactm-muted block">Source quality & coverage weighted</span>
        </div>

        <div className="p-4 rounded-lg bg-hactm-card border border-hactm-card border-hactm-border space-y-1">
          <span className="text-xs text-hactm-muted block">Domain Coverage Ratio</span>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-mono font-bold text-hactm-accent">
              {fusion?.unique_domain_count || 0} / 5
            </span>
            <span className="text-xs font-mono text-hactm-muted">
              {fusion ? ((fusion.unique_domain_count / 5.0) * 100).toFixed(0) : 0}% domains
            </span>
          </div>
          <span className="text-[11px] text-hactm-muted block">Observed independent telemetry</span>
        </div>

        <div className="p-4 rounded-lg bg-hactm-card border border-hactm-border space-y-1">
          <span className="text-xs text-hactm-muted block">Evidence Conflicts</span>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-mono font-bold text-hactm-text">
              {conflictsList.length}
            </span>
            <span className="text-xs font-mono text-emerald-400">
              {fusion?.supporting_evidence_count || 0} supporting
            </span>
          </div>
          <span className="text-[11px] text-hactm-muted block">Explicit risk disagreement logs</span>
        </div>
      </div>

      {/* Central Unified Cyber Risk Panel */}
      <div className="p-5 rounded-lg bg-hactm-card border border-hactm-border space-y-4">
        <div className="flex items-center justify-between border-b border-hactm-border pb-3">
          <div>
            <h2 className="text-sm font-semibold text-hactm-text flex items-center gap-2">
              <GitMerge size={16} className="text-hactm-accent" />
              <span>Unified Cyber Risk Decision</span>
            </h2>
            <p className="text-xs text-hactm-muted">
              Target Entity: <code className="text-hactm-accent">{selectedEntityId}</code> • Algorithm: <code className="text-hactm-muted">{fusion?.fusion_algorithm} v{fusion?.fusion_version}</code>
            </p>
          </div>
          <span className="text-[11px] font-mono px-2 py-1 rounded bg-hactm-panel border border-hactm-border text-hactm-muted">
            Correlation Window: {fusion?.temporal_window}s
          </span>
        </div>

        {/* Explainability Callout Box */}
        <div className="p-4 rounded-lg bg-hactm-panel/80 border border-hactm-border space-y-2 text-xs">
          <strong className="text-hactm-text font-semibold flex items-center gap-1.5 text-xs">
            <HelpCircle size={14} className="text-hactm-accent" /> Why is the risk elevated?
          </strong>
          <pre className="whitespace-pre-wrap font-mono text-[11px] text-hactm-text leading-relaxed bg-hactm-card p-3 rounded border border-hactm-border/60">
            {fusion?.explanation || 'No evidence correlated.'}
          </pre>
        </div>
      </div>

      {/* Evidence Conflicts View */}
      {conflictsList.length > 0 && (
        <div className="p-5 rounded-lg bg-hactm-card border border-amber-500/30 space-y-3">
          <h2 className="text-xs font-semibold text-amber-400 tracking-wide flex items-center gap-2">
            <AlertTriangle size={16} />
            <span>Detected Cross-Domain Evidence Conflicts ({conflictsList.length})</span>
          </h2>
          <div className="space-y-2 text-xs">
            {conflictsList.map((c: any) => (
              <div key={c.conflict_id} className="p-3 rounded bg-hactm-panel border border-hactm-border flex items-start justify-between">
                <div>
                  <span className="font-mono text-amber-400 font-semibold block mb-1">
                    [{c.conflict_type}] Severity: {c.severity} • Risk Delta: {c.risk_difference?.toFixed(2)}
                  </span>
                  <p className="text-hactm-muted text-[11px] leading-relaxed">
                    {c.explanation}
                  </p>
                </div>
                <span className="text-[10px] font-mono text-hactm-muted shrink-0 ml-4">
                  ID: {c.conflict_id}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Research Evaluation Results Panel */}
      {evalResults && (
        <div className="p-5 rounded-lg bg-hactm-card border border-hactm-accent/40 space-y-4 animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-3 border-b border-hactm-border">
            <div>
              <h2 className="text-sm font-semibold text-hactm-accent flex items-center gap-2">
                <BarChart3 size={16} />
                <span>Empirical Evaluation & Hypotheses Validation (H1 – H5)</span>
              </h2>
              <p className="text-xs text-hactm-muted">
                Runtime: {evalResults.evaluation_runtime_seconds}s • Evaluated {evalResults.scenarios_evaluated} controlled scenarios
              </p>
            </div>
            <button
              onClick={() => setEvalResults(null)}
              className="text-xs text-hactm-muted hover:text-hactm-text"
            >
              Dismiss
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-2 p-3 rounded bg-hactm-panel border border-hactm-border">
              <strong className="text-hactm-text block text-xs">Baseline Model Comparison:</strong>
              <div className="space-y-1 font-mono text-[11px]">
                <p>Baseline A (Single Max Risk): {evalResults.baselines_comparison?.baseline_a_single_domain_max}</p>
                <p>Baseline B (Simple Average): {evalResults.baselines_comparison?.baseline_b_simple_average}</p>
                <p>Baseline C (Weighted Average): {evalResults.baselines_comparison?.baseline_c_weighted_average}</p>
                <p className="text-hactm-accent font-semibold">
                  Proposed Context-Aware Fusion: {evalResults.baselines_comparison?.proposed_context_aware_fusion}
                </p>
              </div>
            </div>

            <div className="space-y-2 p-3 rounded bg-hactm-panel border border-hactm-border">
              <strong className="text-hactm-text block text-xs">Redundancy & Ablation Findings:</strong>
              <div className="space-y-1 font-mono text-[11px]">
                <p>Ablation 1 (Without Quality Weight): {evalResults.ablations_results?.ablation_1_without_quality_weight}</p>
                <p>Ablation 6 (Naive Redundant Risk): {evalResults.ablations_results?.ablation_6_naive_redundant_risk}</p>
                <p className="text-emerald-400 font-semibold">
                  Redundancy Prevented Inflation: +{evalResults.ablations_results?.redundancy_prevented_inflation}
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <strong className="text-hactm-text block text-xs">Hypothesis Testing Results:</strong>
            <div className="grid grid-cols-1 gap-2 text-[11px]">
              {Object.entries(evalResults.hypotheses_validation || {}).map(([key, h]: [string, any]) => (
                <div key={key} className="p-2.5 rounded bg-hactm-panel/60 border border-hactm-border flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-hactm-text font-semibold block">{key}</strong>
                    <span className="text-hactm-muted">{h.finding}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
