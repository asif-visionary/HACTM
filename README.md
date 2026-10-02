# 🛡️ HACTM — Hierarchical Adaptive Cyber Trust Mesh

<p align="center">

### Reliability- and Uncertainty-Aware Multi-Agent Architecture for Cross-Domain Threat Detection and Adaptive Zero-Trust Micro-Segmentation

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-Frontend-3178C6?logo=typescript)
![Security](https://img.shields.io/badge/Cybersecurity-Research-critical)
![Status](https://img.shields.io/badge/Status-Research%20Project-purple)

</p>

> **From isolated security alerts to adaptive, evidence-driven cyber trust.**

---

# 📌 Overview

**HACTM (Hierarchical Adaptive Cyber Trust Mesh)** is a multi-agent cybersecurity architecture that combines security evidence from different domains and converts it into a unified, context-aware cyber-risk decision.

Instead of treating every alert independently, HACTM correlates:

- 🌐 Network Security
- 📧 Phishing & Email Security
- 👤 User Behavior Analytics
- 🔐 Identity & Authentication
- 💳 Transaction Security
- 🤖 AI-Agent Security
- 🌍 Threat Intelligence

The evidence is processed through reliability, uncertainty, context, temporal and graph reasoning before generating an adaptive security decision.

---

# 🎯 Problem

Traditional security systems often operate independently:

```text
Network IDS       → Network Alert
Email Security    → Phishing Alert
Identity System   → Login Alert
UBA               → Behavior Alert
Transaction       → Fraud Alert

A single alert may not be enough to determine the actual risk.
HACTM correlates multiple signals:
Suspicious Login
      +
Phishing Email
      +
Abnormal Network Activity
      +
Unusual Transaction
      +
Historical Evidence
      ↓
Contextual Cyber Risk

🏗️ HACTM Architecture
┌──────────────────────────────────────────┐
│       1. MULTI-DOMAIN DATA SOURCES      │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       2. DATA INGESTION & PREPROCESSING │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       3. SPECIALIZED SECURITY AGENTS    │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       4. DYNAMIC SECURITY CONTEXT       │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       5. LOCAL EVIDENCE FUSION          │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       6. ADAPTIVE EVIDENCE MEMORY       │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       7. AGENT RELIABILITY & SAFETY     │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       8. UNCERTAINTY & CALIBRATION      │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       9. REGIONAL TRUST ORCHESTRATOR    │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│      10. GLOBAL ADAPTIVE ORCHESTRATOR   │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       11. CYBER RISK ASSESSMENT         │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       12. ADAPTIVE POLICY DECISION      │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       13. ADAPTIVE MICRO-SEGMENTATION   │
└──────────────────┬───────────────────────┘
                   ↓
┌──────────────────────────────────────────┐
│       14. TELEMETRY & FEEDBACK           │
└──────────────────┬───────────────────────┘
                   │
                   └──────────→ REASSESS

🔄 Complete Working Flow
                    DATA SOURCES
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
     Network           Email           Identity
        ↓                ↓                ↓
       UBA          Transaction        Endpoint
        └────────────────┼────────────────┘
                         ↓
                  DATA INGESTION
                         ↓
               NORMALIZATION / PARSING
                         ↓
                  ENTITY RESOLUTION
                         ↓
                  FEATURE EXTRACTION
                         ↓
                  TEMPORAL ALIGNMENT
                         ↓
                     ENRICHMENT
                         ↓
                  SECURITY EVIDENCE
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   Network Agent   Phishing Agent     UBA Agent
        ↓                ↓                ↓
   Identity Agent  Transaction Agent  AI-Agent / TI
        └────────────────┼────────────────┘
                         ↓
                LOCAL EVIDENCE FUSION
                         ↓
               RELIABILITY + UNCERTAINTY
                         ↓
                  EVIDENCE MEMORY
                         ↓
               REGIONAL ORCHESTRATOR
                         ↓
                GLOBAL ORCHESTRATOR
                         ↓
              TEMPORAL + GRAPH + CONTEXT
                         ↓
                    CYBER RISK
                         ↓
                   POLICY ENGINE
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
           ALLOW       VERIFY     QUARANTINE
             │                       │
             └───────────┬───────────┘
                         ↓
                       BLOCK
                         ↓
                    ENFORCEMENT
                         ↓
                     TELEMETRY
                         ↓
                   NEW EVIDENCE
                         ↓
                      REASSESS

⚙️ How Each Layer Works
1️⃣ Multi-Domain Data Sources
Collects security information from different environments.
Network + Email + Identity + UBA
+ Transactions + AI Agents + Threat Intel
                     ↓
              Raw Security Data

Examples:
- Network flows
- Emails and URLs
- Login events
- User activity
- Transactions
- Threat intelligence
2️⃣ Data Ingestion & Preprocessing
Converts different input formats into a common structure.
Raw Data
   ↓
Collection
   ↓
Normalization
   ↓
Parsing
   ↓
Validation
   ↓
Entity Resolution
   ↓
Feature Extraction
   ↓
Enrichment
   ↓
Prepared Security Data

3️⃣ Specialized Security Agents
Each agent analyzes a specific security domain.
                 SECURITY AGENTS
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
   Network         Phishing           UBA
       ↓               ↓               ↓
   Identity       Transaction      AI-Agent
                       │
                 Threat Intel
                       ↓
                Security Evidence

Network Agent
Network Activity
      ↓
Signature / Anomaly Analysis
      ↓
Flow & Behavioral Analysis
      ↓
Network Risk

Detects suspicious traffic, attacks, lateral movement and segmentation violations.
Phishing Agent
Email
 ↓
Content + URL + Sender + Attachment
 ↓
NLP / Classification
 ↓
Phishing Risk

UBA Agent
User Activity
 ↓
Behavior Profile
 ↓
Historical Comparison
 ↓
Anomaly Detection
 ↓
User Risk

Identity Agent
Login
 ↓
Credential / 2FA
 ↓
Device + Location + Time
 ↓
Identity Risk

Transaction Agent
Transaction
 ↓
Entity + Amount + Recipient
 ↓
Historical Behavior
 ↓
Transaction Graph
 ↓
Fraud / Anomaly Risk

AI-Agent Security
Session 1
   ↓
Session 2
   ↓
Session 3
   ↓
Cross-Session Evidence
   ↓
Attack Chain

Threat Intelligence
External Intelligence
        ↓
Normalization
        ↓
Reliability + Uncertainty
        ↓
Context
        ↓
Security Evidence

Threat intelligence supports the decision; it does not directly decide ALLOW or BLOCK.
4️⃣ Dynamic Security Context
Converts evidence into context about the entity.
Entity
  ↓
Identity
  ↓
Security Tags
  ↓
Security Group
  ↓
Security Zone
  ↓
Asset Dependencies

Example tags:
TRUSTED
HIGH_RISK
COMPROMISED
PRIVILEGED
THIRD_PARTY
CRITICAL

This context influences later risk and policy decisions.
5️⃣ Local Evidence Fusion
Combines evidence close to its source.
Network Evidence
Phishing Evidence
UBA Evidence
Identity Evidence
Transaction Evidence
        ↓
Standardized Evidence
        ↓
Local Correlation
        ↓
Local Risk
        ↓
Local Uncertainty
        ↓
Regional Evidence

This reduces unnecessary raw-event transmission to the global layer.
6️⃣ Adaptive Evidence Memory
Maintains useful historical evidence.
Current Event
     ↓
Recent Evidence
     ↓
Historical Evidence
     ↓
Entity History
     ↓
Cross-Session Reasoning
     ↓
Attack Progression

Memory supports:
- Historical comparison
- Cross-session correlation
- Attack progression
- Entity-based reasoning
7️⃣ Agent Reliability & Safety
HACTM does not assume every security agent is equally reliable.
Agent Performance
      ↓
Accuracy
      ↓
False Positive / Negative Rate
      ↓
Availability + Latency
      ↓
Historical Reliability

Failure handling:
Agent Failure
     ↓
Timeout
     ↓
Retry
     ↓
Circuit Breaker
     ↓
Fallback / Escalation

8️⃣ Uncertainty & Calibration
Raw model confidence is not automatically treated as trustworthy.
Prediction
    +
Confidence
    +
Uncertainty
    +
Evidence Quality
    ↓
Calibrated Security Evidence

Possible calibration methods:
- Temperature Scaling
- Isotonic Regression
- Conformal Prediction
9️⃣ Regional Trust Orchestrator
Combines evidence from multiple local environments.
Site A ──→ Local Evidence ──┐
Site B ──→ Local Evidence ──┼→ Regional Orchestrator
Site C ──→ Local Evidence ──┘
                                  ↓
                         Regional Risk

Performs:
- Temporal correlation
- Sequence analysis
- Graph reasoning
- Cross-site correlation
- Regional risk assessment
🔟 Global Adaptive Orchestrator
Acts as the central reasoning layer.
                 GLOBAL ORCHESTRATOR
                         │
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
 Agent Selection   Evidence Fusion    Graph Reasoning
       └─────────────────┼─────────────────┘
                         ↓
                Temporal Reasoning
                         ↓
                Resource Scheduling
                         ↓
                  Explainability

It considers:
Risk
+
Uncertainty
+
Reliability
+
Historical Evidence
+
Context
+
Temporal Relationships
+
Graph Relationships
+
Investigation Cost

It is not simply another classifier.
1️⃣1️⃣ Cyber Risk Assessment
Combines all relevant evidence.
Calibrated Evidence
       +
Uncertainty
       +
Reliability
       +
Context
       +
Attack Chain
       +
Historical Evidence
       ↓
Unified Cyber Risk

Conceptually:
0 ─────────────────────────── 1
Trusted                    High Risk

1️⃣2️⃣ Adaptive Policy Decision
Converts risk into an action.
                 CYBER RISK
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        LOW        MEDIUM      HIGH
          ↓          ↓          ↓
       ALLOW       VERIFY    QUARANTINE
                                  ↓
                                BLOCK

Possible actions:
- ALLOW
- MONITOR
- VERIFY
- QUARANTINE
- BLOCK
1️⃣3️⃣ Adaptive Micro-Segmentation
Uses risk to control network/workload access.
Risk Decision
      ↓
Firewall / SDN / Cloud / Kubernetes
      ↓
┌─────────────┬──────────────┬──────────────┐
↓             ↓              ↓
Normal       Restricted     Quarantine
Zone         Zone           Zone

Goal:
Reduce lateral movement and limit blast radius.

1️⃣4️⃣ Telemetry & Feedback
The final layer closes the loop.
Policy Decision
      ↓
Enforcement
      ↓
Telemetry
      ↓
Observe Result
      ↓
Measure Effectiveness
      ↓
New Evidence
      ↓
Reassess Risk
      ↓
Update Policy / Agent
      ↺

Telemetry can include:
- Allow / deny events
- Segmentation violations
- Reachable assets
- Blast radius
- Containment time
- Agent performance
- False positives / negatives
🧠 Core Evidence Model
All agents produce a common SecurityEvidence structure.
SecurityEvidence
├── event_id
├── agent_id
├── entity_id
├── event_type
├── timestamp
├── risk_score
├── confidence
├── uncertainty
├── evidence
├── security_tags
├── security_group
├── security_zone
└── model_version

This allows different security agents to communicate using a common format.
🔗 Cross-Domain Reasoning
The main strength of HACTM is combining evidence across domains.
Example attack chain:
Phishing Email
      ↓
Credential Compromise
      ↓
Suspicious Login
      ↓
Abnormal Network Activity
      ↓
Privilege Abuse
      ↓
Suspicious Transaction

Instead of six isolated alerts:
6 Alerts
  ↓
Correlated Evidence
  ↓
Attack Chain
  ↓
Higher Contextual Risk

🎯 Adaptive Agent Selection
HACTM can decide which additional agent should investigate next.
Current Evidence
      ↓
Current Risk
      ↓
Uncertainty
      ↓
Agent Reliability
      ↓
Historical Evidence
      ↓
Investigation Cost
      ↓
Next Agent

Goal:
More Useful Evidence
        +
Less Unnecessary Computation
        ↓
Adaptive Investigation

🕸️ Graph + Temporal Reasoning
Graph Reasoning
User
 ├── Device
 ├── Application
 └── Account

Relationships between entities can reveal attack paths.
Temporal Reasoning
T1 Phishing
     ↓
T2 Credential Capture
     ↓
T3 Suspicious Login
     ↓
T4 Network Anomaly
     ↓
T5 Privilege Abuse
     ↓
T6 Suspicious Transaction

HACTM considers both relationships and event order.
🧠 Model Strategy
HACTM is model-agnostic.
Possible approaches include:
Agent	Possible Approaches
Network	Random Forest, Gradient Boosting, Isolation Forest, Autoencoders
Phishing	TF-IDF, Classical ML, Transformers, URL Models
UBA	Statistical Detection, Clustering, Isolation Forest, Sequence Models
Identity	Authentication Analysis, 2FA, Biometrics, Behavioral Analysis
Transaction	Fraud Models, Anomaly Detection, Graph Analysis


Exact model assignments should only be reported after they are actually implemented and evaluated.

🧪 Dataset Strategy
HACTM uses domain-specific datasets.
Dataset
   ↓
Dataset Loader
   ↓
Validation
   ↓
Cleaning
   ↓
Feature Engineering
   ↓
Model / Detector
   ↓
Prediction
   ↓
Confidence
   ↓
Uncertainty
   ↓
Reliability
   ↓
SecurityEvidence
   ↓
Evidence Fusion

Main Dataset Groups
Network
├── CIC-IDS2017
├── CSE-CIC-IDS2018
├── UNSW-NB15
├── BoT-IoT
└── ToN-IoT

Phishing
├── SpamAssassin
├── Enron
├── Phishing Datasets
└── PhishTank

UBA
├── CERT Insider Threat
├── LANL Authentication
└── LANL Multi-Source

Identity
├── LANL Authentication
├── NIST FRTE/FATE
├── FERET
└── Synthetic 2FA

Transaction
├── ULB Credit Card Fraud
├── Synthetic Transactions
├── Company-Bank Network
└── Uniswap

Threat Intelligence
├── MISP Galaxy
├── PhishTank
├── NVD
└── AbuseIPDB

Large raw datasets are kept outside the Git repository.
🛠️ Technology Stack
Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite
- REST API
Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Chart.js
- Recharts
Security / AI
- Intrusion Detection
- Phishing Detection
- UBA
- Identity Security
- Fraud Detection
- NLP
- Machine Learning
- Anomaly Detection
- Graph Analysis
- Threat Intelligence
- Zero Trust
- Micro-Segmentation
📂 Project Structure
HACTM/
├── backend/
│   ├── src/
│   │   └── hactm/
│   │       ├── api/
│   │       ├── core/
│   │       ├── fusion/
│   │       ├── graph/
│   │       ├── identity/
│   │       ├── ingestion/
│   │       ├── memory/
│   │       ├── network/
│   │       ├── orchestration/
│   │       ├── phishing/
│   │       ├── reliability/
│   │       ├── services/
│   │       ├── storage/
│   │       ├── temporal/
│   │       ├── transaction/
│   │       ├── uba/
│   │       └── zerotrust/
│   └── data/
│
├── frontend/
│   ├── src/
│   └── public/
│
├── data/
│   └── raw/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── benchmarks/
│
├── docs/
├── scripts/
├── .env.example
├── .gitignore
└── README.md

⚙️ Installation
git clone https://github.com/asif-visionary/HACTM.git
cd HACTM

Backend
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt

Frontend
cd frontend
npm install
npm run dev

🧪 Testing
pytest

Testing covers the major pipeline components:
Data
 ↓
Agents
 ↓
Evidence
 ↓
Fusion
 ↓
Risk
 ↓
Policy

📊 Evaluation
HACTM evaluates more than detection accuracy.
Detection
- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC
- FPR
- FNR
Calibration
- ECE
- Brier Score
- Coverage
- AUSE
System
- Agent latency
- Availability
- Failure rate
- Resource usage
- Agent invocation count
- Inference cost
Security
- Containment time
- Blast radius
- Policy effectiveness
- Segmentation violations
🔬 Research Focus
HACTM investigates:
Adaptive Agent Selection
        +
Reliability-Aware Fusion
        +
Uncertainty Awareness
        +
Cross-Session Memory
        +
Temporal Reasoning
        +
Graph Reasoning
        +
Adaptive Micro-Segmentation
        +
Closed-Loop Telemetry

The research focus is the coordination of heterogeneous security systems, rather than claiming that individual technologies such as IDS, UBA, Zero Trust or micro-segmentation are themselves novel.
🧭 Roadmap
Phase 1  → Foundation & Common Data Model
Phase 2  → Data Ingestion & Preprocessing
Phase 3  → Specialized Security Agents
Phase 4  → Evidence & Local Fusion
Phase 5  → Evidence Memory
Phase 6  → Reliability & Uncertainty
Phase 7  → Regional Orchestration
Phase 8  → Global Orchestration
Phase 9  → Risk Assessment
Phase 10 → Adaptive Policy
Phase 11 → Micro-Segmentation
Phase 12 → Telemetry & Feedback
Phase 13 → Evaluation & Research

🖥️ Dashboard
The dashboard provides visibility into:
Security Events
      ↓
Evidence Explorer
      ↓
Agent Results
      ↓
Risk Assessment
      ↓
Policy Decision
      ↓
Security Context
      ↓
Threat Intelligence
      ↓
Historical Evidence

📄 Security Reporting
Security Events
      ↓
Evidence
      ↓
Risk
      ↓
Decision
      ↓
Enforcement
      ↓
Security Report

Reports can contain:
- Security events
- Evidence
- Risk
- Agent contributions
- Context
- Threat intelligence
- Policy decisions
- Enforcement actions
- Historical evidence
⚠️ Ethical Use
HACTM is intended for:
- Education
- Cybersecurity research
- Academic projects
- Security experimentation
- Authorized assessments
- Laboratory environments
Do not use HACTM against systems, accounts, networks or data without appropriate authorization.
👨‍💻 Author
Mohamed Asif
Cybersecurity Enthusiast | Security Researcher | Developer
GitHub:
https://github.com/asif-visionary
📜 License
Add the selected open-source license in:
LICENSE

🛡️ HACTM — Final Architecture
                ┌───────────────────────┐
                │     DATA SOURCES      │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │    PREPROCESSING      │
                └───────────┬───────────┘
                            ↓
          ┌───────────────────────────────────┐
          │        SPECIALIZED AGENTS         │
          │                                   │
          │ Network | Phishing | UBA          │
          │ Identity | Transaction | AI/TI    │
          └────────────────┬──────────────────┘
                           ↓
                ┌───────────────────────┐
                │  SECURITY EVIDENCE    │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │   EVIDENCE FUSION     │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │ RELIABILITY +         │
                │ UNCERTAINTY           │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │  CONTEXT + MEMORY     │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │ REGIONAL ORCHESTRATOR │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │ GLOBAL ORCHESTRATOR   │
                │                       │
                │ Graph + Temporal      │
                │ Agent Selection       │
                │ Explainability        │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │      CYBER RISK       │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │    POLICY ENGINE      │
                └───────────┬───────────┘
                            ↓
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
           ALLOW          VERIFY       QUARANTINE
                                            ↓
                                          BLOCK
                            ↓
                ┌───────────────────────┐
                │ MICRO-SEGMENTATION    │
                └───────────┬───────────┘
                            ↓
                ┌───────────────────────┐
                │ TELEMETRY + FEEDBACK  │
                └───────────┬───────────┘
                            │
                            └────→ REASSESS

HACTM — From isolated security alerts to adaptive, evidence-driven cyber trust.
