# HACTM Central Agent Supervisor (CAS) — Telemetry Event Contract

## 1. Specification Standard

All runtime telemetry emitted by HACTM cybersecurity agents, orchestrators, and governance nodes must conform to the strict JSON schemas enforced by the CAS `TelemetryCollector`. Events are validated at the gateway using Pydantic V2 schemas before buffer ingestion.

---

## 2. Telemetry Ingestion Schemas

### 2.1 Core Telemetry Event Schema (`POST /api/v1/supervisor/telemetry`)

```json
{
  "event_id": "EVT-7B9C318A",
  "agent_id": "network_security_analyst",
  "event_type": "TOOL_INVOCATION",
  "incident_id": "INC-2026-8801",
  "task_id": "TASK-PCAP-09",
  "timestamp": "2026-11-08T10:14:22.105Z",
  "tenant_id": "tenant_default",
  "payload": {
    "tool_name": "network_flow_analyzer",
    "execution_ms": 142.5,
    "input_parameters": {
      "interface": "eth0",
      "pcap_filter": "tcp port 443"
    },
    "evidence": {
      "event_id": "EVD-FLOW-091",
      "agent_id": "network_security_analyst",
      "entity_id": "192.168.10.45",
      "risk_score": 0.78,
      "confidence": 0.85,
      "uncertainty": 0.15,
      "summary": "High volume SYN flood detected from source IP."
    }
  }
}
```

#### Field Specifications:
- `event_id` (`string`, required): Unique event identifier formatted as `EVT-<hex:8>`.
- `agent_id` (`string`, required): Identifier of emitting agent matching an active registration in `AgentRegistry`.
- `event_type` (`string`, required): One of `HEARTBEAT`, `TOOL_INVOCATION`, `TASK_START`, `TASK_COMPLETE`, `TASK_FAILED`, `AGENT_COMMUNICATION`, `TASK_HANDOFF`, `EVIDENCE_SUBMITTED`.
- `incident_id` (`string`, optional): Scoped security incident reference.
- `payload` (`object`, required): Dynamic payload containing execution metrics, tool names, or evidence structures.

---

### 2.2 Periodic Agent Heartbeat Schema (`POST /api/v1/supervisor/heartbeat`)

Agents transmit heartbeats every 10.0 seconds ($\pm 1.5s$) to certify liveliness:

```json
{
  "agent_id": "phishing_analyst",
  "status": "OPERATIONAL",
  "task": "EMAIL_HEADER_ANALYSIS",
  "heartbeat_interval_sec": 10.0,
  "cpu_load": 18.4,
  "memory_mb": 210.8,
  "queue_len": 2
}
```

#### Response Structure:
```json
{
  "agent_id": "phishing_analyst",
  "status": "OPERATIONAL",
  "is_online": true,
  "last_heartbeat": "2026-11-08T10:14:25.000Z",
  "heartbeat_interval_sec": 10.0,
  "time_since_heartbeat_sec": 0.12,
  "active_task": "EMAIL_HEADER_ANALYSIS",
  "consecutive_failures": 0,
  "is_stuck": false,
  "cpu_load": 18.4,
  "memory_mb": 210.8,
  "queue_length": 2,
  "health_score": 1.0
}
```

---

## 3. Tool Gateway Request Contract

When an agent invokes a tool, the request is intercepted and validated against active permissions or work order scopes:

```json
{
  "agent_id": "network_security_analyst",
  "tool_name": "pcap_parser",
  "tool_args": {
    "capture_file": "/var/log/traffic_sample_01.pcap"
  },
  "work_order_id": "WO-NET-882"
}
```

### Authorization Response:
```json
{
  "is_allowed": true,
  "anomaly": null
}
```

### Rejection Response (e.g. Forbidden Action Violation):
```json
{
  "is_allowed": false,
  "anomaly": {
    "type": "FORBIDDEN_TOOL_REQUEST",
    "severity": "CRITICAL",
    "agent_id": "network_security_analyst",
    "desc": "Agent 'network_security_analyst' attempted forbidden action 'raw_shell_exec' prohibited by Work Order 'WO-NET-882'.",
    "recommended_action": "ISOLATE_AGENT"
  }
}
```

---

## 4. Anomaly Notification Event Contract (Workspace SSE)

When an anomaly is registered, CAS emits a real-time Server-Sent Event to the workspace UI:

```json
{
  "event_id": "EVT-ANOM-1029",
  "event_type": "agent_anomaly_detected",
  "timestamp": "2026-11-08T10:14:30.150Z",
  "agent_id": "threat_intel_specialist",
  "incident_id": "INC-2026-8801",
  "message": "[CRITICAL] Adversarial prompt injection pattern detected in evidence payload.",
  "data": {
    "alert_id": "ALR-5A2C8F9E",
    "anomaly_type": "PROMPT_INJECTION_DETECTED",
    "severity": "CRITICAL",
    "source": "EVIDENCE_MONITOR",
    "recommended_action": "SANITIZE_AND_FLAG"
  }
}
```

