import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export const ResearchLabPage: React.FC = () => {
  const [evalData, setEvalData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadEval();
  }, []);

  const loadEval = async () => {
    setLoading(true);
    try {
      const res = await api.evaluateAdaptiveMemory();
      setEvalData(res);
    } catch (err) {
      console.error('Failed to run Adaptive Memory & Graph evaluation', err);
    } finally {
      setLoading(false);
    }
  };

  const baselines = evalData?.baseline_comparison || {};
  const ablations = evalData?.ablation_studies || {};

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-cyan-400">Adaptive Memory & Graph Research Lab</h1>
          <p className="text-sm text-slate-400">
            Empirical evaluation comparing historical memory baselines and graph ablation studies.
          </p>
        </div>
        <button
          onClick={loadEval}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded shadow transition"
        >
          Re-Run Benchmarks
        </button>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm py-20 text-center">Executing Adaptive Memory & Graph experimental evaluation suite...</div>
      ) : (
        <>
          {/* Baseline Comparison Table */}
          <div className="bg-slate-900 rounded-lg border border-slate-800 p-6 space-y-4">
            <h2 className="text-lg font-semibold text-slate-200">
              Memory Baseline Comparison (Hypothesis H1 & H2)
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                  <tr>
                    <th className="p-3">Memory Architecture</th>
                    <th className="p-3">Multi-Stage Recall</th>
                    <th className="p-3">Memory Hit Rate</th>
                    <th className="p-3">Latency (ms/event)</th>
                    <th className="p-3">Memory Entries</th>
                    <th className="p-3">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {Object.entries(baselines).map(([key, val]: [string, any]) => (
                    <tr
                      key={key}
                      className={key === 'Proposed_AdaptiveMemory' ? 'bg-cyan-950/40 font-semibold' : 'hover:bg-slate-800/30'}
                    >
                      <td className="p-3 font-mono text-cyan-400">
                        {key} {key === 'Proposed_AdaptiveMemory' && '(PROPOSED)'}
                      </td>
                      <td className="p-3 font-mono text-emerald-400 font-bold">
                        {Math.round((val.multi_stage_recall || 0) * 100)}%
                      </td>
                      <td className="p-3 font-mono text-cyan-300">
                        {Math.round((val.memory_hit_rate || 0) * 100)}%
                      </td>
                      <td className="p-3 font-mono text-slate-300">{val.latency_ms_per_event} ms</td>
                      <td className="p-3 font-mono text-slate-400">{val.memory_entries}</td>
                      <td className="p-3 text-xs text-slate-400">{val.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Ablation Studies Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Memory Ablation */}
            <div className="bg-slate-900 rounded-lg border border-slate-800 p-6 space-y-4">
              <h3 className="text-md font-semibold text-slate-200">Memory Component Ablation</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
                    <tr>
                      <th className="p-2.5">Variant</th>
                      <th className="p-2.5">Recall</th>
                      <th className="p-2.5">Hit Rate</th>
                      <th className="p-2.5">False Corr Rate</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {Object.entries(ablations.memory_ablation || {}).map(([v, val]: [string, any]) => (
                      <tr key={v}>
                        <td className="p-2.5 font-mono text-slate-300">{v}</td>
                        <td className="p-2.5 font-mono text-emerald-400 font-bold">{val.recall}</td>
                        <td className="p-2.5 font-mono text-cyan-300">{val.hit_rate}</td>
                        <td className="p-2.5 font-mono text-rose-400">{val.false_correlation_rate}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Graph Ablation */}
            <div className="bg-slate-900 rounded-lg border border-slate-800 p-6 space-y-4">
              <h3 className="text-md font-semibold text-slate-200">Graph Reasoning Ablation</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
                    <tr>
                      <th className="p-2.5">Graph Model</th>
                      <th className="p-2.5">Multi-Stage F1</th>
                      <th className="p-2.5">False Corr Rate</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {Object.entries(ablations.graph_ablation || {}).map(([g, val]: [string, any]) => (
                      <tr key={g}>
                        <td className="p-2.5 font-mono text-slate-300">{g}</td>
                        <td className="p-2.5 font-mono text-emerald-400 font-bold">{val.multi_stage_detection_f1}</td>
                        <td className="p-2.5 font-mono text-rose-400">{val.false_correlation_rate}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
