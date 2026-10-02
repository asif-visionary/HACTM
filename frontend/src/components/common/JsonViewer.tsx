import React, { useState } from 'react';
import { Copy, Check, ChevronDown, ChevronRight } from 'lucide-react';

interface JsonViewerProps {
  data: any;
  title?: string;
  initialExpanded?: boolean;
}

export const JsonViewer: React.FC<JsonViewerProps> = ({
  data,
  title = 'Structured Telemetry / Evidence Data',
  initialExpanded = true,
}) => {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(initialExpanded);

  const formattedJson = JSON.stringify(data, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(formattedJson);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded border border-hactm-border bg-hactm-surface overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 bg-hactm-panel/70 border-b border-hactm-border text-xs">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-1.5 font-medium text-hactm-text hover:text-white transition-colors focus:outline-none focus:ring-1 focus:ring-hactm-accent/50 rounded"
          aria-expanded={expanded}
        >
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          <span>{title}</span>
          <span className="text-hactm-muted font-mono">({Object.keys(data || {}).length} keys)</span>
        </button>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-hactm-muted hover:text-hactm-accent transition-colors px-2 py-0.5 rounded hover:bg-hactm-card focus:outline-none"
          title="Copy JSON to clipboard"
          aria-label="Copy JSON"
        >
          {copied ? <Check size={13} className="text-risk-low" /> : <Copy size={13} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      {expanded && (
        <pre className="p-3 text-xs font-mono text-emerald-400/90 overflow-x-auto max-h-80 leading-relaxed bg-[#05080E]">
          <code>{formattedJson}</code>
        </pre>
      )}
    </div>
  );
};
