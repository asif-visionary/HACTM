/**
 * Agent Communication & Task Handoff Panel.
 * Displays verified agent-to-agent communications, telemetry handoffs, and evidence exchanges.
 */

import React, { useState } from 'react';
import { AgentMessageItem } from '../../types/workspace';
import {
  MessageSquare,
  ArrowRight,
  Shield,
  FileSearch,
  Clock,
  Filter,
  CheckCircle,
  Radio,
} from 'lucide-react';
import { SuperIcon } from '../common/SuperIcon';

interface AgentCommunicationPanelProps {
  messages: AgentMessageItem[];
  onSelectEvidence?: (evidenceId: string) => void;
  selectedAgentId?: string | null;
}

export const AgentCommunicationPanel: React.FC<AgentCommunicationPanelProps> = ({
  messages,
  onSelectEvidence,
  selectedAgentId,
}) => {
  const [filterAgent, setFilterAgent] = useState<string>('ALL');

  const filtered = messages.filter((m) => {
    if (filterAgent !== 'ALL') {
      return m.sender === filterAgent || m.recipient === filterAgent;
    }
    if (selectedAgentId) {
      return m.sender === selectedAgentId || m.recipient === selectedAgentId;
    }
    return true;
  });

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl text-xs">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800 bg-slate-950/60">
        <div className="flex items-center space-x-2">
          <SuperIcon name="a2a" style="color" size={18} alt="Agent to Agent Communication" />
          <h3 className="font-bold text-white tracking-wide">AGENT COMMUNICATIONS & HANDOFF</h3>
          <span className="px-2 py-0.5 bg-slate-800 text-slate-300 rounded-full font-mono text-[10px]">
            {filtered.length} MESSAGES
          </span>
        </div>

        {selectedAgentId && (
          <span className="text-[10px] text-cyan-400 font-mono">
            FILTER: {selectedAgentId}
          </span>
        )}
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {filtered.map((msg) => {
          const isHandoff = msg.status === 'HANDOFF';
          return (
            <div
              key={msg.id}
              className={`p-3 rounded-lg border transition ${
                isHandoff
                  ? 'bg-fuchsia-950/20 border-fuchsia-700/50'
                  : 'bg-slate-800/50 border-slate-700/40 hover:border-slate-600'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center space-x-1.5 font-mono text-[11px]">
                  <SuperIcon
                    name={isHandoff ? 'task' : 'reasoning'}
                    style={isHandoff ? 'color' : 'duotone'}
                    size={14}
                    className="mr-0.5 flex-shrink-0"
                  />
                  <span className="text-cyan-300 font-semibold">{msg.sender}</span>
                  <ArrowRight size={12} className="text-slate-400" />
                  <span className="text-purple-300 font-semibold">{msg.recipient}</span>
                </div>
                <div className="flex items-center space-x-2 text-[10px] text-slate-400 font-mono">
                  {msg.incidentId && <span className="text-slate-500">[{msg.incidentId}]</span>}
                  <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>

              <p className="text-slate-200 leading-relaxed font-sans">{msg.message}</p>

              {msg.evidenceRef && (
                <div className="mt-2 flex items-center justify-between pt-1.5 border-t border-slate-800">
                  <button
                    onClick={() => onSelectEvidence && onSelectEvidence(msg.evidenceRef!)}
                    className="flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 text-[10px] font-mono transition"
                  >
                    <SuperIcon name="citations" style="two-tone" size={13} className="mr-0.5" />
                    <span>REF: {msg.evidenceRef}</span>
                  </button>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono uppercase bg-cyan-950/60 text-cyan-300 border border-cyan-800/40 flex items-center space-x-1">
                    <SuperIcon name="task" style="stroke" size={10} className="mr-0.5" />
                    <span>EVIDENCE HANDOFF</span>
                  </span>
                </div>
              )}
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="py-12 text-center text-slate-500">
            <Radio size={24} className="mx-auto mb-2 opacity-50" />
            <p>No active communications recorded for this filter.</p>
          </div>
        )}
      </div>
    </div>
  );
};

