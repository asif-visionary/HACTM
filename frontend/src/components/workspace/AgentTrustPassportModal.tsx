/**
 * Agent Trust Passport Modal / Drawer.
 * Displays authoritative backend agent specifications, reliability bounds,
 * model versions, permitted tools, and real-time governance isolation controls.
 */

import React from 'react';
import {
  AgentTrustPassport,
  WorkspaceAgentState,
} from '../../types/workspace';
import {
  ShieldCheck,
  ShieldAlert,
  X,
  Cpu,
  Activity,
  Layers,
  Wrench,
  CheckCircle,
  AlertTriangle,
  Lock,
  Unlock,
  Radio,
  FileText,
} from 'lucide-react';
import { SuperIcon } from '../common/SuperIcon';

interface AgentTrustPassportModalProps {
  passport: AgentTrustPassport | null;
  agentState: WorkspaceAgentState | null;
  onClose: () => void;
  onToggleIsolation: (agentId: string, action: 'ISOLATE' | 'REINSTATE', reason: string) => void;
  isToggling?: boolean;
}

export const AgentTrustPassportModal: React.FC<AgentTrustPassportModalProps> = ({
  passport,
  agentState,
  onClose,
  onToggleIsolation,
  isToggling,
}) => {
  if (!passport) return null;

  const isIsolated = passport.is_isolated;
  const relScore = passport.reliability_score !== undefined && passport.reliability_score !== null
    ? `${(passport.reliability_score * 100).toFixed(1)}%`
    : 'Not available';

  const lowerBound = passport.reliability_lower_bound !== undefined && passport.reliability_lower_bound !== null
    ? `${(passport.reliability_lower_bound * 100).toFixed(1)}%`
    : 'Not available';

  const upperBound = passport.reliability_upper_bound !== undefined && passport.reliability_upper_bound !== null
    ? `${(passport.reliability_upper_bound * 100).toFixed(1)}%`
    : 'Not available';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-700/80 rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header with Security Passport Identity */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/70">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${isIsolated ? 'bg-red-500/20 text-red-400' : 'bg-cyan-500/20 text-cyan-400'}`}>
              <SuperIcon
                name={isIsolated ? 'sandbox' : 'agent'}
                style={isIsolated ? 'color' : 'duotone'}
                size={24}
              />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-lg font-bold text-white tracking-wide">{passport.agent_name}</h3>
                <span className={`px-2 py-0.5 text-xs font-semibold rounded-full uppercase tracking-wider ${
                  isIsolated
                    ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                }`}>
                  {passport.current_status}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                AGENT ID: <span className="text-cyan-400">{passport.agent_id}</span> | {passport.department}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto text-sm">
          {/* Trust Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
              <span className="text-xs text-slate-400 block flex items-center justify-between">
                <span>Trust Reliability</span>
                <SuperIcon name="evaluation" style="duotone" size={13} />
              </span>
              <span className="text-xl font-bold text-cyan-400 font-mono">{relScore}</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">[{lowerBound} - {upperBound}]</span>
            </div>

            <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
              <span className="text-xs text-slate-400 block flex items-center justify-between">
                <span>Drift & Calibration</span>
                <SuperIcon name="reflection" style="color" size={13} />
              </span>
              <span className="text-sm font-semibold text-emerald-400 block mt-1">{passport.drift_status}</span>
              <span className="text-[10px] text-slate-500 block">{passport.calibration_status}</span>
            </div>

            <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
              <span className="text-xs text-slate-400 block flex items-center justify-between">
                <span>Events Processed</span>
                <SuperIcon name="task" style="stroke" size={13} />
              </span>
              <span className="text-xl font-bold text-slate-200 font-mono">{passport.events_processed}</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">{passport.detections_generated} Detections</span>
            </div>

            <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
              <span className="text-xs text-slate-400 block flex items-center justify-between">
                <span>Avg Latency</span>
                <SuperIcon name="feedback-loop" style="duotone" size={13} />
              </span>
              <span className="text-xl font-bold text-purple-400 font-mono">{passport.average_latency_ms.toFixed(1)} ms</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">Telemetry verified</span>
            </div>
          </div>

          {/* Model & Version Specification */}
          <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-700/50 space-y-2">
            <div className="flex items-center space-x-2 text-slate-300 font-medium text-xs">
              <SuperIcon name="memory" style="color" size={15} />
              <span>MODEL RUNTIME & TENANT SCOPE</span>
            </div>
            <div className="grid grid-cols-2 gap-4 text-xs font-mono">
              <div>
                <span className="text-slate-400">Model Specification:</span>
                <p className="text-slate-200">{passport.model_and_version}</p>
              </div>
              <div>
                <span className="text-slate-400">Tenant Authorization Scope:</span>
                <p className="text-slate-200">{passport.tenant_scope}</p>
              </div>
              <div>
                <span className="text-slate-400">Agent Class:</span>
                <p className="text-slate-200">{passport.agent_type}</p>
              </div>
              <div>
                <span className="text-slate-400">Last Verified Activity:</span>
                <p className="text-slate-200">{new Date(passport.last_activity).toLocaleTimeString()}</p>
              </div>
            </div>
          </div>

          {/* Allowed Capabilities */}
          <div>
            <div className="flex items-center space-x-2 text-slate-300 font-medium text-xs mb-2">
              <SuperIcon name="permissions" style="color" size={15} />
              <span>AUTHORIZED CAPABILITIES</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {passport.allowed_capabilities.map((cap) => (
                <span
                  key={cap}
                  className="px-2.5 py-1 bg-cyan-950/60 border border-cyan-800/50 text-cyan-300 text-xs rounded-md font-mono"
                >
                  ✓ {cap}
                </span>
              ))}
              {passport.allowed_capabilities.length === 0 && (
                <span className="text-xs text-slate-500 italic">No capabilities authorized</span>
              )}
            </div>
          </div>

          {/* Tool Permissions */}
          <div>
            <div className="flex items-center space-x-2 text-slate-300 font-medium text-xs mb-2">
              <SuperIcon name="tools" style="color" size={15} />
              <span>TOOL ACCESS PERMISSIONS (SECTION 10 GOVERNANCE GATE)</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 font-mono text-xs">
              {passport.tool_permissions.map((tool) => (
                <div
                  key={tool}
                  className="p-2 bg-slate-800/60 border border-slate-700/60 rounded flex items-center justify-between"
                >
                  <span className="text-slate-300">{tool}</span>
                  <span className="text-[10px] text-emerald-400 font-semibold uppercase">Permitted</span>
                </div>
              ))}
              {passport.tool_permissions.length === 0 && (
                <span className="text-xs text-slate-500 italic">Not available</span>
              )}
            </div>
          </div>

          {/* Active Detectors */}
          <div>
            <div className="flex items-center space-x-2 text-slate-300 font-medium text-xs mb-2">
              <Activity size={16} className="text-purple-400" />
              <span>ACTIVE DETECTOR ENGINES</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {passport.active_detectors.map((det) => (
                <span
                  key={det}
                  className="px-2 py-0.5 bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded font-mono"
                >
                  {det}
                </span>
              ))}
              {passport.active_detectors.length === 0 && (
                <span className="text-xs text-slate-500 italic">Not available</span>
              )}
            </div>
          </div>

          {/* Self-Defense Isolation & Policy Enforcement */}
          <div className={`p-4 rounded-lg border ${isIsolated ? 'bg-red-950/30 border-red-800/60' : 'bg-slate-800/40 border-slate-700/50'}`}>
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-semibold text-white">
                  {isIsolated ? 'Agent Is Isolated from Mesh' : 'Agent Defense & Isolation Controls'}
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  {isIsolated
                    ? `Isolated: ${passport.isolation_reason || 'Policy violation detected.'}`
                    : 'Revoke tool access or isolate agent in case of compromised behavior or anomaly.'}
                </p>
              </div>

              <button
                disabled={isToggling}
                onClick={() => {
                  if (isIsolated) {
                    onToggleIsolation(passport.agent_id, 'REINSTATE', 'Manual operator reinstatement after verification.');
                  } else {
                    onToggleIsolation(
                      passport.agent_id,
                      'ISOLATE',
                      'Operator initiated defensive isolation due to suspicious telemetry.'
                    );
                  }
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                  isIsolated
                    ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                    : 'bg-red-600 hover:bg-red-500 text-white'
                }`}
              >
                {isIsolated ? <Unlock size={14} /> : <Lock size={14} />}
                <span>{isIsolated ? 'Reinstate Agent' : 'Isolate Agent'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/70 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg transition"
          >
            Close Passport
          </button>
        </div>
      </div>
    </div>
  );
};

