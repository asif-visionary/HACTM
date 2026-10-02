import React, { useState, useEffect } from 'react';
import { EvidenceReportBuilder } from '../components/reports/EvidenceReportBuilder';
import { Download, FileText, CheckCircle, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export const Reports: React.FC = () => {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [reportFmt, setReportFmt] = useState<string>('PDF');

  const fetchReports = async () => {
    try {
      const res = await api.listResearchReports();
      setReports(res.reports || []);
    } catch (err) {
      console.error('Failed to load reports', err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGenerateResearchReport = async () => {
    setLoading(true);
    try {
      await api.generateResearchReport('EXP_14_END_TO_END', 'HACTM Architecture Final Research Report', reportFmt);
      fetchReports();
    } catch (err: any) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-hactm-border pb-4">
        <div>
          <h1 className="text-xl font-bold text-hactm-heading tracking-tight flex items-center gap-2">
            <span>Security & Research Reports</span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-normal">
              Evaluation Exports
            </span>
          </h1>
          <p className="text-xs text-hactm-muted mt-1">
            Synthesize evidence audits and generate reproducible Evaluation evaluation research reports (PDF, JSON, CSV).
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={reportFmt}
            onChange={(e) => setReportFmt(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-white text-xs rounded-lg p-2 font-mono"
          >
            <option value="PDF">PDF Report</option>
            <option value="JSON">JSON Data</option>
            <option value="CSV">CSV Summary</option>
          </select>
          <button
            onClick={handleGenerateResearchReport}
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition shadow"
          >
            <FileText className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Generate Research Export
          </button>
        </div>
      </div>

      {reports.length > 0 && (
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Download className="w-4 h-4 text-indigo-400" /> Evaluation Reproducible Report Artifacts
          </h3>
          <div className="space-y-2">
            {reports.map((r: any) => (
              <div key={r.report_id} className="p-3 bg-slate-800/40 border border-slate-700/50 rounded-lg flex items-center justify-between text-xs">
                <div>
                  <span className="font-semibold text-white">{r.title}</span>
                  <p className="text-slate-400 text-[11px] font-mono mt-0.5">Format: {r.format} | ID: {r.report_id}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 font-mono text-[10px] rounded">
                    SHA-256: {r.reproducibility_checksum?.slice(0, 10)}...
                  </span>
                  <a
                    href={`/api/v1/reports/${r.report_id}/export`}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded flex items-center gap-1 transition"
                  >
                    <Download className="w-3 h-3" /> Download
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <EvidenceReportBuilder />
    </div>
  );
};
