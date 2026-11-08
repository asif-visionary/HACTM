# HACTM Central Agent Supervisor (CAS) — Architecture Specification

## 1. Executive Overview

The **Central Agent Supervisor (CAS)** is an autonomous, high-assurance meta-supervisory subsystem embedded within the **Hierarchical Adaptive Cyber Trust Mesh (HACTM)**. While individual cybersecurity agents execute specialized investigative tasks (network packet inspection, phishing heuristics, behavioral anomaly evaluation, identity tracking) and orchestrators coordinate operational workflows, the Central Agent Supervisor maintains continuous, evidence-based oversight over the entire agent ecosystem.

```mermaid
graph TD
    subgraph Operational Mesh
        NS[Network Security Agent]
        PI[Phishing Intelligence Agent]
        UBA[User Behavior Analytics Agent]
        IA[Identity & Access Agent]
        TI[Threat Intel Specialist]
        FR[Fraud & Transaction Agent]
        CS[Cloud Security Agent]
    end

    subgraph Orchestration Layer
        RO[Regional Orchestrators]
        GAO[Global Adaptive Orchestrator]
    end

    subgraph Central Agent Supervisor [CAS]
        TC[Telemetry Collector]
        AHM[Agent Health Monitor]
        ABM[Behaviour Monitor]
        TAM[Tool Activity Monitor]
        EIM[Evidence Integrity Monitor]
        ADE[Anomaly Detection Engine]
        ATE[Trust Evaluator]
        SIA[Supervisor Intelligence Agent]
        GA[Governance & Enforcement Adapter]
        OM[Orchestrator Monitor]
        WD[Independent Watchdog]
    end

    NS -->|Telemetry Events & Heartbeats| TC
    PI -->|Telemetry Events & Heartbeats| TC
    UBA -->|Telemetry Events & Heartbeats| TC
    IA -->|Telemetry Events & Heartbeats| TC
    TI -->|Telemetry Events & Heartbeats| TC
    FR -->|Telemetry Events & Heartbeats| TC
    CS -->|Telemetry Events & Heartbeats| TC

    RO -->|Dispatch & Planning Actions| OM
    GAO -->|Work Order Scopes| OM

    TC --> AHM & ABM & TAM & EIM
    AHM & ABM & TAM & EIM --> ADE
    ADE --> ATE
    ATE --> GA
    GA -->|Level 0-5 Containment| Operational Mesh
    OM --> ADE
    SIA -->|Supervisory Briefs| GA
    WD -->|Health SLA Checks| CAS
```

---

## 2. Separation of Concerns: GAO vs. CAS

A foundational architectural requirement in HACTM is the strict structural separation between operational coordination and supervisory governance. The Global Adaptive Orchestrator must not be the judge of its own operational compliance.

| Dimension | Global Adaptive Orchestrator (GAO) | Central Agent Supervisor (CAS) |
|---|---|---|
| **Primary Mission** | Incident resolution & investigation coordination | Agent behavioral oversight & cybersecurity mesh integrity |
| **Operational Scope** | Security entities, alerts, investigation work orders | Registered agents, runtime telemetry, tools, audit chains |
| **Evidence Processing**| Multi-source evidence fusion & Bayesian inference | Verification of evidence schemas, provenance, & injection patterns |
| **Agent Selection** | Selects specialist agents based on domain & capability | Authorizes or blocks agent participation based on trust status |
| **Failure Response** | Replanning, delegating tasks, dynamic investigation tree | Quarantining agents, restricting capabilities, human escalation |
| **Supervisory Power**| Constrained by CAS governance directives | Authority to isolate rogue agents or abort invalid orchestrations |

---

## 3. Subsystem Component Topology

The CAS subsystem is organized into 11 modular micro-components located in `backend/src/hactm/supervisor/`:

1. **`TelemetryCollector` (`collector.py`)**: Ingests, normalizes, and validates high-frequency runtime events from agents and orchestrators against the authoritative `AgentRegistry`.
2. **`AgentHealthMonitor` (`health_monitor.py`)**: Continuously monitors heartbeats, tracks execution duration, flags stuck tasks (>30s), and computes composite health scores ($[0.0, 1.0]$).
3. **`AgentBehaviourMonitor` (`behaviour_monitor.py`)**: Maintains a 15-minute sliding window of agent actions, computing baseline deviations, action velocity, handoff frequencies, and tool consumption.
4. **`ToolActivityMonitor` (`tool_monitor.py`)**: Real-time gateway intercepter enforcing allow-lists, work order boundaries, deny-first forbidden actions, and immediate containment for isolated agents.
5. **`EvidenceIntegrityMonitor` (`evidence_monitor.py`)**: Inspects all `SecurityEvidence` submissions for schema compliance, cryptographic provenance, probability calibration consistency, and adversarial prompt injection patterns.
6. **`AgentTrustEvaluator` (`trust_evaluator.py`)**: Computes deterministic, auditable Agent Trust Assessments, classifying agents into 7 discrete trust tiers with explicit epistemic uncertainty.
7. **`AnomalyDetectionEngine` (`anomaly_engine.py`)**: Central registry for all operational and security anomalies with deduplication, severity grading (CRITICAL, HIGH, MEDIUM, LOW), and database persistence.
8. **`SupervisorIntelligenceAgent` (`intelligence_agent.py`)**: Executive reasoning engine providing explainable trust transition summaries, multi-alert correlation, and automated incident briefs.
9. **`GovernanceAdapter` (`governance_adapter.py`)**: Authoritative enforcement adapter mapping anomalies into a 6-tier governance model (Level 0 Normal to Level 5 Human Security Review), updating cryptographic SHA-256 audit chains, and publishing live SSE events.
10. **`OrchestratorMonitor` (`orchestrator_monitor.py`)**: Specialized watchdog tracking Regional and Global Orchestrators to prevent task dispatch to quarantined agents and stop orchestration thrashing.
11. **`SupervisorWatchdog` (`watchdog.py`)**: Independent latency and queue monitor ensuring CAS operates within a sub-15ms processing SLA without deadlocks.

---

## 4. Database Schema Specifications

CAS introduces seven dedicated persistence models in `backend/src/hactm/storage/models.py`:

```
   ┌────────────────────────┐         ┌────────────────────────┐
   │  cas_agent_heartbeats  │         │cas_behaviour_observat. │
   ├────────────────────────┤         ├────────────────────────┤
   │ id (PK)                │         │ id (PK)                │
   │ agent_id (FK)          │         │ agent_id (FK)          │
   │ timestamp              │         │ event_type             │
   │ status                 │         │ execution_ms           │
   │ current_task           │         │ is_tool_call           │
   │ cpu_load, memory_mb    │         │ is_handoff             │
   └────────────────────────┘         └────────────────────────┘
                 │                                │
                 ▼                                ▼
   ┌───────────────────────────────────────────────────────────┐
   │                    cas_agent_anomalies                    │
   ├───────────────────────────────────────────────────────────┤
   │ alert_id (PK, UUID)                                       │
   │ agent_id (Index), anomaly_type, severity                  │
   │ description, recommended_action, is_active                │
   │ evidence_references (JSON)                                │
   └───────────────────────────────────────────────────────────┘
                 │
                 ▼
   ┌───────────────────────────────────────────────────────────┐
   │                  cas_trust_assessments                    │
   ├───────────────────────────────────────────────────────────┤
   │ assessment_id (PK)                                        │
   │ agent_id, trust_status, trust_score, reliability_score    │
   │ compliance_score, uncertainty, reasoning_summary          │
   └───────────────────────────────────────────────────────────┘
                 │
                 ▼
   ┌───────────────────────────────────────────────────────────┐
   │                 cas_supervisor_decisions                  │
   ├───────────────────────────────────────────────────────────┤
   │ decision_id (PK)                                          │
   │ agent_id, governance_level (0-5), decision_type           │
   │ justification, action_payload (JSON), operator_identity   │
   └───────────────────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
 ┌───────────────┐ ┌───────────────┐
 │cas_isolation_r│ │cas_recovery_re│
 └───────────────┘ └───────────────┘
```

---

## 5. Security & Isolation Boundaries

- **Deny-First Execution**: The CAS gateway guarantees that forbidden actions and quarantined states cannot be bypassed even if a work order erroneously authorizes a tool.
- **Fail-Safe Fallback**: If an agent experiences an unhandled crash or network partition, the CAS watchdog transitions the agent's health to `OFFLINE` and trust to `UNDER_OBSERVATION` within 30 seconds.
- **Tamper-Evident Auditability**: Every governance decision is chained via SHA-256 HMAC logging into the HACTM cryptographic audit trail.

