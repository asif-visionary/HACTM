import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ShieldCheck,
  ShieldAlert,
  FileCheck,
  CheckCircle2,
  XCircle,
  Clock,
  Lock,
  AlertTriangle,
  Play,
  FileText,
  Search,
  UserCheck,
  RefreshCw,
  Hash,
  Activity,
  Layers,
  ArrowRight,
  Shield,
  Zap,
} from 'lucide-react';
import { api } from '../services/api';

type TabType = 'work-orders' | 'approvals' | 'audit' | 'explanation' | 'resilience';

export const GovernedResilienceDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('work-orders');
  const [selectedRole, setSelectedRole] = useState<'ANALYST' | 'ADMIN' | 'SECURITY_OPERATOR'>('ANALYST');
  const [approverName, setApproverName] = useState<string>('ANALYST-JANE-DOE');
  const [incidentSearchId, setIncidentSearchId] = useState<string>('INC-001');

  const queryClient = useQueryClient();

  // Queries
  const { data: workOrdersData, isLoading: loadingWO } = useQuery({
    queryKey: ['governance-work-orders'],
    queryFn: () => api.getWorkOrders(),
  });

  const { data: approvalsData, isLoading: loadingAppr } = useQuery({
    queryKey: ['governance-approvals'],
    queryFn: () => api.getApprovalRequests(),
  });

  const { data: auditData, isLoading: loadingAudit } = useQuery({
    queryKey: ['governance-audit-trail'],
    queryFn: () => api.getAuditTrail(),
  });

  const { data: auditVerifyData, refetch: recheckIntegrity } = useQuery({
    queryKey: ['governance-audit-verify'],
    queryFn: () => api.verifyAuditTrail(),
  });

  const { data: explanationData, refetch: fetchExplanation } = useQuery({
    queryKey: ['incident-explanation', incidentSearchId],
    queryFn: () => api.getIncidentExplanation(incidentSearchId),
    enabled: !!incidentSearchId,
  });

  const { data: resilienceScenariosData } = useQuery({
    queryKey: ['resilience-scenarios'],
    queryFn: () => api.getResilienceScenarios(),
  });

  // Mutations
  const runEvaluationMutation = useMutation({
    mutationFn: () => api.runResilienceEvaluation(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance-audit-trail'] });
    },
  });

  const approveMutation = useMutation({
    mutationFn: (requestId: string) =>
      api.approveAction({
        request_id: requestId,
        approver_identity: approverName,
        approver_role: selectedRole,
        notes: `Approved via Governance Dashboard by ${approverName}`,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance-approvals'] });
      queryClient.invalidateQueries({ queryKey: ['governance-audit-trail'] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (requestId: string) =>
      api.rejectAction({
        request_id: requestId,
        approver_identity: approverName,
        approver_role: selectedRole,
        notes: `Rejected via Governance Dashboard by ${approverName}`,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance-approvals'] });
      queryClient.invalidateQueries({ queryKey: ['governance-audit-trail'] });
    },
  });

  const requestEvidenceMutation = useMutation({
    mutationFn: (requestId: string) =>
      api.requestMoreEvidence({
        request_id: requestId,
        approver_identity: approverName,
        approver_role: selectedRole,
        notes: `Additional evidence requested by ${approverName}`,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['governance-approvals'] });
    },
  });

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ShieldCheck className="text-emerald-400 h-7 w-7" />
            Governed Investigation & Resilience Dashboard
          </h1>
          <p className="text-sm text-slate-400">
            Work order enforcement, human response gating, tamper-evident audit trail, and resilience evaluation.
          </p>
        </div>

        {/* Role Selector Context */}
        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 p-2 rounded-lg">
          <UserCheck className="h-4 w-4 text-cyan-400" />
          <span className="text-xs text-slate-400 font-medium">Analyst Context:</span>
          <input
            type="text"
            value={approverName}
            onChange={(e) => setApproverName(e.target.value)}
            className="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-cyan-300 w-36"
            placeholder="Approver ID"
          />
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value as any)}
            className="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-white"
          >
            <option value="ANALYST">ANALYST</option>
            <option value="ADMIN">ADMIN</option>
            <option value="SECURITY_OPERATOR">SECURITY_OPERATOR</option>
          </select>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('work-orders')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'work-orders'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <FileCheck className="h-4 w-4" />
          Work Orders ({workOrdersData?.data?.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('approvals')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'approvals'
              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <Lock className="h-4 w-4" />
          Human Approval Gate ({approvalsData?.data?.length || 0})
        </button>

        <button
          onClick={() => setActiveTab('audit')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'audit'
              ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <Hash className="h-4 w-4" />
          Audit Trail & Hash Integrity
        </button>

        <button
          onClick={() => setActiveTab('explanation')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'explanation'
              ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <FileText className="h-4 w-4" />
          Incident Explanation
        </button>

        <button
          onClick={() => setActiveTab('resilience')}
          className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
            activeTab === 'resilience'
              ? 'bg-purple-500/10 text-purple-400 border border-purple-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <Zap className="h-4 w-4" />
          Resilience Evaluation Benchmark
        </button>
      </div>

      {/* TAB 1: WORK ORDERS */}
      {activeTab === 'work-orders' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            {loadingWO ? (
              <div className="p-8 text-center text-slate-400">Loading Governed Work Orders...</div>
            ) : workOrdersData?.data?.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-400">
                No active work orders. Run a resilience scenario to issue work orders automatically.
              </div>
            ) : (
              workOrdersData?.data?.map((wo: any) => (
                <div key={wo.work_order_id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-emerald-400">{wo.work_order_id}</span>
                        <span className="text-xs text-slate-400">({wo.investigation_id})</span>
                        <span
                          className={`px-2 py-0.5 text-xs rounded-full font-semibold ${
                            wo.status === 'COMPLETED'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : wo.status === 'PARTIAL'
                              ? 'bg-amber-500/20 text-amber-400'
                              : 'bg-blue-500/20 text-blue-400'
                          }`}
                        >
                          {wo.status}
                        </span>
                      </div>
                      <h3 className="text-base font-semibold text-white mt-1">{wo.objective}</h3>
                    </div>
                    <span className="text-xs text-slate-400 font-mono">Assigned Agent: {wo.assigned_agent_id}</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-slate-950 p-3 rounded-lg text-xs">
                    <div>
                      <span className="text-slate-400 block mb-1 font-medium">Permitted Tools:</span>
                      <div className="flex flex-wrap gap-1">
                        {wo.permitted_tools?.map((t: string) => (
                          <span key={t} className="bg-emerald-950 text-emerald-300 border border-emerald-800 px-1.5 py-0.5 rounded">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400 block mb-1 font-medium">Forbidden Actions:</span>
                      <div className="flex flex-wrap gap-1">
                        {wo.forbidden_actions?.map((a: string) => (
                          <span key={a} className="bg-red-950 text-red-300 border border-red-800 px-1.5 py-0.5 rounded">
                            {a}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="text-slate-400 block mb-1 font-medium">Resource Budget:</span>
                      <span className="font-mono text-slate-300">
                        Max Time: {wo.resource_limits?.max_execution_time_ms || 30000}ms
                      </span>
                    </div>
                  </div>

                  {wo.evidence_pack && (
                    <div className="bg-slate-950 border border-slate-800/80 p-3 rounded-lg space-y-2">
                      <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-2">
                        <span className="font-semibold text-cyan-400 flex items-center gap-1">
                          <CheckCircle2 className="h-3.5 w-3.5" /> Validated Evidence Pack Submitted
                        </span>
                        <div className="space-x-3 font-mono">
                          <span>Confidence: <strong className="text-emerald-400">{wo.evidence_pack.confidence}</strong></span>
                          <span>Uncertainty: <strong className="text-amber-400">{wo.evidence_pack.uncertainty}</strong></span>
                        </div>
                      </div>
                      <div className="text-xs text-slate-300">
                        <strong>Claims:</strong> {JSON.stringify(wo.evidence_pack.claims)}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* TAB 2: HUMAN APPROVAL GATE */}
      {activeTab === 'approvals' && (
        <div className="space-y-4">
          <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl flex items-center justify-between text-xs text-amber-300">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-5 w-5 text-amber-400 flex-shrink-0" />
              <span>
                <strong>Response Action Gate Active:</strong> High-impact actions (Account Suspension, Network Isolation, Critical Resource Block) cannot execute without explicit human approval.
              </span>
            </div>
            <span className="bg-amber-950 border border-amber-800 px-2 py-1 rounded font-mono">Mode: SIMULATED_ENFORCEMENT</span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {loadingAppr ? (
              <div className="p-8 text-center text-slate-400">Loading Approval Requests...</div>
            ) : approvalsData?.data?.length === 0 ? (
              <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-xl text-slate-400">
                No approval requests in gate. Run scenario 7 or 8 in the Resilience tab to trigger high-impact approvals.
              </div>
            ) : (
              approvalsData?.data?.map((req: any) => (
                <div key={req.request_id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-amber-400">{req.request_id}</span>
                        <span className="text-xs font-mono text-slate-400">Entity: {req.entity_id}</span>
                        <span
                          className={`px-2 py-0.5 text-xs rounded-full font-bold ${
                            req.status === 'PENDING_APPROVAL'
                              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40 animate-pulse'
                              : req.status === 'APPROVED'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-red-500/20 text-red-400'
                          }`}
                        >
                          {req.status}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-white mt-1">{req.proposed_action}</h3>
                    </div>

                    <div className="text-right text-xs font-mono space-y-1">
                      <div>Risk: <strong className="text-red-400">{req.risk_score}</strong></div>
                      <div>Confidence: <strong className="text-emerald-400">{req.confidence}</strong></div>
                      <div>Uncertainty: <strong className="text-amber-400">{req.uncertainty}</strong></div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-3 rounded-lg text-xs space-y-2 border border-slate-850">
                    <div><strong className="text-slate-400">Justification:</strong> {req.justification}</div>
                    <div><strong className="text-slate-400">Expected Impact:</strong> {req.expected_impact}</div>
                  </div>

                  {req.status === 'PENDING_APPROVAL' ? (
                    <div className="flex items-center gap-3 pt-2">
                      <button
                        onClick={() => approveMutation.mutate(req.request_id)}
                        disabled={approveMutation.isPending}
                        className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-colors"
                      >
                        <CheckCircle2 className="h-4 w-4" /> Approve Action
                      </button>
                      <button
                        onClick={() => rejectMutation.mutate(req.request_id)}
                        disabled={rejectMutation.isPending}
                        className="flex items-center gap-1.5 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-bold transition-colors"
                      >
                        <XCircle className="h-4 w-4" /> Reject Action
                      </button>
                      <button
                        onClick={() => requestEvidenceMutation.mutate(req.request_id)}
                        disabled={requestEvidenceMutation.isPending}
                        className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-bold transition-colors"
                      >
                        <AlertTriangle className="h-4 w-4 text-amber-400" /> Request More Evidence
                      </button>
                    </div>
                  ) : (
                    <div className="text-xs text-slate-400 font-mono bg-slate-950 p-2.5 rounded border border-slate-800 flex items-center justify-between">
                      <span>Approver: <strong className="text-cyan-300">{req.approver_identity}</strong> ({req.approver_role})</span>
                      <span>Execution Status: <strong className="text-emerald-400">{req.execution_status}</strong></span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* TAB 3: AUDIT TRAIL & HASH INTEGRITY */}
      {activeTab === 'audit' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <div className="flex items-center gap-3">
              <div
                className={`p-2 rounded-lg ${
                  auditVerifyData?.data?.valid ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                }`}
              >
                <Hash className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Cryptographic Audit Chain Status</h3>
                <p className="text-xs text-slate-400">
                  {auditVerifyData?.data?.message || 'Verifying SHA-256 hash chain integrity...'}
                </p>
              </div>
            </div>

            <button
              onClick={() => recheckIntegrity()}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs text-white rounded-lg font-medium transition-colors"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Re-Verify Integrity
            </button>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-800 font-semibold text-xs text-slate-400 flex items-center justify-between">
              <span>Append-Only Decision Log ({auditData?.data?.length || 0} Records)</span>
              <span className="text-[10px] text-slate-500 font-mono">SQLite Local Store Notice: Local store protects app transitions</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300 font-mono">
                <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                  <tr>
                    <th className="px-4 py-2.5">Event ID</th>
                    <th className="px-4 py-2.5">Timestamp (UTC)</th>
                    <th className="px-4 py-2.5">Actor</th>
                    <th className="px-4 py-2.5">Event Type</th>
                    <th className="px-4 py-2.5">Rationale / Action</th>
                    <th className="px-4 py-2.5">Record Hash (SHA-256)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {auditData?.data?.map((evt: any) => (
                    <tr key={evt.event_id} className="hover:bg-slate-850/50">
                      <td className="px-4 py-2.5 font-bold text-cyan-400">{evt.event_id}</td>
                      <td className="px-4 py-2.5 text-slate-400">{evt.timestamp}</td>
                      <td className="px-4 py-2.5 text-slate-200">{evt.actor_id} <span className="text-[10px] text-slate-500">({evt.actor_type})</span></td>
                      <td className="px-4 py-2.5 font-semibold text-amber-300">{evt.event_type}</td>
                      <td className="px-4 py-2.5 text-slate-300 max-w-xs truncate">{evt.decision_rationale || evt.proposed_or_executed_action || 'N/A'}</td>
                      <td className="px-4 py-2.5 text-emerald-400 font-mono text-[10px] truncate max-w-[140px]" title={evt.record_hash}>
                        {evt.record_hash}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: INCIDENT EXPLANATION */}
      {activeTab === 'explanation' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 p-3 rounded-xl">
            <Search className="h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={incidentSearchId}
              onChange={(e) => setIncidentSearchId(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-xs text-white w-64"
              placeholder="Enter Incident ID (e.g. INC-001)"
            />
            <button
              onClick={() => fetchExplanation()}
              className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold"
            >
              Generate Explanation
            </button>
          </div>

          {explanationData?.data && (
            <div className="space-y-4">
              {/* Plain Language Summary */}
              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-2">
                <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-wider">Plain-Language Incident Summary</h3>
                <p className="text-sm text-slate-200 leading-relaxed font-sans">{explanationData.data.plain_language_summary}</p>
              </div>

              {/* Likely Hypothesis vs Alternatives */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-900 border border-emerald-500/30 p-4 rounded-xl space-y-2">
                  <span className="text-xs font-bold text-emerald-400 uppercase">Primary Hypothesis (Likely Explanation)</span>
                  <h4 className="text-base font-bold text-white">{explanationData.data.likely_explanation?.hypothesis}</h4>
                  <p className="text-xs text-slate-300">{explanationData.data.likely_explanation?.justification}</p>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-2">
                  <span className="text-xs font-bold text-amber-400 uppercase">Alternative Hypotheses</span>
                  {explanationData.data.alternative_hypotheses?.map((alt: any, idx: number) => (
                    <div key={idx} className="text-xs border-b border-slate-800 pb-2 last:border-0">
                      <strong className="text-slate-200 block">{alt.hypothesis}</strong>
                      <span className="text-slate-400">{alt.justification}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Timeline */}
              <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
                <h3 className="text-sm font-bold text-white">Chronological Event Timeline</h3>
                <div className="space-y-2 font-mono text-xs">
                  {explanationData.data.chronological_timeline?.map((step: any) => (
                    <div key={step.step} className="flex items-center gap-3 bg-slate-950 p-2.5 rounded border border-slate-800">
                      <span className="bg-slate-800 text-cyan-400 px-2 py-0.5 rounded font-bold">{step.step}</span>
                      <span className="text-slate-400">{step.timestamp}</span>
                      <span className="text-amber-300 font-bold">{step.event_type}</span>
                      <span className="text-slate-200 flex-1">{step.summary}</span>
                      <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{step.fact_type}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 5: RESILIENCE EVALUATION BENCHMARK */}
      {activeTab === 'resilience' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between bg-slate-900 border border-purple-500/30 p-5 rounded-xl">
            <div>
              <h2 className="text-lg font-bold text-purple-300 flex items-center gap-2">
                <Zap className="h-5 w-5 text-purple-400" /> Resilience Evaluation Harness
              </h2>
              <p className="text-xs text-slate-400">
                Runs 8 controlled scenarios comparing Baseline (Fixed Rule Alerts) vs. HACTM (Governed Agents + Fusion + Human Gate).
              </p>
            </div>
            <button
              onClick={() => runEvaluationMutation.mutate()}
              disabled={runEvaluationMutation.isPending}
              className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg text-sm transition-colors"
            >
              <Play className="h-4 w-4" /> Run Full 8-Scenario Benchmark
            </button>
          </div>

          {runEvaluationMutation.data?.data && (
            <div className="space-y-6">
              {/* Comparative Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">F1 Score</span>
                  <div className="text-2xl font-bold text-white mt-1">
                    {runEvaluationMutation.data.data.hactm_summary.f1_score}{' '}
                    <span className="text-xs text-emerald-400 font-normal">
                      (vs {runEvaluationMutation.data.data.baseline_summary.f1_score})
                    </span>
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">False Positive Rate</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">
                    {runEvaluationMutation.data.data.hactm_summary.false_positive_rate}{' '}
                    <span className="text-xs text-slate-400 font-normal">
                      (vs {runEvaluationMutation.data.data.baseline_summary.false_positive_rate})
                    </span>
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Bypass Attempts Blocked</span>
                  <div className="text-2xl font-bold text-cyan-400 mt-1">
                    {runEvaluationMutation.data.data.hactm_summary.approval_bypass_attempts_blocked}
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
                  <span className="text-xs text-slate-400">Adversarial Inputs Neutralized</span>
                  <div className="text-2xl font-bold text-purple-400 mt-1">
                    {runEvaluationMutation.data.data.comparative_improvements.adversarial_resilience}
                  </div>
                </div>
              </div>

              {/* Comparative Matrix Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
                <div className="px-4 py-3 border-b border-slate-800 font-bold text-xs text-slate-300">
                  Scenario-by-Scenario Evaluation Outcomes
                </div>
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] font-mono">
                    <tr>
                      <th className="px-4 py-3">Scenario Name</th>
                      <th className="px-4 py-3">Ground Truth</th>
                      <th className="px-4 py-3">Baseline Detection</th>
                      <th className="px-4 py-3">HACTM Prediction</th>
                      <th className="px-4 py-3">Human Gate Effort</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {runEvaluationMutation.data.data.scenario_details?.map((item: any) => (
                      <tr key={item.scenario.id} className="hover:bg-slate-850">
                        <td className="px-4 py-3 font-semibold text-white">{item.scenario.name}</td>
                        <td className="px-4 py-3 font-mono text-cyan-400">{item.scenario.ground_truth_label}</td>
                        <td className="px-4 py-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              item.baseline.predicted_positive ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-400'
                            }`}
                          >
                            {item.baseline.predicted_positive ? 'DETECTED' : 'CLEAN'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              item.hactm.predicted_positive ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-400'
                            }`}
                          >
                            {item.hactm.predicted_positive ? 'GOVERNED DETECT' : 'SAFE'}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-mono text-purple-300">{item.hactm.human_approval_effort_count} Human Review</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
