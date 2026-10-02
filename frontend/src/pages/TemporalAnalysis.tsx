import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

export const TemporalAnalysisPage: React.FC = () => {
  const [targetEntity, setTargetEntity] = useState<string>('USER-103');
  const [timelineData, setTimelineData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadTimeline();
  }, []);

  const loadTimeline = async () => {
    setLoading(true);
    try {
      const data = await api.getTemporalTimeline(targetEntity);
      setTimelineData(data);
    } catch (err) {
      console.error('Failed to load temporal timeline', err);
    } finally {
      setLoading(false);
    }
  };

  const getDomainColor = (domain: string) => {
    switch (domain?.toLowerCase()) {
      case 'phishing': return 'border-amber-500/40 text-amber-400 bg-amber-500/10';
      case 'identity': return 'border-purple-500/40 text-purple-400 bg-purple-500/10';
      case 'network': return 'border-cyan-500/40 text-cyan-400 bg-cyan-500/10';
      case 'transaction': return 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10';
      default: return 'border-slate-700 text-slate-300 bg-slate-800';
    }
  };

  const entries = timelineData?.memory?.entries || [];

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-cyan-400">Temporal Evidence Correlation</h1>
        <p className="text-sm text-slate-400">
          Event-time ordering, cross-session evidence correlation, and multi-stage sequence gap detection.
        </p>
      </div>

      {/* Query Bar */}
      <div className="flex items-center space-x-3 bg-slate-900 p-4 rounded-lg border border-slate-800">
        <label className="text-xs font-semibold text-slate-400 uppercase">Target Entity:</label>
        <input
          type="text"
          value={targetEntity}
          onChange={(e) => setTargetEntity(e.target.value)}
          className="px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-xs font-mono text-cyan-300 w-48"
          placeholder="USER-103"
        />
        <button
          onClick={loadTimeline}
          className="px-3.5 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded transition"
        >
          Analyze Timeline
        </button>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline Event Flow */}
        <div className="lg:col-span-2 bg-slate-900 rounded-lg border border-slate-800 p-6 space-y-4">
          <h2 className="text-md font-semibold text-slate-200 flex justify-between items-center">
            <span>Event-Time Chronological Flow (<span className="text-cyan-400 font-mono">{targetEntity}</span>)</span>
            <span className="text-xs text-slate-400 font-normal">Coverage: {Math.round((timelineData?.memory?.coverage || 0) * 100)}%</span>
          </h2>

          {loading ? (
            <div className="text-slate-500 text-sm py-12 text-center">Analyzing temporal timeline...</div>
          ) : entries.length === 0 ? (
            <div className="text-slate-500 text-sm py-12 text-center">
              No historical security evidence found for entity '{targetEntity}'.
            </div>
          ) : (
            <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6">
              {entries.map((ev: any, idx: number) => (
                <div key={ev.memory_id} className="relative group">
                  {/* Timeline Dot */}
                  <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-cyan-500 border-4 border-slate-950 shadow-md"></div>

                  {/* Card */}
                  <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 space-y-2 hover:border-slate-700 transition">
                    <div className="flex justify-between items-start">
                      <span className={`px-2 py-0.5 rounded text-xs font-mono font-semibold border ${getDomainColor(ev.domain)}`}>
                        {ev.domain.toUpperCase()}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        {new Date(ev.timestamp).toLocaleString()}
                      </span>
                    </div>

                    <div className="text-sm font-semibold text-slate-200">{ev.event_type}</div>

                    <div className="flex items-center space-x-4 text-xs font-mono text-slate-400 pt-1">
                      <div>Risk Score: <span className="text-rose-400 font-bold">{ev.risk_score}</span></div>
                      <div>Confidence: <span className="text-emerald-400">{ev.confidence}</span></div>
                      <div>Tier: <span className="text-cyan-300">{ev.memory_tier}</span></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pattern & Candidate Breakdown */}
        <div className="space-y-6">
          <div className="bg-slate-900 rounded-lg border border-slate-800 p-4 space-y-3">
            <h3 className="text-sm font-semibold text-slate-200">Temporal Candidate Attack Chains</h3>
            {(!timelineData?.attack_chain_candidates || timelineData.attack_chain_candidates.length === 0) ? (
              <div className="text-slate-500 text-xs py-4 text-center">
                No multi-stage attack candidates detected for entity timeline.
              </div>
            ) : (
              timelineData.attack_chain_candidates.map((cand: any) => (
                <div key={cand.chain_id} className="p-3 bg-slate-950 rounded border border-rose-500/40 space-y-1">
                  <div className="text-xs font-bold text-rose-400">{cand.pattern_id}</div>
                  <div className="text-xs text-slate-300">Completeness: {Math.round(cand.completeness * 100)}%</div>
                  <div className="text-[11px] text-slate-400 font-mono">Confidence: {cand.confidence}</div>
                </div>
              ))
            )}
          </div>

          <div className="bg-slate-900 rounded-lg border border-slate-800 p-4 space-y-3">
            <h3 className="text-sm font-semibold text-slate-200">Temporal Relationship Types</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
                <span className="font-mono text-cyan-400 font-semibold">WITHIN_WINDOW</span>
                <span className="text-slate-400">&le; 30 minutes</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
                <span className="font-mono text-purple-400 font-semibold">BURST</span>
                <span className="text-slate-400">&gt; 5 events in 60s</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
                <span className="font-mono text-amber-400 font-semibold">GAP</span>
                <span className="text-slate-400">Significant time delta</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
