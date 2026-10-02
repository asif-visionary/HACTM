import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { Mail, AlertTriangle, ShieldAlert, FileText, CheckCircle2, ChevronRight, Search } from 'lucide-react';

export const PhishingIntelligence: React.FC = () => {
  const [page, setPage] = useState(1);
  const [selectedDetection, setSelectedDetection] = useState<any>(null);

  const { data: metricsData } = useQuery({
    queryKey: ['phishingMetrics'],
    queryFn: () => api.getPhishingMetrics(),
  });

  const { data: eventsData, isLoading: eventsLoading } = useQuery({
    queryKey: ['phishingEvents', page],
    queryFn: () => api.getPhishingEvents(page, 20),
  });

  const { data: detectionsData } = useQuery({
    queryKey: ['phishingDetections', page],
    queryFn: () => api.getPhishingDetections(page, 20),
  });

  const health = metricsData?.agent_health || {};
  const evalMetrics = metricsData?.evaluation || {};

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="flex items-center justify-between bg-hactm-surface border border-hactm-border rounded-lg p-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-400 rounded-lg border border-amber-500/20">
            <Mail size={28} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-hactm-heading">Phishing Intelligence Agent</h1>
            <p className="text-xs text-hactm-muted mt-0.5">
              Domain-Specific Email & Messaging Threat Analysis Engine (Agent ID: <code className="text-hactm-accent">phishing-intelligence-agent</code>)
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 text-xs font-mono rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
            <CheckCircle2 size={14} /> {health.status || 'OPERATIONAL'}
          </span>
          <span className="text-xs font-mono text-hactm-muted bg-hactm-panel px-3 py-1 rounded border border-hactm-border">
            Model: {health.model_version || 'phish_tfidf_v1.0'}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Emails Processed</div>
          <div className="text-2xl font-bold text-hactm-heading mt-1">{health.events_processed || 0}</div>
          <div className="text-[11px] text-hactm-muted mt-1">Rate: {health.processing_rate_events_per_sec || 0} evts/sec</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Generic Phishing</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {evalMetrics.generic_phishing_metrics?.true_positives || 0}
          </div>
          <div className="text-[11px] text-hactm-muted mt-1">TF-IDF NLP Classifier</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">Spear-Phishing Indicators</div>
          <div className="text-2xl font-bold text-red-400 mt-1">
            {evalMetrics.spear_phishing_metrics?.true_positives || 0}
          </div>
          <div className="text-[11px] text-hactm-muted mt-1">Targeted Recipient Lures</div>
        </div>
        <div className="bg-hactm-surface border border-hactm-border p-4 rounded-lg">
          <div className="text-xs font-mono text-hactm-muted uppercase">BEC Indicators</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">
            {evalMetrics.bec_metrics?.true_positives || 0}
          </div>
          <div className="text-[11px] text-hactm-muted mt-1">Executive Financial Lures</div>
        </div>
      </div>

      {/* Main Content Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Detections List Table */}
        <div className="lg:col-span-2 bg-hactm-surface border border-hactm-border rounded-lg p-5">
          <h2 className="text-sm font-semibold text-hactm-heading uppercase tracking-wider mb-4 flex items-center justify-between">
            <span>Phishing Detections Stream</span>
            <span className="text-xs font-mono text-hactm-muted">Actual Stored API State</span>
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-hactm-panel border-b border-hactm-border text-hactm-muted font-mono uppercase">
                <tr>
                  <th className="p-3">Detection ID</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Detector</th>
                  <th className="p-3">Cyber Risk Score</th>
                  <th className="p-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-hactm-border/60 text-hactm-text">
                {(detectionsData?.items || []).map((det: any) => (
                  <tr key={det.detection_id} className="hover:bg-hactm-panel/50 transition-colors">
                    <td className="p-3 font-mono text-hactm-accent">{det.detection_id}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                        det.category === 'BEC_INDICATORS' ? 'bg-purple-500/10 text-purple-400 border-purple-500/20' :
                        det.category === 'SPEAR_PHISHING_INDICATORS' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                        'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                        {det.category}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-hactm-muted">{det.detector_type}</td>
                    <td className="p-3 font-mono font-bold">
                      <span className={det.risk_score >= 0.7 ? 'text-red-400' : 'text-amber-400'}>
                        {det.risk_score.toFixed(2)}
                      </span>
                    </td>
                    <td className="p-3">
                      <button
                        onClick={() => setSelectedDetection(det)}
                        className="text-hactm-accent hover:underline flex items-center gap-1 font-mono text-[11px]"
                      >
                        Details <ChevronRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Explainable Detail View */}
        <div className="bg-hactm-surface border border-hactm-border rounded-lg p-5">
          <h2 className="text-sm font-semibold text-hactm-heading uppercase tracking-wider mb-4">
            Detection Explanation & Evidence
          </h2>

          {selectedDetection ? (
            <div className="space-y-4 text-xs">
              <div className="p-3 bg-hactm-panel rounded border border-hactm-border space-y-2">
                <div className="text-hactm-muted font-mono">Detection ID: {selectedDetection.detection_id}</div>
                <div className="text-hactm-heading font-semibold">Why Flagged:</div>
                <div className="text-amber-300 bg-amber-500/10 p-2 rounded border border-amber-500/20 leading-relaxed font-mono">
                  {selectedDetection.explanation}
                </div>
              </div>

              <div className="space-y-2">
                <div className="font-semibold text-hactm-heading">Metrics & Uncertainty:</div>
                <div className="grid grid-cols-3 gap-2 text-center font-mono">
                  <div className="p-2 bg-hactm-panel rounded border border-hactm-border">
                    <div className="text-[10px] text-hactm-muted">Cyber Risk</div>
                    <div className="font-bold text-red-400">{selectedDetection.risk_score}</div>
                  </div>
                  <div className="p-2 bg-hactm-panel rounded border border-hactm-border">
                    <div className="text-[10px] text-hactm-muted">Confidence</div>
                    <div className="font-bold text-emerald-400">{selectedDetection.confidence}</div>
                  </div>
                  <div className="p-2 bg-hactm-panel rounded border border-hactm-border">
                    <div className="text-[10px] text-hactm-muted">Uncertainty</div>
                    <div className="font-bold text-hactm-muted">{selectedDetection.uncertainty}</div>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="font-semibold text-hactm-heading">Extracted Features:</div>
                <pre className="p-3 bg-hactm-panel rounded border border-hactm-border font-mono text-[11px] overflow-x-auto text-hactm-text">
                  {JSON.stringify(selectedDetection.features_used, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-hactm-muted border border-dashed border-hactm-border rounded">
              Select a detection to view complete explainability & feature analysis.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
