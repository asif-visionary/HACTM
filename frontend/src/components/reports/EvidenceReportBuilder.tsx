import React, { useState } from 'react';
import { FileBarChart2, Download, ShieldCheck, FileText, CheckCircle2, AlertTriangle, RefreshCw, FileCode } from 'lucide-react';
import { api } from '../../services/api';
import { formatTimestamp } from '../../lib/utils';
import { RiskBadge } from '../common/RiskBadge';

export const EvidenceReportBuilder: React.FC = () => {
  const [entityId, setEntityId] = useState('');
  const [eventType, setEventType] = useState('');
  const [source, setSource] = useState('');
  const [minRisk, setMinRisk] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [reportResult, setReportResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getPayload = () => {
    const payload: any = {};
    if (entityId.trim()) payload.entity_id = entityId.trim();
    if (eventType) payload.event_type = eventType;
    if (source.trim()) payload.source = source.trim();
    if (minRisk !== '') payload.min_risk = parseFloat(minRisk);
    return payload;
  };

  const validateInputs = (): boolean => {
    if (minRisk !== '') {
      const parsed = parseFloat(minRisk);
      if (isNaN(parsed) || parsed < 0 || parsed > 1) {
        setError('Minimum Cyber Risk must be a valid number between 0 and 1.');
        return false;
      }
    }
    return true;
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isGenerating) return;

    setError(null);
    if (!validateInputs()) return;

    setIsGenerating(true);
    try {
      const payload = getPayload();
      const res = await api.generateEvidenceReport(payload);
      setReportResult(res.data);
    } catch (err: any) {
      setError(err.message || 'Unable to generate the evidence report.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExportPdf = async () => {
    if (!reportResult || isDownloadingPdf) return;
    setIsDownloadingPdf(true);
    setError(null);
    try {
      const payload = getPayload();
      const blob = await api.downloadEvidenceReportPdf(payload);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportResult.report_id || 'evidence_report'}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message || 'Unable to download PDF evidence report.');
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  const handleExportJson = () => {
    if (!reportResult) return;
    try {
      const jsonStr = JSON.stringify(reportResult, null, 2);
      const blob = new Blob([jsonStr], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportResult.report_id || 'evidence_report'}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError('Unable to export JSON evidence report.');
    }
  };

  const handleResetFilters = () => {
    setEntityId('');
    setEventType('');
    setSource('');
    setMinRisk('');
    setError(null);
    setReportResult(null);
  };

  return (
    <div className="space-y-6">
      {/* Report Categories */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Evidence Report - Active */}
        <div className="p-4 rounded-lg bg-hactm-card border-2 border-hactm-accent/40 shadow-panel relative">
          <div className="flex items-center gap-2 mb-2 text-hactm-accent font-semibold text-sm">
            <FileBarChart2 size={16} />
            <span>Evidence Report</span>
          </div>
          <p className="text-xs text-hactm-muted mb-3">
            Synthesizes structured audit reports from canonical Common Security Evidence.
          </p>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hactm-accent/10 text-hactm-accent border border-hactm-accent/30 flex items-center gap-1 w-fit">
            <CheckCircle2 size={12} />
            <span>Active Service</span>
          </span>
        </div>

        {/* Incident Report */}
        <div className="p-4 rounded-lg bg-hactm-card/50 border border-hactm-border opacity-70">
          <div className="flex items-center gap-2 mb-2 text-hactm-muted font-semibold text-sm">
            <ShieldCheck size={16} />
            <span>Autonomous Incident Report</span>
          </div>
          <p className="text-xs text-hactm-muted mb-3">
            Multi-agent incident timeline narrative and autonomous root-cause synthesis.
          </p>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hactm-panel text-hactm-muted border border-hactm-border">
            Available in Evidence Fusion
          </span>
        </div>

        {/* Risk Assessment */}
        <div className="p-4 rounded-lg bg-hactm-card/50 border border-hactm-border opacity-70">
          <div className="flex items-center gap-2 mb-2 text-hactm-muted font-semibold text-sm">
            <FileText size={16} />
            <span>Cyber Trust Risk Assessment</span>
          </div>
          <p className="text-xs text-hactm-muted mb-3">
            Quantitative trust mesh evaluation, uncertainty calibration, and Zero Trust scoring.
          </p>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-hactm-panel text-hactm-muted border border-hactm-border">
            Available in Reliability & Trust
          </span>
        </div>
      </div>

      {/* Report Generator Controls */}
      <div className="p-5 rounded-lg bg-hactm-card border border-hactm-border shadow-panel">
        <h3 className="text-sm font-semibold text-hactm-heading mb-1">
          Generate Structured Evidence Report
        </h3>
        <p className="text-xs text-hactm-muted mb-4">
          Select filtering parameters to extract and synthesize stored evidence into an auditable report.
        </p>

        <form onSubmit={handleGenerate} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div>
            <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
              Filter by Entity ID
            </label>
            <input
              type="text"
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
              placeholder="e.g. IP:192.168.1.1"
              className="w-full px-3 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text font-mono text-xs focus:ring-1 focus:ring-hactm-accent"
            />
          </div>

          <div>
            <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
              Event Type
            </label>
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="w-full px-3 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text font-mono text-xs focus:ring-1 focus:ring-hactm-accent"
            >
              <option value="">All Types</option>
              <option value="NETWORK">NETWORK</option>
              <option value="AUTHENTICATION">AUTHENTICATION</option>
              <option value="EMAIL">EMAIL</option>
              <option value="UBA">UBA</option>
              <option value="TRANSACTION">TRANSACTION</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
              Source / Sensor
            </label>
            <input
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              placeholder="e.g. CIC-IDS2017"
              className="w-full px-3 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text font-mono text-xs focus:ring-1 focus:ring-hactm-accent"
            />
          </div>

          <div>
            <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
              Min Cyber Risk (0 - 1)
            </label>
            <input
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={minRisk}
              onChange={(e) => setMinRisk(e.target.value)}
              placeholder="e.g. 0.5"
              className="w-full px-3 py-1.5 rounded bg-hactm-surface border border-hactm-border text-hactm-text font-mono text-xs focus:ring-1 focus:ring-hactm-accent"
            />
          </div>

          <div className="sm:col-span-2 md:col-span-4 flex items-center justify-between pt-2 border-t border-hactm-border/60">
            <span className="text-[11px] text-hactm-muted flex items-center gap-1.5 font-mono">
              <span>PDF Export:</span>
              <span className="text-emerald-400 font-semibold">Available</span>
            </span>
            <button
              type="submit"
              disabled={isGenerating}
              className="px-4 py-2 rounded bg-hactm-accent text-black font-semibold hover:bg-hactm-accent/90 disabled:opacity-50 transition-colors text-xs flex items-center gap-1.5"
            >
              {isGenerating ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  <span>Generating Report...</span>
                </>
              ) : (
                <>
                  <FileBarChart2 size={14} />
                  <span>Generate Evidence Report</span>
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 rounded bg-red-950/30 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
            <AlertTriangle size={16} className="text-red-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Generated Report View */}
      {reportResult && (
        <div className="p-6 rounded-lg bg-hactm-card border border-hactm-border shadow-panel space-y-5 animate-in fade-in duration-200">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-hactm-border pb-4">
            <div>
              <h3 className="text-base font-bold text-hactm-heading">{reportResult.title}</h3>
              <div className="text-xs text-hactm-muted font-mono mt-0.5 space-x-3">
                <span>ID: <strong className="text-hactm-accent">{reportResult.report_id}</strong></span>
                <span>•</span>
                <span>Generated: {formatTimestamp(reportResult.generated_at)}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleExportPdf}
                disabled={isDownloadingPdf || reportResult.evidence_count === 0}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-hactm-accent text-black font-semibold text-xs hover:bg-hactm-accent/90 disabled:opacity-40 transition-colors"
                title="Export report as formatted PDF"
              >
                <Download size={13} className={isDownloadingPdf ? 'animate-spin' : ''} />
                <span>{isDownloadingPdf ? 'Generating PDF...' : 'Export PDF'}</span>
              </button>

              <button
                onClick={handleExportJson}
                disabled={reportResult.evidence_count === 0}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-hactm-panel border border-hactm-border text-slate-200 hover:text-white hover:bg-slate-800 text-xs disabled:opacity-40 transition-colors"
                title="Export report JSON payload"
              >
                <FileCode size={13} />
                <span>Export JSON</span>
              </button>
            </div>
          </div>

          {/* Applied Filters Badge Bar */}
          <div className="p-3 bg-hactm-surface border border-hactm-border rounded-lg text-xs space-y-1">
            <span className="text-[10px] uppercase font-semibold text-hactm-muted tracking-wider block">Applied Report Filters</span>
            <div className="flex flex-wrap gap-2 pt-1 font-mono text-[11px]">
              {reportResult.filters?.entity_id && (
                <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-indigo-300">
                  Entity: {reportResult.filters.entity_id}
                </span>
              )}
              {reportResult.filters?.event_type && (
                <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-cyan-300">
                  Type: {reportResult.filters.event_type}
                </span>
              )}
              {reportResult.filters?.source && (
                <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                  Source: {reportResult.filters.source}
                </span>
              )}
              {reportResult.filters?.min_risk !== undefined && (
                <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-amber-300">
                  Min Risk: {reportResult.filters.min_risk}
                </span>
              )}
              {!Object.keys(reportResult.filters || {}).length && (
                <span className="text-slate-400 italic">None (All stored evidence in scope)</span>
              )}
            </div>
          </div>

          {/* Empty Results State */}
          {reportResult.evidence_count === 0 ? (
            <div className="p-8 text-center bg-hactm-surface border border-hactm-border rounded-xl space-y-3">
              <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto opacity-80" />
              <p className="text-sm text-slate-200 font-semibold">No evidence matched the selected filters.</p>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Try widening your filtering parameters or resetting minimum cyber risk.
              </p>
              <button
                onClick={handleResetFilters}
                className="px-3.5 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
              >
                Adjust Filters
              </button>
            </div>
          ) : (
            <>
              {/* Report Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded bg-hactm-surface border border-hactm-border text-center">
                  <span className="text-[10px] text-hactm-muted uppercase block">Matching Evidence</span>
                  <span className="text-xl font-bold font-mono text-hactm-text">
                    {reportResult.evidence_count}
                  </span>
                </div>
                <div className="p-3 rounded bg-hactm-surface border border-hactm-border text-center">
                  <span className="text-[10px] text-hactm-muted uppercase block">Average Cyber Risk</span>
                  <span className="text-xl font-bold font-mono text-hactm-accent">
                    {reportResult.summary?.average_cyber_risk_score}
                  </span>
                </div>
                <div className="p-3 rounded bg-hactm-surface border border-hactm-border text-center">
                  <span className="text-[10px] text-hactm-muted uppercase block">High-Risk Count</span>
                  <span className="text-xl font-bold font-mono text-risk-critical">
                    {reportResult.summary?.high_risk_events_count}
                  </span>
                </div>
                <div className="p-3 rounded bg-hactm-surface border border-hactm-border text-center">
                  <span className="text-[10px] text-hactm-muted uppercase block">Represented Entities</span>
                  <span className="text-xl font-bold font-mono text-indigo-400">
                    {reportResult.summary?.entities_represented || 1}
                  </span>
                </div>
              </div>

              {/* Records Table */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-hactm-heading uppercase tracking-wider">
                  Audited Evidence Records
                </h4>
                <div className="rounded border border-hactm-border bg-hactm-surface overflow-hidden">
                  <table className="w-full text-left text-xs border-collapse font-mono">
                    <thead>
                      <tr className="border-b border-hactm-border bg-hactm-panel/60 text-hactm-muted text-[10px] uppercase">
                        <th className="py-2 px-3">Event ID</th>
                        <th className="py-2 px-3">Source / Agent</th>
                        <th className="py-2 px-3">Target Entity</th>
                        <th className="py-2 px-3">Type</th>
                        <th className="py-2 px-3">Severity</th>
                        <th className="py-2 px-3">Cyber Risk</th>
                        <th className="py-2 px-3">Confidence</th>
                        <th className="py-2 px-3">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-hactm-border/50">
                      {reportResult.records.map((r: any) => (
                        <tr key={r.event_id} className="hover:bg-hactm-hover/50">
                          <td className="py-2 px-3 text-hactm-accent font-semibold">{r.event_id}</td>
                          <td className="py-2 px-3 text-slate-300">{r.agent_id || r.source || 'agent-network'}</td>
                          <td className="py-2 px-3 text-hactm-text">{r.entity_id}</td>
                          <td className="py-2 px-3 text-hactm-muted">{r.event_type}</td>
                          <td className="py-2 px-3">
                            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              r.severity === 'CRITICAL' || r.severity === 'HIGH' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                              r.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                              'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            }`}>
                              {r.severity}
                            </span>
                          </td>
                          <td className="py-2 px-3">
                            <RiskBadge score={r.risk_score} />
                          </td>
                          <td className="py-2 px-3 text-hactm-text">{r.confidence ? r.confidence.toFixed(2) : '1.00'}</td>
                          <td className="py-2 px-3 text-hactm-muted">{formatTimestamp(r.timestamp)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};
