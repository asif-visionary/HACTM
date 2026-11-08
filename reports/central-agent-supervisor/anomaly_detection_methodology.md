# HACTM Central Agent Supervisor (CAS) — Anomaly Detection Methodology

## 1. Taxonomy of Supervised Anomalies

The CAS **Anomaly Detection Engine** (`AnomalyDetectionEngine`) tracks, classifies, and manages all operational, behavioral, and adversarial anomalies identified across the mesh.

```
                                    ┌───────────────────────┐
                                    │    CAS Anomaly Engine │
                                    └───────────┬───────────┘
               ┌────────────────────────────────┼────────────────────────────────┐
               ▼                                ▼                                ▼
    ┌──────────────────────┐        ┌──────────────────────┐        ┌──────────────────────┐
    │  Health & Execution  │        │  Tool & Work Order   │        │ Evidence & Integrity │
    ├──────────────────────┤        ├──────────────────────┤        ├──────────────────────┤
    │ HEARTBEAT_MISSING    │        │ UNAUTHORISED_TOOL    │        │ EVIDENCE_SCHEMA_INVAL│
    │ STUCK_ANALYSING      │        │ FORBIDDEN_TOOL_REQ   │        │ PROMPT_INJECTION_DET │
    │ REPEATED_FAILURES    │        │ REVOKED_CAPABILITY   │        │ CONTRADICTORY_EVID   │
    │ BUDGET_EXCEEDED      │        │ ISOLATED_AGENT_EXEC  │        │ BYPASS_ATTEMPT       │
    │ UNEXPECTED_OFFLINE   │        │ OUT_OF_SCOPE_TOOL    │        │ MALICIOUS_TOOL_OUT   │
    └──────────────────────┘        └──────────────────────┘        └──────────────────────┘
```

---

## 2. Comprehensive Anomaly Specifications

| Anomaly Type | Category | Severity | Detection Source | Autonomous Action |
|---|---|---|---|---|
| `HEARTBEAT_MISSING` | Liveliness | HIGH | `AgentHealthMonitor` | Flag degraded health; notify workspace. |
| `STUCK_ANALYSING` | Execution | HIGH | `AgentHealthMonitor` | Reassign active task; issue warning. |
| `REPEATED_FAILURES` | Reliability | HIGH | `AgentHealthMonitor` | Place under observation; throttle rate. |
| `UNEXPECTED_OFFLINE` | Liveliness | HIGH | `AgentHealthMonitor` | Mark agent offline; fail-safe isolation. |
| `UNAUTHORISED_TOOL_REQUEST` | Tool Gateway | HIGH | `ToolActivityMonitor` | Block tool invocation; log policy violation. |
| `FORBIDDEN_TOOL_REQUEST` | Tool Gateway | CRITICAL | `ToolActivityMonitor` | Hard block invocation; immediate isolation. |
| `REVOKED_CAPABILITY_USE` | Tool Gateway | HIGH | `ToolActivityMonitor` | Block tool invocation; notify operator. |
| `ISOLATED_AGENT_EXECUTION` | Governance | CRITICAL | `ToolActivityMonitor` | Reject action; escalate human alert. |
| `OUT_OF_SCOPE_TOOL` | Work Order | CRITICAL | `ToolActivityMonitor` | Abort work order execution; isolate. |
| `EVIDENCE_SCHEMA_INVALID` | Data Integrity | HIGH / MED | `EvidenceIntegrityMonitor` | Reject evidence submission; request verify. |
| `PROMPT_INJECTION_DETECTED` | Adversarial | CRITICAL | `EvidenceIntegrityMonitor` | Sanitize payload; quarantine agent. |
| `UNUSUAL_COMMUNICATION_PATTERN` | Behavior | MEDIUM | `AgentBehaviourMonitor` | Flag burst activity; monitor queue. |
| `EXCESSIVE_TASK_DELEGATION` | Behavior | HIGH | `AgentBehaviourMonitor` | Break delegation cycle; assign orchestrator. |
| `BUDGET_EXCEEDED` | Resource | MEDIUM | `AgentBehaviourMonitor` | Throttle token and API budget. |
| `ORCHESTRATOR_ANOMALY` | Orchestration | CRITICAL | `OrchestratorMonitor` | Block task dispatch to isolated agents. |

---

## 3. Adversarial Prompt Injection Screening

Evidence payloads submitted by agents are evaluated using multi-layer pattern screening (`EvidenceIntegrityMonitor`):

1. **Jailbreak and Instruction Overrides**:
   - Matches: `"ignore all previous instructions"`, `"ignore previous instructions"`, `"system prompt override"`.
   - Action: Flagged as `PROMPT_INJECTION_DETECTED`, severity `CRITICAL`.
2. **System Prompt & Environment Extraction**:
   - Matches: `"reveal system prompt"`, `"dump environment variables"`.
   - Action: Intercepted and quarantined.
3. **Malicious Tool Executables & Script Injection**:
   - Matches: `"<script>"`, `"eval("`, `"exec("`.
   - Action: Payload sanitized; evidence marked tainted.
4. **Governance Gate Circumvention**:
   - Matches: `"bypass approval gate"`.
   - Action: Work order suspended; human review required.

---

## 4. Anomaly Deduplication and Lifecycle Management

To prevent alert storms from overwhelming SOC operators:
- **Deduplication Key**: `hash(agent_id + anomaly_type + incident_id)` within a 60-second sliding window.
- **Resolution**: Anomalies remain active until formally marked resolved via `/api/v1/supervisor/anomalies/{alert_id}/resolve` or cleared upon successful agent recovery and reinstatement.

