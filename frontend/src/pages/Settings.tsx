import React, { useState } from 'react';
import { Database, AlertCircle, CheckCircle2, ShieldAlert, Play, Info } from 'lucide-react';
import { api } from '../services/api';
import { IngestionRunResult } from '../types/evidence';
import { useSystemStatus } from '../hooks/useSystemStatus';

export const Settings: React.FC = () => {
  const { status } = useSystemStatus();
  const [filePath, setFilePath] = useState('data/sample/sample_evidence.csv');
  const [policy, setPolicy] = useState('QUARANTINE_INVALID');
  const [batchSize, setBatchSize] = useState(1000);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestionResult, setIngestionResult] = useState<IngestionRunResult | null>(null);
  const [ingestionError, setIngestionError] = useState<string | null>(null);

  const handleIngest = async (targetPath?: string) => {
    setIsIngesting(true);
    setIngestionError(null);
    setIngestionResult(null);
    try {
      const res = await api.triggerIngestion({
        file_path: targetPath || filePath,
        policy,
        batch_size: batchSize,
      });
      setIngestionResult(res.data);
    } catch (err: any) {
      setIngestionError(err.message || 'Ingestion failed');
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-hactm-heading tracking-tight flex items-center gap-2">
          <span>System & Ingestion Settings</span>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-hactm-panel text-hactm-muted border border-hactm-border font-normal">
            HACTM Core Config
          </span>
        </h1>
        <p className="text-xs text-hactm-muted mt-1">
          Manage dataset ingestion pipelines, data quarantine policies, and system environment parameters.
        </p>
      </div>

      {/* Synthetic Data Transparency Notice */}
      <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-start gap-3">
        <ShieldAlert size={18} className="text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-amber-200/90 leading-relaxed">
          <div className="font-bold text-amber-300 uppercase tracking-wider mb-1 flex items-center gap-2">
            <span>SYNTHETIC / DEMONSTRATION DATA MODE ACTIVE</span>
          </div>
          The provided sample datasets consist exclusively of synthesized cyber telemetry (network flows, mocked auth logs,
          synthetic emails, and transaction events). No real personally identifiable information (PII) or proprietary secrets
          are ingested.
        </div>
      </div>

      {/* Dataset Ingestion Tool */}
      <div className="p-5 rounded-lg bg-hactm-card border border-hactm-border shadow-panel space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-hactm-heading flex items-center gap-2">
            <Database size={16} className="text-hactm-accent" />
            <span>Dataset Pipeline Ingestion Tool</span>
          </h3>
          <p className="text-xs text-hactm-muted mt-0.5">
            Load local dataset files (.csv, .json, .jsonl) with deterministic entity resolution and quarantine enforcement.
          </p>
        </div>

        {/* Quick Sample Buttons */}
        <div className="space-y-2">
          <span className="text-[10px] uppercase font-mono text-hactm-muted block font-medium">
            Quick Ingest Synthetic Samples
          </span>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => {
                setFilePath('data/sample/sample_evidence.csv');
                handleIngest('data/sample/sample_evidence.csv');
              }}
              disabled={isIngesting}
              className="px-3 py-1.5 rounded bg-hactm-panel hover:bg-hactm-hover border border-hactm-border text-xs font-mono text-hactm-text transition-colors flex items-center gap-1.5"
            >
              <Play size={12} className="text-hactm-accent" />
              <span>sample_evidence.csv</span>
            </button>

            <button
              onClick={() => {
                setFilePath('data/sample/sample_evidence.json');
                handleIngest('data/sample/sample_evidence.json');
              }}
              disabled={isIngesting}
              className="px-3 py-1.5 rounded bg-hactm-panel hover:bg-hactm-hover border border-hactm-border text-xs font-mono text-hactm-text transition-colors flex items-center gap-1.5"
            >
              <Play size={12} className="text-hactm-accent" />
              <span>sample_evidence.json</span>
            </button>

            <button
              onClick={() => {
                setFilePath('data/sample/sample_evidence.jsonl');
                handleIngest('data/sample/sample_evidence.jsonl');
              }}
              disabled={isIngesting}
              className="px-3 py-1.5 rounded bg-hactm-panel hover:bg-hactm-hover border border-hactm-border text-xs font-mono text-hactm-text transition-colors flex items-center gap-1.5"
            >
              <Play size={12} className="text-hactm-accent" />
              <span>sample_evidence.jsonl</span>
            </button>
          </div>
        </div>

        {/* Custom Ingestion Form */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-hactm-border/60 text-xs">
          <div className="sm:col-span-2">
            <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
              File Path (Relative or Absolute)
            </label>
            <input
              type="text"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="e.g. data/sample/sample_evidence.csv"
              className="w-full px-3 py-2 rounded bg-hactm-surface border border-hactm-border text-xs text-hactm-text font-mono focus:ring-1 focus:ring-hactm-accent focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-[10px] uppercase text-hactm-muted mb-1 font-medium">
              Error Policy
            </label>
            <select
              value={policy}
              onChange={(e) => setPolicy(e.target.value)}
              className="w-full px-3 py-2 rounded bg-hactm-surface border border-hactm-border text-xs text-hactm-text font-mono focus:ring-1 focus:ring-hactm-accent focus:outline-none"
            >
              <option value="QUARANTINE_INVALID">QUARANTINE_INVALID (Isolate Bad Records)</option>
              <option value="SKIP_INVALID">SKIP_INVALID (Skip on Error)</option>
              <option value="STRICT">STRICT (Rollback on Error)</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            onClick={() => handleIngest()}
            disabled={isIngesting || !filePath.trim()}
            className="px-4 py-2 rounded bg-hactm-accent text-black font-semibold text-xs hover:bg-hactm-accent/90 disabled:opacity-50 transition-colors flex items-center gap-1.5 shadow-accent-subtle"
          >
            <Play size={14} />
            <span>{isIngesting ? 'Ingesting Dataset...' : 'Trigger Pipeline Ingestion'}</span>
          </button>
        </div>

        {/* Ingestion Result Box */}
        {ingestionResult && (
          <div className="p-4 rounded-lg bg-hactm-surface border border-hactm-accent/40 space-y-3 animate-in fade-in">
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
              <CheckCircle2 size={16} />
              <span>Idempotent Ingestion Completed</span>
              <span className="font-mono text-hactm-muted">({ingestionResult.run_id})</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-6 gap-2 text-center font-mono">
              <div className="p-2 rounded bg-hactm-panel border border-hactm-border">
                <span className="text-[10px] text-hactm-muted uppercase block">Total</span>
                <span className="text-sm font-bold text-hactm-text">{ingestionResult.total}</span>
              </div>
              <div className="p-2 rounded bg-hactm-panel border border-hactm-border">
                <span className="text-[10px] text-hactm-muted uppercase block">Inserted</span>
                <span className="text-sm font-bold text-emerald-400">{ingestionResult.inserted}</span>
              </div>
              <div className="p-2 rounded bg-hactm-panel border border-hactm-border">
                <span className="text-[10px] text-hactm-muted uppercase block">Duplicates</span>
                <span className="text-sm font-bold text-amber-400">{ingestionResult.duplicates}</span>
              </div>
              <div className="p-2 rounded bg-hactm-panel border border-hactm-border">
                <span className="text-[10px] text-hactm-muted uppercase block">Invalid</span>
                <span className="text-sm font-bold text-orange-400">{ingestionResult.invalid}</span>
              </div>
              <div className="p-2 rounded bg-hactm-panel border border-hactm-border">
                <span className="text-[10px] text-hactm-muted uppercase block">Quarantined</span>
                <span className="text-sm font-bold text-red-400">{ingestionResult.quarantined}</span>
              </div>
              <div className="p-2 rounded bg-hactm-panel border border-hactm-border">
                <span className="text-[10px] text-hactm-muted uppercase block">Failed</span>
                <span className="text-sm font-bold text-red-400">{ingestionResult.failed}</span>
              </div>
            </div>

            {ingestionResult.quarantined > 0 && (
              <p className="text-[11px] text-hactm-muted italic">
                Quarantined records saved to <code className="text-hactm-text font-mono">data/processed/quarantine/</code> for research audit.
              </p>
            )}
          </div>
        )}

        {ingestionError && (
          <div className="p-4 rounded-lg bg-red-950/30 border border-red-500/40 text-red-300 text-xs flex items-start gap-2">
            <AlertCircle size={16} className="shrink-0 mt-0.5" />
            <span>{ingestionError}</span>
          </div>
        )}
      </div>

      {/* System Diagnostics */}
      <div className="p-5 rounded-lg bg-hactm-card border border-hactm-border shadow-panel space-y-3">
        <h3 className="text-sm font-semibold text-hactm-heading flex items-center gap-2">
          <Info size={16} className="text-hactm-muted" />
          <span>Core System Diagnostics</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-xs font-mono">
          <div className="p-3 rounded bg-hactm-surface border border-hactm-border">
            <span className="text-hactm-muted block text-[10px]">SERVICE</span>
            <span className="text-hactm-text">{status?.service || 'HACTM Mesh'}</span>
          </div>
          <div className="p-3 rounded bg-hactm-surface border border-hactm-border">
            <span className="text-hactm-muted block text-[10px]">PHASE</span>
            <span className="text-hactm-accent font-semibold">{status?.phase || 'Foundation Architecture'}</span>
          </div>
          <div className="p-3 rounded bg-hactm-surface border border-hactm-border">
            <span className="text-hactm-muted block text-[10px]">SCHEMA VERSION</span>
            <span className="text-hactm-text">{status?.schema_version || '1.0.0'}</span>
          </div>
          <div className="p-3 rounded bg-hactm-surface border border-hactm-border">
            <span className="text-hactm-muted block text-[10px]">DATABASE ENGINE</span>
            <span className="text-emerald-400 font-semibold">{status?.database || 'SQLite / SQLAlchemy 2.x'}</span>
          </div>
          <div className="p-3 rounded bg-hactm-surface border border-hactm-border">
            <span className="text-hactm-muted block text-[10px]">PERSISTENT QUARANTINE</span>
            <span className="text-hactm-text font-mono text-[11px]">data/processed/quarantine/</span>
          </div>
          <div className="p-3 rounded bg-hactm-surface border border-hactm-border">
            <span className="text-hactm-muted block text-[10px]">RISK SCORE SCALE</span>
            <span className="text-hactm-text">0.0 (Benign) → 1.0 (Critical Threat)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
