/**
 * Human Approval Gate Modal for HACTM Cyber Operations.
 * Connected directly to /api/v1/governance/approvals endpoints.
 * Enforces human-in-the-loop authorization for high-impact response actions.
 */

import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Clock,
  UserCheck,
  AlertTriangle,
  X,
  FileText,
} from 'lucide-react';
import { SuperIcon } from '../common/SuperIcon';

export interface ApprovalRequestItem {
  request_id: string;
  incident_id: string;
  entity_id: string;
  policy_id: string;
  action_type: string;
  proposed_action: string;
  risk_score: number;
  confidence: number;
  uncertainty: number;
  is_high_impact: number;
  justification: string;
  expected_impact?: string;
  alternatives?: string[];
  status: 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
  approver_identity?: string;
  approver_role?: string;
  created_at: string;
  expires_at?: string;
}

interface HumanApprovalModalProps {
  request: ApprovalRequestItem | null;
  onClose: () => void;
  onApprove: (requestId: string, notes: string, approverRole: string) => Promise<void>;
  onReject: (requestId: string, notes: string, approverRole: string) => Promise<void>;
  onRequestEvidence: (requestId: string, notes: string, approverRole: string) => Promise<void>;
}

export const HumanApprovalModal: React.FC<HumanApprovalModalProps> = ({
  request,
  onClose,
  onApprove,
  onReject,
  onRequestEvidence,
}) => {
  const [decisionNotes, setDecisionNotes] = useState<string>('');
  const [selectedRole, setSelectedRole] = useState<string>('SECURITY_OPERATOR');
  const [operatorId, setOperatorId] = useState<string>('sec_analyst_lead');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!request) return null;

  const isPending = request.status === 'PENDING_APPROVAL';

  const handleAction = async (actionType: 'approve' | 'reject' | 'evidence') => {
    if (operatorId.startsWith('AGENT') || operatorId.startsWith('AI_')) {
      setErrorMessage('AI agents are strictly forbidden from approving gated responses.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      if (actionType === 'approve') {
        await onApprove(request.request_id, decisionNotes || 'Approved by human security operator.', selectedRole);
      } else if (actionType === 'reject') {
        await onReject(request.request_id, decisionNotes || 'Rejected by operator.', selectedRole);
      } else {
        await onRequestEvidence(request.request_id, decisionNotes || 'Additional forensic evidence required before containment.', selectedRole);
      }
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit approval decision.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="relative w-full max-w-xl bg-slate-900 border border-amber-500/40 rounded-xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-amber-950/20">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400">
              <SuperIcon name="human-approval" style="color" size={26} alt="Human Approval Gate" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-white tracking-wide">HUMAN RESPONSE APPROVAL GATE</h3>
                <span className={`px-2 py-0.5 text-xs font-semibold rounded-full uppercase tracking-wider ${
                  request.status === 'APPROVED'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : request.status === 'REJECTED'
                    ? 'bg-red-500/20 text-red-400'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/50'
                }`}>
                  {request.status.replace(/_/g, ' ')}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                REQ: {request.request_id} | INCIDENT: {request.incident_id}
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
        <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto text-xs">
          {errorMessage && (
            <div className="p-3 bg-red-950/50 border border-red-800 text-red-300 rounded-lg flex items-center space-x-2">
              <AlertTriangle size={16} />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Gated Action Details */}
          <div className="p-4 bg-slate-800/60 rounded-lg border border-slate-700/60 space-y-2">
            <div className="flex items-center space-x-1.5">
              <SuperIcon name="permissions" style="color" size={14} />
              <span className="text-[11px] text-amber-400 font-bold uppercase tracking-wider block">
                GATED RESPONSE OPERATION:
              </span>
            </div>
            <p className="text-sm font-semibold text-slate-100">{request.proposed_action}</p>
            <div className="flex items-center space-x-4 text-slate-400 font-mono pt-1 text-[11px]">
              <span>ACTION TYPE: <strong className="text-slate-200">{request.action_type}</strong></span>
              <span>TARGET ENTITY: <strong className="text-cyan-400">{request.entity_id}</strong></span>
            </div>
          </div>

          {/* Risk Context & Uncertainty */}
          <div className="grid grid-cols-3 gap-3 font-mono">
            <div className="p-3 bg-slate-800/40 rounded border border-slate-700">
              <span className="text-slate-400 block text-[10px]">RISK SCORE</span>
              <span className="text-base font-bold text-red-400">{(request.risk_score * 100).toFixed(0)}%</span>
            </div>
            <div className="p-3 bg-slate-800/40 rounded border border-slate-700">
              <span className="text-slate-400 block text-[10px]">CONFIDENCE</span>
              <span className="text-base font-bold text-emerald-400">{(request.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="p-3 bg-slate-800/40 rounded border border-slate-700">
              <span className="text-slate-400 block text-[10px]">UNCERTAINTY</span>
              <span className="text-base font-bold text-purple-400">{(request.uncertainty * 100).toFixed(0)}%</span>
            </div>
          </div>

          {/* Justification & Expected Impact */}
          <div className="space-y-2">
            <div>
              <div className="flex items-center space-x-1.5 text-slate-400 mb-0.5">
                <SuperIcon name="alignment" style="color" size={14} />
                <span className="font-semibold">Policy Alignment & Justification:</span>
              </div>
              <p className="text-slate-200 mt-0.5">{request.justification}</p>
            </div>
            {request.expected_impact && (
              <div>
                <span className="text-slate-400 block font-semibold">Expected Operational Impact:</span>
                <p className="text-slate-200 mt-0.5">{request.expected_impact}</p>
              </div>
            )}
          </div>

          {/* Human Decision Controls (Visible when Pending) */}
          {isPending ? (
            <div className="pt-2 border-t border-slate-800 space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-slate-400 block mb-1">Approver Identity (Human Operator)</label>
                  <input
                    type="text"
                    value={operatorId}
                    onChange={(e) => setOperatorId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-slate-200 font-mono"
                    placeholder="analyst_callsign"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Required Approver Role</label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-slate-200"
                  >
                    <option value="SECURITY_OPERATOR">SECURITY_OPERATOR</option>
                    <option value="ANALYST">ANALYST</option>
                    <option value="ADMIN">ADMIN</option>
                    <option value="SOC_LEAD">SOC_LEAD</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Decision Rationale & Audit Notes</label>
                <textarea
                  value={decisionNotes}
                  onChange={(e) => setDecisionNotes(e.target.value)}
                  placeholder="Provide explicit operational rationale for this decision..."
                  rows={2}
                  className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-2 pt-2">
                <button
                  disabled={isSubmitting}
                  onClick={() => handleAction('approve')}
                  className="flex items-center justify-center space-x-1.5 px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-medium transition"
                >
                  <CheckCircle2 size={15} />
                  <span>Approve Action</span>
                </button>
                <button
                  disabled={isSubmitting}
                  onClick={() => handleAction('reject')}
                  className="flex items-center justify-center space-x-1.5 px-3 py-2 bg-red-600 hover:bg-red-500 text-white rounded font-medium transition"
                >
                  <XCircle size={15} />
                  <span>Reject Action</span>
                </button>
                <button
                  disabled={isSubmitting}
                  onClick={() => handleAction('evidence')}
                  className="flex items-center justify-center space-x-1.5 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded font-medium transition"
                >
                  <HelpCircle size={15} />
                  <span>Need Evidence</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="p-3 bg-slate-800/40 rounded border border-slate-700 text-slate-300">
              <span className="font-semibold block">Decision Record:</span>
              <p className="mt-1">
                Decision executed by <strong className="text-cyan-400">{request.approver_identity || 'System'}</strong> [
                {request.approver_role || 'Auto-Policy'}].
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/70 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs rounded transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

