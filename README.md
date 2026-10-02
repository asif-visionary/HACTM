# HACTM — Hierarchical Adaptive Cyber Trust Mesh

HACTM is an enterprise-grade, multi-domain cybersecurity evidence platform and cyber-risk reasoning system.

---

## Phase Overview

### Foundation: Common Security Evidence Foundation
Standardized JSON schema, SQLite/PostgreSQL persistence, and baseline ingestion pipeline.

### Network Security Agent: Network Security Agent
Flow telemetry ingestion, heuristic signatures, Isolation Forest ML anomaly detection, and security evidence generation.

### Specialized Security Agents: Multi-Domain Specialized Security Agents
- **Phishing Intelligence Agent**: Phishing indicator scoring and domain detection.
- **User Behavior Analytics (UBA) Agent**: Behavioral baseline drift and anomaly scoring.
- **Identity & Authentication Agent**: Suspicious login, credential reuse, and impossible travel detection.
- **Transaction Security Agent**: Financial transaction anomaly and velocity risk detection.

### Evidence Fusion: Cross-Domain Evidence Fusion & Unified Cyber Risk Assessment
Bounded probabilistic evidence fusion ($1 - \prod(1 - S_{\text{dom}})$), domain weighting, conflict resolution, deduplication, quality scoring, and entity risk trajectory tracking.

### Adaptive Memory & Graph: Adaptive Evidence Memory, Temporal Correlation & Attack Evidence Graph
- **Adaptive Evidence Memory**: Tiered (HOT, WARM, COLD), importance-aware historical evidence storage with auditable promotion/demotion and credential privacy filtering.
- **Temporal Evidence Engine**: Event-time sequence ordering, cross-session correlation, burst detection, gap analysis, and late-event revision logs.
- **Attack Evidence Graph**: Entity-centric graph schema (Users, Devices, Accounts, IPs, Evidence) with bounded $k$-hop traversal ($k \le 4$), cycle prevention, and edge provenance tracking.
- **Declarative Pattern Matcher**: Multi-stage attack chain candidate detection (`configs/attack_patterns.yaml`), computing completeness and candidate confidence while preventing false correlations.
- **Research Evaluation Suite**: Empirical benchmark comparisons and ablation studies.

---

## Configuration Files
- `configs/evidence_memory.yaml`: Memory tier boundaries, importance weights, context limits, and graph traversal caps.
- `configs/attack_patterns.yaml`: Declarative attack patterns.

---

## External Threat Intelligence (AbuseIPDB Integration)

HACTM integrates external threat intelligence from **AbuseIPDB API v2** as an additional security evidence provider.

### Architecture & Non-Blocking Design
- **Role**: AbuseIPDB acts strictly as an external evidence provider. It does NOT make final Zero-Trust policy decisions (`ALLOW`/`VERIFY`/`BLOCK`).
- **Pipeline**: `AbuseIPDB API` → `Evidence Normalization` → `Reliability & Uncertainty` → `HACTM Evidence Fusion` → `Cyber Risk Score` → `Zero-Trust Policy`.
- **IP Validation**: Automatically filters out private RFC1918 IPs (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.1`), link-local, and multicast addresses without invoking external API quota.
- **Caching**: Results cached in-memory by `(IP, maxAgeInDays)` with 24-hour configurable TTL.
- **Failure Isolation**: HTTP 401/403/429/500 errors or network timeouts return provider status `unavailable` or `unconfigured` without crashing the pipeline or artificially elevating cyber risk.
- **Deduplication**: Evidence fusion engine deduplicates threat intelligence evidence for identical indicators.

### Configuration & Environment Variables
Set the following backend environment variables in `.env` (copy from `.env.example`):

```env
ABUSEIPDB_API_KEY=your_abuseipdb_api_key_here
ABUSEIPDB_BASE_URL=https://api.abuseipdb.com/api/v2
ABUSEIPDB_API_TIMEOUT=10
ABUSEIPDB_MAX_AGE_DAYS=30
ABUSEIPDB_RELIABILITY=0.85
ABUSEIPDB_ENABLED=true
```

> **Security Note**: `ABUSEIPDB_API_KEY` is backend-only and is never exposed to the frontend or React/Vite environment variables.

### Threat Intelligence API Endpoints
- `GET /api/v1/threat-intelligence/status`: Health check & AbuseIPDB provider configuration status.
- `GET /api/v1/threat-intelligence/ip/{ip}`: Queries IP reputation evidence.
- `POST /api/v1/threat-intelligence/evidence`: Generates canonical HACTM `SecurityEvidence` from threat intelligence lookup.

---

## Quickstart & Verification

```bash
# 1. Install & Run Tests (242 passing tests)
.\backend\.venv\Scripts\python.exe -m pytest -q

# 2. Run Threat Intelligence Unit Tests
.\backend\.venv\Scripts\python.exe -m pytest tests/unit/test_abuseipdb_threat_intel.py

# 3. Start FastAPI Backend Server
.\backend\.venv\Scripts\python.exe -m uvicorn hactm.api.app:app --host 127.0.0.1 --port 8080

# 4. Start Frontend Dev Server
cd frontend && npm run dev
```
