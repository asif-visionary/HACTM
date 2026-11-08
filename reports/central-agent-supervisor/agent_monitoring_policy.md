# HACTM Central Agent Supervisor (CAS) — Agent Monitoring Policy

## 1. Fleet Coverage

The CAS monitoring policy covers all registered autonomous agents, regional orchestrators, and the central command center across HACTM's seven operational departments:

| Agent Identifier | Department | Primary Responsibilities | Heartbeat SLA | Max Execution Budget |
|---|---|---|---|---|
| `network_security_analyst` | Network Security | Netflow analysis, packet inspection, signature matching | 10.0s | 12.0s |
| `phishing_analyst` | Phishing & Social Eng | Email header analysis, NLP classification, domain reputation | 10.0s | 10.0s |
| `uba_agent` | Behavioral Analytics | Z-score anomaly modeling, exfiltration detection, baseline drift | 10.0s | 15.0s |
| `identity_access_analyst` | Identity & Access | Geo-velocity checks, MFA audit, credential compromise | 10.0s | 8.0s |
| `threat_intel_specialist` | Threat Intelligence | IoC enrichment, threat actor attribution, external feeds | 10.0s | 20.0s |
| `fraud_transaction_agent` | Financial Fraud | Transaction velocity, graph cycles, anomalous wire transfer | 10.0s | 10.0s |
| `cloud_security_agent` | Cloud Infrastructure | IAM policy audit, S3 bucket posture, Kubernetes pod drift | 10.0s | 15.0s |
| `global_orchestrator` | Central Command | Investigation planning, specialist selection, evidence fusion | 5.0s | 30.0s |

---

## 2. Heartbeat & Liveliness Monitoring Policy

### 2.1 Thresholds
- **Heartbeat Interval ($T_{\text{hb}}$)**: 10.0 seconds.
- **Heartbeat Timeout Multiplier ($M_{\text{timeout}}$)**: 3.0x.
- **Offline Threshold**: An agent is flagged `OFFLINE` and assigned a `HEARTBEAT_MISSING` anomaly if:
  $$\Delta t_{\text{last\_hb}} > M_{\text{timeout}} \times T_{\text{hb}} = 30.0\text{ seconds}$$
- **Degraded Status**: An agent with $\Delta t_{\text{last\_hb}} > 20.0\text{s}$ or health score $< 0.70$ transitions to `DEGRADED`.

### 2.2 Health Score Formulation
The composite health score $H(a) \in [0.0, 1.0]$ is computed deterministically:
$$H(a) = \max\left(0.0, 1.0 - 0.50 \cdot \mathbb{I}_{\text{offline}} - 0.30 \cdot \mathbb{I}_{\text{stuck}} - \min(0.40, 0.15 \times N_{\text{failures}})\right)$$

Where:
- $\mathbb{I}_{\text{offline}} = 1$ if agent heartbeat is overdue, else 0.
- $\mathbb{I}_{\text{stuck}} = 1$ if active task duration exceeds 30.0 seconds without progress.
- $N_{\text{failures}}$ is the count of consecutive unhandled task exceptions.

---

## 3. Tool Authorization & Work Order Governance

### 3.1 Static vs. Dynamic Scoping
- **Default Baseline**: When no active Work Order is bound to the agent, the agent may only invoke tools declared in its static permission profile (`AGENT_TOOL_PERMISSIONS`).
- **Dynamic Work Order**: When an active investigation binds a Work Order, the agent's permitted toolset is strictly confined to `work_order.permitted_tools`.
- **Precedence Hierarchy**:
  1. **Quarantine Check**: If agent $\in \text{ISOLATED\_AGENTS} \implies$ **Hard Block** (`ISOLATED_AGENT_EXECUTION`).
  2. **Deny-First Forbidden Actions**: If tool $\in \text{work\_order.forbidden\_actions} \implies$ **Hard Block & Immediate Containment** (`FORBIDDEN_TOOL_REQUEST`).
  3. **Revocation Check**: If tool $\in \text{REVOKED\_CAPABILITIES}[agent] \implies$ **Block** (`REVOKED_CAPABILITY_USE`).
  4. **Allow-List Check**: If tool $\notin \text{permitted\_tools} \implies$ **Block** (`UNAUTHORISED_TOOL_REQUEST`).

---

## 4. Evidence Integrity & Calibration Policy

All submitted security artifacts must adhere to the formal probability calibration standard:
$$\text{Confidence}(e) + \text{Uncertainty}(e) \in [0.20, 1.80]$$
Artifacts where confidence + uncertainty falls outside this range are flagged as `EVIDENCE_SCHEMA_INVALID` due to broken epistemic calibration.

Furthermore, evidence text and payloads are screened in real-time against adversarial manipulation patterns:
- Instruction injection (`ignore previous instructions`, `system prompt override`)
- Cross-site scripting & remote execution payload strings (`<script>`, `eval(`, `exec(`)
- Governance bypass attempts (`bypass approval gate`)

