# HACTM Central Agent Supervisor (CAS) — Trust Evaluation Methodology

## 1. Overview of Seven-Tier Trust Model

Unlike black-box reputation systems, the HACTM CAS **Agent Trust Evaluator** (`AgentTrustEvaluator`) implements a mathematically transparent, auditable evaluation model. Every agent is categorized into one of seven formal trust states:

```
  ┌─────────┐       Zero Anomalies & High Health
  │ TRUSTED │ ◄───────────────────────────────────────┐
  └────┬────┘                                         │
       │ Normal Operational Baseline                  │
       ▼                                              │
  ┌─────────┐       Minor Deviations                  │
  │ NORMAL  │ ──────────────────────► ┌──────────────────┐
  └─────────┘                         │UNDER_OBSERVATION │
       │                              └────────┬─────────┘
       │ High Severity Violations              │
       ▼                                       │ Repeated / Unresolved
  ┌───────────┐ ◄──────────────────────────────┘
  │SUSPICIOUS │
  └─────┬─────┘
        │ Dangerous Capability Used
        ▼
  ┌────────────┐
  │ RESTRICTED │
  └─────┬──────┘
        │ Critical Breach / Active Attack
        ▼
  ┌──────────┐      Formal Recovery Passed     ┌─────────┐
  │ ISOLATED │ ──────────────────────────────► │ NORMAL  │
  └─────┬────┘                                 └─────────┘
        │ Permanent Decommission
        ▼
  ┌─────────┐
  │ REVOKED │
  └─────────┘
```

---

## 2. Mathematical Trust Scoring Formulation

The dynamic agent trust score $T(a) \in [0.0, 1.0]$ is computed as a weighted combination of baseline historical reliability, runtime policy compliance, and operational liveliness:

$$T(a) = 0.50 \cdot R_{\text{base}}(a) + 0.30 \cdot C(a) + 0.20 \cdot H(a)$$

Where:
- $R_{\text{base}}(a) \in [0.0, 1.0]$: Base agent reliability score retrieved from `AgentRegistry`.
- $H(a) \in [0.0, 1.0]$: Real-time health score computed by `AgentHealthMonitor`.
- $C(a) \in [0.0, 1.0]$: Compliance score derived from active anomalies:

$$C(a) = \max\left(0.0, \, 1.0 - 0.15 \times N_{\text{anomalies}} - 0.40 \cdot \mathbb{I}_{\text{critical}}\right)$$

Where:
- $N_{\text{anomalies}}$ is the count of active unresolved anomalies registered against agent $a$.
- $\mathbb{I}_{\text{critical}} = 1$ if at least one active anomaly has `CRITICAL` severity, else 0.

---

## 3. Epistemic Uncertainty Formulation

Trust cannot be asserted with absolute confidence when telemetry is sparse or actively volatile. The epistemic uncertainty $U(a) \in [0.05, 0.50]$ scales directly with anomaly density:

$$U(a) = \min\left(0.50, \, 0.05 + 0.08 \times N_{\text{anomalies}}\right)$$

When $U(a) > 0.30$, orchestrators are barred from executing automated actions on agent recommendations without mandatory human approval.

---

## 4. Deterministic State Transition Matrix

The evaluator assigns formal trust states according to explicit deterministic rules:

| Condition | Assigned Trust Status | Governance Response |
|---|---|---|
| $a \in \text{ISOLATED\_AGENTS}$ | `ISOLATED` | All tool invocations rejected; orchestrator dispatch blocked. |
| $a \in \text{REVOKED\_CAPABILITIES}$ | `RESTRICTED` | Specific sensitive tools blocked; standard tools allowed. |
| $\mathbb{I}_{\text{critical}} = 1 \lor T(a) < 0.45 \lor N_{\text{violations}} \ge 3$ | `SUSPICIOUS` | Human security review requested; elevated telemetry rate. |
| $N_{\text{anomalies}} > 0 \lor H(a) < 0.70 \lor T(a) < 0.75$ | `UNDER_OBSERVATION` | Warning issued; supervisor telemetry sampling rate doubled. |
| $T(a) \ge 0.90 \land N_{\text{anomalies}} = 0 \land H(a) \ge 0.95$ | `TRUSTED` | Full autonomy within assigned work orders. |
| All other nominal operating conditions | `NORMAL` | Standard supervisory oversight. |

---

## 5. Auditability and Explainability

Every evaluation returns a structured `reasoning_summary` string explaining the exact mathematical derivation of the status. For example:
> *"Agent 'network_security_analyst' placed UNDER_OBSERVATION due to minor anomaly activity (anomaly_count=1, compliance=0.85, trust_score=0.742)."*

This eliminates uninterpretable trust assignments and provides clear evidence during SOC incident reviews.

