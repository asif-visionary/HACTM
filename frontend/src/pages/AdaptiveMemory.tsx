import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export const AdaptiveMemoryPage: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [entries, setEntries] = useState<any[]>([]);
  const [transitions, setTransitions] = useState<any[]>([]);
  const [accessLogs, setAccessLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedTier, setSelectedTier] = useState<string>('');
  const [selectedEntry, setSelectedEntry] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, [selectedTier]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [h, e, t, a] = await Promise.all([
        api.getMemoryHealth(),
        api.getMemoryEvidence({ tier: selectedTier || undefined }),
        api.getMemoryTransitions(),
        api.getMemoryAccessLog(),
      ]);
      setHealth(h);
      setEntries(e.entries || []);
      setTransitions(t || []);
      setAccessLogs(a || []);
    } catch (err) {
      console.error('Failed to load adaptive memory data', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-cyan-400">Adaptive Evidence Memory</h1>
        <p className="text-sm text-slate-400">
          Persistent, bounded, tiered (HOT / WARM / COLD), importance-aware historical evidence storage.
        </p>
      </div>

      {/* Tier Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg bg-slate-900 border border-slate-800">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Memory Entries</div>
          <div className="text-3xl font-extrabold text-cyan-400 mt-2">{health?.total_entries ?? 0}</div>
          <div className="text-xs text-slate-500 mt-1">Bounded retention pool</div>
        </div>

        <div className="p-4 rounded-lg bg-slate-900 border border-rose-500/30">
          <div className="text-xs font-semibold text-rose-400 uppercase tracking-wider">HOT Memory Tier</div>
          <div className="text-3xl font-extrabold text-rose-400 mt-2">{health?.hot_entries ?? 0}</div>
          <div className="text-xs text-slate-500 mt-1">Utilization: {health?.hot_utilization_pct ?? 0}% (Max 15m)</div>
        </div>

        <div className="p-4 rounded-lg bg-slate-900 border border-amber-500/30">
          <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider">WARM Memory Tier</div>
          <div className="text-3xl font-extrabold text-amber-400 mt-2">{health?.warm_entries ?? 0}</div>
          <div className="text-xs text-slate-500 mt-1">Utilization: {health?.warm_utilization_pct ?? 0}% (Max 24h)</div>
        </div>

        <div className="p-4 rounded-lg bg-slate-900 border border-indigo-500/30">
          <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">COLD Memory Tier</div>
          <div className="text-3xl font-extrabold text-indigo-400 mt-2">{health?.cold_entries ?? 0}</div>
          <div className="text-xs text-slate-500 mt-1">Archived references (30 days)</div>
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex items-center justify-between bg-slate-900 p-4 rounded-lg border border-slate-800">
        <div className="flex items-center space-x-3">
          <span className="text-sm text-slate-400 font-medium">Filter Tier:</span>
          {['', 'HOT', 'WARM', 'COLD'].map((t) => (
            <button
              key={t}
              onClick={() => setSelectedTier(t)}
              className={`px-3 py-1 rounded text-xs font-semibold transition ${
                selectedTier === t
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {t || 'ALL TIERS'}
            </button>
          ))}
        </div>
        <button
          onClick={loadData}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded font-medium border border-slate-700"
        >
          Refresh Memory
        </button>
      </div>

      {/* Memory Explorer Table */}
      <div className="bg-slate-900 rounded-lg border border-slate-800 p-4">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Historical Memory Explorer</h2>
        {loading ? (
          <div className="text-slate-400 text-sm py-8 text-center">Loading memory entries...</div>
        ) : entries.length === 0 ? (
          <div className="text-slate-500 text-sm py-8 text-center">No evidence memory entries found for selected filter.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                <tr>
                  <th className="p-3">Memory ID</th>
                  <th className="p-3">Evidence ID</th>
                  <th className="p-3">Entities</th>
                  <th className="p-3">Domain</th>
                  <th className="p-3">Tier</th>
                  <th className="p-3">Importance</th>
                  <th className="p-3">Risk Score</th>
                  <th className="p-3">Timestamp</th>
                  <th className="p-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {entries.map((item) => (
                  <tr key={item.memory_id} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-mono text-xs text-cyan-400">{item.memory_id}</td>
                    <td className="p-3 font-mono text-xs text-slate-400">{item.evidence_id}</td>
                    <td className="p-3 font-medium text-slate-200">{(item.entity_ids || []).join(', ')}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded text-xs font-mono bg-slate-800 text-slate-300 border border-slate-700">
                        {item.domain}
                      </span>
                    </td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-semibold ${
                          item.memory_tier === 'HOT'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                            : item.memory_tier === 'WARM'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                            : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
                        }`}
                      >
                        {item.memory_tier}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-cyan-300">{item.importance_score}</td>
                    <td className="p-3 font-mono font-bold text-rose-400">{item.risk_score}</td>
                    <td className="p-3 text-xs text-slate-400">{new Date(item.timestamp).toLocaleString()}</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => setSelectedEntry(item)}
                        className="px-2.5 py-1 bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-800 rounded text-xs font-medium"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Transition & Access Audit Logs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tier Transitions */}
        <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
          <h3 className="text-md font-semibold text-slate-200 mb-3">Auditable Tier Transitions</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
            {transitions.slice(0, 10).map((t, idx) => (
              <div key={idx} className="p-2.5 rounded bg-slate-950 border border-slate-800 text-xs space-y-1">
                <div className="flex justify-between font-mono">
                  <span className="text-cyan-400">{t.memory_id}</span>
                  <span className="text-slate-500">{new Date(t.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="text-slate-300">
                  <span className="text-rose-400">{t.previous_tier}</span> &rarr; <span className="text-emerald-400">{t.new_tier}</span> ({t.reason})
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Access Log */}
        <div className="bg-slate-900 p-4 rounded-lg border border-slate-800">
          <h3 className="text-md font-semibold text-slate-200 mb-3">Historical Access Audit Log</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
            {accessLogs.slice(0, 10).map((a, idx) => (
              <div key={idx} className="p-2.5 rounded bg-slate-950 border border-slate-800 text-xs space-y-1">
                <div className="flex justify-between font-mono">
                  <span className="text-slate-300">{a.requesting_component}</span>
                  <span className="text-slate-500">{new Date(a.access_time).toLocaleTimeString()}</span>
                </div>
                <div className="text-slate-400">
                  Target: <span className="text-cyan-400 font-mono">{a.memory_id}</span> | Rank: {a.retrieval_rank} | {a.reason}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Entry Modal / Drawer */}
      {selectedEntry && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 max-w-xl w-full space-y-4 text-slate-200">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-cyan-400">Memory Entry Inspector</h3>
              <button onClick={() => setSelectedEntry(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <div className="space-y-2 text-xs font-mono bg-slate-950 p-4 rounded border border-slate-800">
              <div><span className="text-slate-500">Memory ID:</span> {selectedEntry.memory_id}</div>
              <div><span className="text-slate-500">Evidence ID:</span> {selectedEntry.evidence_id}</div>
              <div><span className="text-slate-500">Tier:</span> {selectedEntry.memory_tier}</div>
              <div><span className="text-slate-500">Importance:</span> {selectedEntry.importance_score}</div>
              <div><span className="text-slate-500">Risk Score:</span> {selectedEntry.risk_score}</div>
              <div><span className="text-slate-500">Entities:</span> {(selectedEntry.entity_ids || []).join(', ')}</div>
              <div><span className="text-slate-500">Access Count:</span> {selectedEntry.access_count}</div>
              <div><span className="text-slate-500">Last Accessed:</span> {new Date(selectedEntry.last_accessed_at).toLocaleString()}</div>
            </div>

            <div>
              <div className="text-xs font-semibold text-slate-400 uppercase mb-1">Metadata (Privacy Sanitized)</div>
              <pre className="p-3 bg-slate-950 rounded border border-slate-800 text-xs font-mono text-cyan-300 max-h-40 overflow-y-auto">
                {JSON.stringify(selectedEntry.metadata || {}, null, 2)}
              </pre>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedEntry(null)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded"
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
