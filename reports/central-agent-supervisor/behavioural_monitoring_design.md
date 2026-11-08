# HACTM Central Agent Supervisor (CAS) — Behavioural Monitoring Design

## 1. Objective and Theoretical Model

The CAS **Agent Behaviour Monitor** (`AgentBehaviourMonitor`) establishes continuous statistical baselines for agent operations to detect subtle compromises, model drift, denial-of-service loops, or prompt jailbreaks that manifest as anomalous execution patterns rather than explicit syntax errors.

```
Incoming Action Stream ──> Rolling 15-min Window ──> Statistical Feature Extraction ──> Envelope Comparison ──> Anomaly Score [0, 1]
```

---

## 2. Statistical Baselines & Rolling Windows

The monitor maintains a rolling 15-minute event history for every registered agent, computing operational metrics over two temporal windows:
1. **Short Window (1 minute)**: Evaluates instantaneous velocity, action bursts, and rapid loop conditions.
2. **Standard Window (15 minutes)**: Evaluates cumulative tool consumption, delegation patterns, and communication volume.

### Baseline Parameter Envelopes

| Metric | Expected Baseline Envelope | Warning Threshold | Critical Anomaly Condition |
|---|---|---|---|
| **Action Velocity ($V_{\text{task}}$)** | $2.0 - 10.0\text{ actions/min}$ | $> 20.0\text{ actions/min}$ | $> 25.0\text{ actions/min}$ (`BURST_ACTIVITY_SPIKE`) |
| **Task Delegation / Handoffs** | $0 - 4\text{ handoffs/window}$ | $> 8\text{ handoffs}$ | $> 12\text{ handoffs}$ (`EXCESSIVE_HANDOFF_LOOP`) |
| **Tool Call Volume** | $1 - 15\text{ calls/task}$ | $> 20\text{ calls}$ | $> 30\text{ calls}$ (`ELEVATED_TOOL_CALL_VOLUME`) |
| **Average Execution Time** | $120\text{ms} - 4500\text{ms}$ | $> 8000\text{ms}$ | $> 15000\text{ms}$ (`BUDGET_EXCEEDED`) |

---

## 3. Anomaly Scoring Formulation

The composite behavioral anomaly score $A_{\text{beh}}(a) \in [0.0, 1.0]$ is derived from the active flag count:

$$A_{\text{beh}}(a) = \min\left(1.0, \, |\mathcal{F}_{\text{active}}(a)| \times 0.35\right)$$

Where $\mathcal{F}_{\text{active}}(a) \subseteq \{\text{BURST\_ACTIVITY\_SPIKE}, \text{EXCESSIVE\_HANDOFF\_LOOP}, \text{ELEVATED\_TOOL\_CALL\_VOLUME}, \text{HIGH\_EXECUTION\_LATENCY}\}$.

### Baseline Deviation Ratio
The baseline deviation ratio $R_{\text{dev}}(a)$ presented to SOC operators represents deviation above standard operating behavior:
$$R_{\text{dev}}(a) = 1.0 + A_{\text{beh}}(a)$$
- $R_{\text{dev}} = 1.00$: Nominal baseline.
- $1.01 \le R_{\text{dev}} \le 1.35$: Mild variation under observation.
- $R_{\text{dev}} \ge 1.70$: High deviation requiring capability restriction or governance warning.

---

## 4. Loop Detection Heuristics

### Delegation Cycle Detection
A common failure mode in multi-agent autonomous architectures is ping-pong task handoffs where Agent A delegates to Agent B, which immediately delegates back to Agent A:
$$\text{Chain}: A \to B \to A \to B \to A$$

The `AgentBehaviourMonitor` monitors the `is_handoff` flag. When the cumulative handoff count within the 15-minute window exceeds 12 handoffs without an intervening terminal event (`TASK_COMPLETE` or `EVIDENCE_SUBMITTED`), the condition is classified as an `EXCESSIVE_TASK_DELEGATION` anomaly with `HIGH` severity.

### Tool Exhaustion Protection
When an agent attempts repeated exploratory tool invocations (exceeding 30 calls in a single session) without generating validated evidence, the behavior monitor emits a `BUDGET_EXCEEDED` alert, prompting the supervisor to throttle the agent's token and tool budget.

