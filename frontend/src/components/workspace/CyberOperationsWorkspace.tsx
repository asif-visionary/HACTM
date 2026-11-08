/**
 * Master HACTM Cyber Operations Workspace Component.
 * Integrates the interactive Isometric AI-Agent Office with real-time SSE streaming,
 * agent communication ticker, investigation timeline, human approval gate,
 * trust passports, and end-to-end incident demonstration.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  OfficeDepartment,
  WorkspaceAgentState,
  WorkspaceEvent,
  AgentOfficeStatus,
  AgentTrustPassport,
  AgentMessageItem,
  TimelineEntry,
  OfficeDepartmentId,
} from '../../types/workspace';
import { IsometricOfficeCanvas } from './IsometricOfficeCanvas';
import { AgentTrustPassportModal } from './AgentTrustPassportModal';
import { HumanApprovalModal, ApprovalRequestItem } from './HumanApprovalModal';
import { AgentCommunicationPanel } from './AgentCommunicationPanel';
import { InvestigationTimelinePanel } from './InvestigationTimelinePanel';
import { GovernanceDefensePanel } from './GovernanceDefensePanel';
import { CentralAgentSupervisorPanel } from './CentralAgentSupervisorPanel';
import { workspaceEventService, StreamConnectionStatus } from '../../services/workspaceEventService';
import { api } from '../../services/api';
import {
  ShieldAlert,
  ShieldCheck,
  Play,
  Layers,
  MessageSquare,
  Clock,
  Radio,
  RefreshCw,
  Users,
  CheckCircle,
  AlertTriangle,
  FileSearch,
  Sliders,
  ExternalLink,
} from 'lucide-react';
import { SuperIcon } from '../common/SuperIcon';

// Department Layout in Isometric Coordinates
const INITIAL_DEPARTMENTS: OfficeDepartment[] = [
  {
    id: 'command_center',
    name: 'Command Centre',
    code: 'GCC',
    description: 'Central Adaptive Orchestration, Risk Fusion & Governance Hub',
    color: '#00f0ff',
    gridX: -3,
    gridY: -3,
    width: 6,
    height: 6,
    activeAgentsCount: 1,
    totalAlerts: 0,
  },
  {
    id: 'network_ops',
    name: 'Network Operations',
    code: 'NET',
    description: 'Flow Anomaly, Sliding Window Scan & Intrusion Detection',
    color: '#0ea5e9',
    gridX: -11,
    gridY: -10,
    width: 6,
    height: 5,
    activeAgentsCount: 1,
    totalAlerts: 0,
  },
  {
    id: 'phishing_intel',
    name: 'Phishing Intelligence',
    code: 'PHISH',
    description: 'Email Header Forensics, Lookalike URL & NLP Classifier',
    color: '#38bdf8',
    gridX: 5,
    gridY: -10,
    width: 6,
    height: 5,
    activeAgentsCount: 1,
    totalAlerts: 1,
  },
  {
    id: 'identity_sec',
    name: 'Identity Security',
    code: 'AUTH',
    description: 'Brute-Force Velocity, ATO Detection & Impossible Travel',
    color: '#8b5cf6',
    gridX: -11,
    gridY: 5,
    width: 6,
    height: 5,
    activeAgentsCount: 1,
    totalAlerts: 0,
  },
  {
    id: 'behaviour_intel',
    name: 'Behaviour Intelligence',
    code: 'UBA',
    description: 'User Historical Baseline, Exfiltration & Deviation Analysis',
    color: '#f59e0b',
    gridX: 5,
    gridY: 5,
    width: 6,
    height: 5,
    activeAgentsCount: 1,
    totalAlerts: 0,
  },
  {
    id: 'transaction_sec',
    name: 'Transaction Security',
    code: 'TXN',
    description: 'Financial Transaction Velocity & Anomaly Verification',
    color: '#f43f5e',
    gridX: -3,
    gridY: 6,
    width: 6,
    height: 5,
    activeAgentsCount: 1,
    totalAlerts: 0,
  },
  {
    id: 'governance_trust',
    name: 'AI Trust & Governance',
    code: 'GOV',
    description: 'Agent Trust Passport, Tool Authorization & Human Approvals',
    color: '#10b981',
    gridX: -3,
    gridY: -11,
    width: 6,
    height: 5,
    activeAgentsCount: 1,
    totalAlerts: 0,
  },
];

// Initial Real HACTM Agents Data
const INITIAL_AGENTS: WorkspaceAgentState[] = [
  {
    agent_id: 'global-orchestrator',
    name: 'Global Adaptive Orchestrator',
    shortName: 'ORCH',
    departmentId: 'command_center',
    status: 'IDLE',
    currentTask: 'Supervising Hierarchical Cyber Trust Mesh',
    deskPosition: { gridX: 0, gridY: 0 },
    facing: 'SE',
    avatarColor: '#0f172a',
    accentColor: '#00f0ff',
    reliabilityScore: 0.99,
    isIsolated: false,
    lastActiveTimestamp: new Date().toISOString(),
    eventsProcessed: 1420,
    detectionsCount: 88,
    toolPermissions: ['work_order_dispatch', 'evidence_pack_validator', 'candidate_generator'],
  },
  {
    agent_id: 'network-security-agent',
    name: 'Network Security Agent',
    shortName: 'NET',
    departmentId: 'network_ops',
    status: 'IDLE',
    currentTask: 'Ingress flow monitoring and port scan telemetry',
    deskPosition: { gridX: -8, gridY: -8 },
    facing: 'SE',
    avatarColor: '#0f172a',
    accentColor: '#0ea5e9',
    reliabilityScore: 0.91,
    isIsolated: false,
    lastActiveTimestamp: new Date().toISOString(),
    eventsProcessed: 940,
    detectionsCount: 42,
    toolPermissions: ['network_flow_analyzer', 'port_scan_detector'],
  },
  {
    agent_id: 'phishing-intelligence-agent',
    name: 'Phishing Intelligence Agent',
    shortName: 'PHISH',
    departmentId: 'phishing_intel',
    status: 'IDLE',
    currentTask: 'Email stream inspection & URL feature extraction',
    deskPosition: { gridX: 8, gridY: -8 },
    facing: 'SW',
    avatarColor: '#0f172a',
    accentColor: '#38bdf8',
    reliabilityScore: 0.86,
    isIsolated: false,
    lastActiveTimestamp: new Date().toISOString(),
    eventsProcessed: 680,
    detectionsCount: 29,
    toolPermissions: ['email_header_parser', 'url_feature_extractor', 'double_extension_detector'],
  },
  {
    agent_id: 'identity-authentication-agent',
    name: 'Identity & Auth Agent',
    shortName: 'AUTH',
    departmentId: 'identity_sec',
    status: 'IDLE',
    currentTask: 'Authentication velocity & Haversine geo tracking',
    deskPosition: { gridX: -8, gridY: 7 },
    facing: 'NE',
    avatarColor: '#0f172a',
    accentColor: '#8b5cf6',
    reliabilityScore: 0.94,
    isIsolated: false,
    lastActiveTimestamp: new Date().toISOString(),
    eventsProcessed: 520,
    detectionsCount: 18,
    toolPermissions: ['auth_velocity_tracker', 'haversine_geo_evaluator'],
  },
  {
    agent_id: 'uba-agent',
    name: 'Behaviour Intelligence Agent',
    shortName: 'UBA',
    departmentId: 'behaviour_intel',
    status: 'IDLE',
    currentTask: 'Historical user profile baselines & data movement',
    deskPosition: { gridX: 8, gridY: 7 },
    facing: 'NW',
    avatarColor: '#0f172a',
    accentColor: '#f59e0b',
    reliabilityScore: 0.88,
    isIsolated: false,
    lastActiveTimestamp: new Date().toISOString(),
    eventsProcessed: 410,
    detectionsCount: 15,
    toolPermissions: ['user_profile_calculator', 'zscore_anomaly_evaluator'],
  },
  {
    agent_id: 'transaction-security-agent',
    name: 'Transaction Security Agent',
    shortName: 'TXN',
    departmentId: 'transaction_sec',
    status: 'IDLE',
    currentTask: 'Payment velocity & amount anomaly detection',
    deskPosition: { gridX: 0, gridY: 8 },
    facing: 'NE',
    avatarColor: '#0f172a',
    accentColor: '#f43f5e',
    reliabilityScore: 0.89,
    isIsolated: false,
    lastActiveTimestamp: new Date().toISOString(),
    eventsProcessed: 320,
    detectionsCount: 11,
    toolPermissions: ['transaction_velocity_tracker', 'amount_anomaly_detector'],
  },
];

export const CyberOperationsWorkspace: React.FC = () => {
  // State
  const [agents, setAgents] = useState<WorkspaceAgentState[]>(INITIAL_AGENTS);
  const [departments] = useState<OfficeDepartment[]>(INITIAL_DEPARTMENTS);
  const [streamStatus, setStreamStatus] = useState<StreamConnectionStatus>('DISCONNECTED');
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [activeTrustPassport, setActiveTrustPassport] = useState<AgentTrustPassport | null>(null);
  const [activeApprovalRequest, setActiveApprovalRequest] = useState<ApprovalRequestItem | null>(null);
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);
  const [currentIncidentId, setCurrentIncidentId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'office' | 'supervisor' | 'timeline' | 'comms' | 'governance'>('supervisor');
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [isTogglingIsolation, setIsTogglingIsolation] = useState<boolean>(false);

  // Communications & Timeline states
  const [messages, setMessages] = useState<AgentMessageItem[]>([]);
  const [timeline, setTimeline] = useState<TimelineEntry[]>([]);

  // Load Passports and Pending Approvals on Mount
  const refreshPassports = useCallback(async () => {
    try {
      const passports = await api.getTrustPassports();
      if (passports && Array.isArray(passports)) {
        setAgents((prev) =>
          prev.map((ag) => {
            const p = passports.find((item: any) => item.agent_id === ag.agent_id);
            if (p) {
              return {
                ...ag,
                name: p.agent_name,
                status: p.is_isolated ? 'ISOLATED' : ag.status,
                reliabilityScore: p.reliability_score || ag.reliabilityScore,
                isIsolated: p.is_isolated,
                isolationReason: p.isolation_reason,
                eventsProcessed: p.events_processed || ag.eventsProcessed,
                detectionsCount: p.detections_generated || ag.detectionsCount,
                toolPermissions: p.tool_permissions || ag.toolPermissions,
              };
            }
            return ag;
          })
        );
      }
    } catch (err) {
      console.warn('Could not refresh passports from backend:', err);
    }
  }, []);

  const refreshPendingApprovals = useCallback(async () => {
    try {
      const res = await api.getApprovalRequests('PENDING_APPROVAL');
      const items = res?.data || [];
      setPendingApprovalsCount(items.length);
      if (items.length > 0 && !activeApprovalRequest) {
        setActiveApprovalRequest(items[0]);
      }
    } catch (err) {
      console.warn('Could not fetch approval requests:', err);
    }
  }, [activeApprovalRequest]);

  // Connect SSE Stream & Handle Real Events
  useEffect(() => {
    workspaceEventService.connect();

    const unsubStatus = workspaceEventService.onStatusChange((status) => {
      setStreamStatus(status);
    });

    const unsubEvents = workspaceEventService.onEvent((event: WorkspaceEvent) => {
      handleRealEvent(event);
    });

    refreshPassports();
    refreshPendingApprovals();

    return () => {
      unsubStatus();
      unsubEvents();
      workspaceEventService.disconnect();
    };
  }, [refreshPassports, refreshPendingApprovals]);

  // Handle incoming real-time backend event
  const handleRealEvent = (evt: WorkspaceEvent) => {
    if (evt.incident_id) {
      setCurrentIncidentId(evt.incident_id);
    }

    // 1. Update Agent Status
    if (evt.agent_id && evt.status) {
      setAgents((prev) =>
        prev.map((a) => {
          if (a.agent_id === evt.agent_id) {
            return {
              ...a,
              status: evt.status as AgentOfficeStatus,
              currentTask: evt.message,
              lastMessage: evt.message,
              lastActiveTimestamp: evt.timestamp,
              isIsolated: evt.status === 'ISOLATED' ? true : a.isIsolated,
            };
          }
          return a;
        })
      );
    }

    // 2. Append Timeline Entry
    const newTimelineEntry: TimelineEntry = {
      id: evt.event_id || `TL-${Date.now()}`,
      step: evt.event_type,
      title: evt.event_type.replace(/_/g, ' ').toUpperCase(),
      description: evt.message,
      timestamp: evt.timestamp,
      status: evt.event_type.includes('denied') || evt.event_type.includes('isolated')
        ? 'BLOCKED'
        : evt.event_type.includes('requested')
        ? 'ALERT'
        : 'COMPLETED',
      incidentId: evt.incident_id,
      agentId: evt.agent_id,
      evidenceId: evt.data?.evidence_id,
      riskScore: evt.data?.risk_score,
    };
    setTimeline((prev) => [newTimelineEntry, ...prev.slice(0, 49)]);

    // 3. Append to Communications if agent message
    if (evt.event_type === 'agent_message' || evt.event_type === 'task_assigned') {
      const msgItem: AgentMessageItem = {
        id: evt.event_id || `MSG-${Date.now()}`,
        sender: evt.data?.sender || evt.agent_id || 'System',
        recipient: evt.data?.recipient || 'global-orchestrator',
        incidentId: evt.incident_id,
        taskId: evt.task_id,
        message: evt.message,
        evidenceRef: evt.data?.evidence_ref,
        timestamp: evt.timestamp,
        status: (evt.status as AgentOfficeStatus) || 'COMMUNICATING',
      };
      setMessages((prev) => [msgItem, ...prev.slice(0, 49)]);
    }

    // 4. Handle Human Approval Notification
    if (evt.event_type === 'approval_requested') {
      refreshPendingApprovals();
      if (evt.data?.request_id) {
        setActiveApprovalRequest({
          request_id: evt.data.request_id,
          incident_id: evt.incident_id || 'INC-LIVE',
          entity_id: evt.data.entity_id || 'user@enterprise.internal',
          policy_id: 'POL-ZERO-TRUST-001',
          action_type: evt.data.action || 'ISOLATE_ACCOUNT_AND_REVOKE_SESSIONS',
          proposed_action: evt.message,
          risk_score: evt.data.risk_score || 0.88,
          confidence: 0.94,
          uncertainty: 0.06,
          is_high_impact: 1,
          justification: 'High-risk phishing campaign with executable attachment detected.',
          status: 'PENDING_APPROVAL',
          created_at: evt.timestamp,
        });
      }
    }
  };

  // Open Trust Passport for an Agent
  const handleSelectAgent = async (agentId: string) => {
    setSelectedAgentId(agentId);
    try {
      const passport = await api.getTrustPassport(agentId);
      setActiveTrustPassport(passport);
    } catch (err) {
      console.warn('Could not fetch specific passport:', err);
      // Fallback from local state
      const ag = agents.find((a) => a.agent_id === agentId);
      if (ag) {
        setActiveTrustPassport({
          agent_id: ag.agent_id,
          agent_name: ag.name,
          department: ag.departmentId,
          agent_type: 'Autonomous Cyber Agent',
          model_and_version: 'HACTM-v1.0.0',
          current_status: ag.status,
          allowed_capabilities: ag.toolPermissions,
          tool_permissions: ag.toolPermissions,
          tenant_scope: 'enterprise_primary',
          reliability_score: ag.reliabilityScore,
          drift_status: 'STABLE',
          calibration_status: 'CALIBRATED',
          health_status: 'OPERATIONAL',
          average_latency_ms: 120.0,
          events_processed: ag.eventsProcessed,
          detections_generated: ag.detectionsCount,
          active_detectors: ['AnomalyDetector', 'SignatureDetector'],
          violation_history: [],
          last_activity: ag.lastActiveTimestamp,
          is_isolated: ag.isIsolated,
          revoked_capabilities: [],
        });
      }
    }
  };

  // Run Phishing Incident Demonstration (Section 13)
  const handleRunDemoIncident = async () => {
    setIsSimulating(true);
    try {
      await api.simulateDemoIncident({
        scenario: 'PHISHING_CREDENTIAL_HARVESTING',
        sender: 'security-alert@micros0ft-support.ru',
        subject: 'URGENT: Microsoft 365 Password Expiration in 1 Hour',
        target_user: 'cfo@hactm-enterprise.internal',
        suspicious_url: 'https://micros0ft-login-verify.ru/token-update',
        attachment_name: 'Corporate_Invoice_Overdue.pdf.exe',
      });
      await refreshPendingApprovals();
    } catch (err: any) {
      console.error('Demo simulation error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  // Defensive Agent Isolation Toggle
  const handleToggleIsolation = async (
    agentId: string,
    action: 'ISOLATE' | 'REINSTATE',
    reason: string
  ) => {
    setIsTogglingIsolation(true);
    try {
      await api.toggleAgentIsolation({
        agent_id: agentId,
        action,
        reason,
        operator_role: 'SECURITY_OPERATOR',
      });
      await refreshPassports();
      if (activeTrustPassport?.agent_id === agentId) {
        const updated = await api.getTrustPassport(agentId);
        setActiveTrustPassport(updated);
      }
    } catch (err: any) {
      console.error('Failed to toggle isolation:', err);
    } finally {
      setIsTogglingIsolation(false);
    }
  };

  // Human Approval Handlers
  const handleApprove = async (requestId: string, notes: string, approverRole: string) => {
    await api.approveAction({
      request_id: requestId,
      approver_identity: 'sec_operator_lead',
      approver_role: approverRole || 'SECURITY_OPERATOR',
      notes,
    });
    setPendingApprovalsCount((prev) => Math.max(0, prev - 1));
    setActiveApprovalRequest(null);
  };

  const handleReject = async (requestId: string, notes: string, approverRole: string) => {
    await api.rejectAction({
      request_id: requestId,
      approver_identity: 'sec_operator_lead',
      approver_role: approverRole || 'SECURITY_OPERATOR',
      notes,
    });
    setPendingApprovalsCount((prev) => Math.max(0, prev - 1));
    setActiveApprovalRequest(null);
  };

  const handleRequestEvidence = async (requestId: string, notes: string, approverRole: string) => {
    await api.requestMoreEvidence({
      request_id: requestId,
      approver_identity: 'sec_operator_lead',
      approver_role: approverRole || 'SECURITY_OPERATOR',
      notes,
    });
    setActiveApprovalRequest(null);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-[#070a13] text-slate-100 overflow-hidden">
      {/* Top Cyber Command Control Bar */}
      <header className="flex-shrink-0 flex items-center justify-between px-5 py-2.5 bg-slate-900/90 border-b border-slate-800 backdrop-blur z-20">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-1.5 bg-cyan-500/20 text-cyan-400 rounded-lg flex items-center justify-center">
              <SuperIcon name="agent-loop" style="color" size={20} alt="HACTM Logo" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white tracking-wider flex items-center space-x-2">
                <span>HACTM CYBER OPERATIONS WORKSPACE</span>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800 rounded">
                  ISOMETRIC AI OFFICE
                </span>
              </h1>
              <p className="text-[11px] text-slate-400 font-mono">
                Unified AI Agent Operations, Centralised Supervision and Cyber Trust Governance
              </p>
            </div>
          </div>

          {/* Connection Status Pill */}
          <div className="hidden md:flex items-center space-x-2 px-2.5 py-1 rounded-full bg-slate-950 border border-slate-800 text-[11px] font-mono">
            <span
              className={`w-2 h-2 rounded-full ${
                streamStatus === 'CONNECTED'
                  ? 'bg-emerald-400 shadow-sm shadow-emerald-400'
                  : streamStatus === 'CONNECTING' || streamStatus === 'RECONNECTING'
                  ? 'bg-amber-400 animate-pulse'
                  : 'bg-red-400'
              }`}
            />
            <span className="text-slate-300">{streamStatus}</span>
          </div>
        </div>

        {/* Action Controls & Gated Approval Badge */}
        <div className="flex items-center space-x-3">
          {/* Quick Central Agent Supervisor Toggle */}
          <button
            onClick={() => setActiveTab(activeTab === 'supervisor' ? 'office' : 'supervisor')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
              activeTab === 'supervisor'
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-md shadow-amber-500/20'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <SuperIcon name="monitoring" style="color" size={15} className="mr-0.5" />
            <span>CENTRAL SUPERVISOR</span>
          </button>

          {/* Pending Approval Gate Alert */}
          {pendingApprovalsCount > 0 && (
            <button
              onClick={() => {
                refreshPendingApprovals();
              }}
              className="flex items-center space-x-2 px-3 py-1.5 bg-amber-500/20 border border-amber-500/50 text-amber-300 rounded-lg text-xs font-semibold animate-pulse hover:bg-amber-500/30 transition shadow-lg shadow-amber-500/10"
            >
              <SuperIcon name="human-approval" style="color" size={15} className="mr-0.5" />
              <span>{pendingApprovalsCount} GATED APPROVAL PENDING</span>
            </button>
          )}

          {/* End-to-End Phishing Demo Button (Section 13) */}
          <button
            disabled={isSimulating}
            onClick={handleRunDemoIncident}
            className="flex items-center space-x-2 px-3.5 py-1.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-semibold transition shadow-lg shadow-cyan-500/20 active:scale-95 disabled:opacity-50"
          >
            <SuperIcon name="agent" style="duotone" size={14} className="mr-0.5" />
            <span>{isSimulating ? 'Simulating Incident…' : 'Run Phishing Investigation Demo'}</span>
          </button>
        </div>
      </header>

      {/* Main Workspace Body */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden relative">
        {/* Primary Viewport: Isometric Canvas Office */}
        <div className="flex-1 relative flex flex-col h-full bg-[#070a13] border-b lg:border-b-0 lg:border-r border-slate-800">
          <IsometricOfficeCanvas
            agents={agents}
            departments={departments}
            selectedAgentId={selectedAgentId}
            onSelectAgent={handleSelectAgent}
            onSelectDepartment={(deptId) => {
              console.log('Selected department:', deptId);
            }}
            onSelectSupervisorStation={() => setActiveTab('supervisor')}
            highlightedIncidentId={currentIncidentId}
          />
        </div>

        {/* Right Collapsible Interactive Operations Panel */}
        <div className={`flex-shrink-0 flex flex-col h-full bg-slate-950 border-slate-800 overflow-hidden transition-all duration-300 ${activeTab === 'supervisor' ? 'w-full lg:w-[620px]' : 'w-full lg:w-[420px]'}`}>
          {/* Panel Tab Navigation */}
          <div className="flex border-b border-slate-800 bg-slate-900/60 p-1 gap-1">
            <button
              onClick={() => setActiveTab('supervisor')}
              className={`flex-1 py-1.5 text-xs font-semibold rounded transition flex items-center justify-center space-x-1.5 ${
                activeTab === 'supervisor'
                  ? 'bg-amber-950/80 text-amber-300 border border-amber-500/50 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <SuperIcon name="monitoring" style="color" size={14} />
              <span>Supervisor</span>
            </button>
            <button
              onClick={() => setActiveTab('office')}
              className={`flex-1 py-1.5 text-xs font-medium rounded transition flex items-center justify-center space-x-1.5 ${
                activeTab === 'office'
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <SuperIcon name="agent" style="duotone" size={14} />
              <span>Agents</span>
            </button>
            <button
              onClick={() => setActiveTab('timeline')}
              className={`flex-1 py-1.5 text-xs font-medium rounded transition flex items-center justify-center space-x-1.5 ${
                activeTab === 'timeline'
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <SuperIcon name="task" style="duotone" size={14} />
              <span>Timeline</span>
            </button>
            <button
              onClick={() => setActiveTab('comms')}
              className={`flex-1 py-1.5 text-xs font-medium rounded transition flex items-center justify-center space-x-1.5 ${
                activeTab === 'comms'
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <SuperIcon name="a2a" style="duotone" size={14} />
              <span>Handoff</span>
            </button>
            <button
              onClick={() => setActiveTab('governance')}
              className={`flex-1 py-1.5 text-xs font-medium rounded transition flex items-center justify-center space-x-1.5 ${
                activeTab === 'governance'
                  ? 'bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <SuperIcon name="permissions" style="duotone" size={14} />
              <span>Defense</span>
            </button>
          </div>

          {/* Panel Content Display */}
          <div className="flex-1 overflow-hidden p-3">
            {activeTab === 'supervisor' && (
              <div className="h-full overflow-y-auto pr-1">
                <CentralAgentSupervisorPanel
                  onSelectAgent={handleSelectAgent}
                  onRefreshWorkspace={refreshPassports}
                />
              </div>
            )}
            {activeTab === 'office' && (
              <div className="h-full flex flex-col space-y-3 overflow-y-auto pr-1">
                <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                  <span>REGISTERED MESH AGENTS</span>
                  <span className="font-mono">{agents.length} DEPLOYED</span>
                </div>

                {agents.map((ag) => (
                  <div
                    key={ag.agent_id}
                    onClick={() => handleSelectAgent(ag.agent_id)}
                    className={`p-3 rounded-lg border cursor-pointer transition ${
                      selectedAgentId === ag.agent_id
                        ? 'bg-slate-800/90 border-cyan-500 shadow-md shadow-cyan-500/10'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5">
                        <SuperIcon
                          name={ag.agent_id.includes('orchestrator') ? 'orchestration' : 'agent'}
                          style={ag.isIsolated ? 'color' : 'duotone'}
                          size={15}
                        />
                        <span className="font-bold text-slate-100 text-xs">{ag.name}</span>
                      </div>
                      <span
                        className={`px-2 py-0.5 text-[10px] font-semibold rounded font-mono uppercase ${
                          ag.status === 'ISOLATED'
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                            : ag.status === 'ANALYSING'
                            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {ag.status}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                      {ag.currentTask || 'Idle at designated workstation.'}
                    </p>

                    <div className="mt-2 flex items-center justify-between text-[10px] font-mono text-slate-400 pt-1.5 border-t border-slate-800">
                      <span>RELIABILITY: {(ag.reliabilityScore * 100).toFixed(0)}%</span>
                      <span className="text-cyan-400 flex items-center space-x-1">
                        <span>Inspect Passport</span>
                        <ExternalLink size={10} />
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'timeline' && (
              <InvestigationTimelinePanel
                timeline={timeline}
                currentIncidentId={currentIncidentId}
                onSelectEvidence={(evId) => {
                  console.log('Selected evidence:', evId);
                }}
              />
            )}

            {activeTab === 'comms' && (
              <AgentCommunicationPanel
                messages={messages}
                selectedAgentId={selectedAgentId}
                onSelectEvidence={(evId) => {
                  console.log('Selected evidence:', evId);
                }}
              />
            )}

            {activeTab === 'governance' && (
              <GovernanceDefensePanel
                agents={agents}
                onToggleIsolation={handleToggleIsolation}
                onRefreshPassports={refreshPassports}
              />
            )}
          </div>
        </div>
      </div>

      {/* Trust Passport Dialog Modal */}
      {activeTrustPassport && (
        <AgentTrustPassportModal
          passport={activeTrustPassport}
          agentState={agents.find((a) => a.agent_id === activeTrustPassport.agent_id) || null}
          onClose={() => setActiveTrustPassport(null)}
          onToggleIsolation={handleToggleIsolation}
          isToggling={isTogglingIsolation}
        />
      )}

      {/* Human Approval Gate Dialog Modal */}
      {activeApprovalRequest && (
        <HumanApprovalModal
          request={activeApprovalRequest}
          onClose={() => setActiveApprovalRequest(null)}
          onApprove={handleApprove}
          onReject={handleReject}
          onRequestEvidence={handleRequestEvidence}
        />
      )}
    </div>
  );
};
