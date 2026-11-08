# HACTM Central Agent Supervisor (CAS) — Isolation and Recovery Workflow

## 1. Six-Tier Risk-Based Governance Framework

The CAS **Governance and Enforcement Adapter** (`GovernanceAdapter`) operationalizes a structured 6-tier containment hierarchy matching incident risk:

```
Level 0: NORMAL ──► Level 1: OBSERVATION ──► Level 2: WARNING ──► Level 3: RESTRICTED ──► Level 4: ISOLATED ──► Level 5: HUMAN REVIEW
```

| Level | Tier Name | Trigger Condition | Enforcement Action | Autonomous Authority |
|---|---|---|---|---|
| **Level 0** | **Normal** | Zero active anomalies; high health score | Standard monitoring; full capability access | Autonomous |
| **Level 1** | **Observation** | Minor deviation (e.g. slight latency drift) | Ingest high-frequency telemetry; sample rate x2 | Autonomous |
| **Level 2** | **Warning** | Single high-severity anomaly | Issue formal warning event to workspace UI | Autonomous |
| **Level 3** | **Restricted** | Multiple high-severity anomalies or budget breach | Revoke sensitive tools (shell, raw network, exfil) | Autonomous |
| **Level 4** | **Isolated** | Critical anomaly, injection, or forbidden action | Full agent quarantine; cancel active work orders | Autonomous |
| **Level 5** | **Human Review**| Agent isolation or severe security incident | Suspend automated actions; require human authorization | Human Gated |

---

## 2. Quarantine Protocol (Agent Isolation)

When an agent enters Level 4 isolation (`isolate_agent`):

1. **State Registration**: The agent ID is recorded in the authoritative runtime quarantine map `ISOLATED_AGENTS`.
2. **Database Persistence**: An active record is inserted into `cas_isolation_records` (`is_active = 1`).
3. **Gateway Interception**: Any subsequent call to `ToolActivityMonitor.inspect_tool_request` immediately fails with `(False, ISOLATED_AGENT_EXECUTION)`.
4. **Work Order Eviction**: The orchestrator is notified to cancel active work orders assigned to the quarantined agent and initiate task reassignment.
5. **Cryptographic Audit**: An immutable entry is written to the SHA-256 HMAC audit log.
6. **Real-time SSE Notification**: Broadcasts `agent_isolated` event to the Cyber Operations Workspace, rendering the isolation badge and anomaly beacon on the isometric office map.

---

## 3. Investigation Task Reassignment

To ensure uninterrupted incident handling when a specialist agent is isolated during an active investigation:

1. **Orchestrator Eviction**: The `GlobalAdaptiveOrchestrator` unbinds the active work order from the quarantined agent.
2. **Candidate Generation**: The candidate generator filters out all agents marked `ISOLATED` or `RESTRICTED`.
3. **Specialist Reassignment**: An alternate agent possessing overlapping capabilities is selected:
   - If `network_security_analyst` is isolated $\implies$ fallback to `cloud_security_agent` (for cloud flows) or `threat_intel_specialist`.
   - If `phishing_analyst` is isolated $\implies$ fallback to `uba_agent` (for credential/behavior checks) or `threat_intel_specialist`.
4. **Re-issuance of Work Order**: A new Work Order with refreshed cryptographic nonces is issued to the replacement agent.

---

## 4. Multi-Step Recovery and Reinstatement Workflow

An isolated agent cannot self-reinstate. Reinstatement requires a verified three-phase recovery protocol:

```
[ Isolated Agent ]
        │
        ▼ Phase 1: Request Recovery & Challenge Generation
[ Memory & State Sanitization ]
        │
        ▼ Phase 2: Synthetic Verification Challenge Evaluation
[ Zero Trust Gate / Human Authorization ]
        │
        ▼ Phase 3: Formal Reinstatement
[ Active Service Restored (UNDER_OBSERVATION) ]
```

### Phase 1: Sanitization & Audit
- Operator initiates recovery via `POST /api/v1/supervisor/request-recovery`.
- CAS cleans temporary agent execution memory, purges cached prompt fragments, and resets unhandled error counters.

### Phase 2: Human Security Gate
- Operator reviews the anomaly root cause and audit log.
- Human security officer approves reinstatement (`POST /api/v1/supervisor/reinstate`).

### Phase 3: Controlled Restoration
- Agent removed from `ISOLATED_AGENTS` and `REVOKED_CAPABILITIES`.
- Isolation record marked resolved (`is_active = 0`, `reinstated_at = NOW`).
- Agent re-enters the mesh in `UNDER_OBSERVATION` state with probationary telemetry logging for 15 minutes before transitioning to `NORMAL`.

