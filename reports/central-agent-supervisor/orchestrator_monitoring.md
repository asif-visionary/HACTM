# HACTM Central Agent Supervisor (CAS) — Orchestrator Monitoring

## 1. Principles of Supervised Orchestration

In complex multi-agent architectures, orchestrators hold wide operational authority: they decompose incidents, construct investigation DAGs, dispatch work orders, and synthesize evidence. If an orchestrator suffers from logic flaws, state desynchronization, or adversarial prompt injection, it could compromise the entire mesh.

The CAS **Orchestrator Monitor** (`OrchestratorMonitor`) acts as an external watchdog ensuring that:
1. Orchestrators strictly respect agent isolation and capability restrictions.
2. Orchestration workflows do not enter infinite replanning or delegation loops.
3. Work orders conform to authorized tenant and incident security boundaries.

```
                    ┌────────────────────────────┐
                    │ Global / Regional          │
                    │ Orchestrator Dispatch      │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
               ┌─────────────────────────────────────┐
               │     CAS Orchestrator Monitor        │
               ├─────────────────────────────────────┤
               │ 1. Is target agent isolated?        │
               │ 2. Is replan count > 10?            │
               │ 3. Is work order scope valid?       │
               └──────────────┬───────────────┬──────┘
                              │               │
                     Valid    │               │ Violation
                              ▼               ▼
                       [ Allow Dispatch ]   [ Intercept & Alert ]
                                            [ Critical Anomaly  ]
```

---

## 2. Detection of Dispatch to Isolated Agents

When an orchestrator issues a task assignment (`action_type = "TASK_DISPATCH"`), the `OrchestratorMonitor` validates the target agent against the authoritative `ISOLATED_AGENTS` registry:

```python
if target_agent_id and target_agent_id in ISOLATED_AGENTS:
    anomaly = {
        "type": "ORCHESTRATOR_ANOMALY",
        "severity": "CRITICAL",
        "agent_id": orchestrator_id,
        "desc": f"Orchestrator '{orchestrator_id}' attempted to assign task to quarantined agent '{target_agent_id}'.",
        "recommended_action": "REJECT_ASSIGNMENT_AND_REPLAN"
    }
    return False, anomaly
```

### Operational Impact
The dispatch attempt is immediately aborted. A `CRITICAL` anomaly is logged against the orchestrator, and an SSE alert informs the SOC operator of the orchestration failure.

---

## 3. Detection of Orchestration Thrashing

During ambiguous or adversarial incidents, an orchestrator might fail to converge on an investigation hypothesis, repeatedly replanning and canceling tasks without progressing evidence fusion.

- **Threshold**: $> 10$ replanning actions (`INVESTIGATION_REPLAN`) within a single incident context.
- **Classification**: Emits an `EXCESSIVE_TASK_DELEGATION` alert with recommendation `REQUEST_HUMAN_SECURITY_REVIEW`.
- **Enforcement**: CAS temporarily suspends automated replanning, freezing the investigation state until a human SOC analyst intervenes.

