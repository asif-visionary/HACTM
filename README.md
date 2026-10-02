# 🛡️ HACTM — Hierarchical Adaptive Cyber Trust Mesh

<p align="center">

### A Reliability- and Uncertainty-Aware Multi-Agent Architecture for Cross-Domain Threat Detection and Adaptive Zero-Trust Micro-Segmentation

</p>

<p align="center">

<img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" alt="Python">
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" alt="FastAPI">
<img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react" alt="React">
<img src="https://img.shields.io/badge/TypeScript-Frontend-3178C6?logo=typescript" alt="TypeScript">
<img src="https://img.shields.io/badge/Machine%20Learning-Security-orange" alt="Machine Learning">
<img src="https://img.shields.io/badge/Zero%20Trust-Security-critical" alt="Zero Trust">
<img src="https://img.shields.io/badge/Status-Research%20Project-purple" alt="Research Project">

</p>

<p align="center">

**From isolated security alerts to adaptive, evidence-driven cyber trust.**

</p>

---

# 📌 Overview

**HACTM (Hierarchical Adaptive Cyber Trust Mesh)** is a research-oriented cybersecurity and digital-trust platform designed to combine security evidence from multiple domains into a unified cyber-risk assessment.

Instead of relying on a single security detector, HACTM organizes specialized security agents for different security domains:

- 🌐 Network Security
- 📧 Phishing & Email Security
- 👤 User Behavior Analytics
- 🔐 Identity & Authentication
- 💳 Transaction Security
- 🤖 AI-Agent Threat Analysis
- 🌍 External Threat Intelligence

The outputs of these agents are converted into a common **Security Evidence** representation.

The evidence is then processed using:

- Evidence Fusion
- Agent Reliability
- Uncertainty Estimation
- Temporal Reasoning
- Context Reasoning
- Graph Reasoning
- Historical Evidence
- Adaptive Agent Selection
- Cyber-Risk Assessment
- Policy Decision
- Adaptive Micro-Segmentation
- Telemetry and Feedback

The overall objective is to move from:

> **Isolated alerts**

toward:

> **Context-aware, evidence-driven and adaptive security decisions**

---

# 🎯 Problem Statement

Modern organizations generate security information from many independent systems.

A typical enterprise may have:

```text
Network IDS
    ↓
Network Alerts


Email Security
    ↓
Phishing Alerts


Identity Systems
    ↓
Authentication Alerts


Endpoint Security
    ↓
Endpoint Alerts


User Behavior Analytics
    ↓
Behavior Alerts


Transaction Monitoring
    ↓
Fraud Alerts

The problem is that these systems often operate independently.
A single alert may not provide enough information to determine whether an entity is genuinely at risk.
For example:
Suspicious Login
        +
Phishing Email
        +
Abnormal Network Traffic
        +
Unusual Transaction
        +
Previous Suspicious Activity
        ↓
Higher Contextual Risk

HACTM addresses this problem by correlating heterogeneous security signals rather than treating every alert as an isolated event.
🧠 Core Idea
The central idea of HACTM is:
Security decisions should be based on correlated, contextual, reliable and uncertainty-aware evidence rather than isolated alerts.

HACTM transforms:
Raw Security Data
        ↓
Security Events
        ↓
Normalized Evidence
        ↓
Agent Analysis
        ↓
Local Evidence Fusion
        ↓
Reliability & Calibration
        ↓
Temporal + Contextual Reasoning
        ↓
Global Evidence Fusion
        ↓
Cyber Risk
        ↓
Policy Decision
        ↓
Security Enforcement
        ↓
Telemetry
        ↓
New Evidence
        ↓
Reassessment

This creates a continuous security feedback loop.
🏗️ Architecture
HACTM consists of multiple logical layers:
┌──────────────────────────────────────────────┐
│       1. MULTI-DOMAIN DATA SOURCES          │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       2. DATA INGESTION & PREPROCESSING     │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       3. SPECIALIZED SECURITY AGENTS        │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       4. DYNAMIC SECURITY CONTEXT            │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       5. LOCAL EVIDENCE FUSION               │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       6. ADAPTIVE EVIDENCE MEMORY            │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       7. AGENT RELIABILITY & SAFETY          │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       8. UNCERTAINTY & CALIBRATION           │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       9. REGIONAL TRUST ORCHESTRATOR         │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       10. GLOBAL ADAPTIVE ORCHESTRATOR       │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       11. CYBER RISK ASSESSMENT              │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       12. ADAPTIVE POLICY DECISION           │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       13. ADAPTIVE MICRO-SEGMENTATION        │
└───────────────────────┬──────────────────────┘
                        ↓
┌──────────────────────────────────────────────┐
│       14. TELEMETRY & FEEDBACK LOOP          │
└───────────────────────┬──────────────────────┘
                        │
                        └──────────────→ REASSESS

🔄 Complete End-to-End Flow
                         DATA SOURCES
                              │
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
          Network           Email          Identity
              ↓               ↓               ↓
             UBA         Transactions       Endpoint
              └───────────────┼───────────────┘
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
           ┌──────────────────┼──────────────────┐
           ↓                  ↓                  ↓
      Network Agent     Phishing Agent       UBA Agent
           ↓                  ↓                  ↓
      Identity Agent    Transaction Agent    AI-Agent / TI
           └──────────────────┼──────────────────┘
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
              ┌───────────────┼────────────────┐
              ↓               ↓                ↓
            ALLOW           MONITOR           VERIFY
                                                  ↓
                                           QUARANTINE
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

✨ Key Features
Feature	Description
🌐 Multi-Domain Security	Combines evidence from network, email, identity, UBA, transactions and AI-agent environments
🧩 Evidence Fusion	Correlates heterogeneous security signals
🛡️ Reliability-Aware Security	Considers historical performance and reliability of security agents
📐 Uncertainty Awareness	Separates confidence from uncertainty and supports calibration
🧠 Evidence Memory	Maintains relevant historical and cross-session evidence
🕒 Temporal Reasoning	Detects relationships between events occurring over time
🕸️ Graph Reasoning	Represents users, devices, applications, transactions and attack relationships
🎯 Adaptive Agent Selection	Dynamically selects additional agents based on current security state
🌍 Regional Orchestration	Combines evidence from local or edge environments
🌐 Global Orchestration	Performs cross-domain security reasoning
🚦 Adaptive Policy	Converts cyber risk into security actions
🧱 Micro-Segmentation	Enables risk-driven isolation and segmentation
🔁 Telemetry Feedback	Uses enforcement results to generate new evidence
🔎 Explainability	Records contributing evidence and reasoning context
🌍 Threat Intelligence	Integrates external security intelligence as evidence
📄 Security Reporting	Produces structured security reports


📚 Layer-by-Layer Architecture
1. Multi-Domain Data Sources
HACTM accepts information from multiple cybersecurity domains.
🌐 Network Security
Datasets and sources include:
- CIC-IDS2017
- CSE-CIC-IDS2018
- UNSW-NB15
- BoT-IoT
- ToN-IoT
- NetFlow
- PCAP
- DNS Logs
- Firewall Logs
- IDS/IPS Logs
📧 Email & Phishing
Sources include:
- Phishing Email Datasets
- SpamAssassin
- Enron
- PhishTank
- Recent phishing datasets
💻 Endpoint
Potential sources include:
- Windows Logs
- Linux Logs
- Endpoint Telemetry
- Process Events
- File Events
- Registry Events
- EDR Data
🔐 Identity
Sources include:
- LANL Authentication Data
- NIST FRTE/FATE
- FERET
- Synthetic 2FA Data
💳 Transactions
Sources include:
- ULB Credit Card Fraud
- Synthetic Transaction Data
- Company-Bank Network Data
- E-commerce / Banking Data
- Uniswap Transaction Data
🤖 AI-Agent Security
Sources include:
- CSTM-Bench
- Cross-session attack scenarios
- Benign-hard scenarios
- AI-agent misuse scenarios
- Prompt/agent attack scenarios
🌍 Threat Intelligence
Potential external sources include:
- MISP Galaxy
- PhishTank
- OSINT Feeds
- NVD
- AbuseIPDB
2. Data Ingestion & Preprocessing
Raw data cannot directly enter the orchestration layer.
HACTM first converts heterogeneous information into a common structure.
Raw Data
   ↓
Collection
   ↓
Normalization
   ↓
Parsing
   ↓
Schema Validation
   ↓
Entity Resolution
   ↓
Feature Extraction
   ↓
Time Synchronization
   ↓
Threat Intelligence Enrichment
   ↓
Context Enrichment
   ↓
Preprocessed Security Data

Entity Resolution
HACTM can associate events with entities such as:
- User
- Device
- IP Address
- Account
- Application
- Workload
- Transaction
- Email Address
- Domain
The purpose is to determine which events belong to the same entity or related entities.
3. Security Evidence Model
All security agents communicate using a common evidence representation.
A conceptual SecurityEvidence object contains:
event_id
agent_id
entity_id
event_type
timestamp
risk_score
confidence
uncertainty
evidence
security_tags
security_group
security_zone
model_version

External intelligence can additionally contain:
source_provider
source_type
indicator_type
indicator
reliability
observed_at
expires_at
normalization_version

This common representation prevents every security agent from producing incompatible outputs.
4. Specialized Security Agents
                    SECURITY AGENTS
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
    Network Agent    Phishing Agent      UBA Agent
          │                │                │
          ├────────┬───────┴───────┬────────┤
          ↓        ↓               ↓        ↓
      Identity  Transaction    AI-Agent  Threat Intel
       Agent      Agent          Agent     Evidence
          │        │               │         │
          └────────┴───────────────┴─────────┘
                           ↓
                    SECURITY EVIDENCE

🌐 5. Network Security Agent
Purpose
The Network Security Agent analyzes network activity and identifies suspicious behavior.
Detection Flow
Known Attacks
      ↓
Signature / IOC Matching


Unknown Behavior
      ↓
Anomaly Detection


Network Relationships
      ↓
Flow / Graph Analysis


Post-Compromise Movement
      ↓
Lateral Movement Analysis

Detection Techniques
- Signature-based detection
- Anomaly-based detection
- Flow analysis
- Behavioral analysis
- Zero-day-like detection
- Lateral movement detection
- East-west traffic analysis
- Micro-segmentation violation detection
Datasets
- CIC-IDS2017
- CSE-CIC-IDS2018
- UNSW-NB15
- BoT-IoT
- ToN-IoT
Output
- Network Anomaly
- Intrusion Alert
- Attack Type
- Risk Score
- Confidence
- Uncertainty
- Policy Violation
📧 6. Phishing Intelligence Agent
Purpose
The Phishing Intelligence Agent evaluates:
- Emails
- URLs
- Senders
- Attachments
- Related Content
Flow
Email
 ↓
Content Extraction
 ↓
URL Extraction
 ↓
Attachment Analysis
 ↓
Sender Analysis
 ↓
NLP Analysis
 ↓
Phishing Classification
 ↓
Security Evidence

Techniques
- NLP-based filtering
- URL analysis
- Sender reputation
- Attachment analysis
- Transformer-based classification
- Generic phishing detection
- Spear-phishing detection
- Business Email Compromise analysis
Datasets
- Phishing Email Datasets
- SpamAssassin
- Enron
- PhishTank
- Recent phishing datasets
Output
- Phishing Probability
- Phishing Category
- Malicious URL Indicators
- Sender Reputation
- Spam Classification
- Risk Score
- Confidence
- Uncertainty
👤 7. User Behavior Analytics Agent
Purpose
The UBA Agent identifies abnormal user behavior.
Flow
User Activity
      ↓
Behavior Profile
      ↓
Historical Comparison
      ↓
Activity Anomaly Detection
      ↓
Privilege Analysis
      ↓
Risk Assessment

Techniques
- Behavioral profiling
- Activity modeling
- Anomaly detection
- Insider-threat analysis
- Privilege-abuse detection
- Abnormal data movement analysis
Datasets
- CERT Insider Threat
- LANL Authentication Data
- LANL Multi-Source Data
- Multi-source behavioral datasets
Output
- Behavior Anomaly
- Insider-Risk Indicator
- Privilege-Abuse Indicator
- User Risk
- Confidence
- Uncertainty
🔐 8. Identity & Authentication Agent
Purpose
The Identity Agent evaluates authentication and identity-related events.
Flow
Login
 ↓
Credential Verification
 ↓
2FA Verification
 ↓
Device / Location / Time Analysis
 ↓
Identity Risk
 ↓
Account Takeover Assessment

Techniques
- Login analysis
- Password + 2FA
- Biometric verification
- Device trust
- Location analysis
- Time-pattern analysis
- Account takeover detection
Datasets
- LANL Authentication
- NIST FRTE/FATE
- FERET
- Synthetic 2FA datasets
Output
- Identity Risk
- Authentication Result
- 2FA Result
- Biometric Match Result
- Anomalous Login
- Account Takeover Indicator
💳 9. Transaction Security Agent
Purpose
The Transaction Agent identifies suspicious financial and transaction behavior.
Flow
Transaction
     ↓
Entity Identification
     ↓
Amount / Recipient Analysis
     ↓
Historical Behavior
     ↓
Transaction Graph
     ↓
Fraud / Anomaly Analysis
     ↓
Transaction Evidence

Techniques
- Fraud detection
- Transaction anomaly detection
- Graph analysis
- Money-flow analysis
- Suspicious relationship detection
- Multi-layer transaction reasoning
Datasets
- ULB Credit Card Fraud
- Synthetic transaction data
- Company-Bank network data
- Uniswap transaction data
Output
- Transaction Risk
- Fraud Indicator
- Anomaly Score
- Suspicious Relationship
- Money-Flow Anomaly
🤖 10. AI-Agent Threat Analysis
HACTM also considers threats involving AI agents.
The architecture considers:
- CSTM-Bench
- Cross-session attacks
- Benign-hard scenarios
- AI-agent misuse
- Prompt/agent attack scenarios
Cross-Session Flow
Session 1
   ↓
Session 2
   ↓
Session 3
   ↓
Cross-Session Evidence
   ↓
Attack Chain

The purpose is to avoid treating every AI-agent interaction as an isolated event.
🌍 11. Threat Intelligence Layer
External intelligence is treated as evidence, not as the final decision.
Potential Integrations
AbuseIPDB
Used for:
- IP reputation
- Abuse confidence
- Report information
- ISP/domain information
- IP enrichment
NVD
Used for:
- CVE information
- CVSS information
- Affected products
- CPE information
- CWE information
- Vulnerability descriptions
Threat Intelligence Flow
External Intelligence
        ↓
Evidence Provider
        ↓
Normalization
        ↓
Reliability
        ↓
Uncertainty
        ↓
Contextual Relevance
        ↓
Temporal Relevance
        ↓
HACTM Evidence Fusion
        ↓
Cyber Risk
        ↓
Policy Decision

External intelligence does not directly produce:
BLOCK

or:
ALLOW

The final decision remains within the HACTM decision architecture.
🏷️ 12. Dynamic Security Context
Security evidence is converted into dynamic security context.
Entity
  ↓
Identity
  ↓
Security Tags
  ↓
Security Groups
  ↓
Security Zones
  ↓
Asset Dependencies

Example Security Tags
TRUSTED
HIGH_RISK
COMPROMISED
PRIVILEGED
THIRD_PARTY
CRITICAL

Security Groups
Examples:
- User Groups
- Application Groups
- Workload Groups
- IoT Groups
- Vehicle Groups
- Third-Party Groups
Security Zones
Examples:
- User Zone
- Application Zone
- Database Zone
- IoT Zone
- Admin Zone
- Third-Party Zone
This context later influences policy enforcement.
🔗 13. Local Evidence Fusion
Each site or edge environment can combine agent outputs locally.
Network Evidence
       │
Phishing Evidence
       │
UBA Evidence
       │
Identity Evidence
       │
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

The purpose is to avoid sending every raw event directly to the global orchestrator.
🧠 14. Adaptive Evidence Memory
HACTM maintains relevant evidence across sessions.
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

Memory Functions
- Recent evidence storage
- Historical evidence
- Entity-based memory
- Relevance scoring
- Evidence compression
- Cross-session correlation
- Attack progression tracking
- Historical evidence retrieval
The memory layer is intended to remain bounded so that storage does not grow without control.
🛡️ 15. Agent Reliability & Safety
HACTM does not automatically treat every agent as equally reliable.
Reliability Signals
- Accuracy
- False Positive Rate
- False Negative Rate
- Availability
- Latency
- Resource Usage
- Historical Performance
Failure Handling
Agent Failure
     ↓
Timeout
     ↓
Retry
     ↓
Circuit Breaker
     ↓
Fallback / Escalation

Additional Controls
- Schema validation
- Message ordering
- Idempotency
- Timestamp validation
- Stale evidence detection
- Conflict resolution
- Performance drift detection
- Calibration drift detection
- Data distribution shift detection
📐 16. Uncertainty & Calibration
HACTM does not assume that raw model confidence is automatically trustworthy.
The architecture includes a dedicated uncertainty and calibration layer.
Calibration Methods
- Temperature scaling
- Isotonic regression
- Conformal prediction
Evaluation Metrics
- Expected Calibration Error (ECE)
- Brier Score
- Calibration Error
- Empirical Coverage
- AUSE
Uncertainty Types
- Predictive uncertainty
- Epistemic uncertainty
- Aleatoric uncertainty
- Confidence interval
Result
Calibrated Probability
        +
Uncertainty
        +
Evidence Quality
        ↓
Calibrated Security Evidence

🕒 17. Regional Trust Orchestrator
The regional layer combines evidence from local or edge environments.
Site A
  ↓
Local Evidence
  ↓

Site B
  ↓
Local Evidence
  ↓

Site C
  ↓
Local Evidence
  ↓

Regional Trust Orchestrator

Functions
- Temporal correlation
- Sequence analysis
- Local attack-chain detection
- Entity relationships
- Local graph reasoning
- Weighted evidence fusion
- Confidence aggregation
- Regional risk assessment
- Cross-site correlation
High-signal evidence can then be forwarded to the global layer.
🌐 18. Global Adaptive Orchestrator
The Global Adaptive Orchestrator is the central intelligence layer.
                GLOBAL ADAPTIVE ORCHESTRATOR
                            │
           ┌────────────────┼────────────────┐
           ↓                ↓                ↓
    Agent Selection   Evidence Fusion   Graph Reasoning
           │                │                │
           └────────────────┼────────────────┘
                            ↓
                 Temporal Attack Reasoning
                            ↓
                     Resource Scheduling
                            ↓
                       Explainability

The central orchestrator combines:
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

to determine how available evidence should contribute to the overall cyber-risk state.
🎯 19. Risk-Driven Agent Selection
HACTM can dynamically select additional security agents based on the current security state.
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
Select Next Agent

The objective is:
More Useful Evidence
        +
Less Unnecessary Computation
        ↓
Adaptive Investigation

This is one of the major research directions of HACTM.
🕸️ 20. Graph Reasoning
HACTM can represent relationships between security entities.
Entity Graph
User
 │
 ├── Device
 │
 ├── Application
 │
 └── Account

Communication Graph
Device A
 │
 ├──── Device B
 │
 └──── Server C

Transaction Graph
Account A
    ↓
Account B
    ↓
Account C
    ↓
Account D

Attack Evidence Graph
Phishing
   ↓
Credential Compromise
   ↓
Suspicious Login
   ↓
Network Access
   ↓
Lateral Movement
   ↓
Transaction

Graph reasoning allows relationships between apparently separate events to be considered together.
⏱️ 21. Temporal Attack-Chain Reasoning
HACTM considers event sequences instead of evaluating only individual events.
Example:
T1
Phishing Email
    ↓
T2
Credential Capture
    ↓
T3
Suspicious Login
    ↓
T4
Abnormal Network Activity
    ↓
T5
Privilege Abuse
    ↓
T6
Suspicious Transaction

The system can correlate:
- Event ordering
- Time gaps
- Entity relationships
- Cross-session activity
- Long-term dependencies
⚙️ 22. Resource-Aware Scheduling
The global orchestrator considers the cost of invoking additional security agents.
Agent Reliability
       +
Detection Value
       +
Current Uncertainty
       +
Latency
       +
Compute Cost
       ↓
Agent Selection

This supports adaptive evidence acquisition.
🔎 23. Explainability
HACTM is designed to provide more than a numerical risk value.
Instead of only:
Risk = 0.82

the system can provide:
Decision: VERIFY

Risk: 0.82

Contributing Evidence:

1. Suspicious authentication
2. Network anomaly
3. Phishing indicator
4. Abnormal transaction
5. Historical entity risk

Supporting Context:

User: user-123
Device: device-22
Zone: Application Zone

Uncertainty: 0.11

The architecture records:
- Key evidence
- Reasoning path
- Context
- Agent contributions
- Risk factors
📊 24. Cyber Risk Assessment
HACTM produces a unified cyber-risk representation.
0.0 ─────────────────────────────── 1.0
Trusted                         High Risk

Risk can be influenced by:
Calibrated Evidence
        +
Uncertainty
        +
Agent Criticality
        +
Attack-Chain State
        +
Entity Context
        +
Security Tags
        +
Security Zone
        +
Historical Evidence
        ↓
Unified Cyber Risk

Conceptually:
0 → Trusted

1 → High Risk

Risk thresholds should be configured and validated experimentally rather than treated as universally correct.

🚦 25. Adaptive Policy Decision Point
The risk state is translated into a security policy action.
                    CYBER RISK
                        │
              ┌─────────┼─────────┐
              ↓         ↓         ↓
            LOW       MEDIUM     HIGH
              │         │         │
              ↓         ↓         ↓
            ALLOW     VERIFY   QUARANTINE
              │                   │
              └─────────┬─────────┘
                        ↓
                      BLOCK

Supported Conceptual Outcomes
ALLOW
Normal access.
MONITOR
Allow access with enhanced monitoring.
VERIFY
Request additional authentication such as:
- 2FA
- Biometric verification
- Additional verification
QUARANTINE
Restrict the entity or move it into an isolated environment.
BLOCK
Deny access and trigger a security response.
🧱 26. Adaptive Micro-Segmentation
Risk decisions can influence network and workload segmentation.
Potential enforcement points include:
Firewall
   ↓
SDN Controller
   ↓
Cloud Security Group
   ↓
Kubernetes NetworkPolicy
   ↓
Enterprise / Cloud / OT / IoT

Example
Normal Entity
     ↓
Normal Zone

Suspicious Entity
     ↓
Restricted Zone

Compromised Entity
     ↓
Quarantine Zone

The objective is to reduce lateral movement and limit the potential blast radius.
🔁 27. Telemetry & Feedback Loop
HACTM closes the loop after enforcement.
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
Generate New Evidence
      ↓
Reassess Risk
      ↓
Update Policy / Agent
      ↓
      ↺

Telemetry can include:
- Allow events
- Deny events
- Reject events
- Segmentation violations
- Reachable assets
- Blast radius
- Containment time
- False-positive rate
- False-negative rate
- Agent performance
🧠 Models & Detection Techniques
Important Research Note
HACTM is model-agnostic at the architecture level.
The architecture defines what each security agent must accomplish. Different models can be evaluated depending on:
- Dataset
- Implementation
- Research experiment
- Detection requirements
The project distinguishes between:
1. Detection techniques
2. Model families
3. Possible implementations
4. Research/planned models
5. Actual experimental models
Exact model assignments should only be reported when they are actually implemented and evaluated.

🌐 Network Agent Models
Detection Families
Signature-Based Detection
        +
Anomaly Detection
        +
Machine Learning / Deep Learning
        +
Flow Analysis

Possible implementations include:
- Random Forest
- Gradient Boosting
- Isolation Forest
- Neural-network-based anomaly detection
- Autoencoders
Network Detection Pipeline
Network Flow
     ↓
Network Dataset
     ↓
Dataset Loader
     ↓
Schema Validation
     ↓
Cleaning
     ↓
Feature Engineering
     ↓
Network Detector / Model
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

📧 Phishing Agent Models
Email
  ↓
NLP
  ↓
Text Representation
  ↓
Classification

Possible implementations include:
- TF-IDF + classical classifier
- Transformer-based classifiers
- URL feature models
- Hybrid email + URL models
The architecture identifies transformer-based models as a possible phishing-analysis method but does not require one specific transformer model.
👤 UBA Agent Models
Behavioral Flow
Behavior Profile
      ↓
Deviation Detection
      ↓
Risk

Possible approaches include:
- Statistical anomaly detection
- Clustering
- Isolation Forest
- Sequence models
- Behavioral profiling
- Graph-based behavior analysis
🔐 Identity Agent
The Identity Agent is not represented as one single machine-learning model.
It combines security mechanisms and behavioral analysis.
Possible techniques include:
- Authentication pattern analysis
- 2FA verification
- Biometric verification
- Device trust
- Time/location analysis
- Login anomaly detection
💳 Transaction Agent
Possible techniques include:
- Fraud classification
- Anomaly detection
- Graph analysis
- Transaction-network analysis
- Money-flow analysis
The architecture emphasizes graph-based reasoning and multi-layer transaction networks.
🧠 Central Orchestrator
The central orchestrator is not simply another classifier.
It combines:
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

The purpose is to determine:
- What evidence is required
- Which agent should be invoked
- How evidence should be weighted
- How uncertainty should affect the decision
- How historical evidence should influence risk
- How the final cyber-risk state should be produced
🧪 Dataset Strategy
HACTM uses domain-specific datasets.
Raw datasets are intentionally not committed to GitHub because some files are extremely large.
For example, individual BoT-IoT CSV files in the development environment can exceed 200 MB.
Therefore:
GitHub Repository
│
├── Backend
├── Frontend
├── Tests
├── Configuration
└── Documentation


Large Research Data
        ↓
Local / External Dataset Storage

📚 Dataset Catalog
🌐 Network Security
Dataset	Purpose
CIC-IDS2017	Intrusion detection
CSE-CIC-IDS2018	Modern network attack detection
UNSW-NB15	Network intrusion analysis
BoT-IoT	IoT botnet and network attacks
ToN-IoT	IoT / IIoT security


📧 Email / Phishing
Dataset / Source	Purpose
SpamAssassin	Spam/email classification
Enron	Email analysis
Phishing Email Datasets	Phishing detection
PhishTank	Malicious URL intelligence
Recent phishing datasets	Current phishing research


👤 User Behavior
Dataset	Purpose
CERT Insider Threat	Insider behavior
LANL Authentication	Authentication/user activity
LANL Multi-Source	Multi-source behavior analysis


🔐 Identity
Dataset	Purpose
LANL Authentication	Login/authentication behavior
NIST FRTE/FATE	Face/biometric evaluation
FERET	Face recognition
Synthetic 2FA	Authentication experiments


💳 Transactions
Dataset	Purpose
ULB Credit Card Fraud	Financial fraud detection
Synthetic Transaction Data	Controlled experiments
Company-Bank Network	Financial relationship analysis
Uniswap datasets	Blockchain transaction analysis


🤖 AI-Agent Security
Dataset / Source	Purpose
CSTM-Bench	Cross-session AI-agent threat evaluation
Multi-session attack scenarios	Longitudinal agent attacks
Benign-hard scenarios	Difficult benign cases


🌍 Threat Intelligence
Source	Purpose
MISP Galaxy	Threat intelligence
PhishTank	Malicious URLs
OSINT feeds	External intelligence
NVD	Vulnerability intelligence
AbuseIPDB	IP reputation


🔄 Dataset → Model → Evidence
Every domain follows the same conceptual pipeline.
Dataset
   ↓
Dataset Loader
   ↓
Schema Validation
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

🔗 Cross-Domain Evidence Fusion
The main architectural advantage of HACTM is that evidence from different domains can be correlated.
Illustrative example:
Phishing Agent
Risk = 0.72
      │
      ↓
Identity Agent
Risk = 0.68
      │
      ↓
Network Agent
Risk = 0.81
      │
      ↓
UBA Agent
Risk = 0.61
      │
      ↓
Transaction Agent
Risk = 0.77
      │
      ▼
CENTRAL TRUST ORCHESTRATOR
      │
      ├── Reliability
      ├── Uncertainty
      ├── Context
      ├── Temporal Reasoning
      ├── Graph Reasoning
      └── Historical Evidence
      │
      ▼
Unified Cyber Risk

Important: The values above are illustrative only and are not experimental results.

🧩 Evidence Deduplication
HACTM should avoid counting the same underlying evidence repeatedly.
Example:
IP 1.2.3.4
     ↓
Network Agent
     ↓
AbuseIPDB
     ↓
Threat Intelligence

If all three sources refer to the same underlying indicator, the system should recognize their relationship rather than blindly counting them as three independent events.
Evidence can be associated with:
indicator
provider
timestamp
evidence_id
entity_id

🔐 Security & Privacy
HACTM follows several security principles.
Secrets
Never commit:
.env
API keys
Passwords
Tokens
Private credentials

Use:
.env.example

as the configuration template.
Dataset Privacy
Sensitive or proprietary datasets should remain outside the public repository.
API Keys
External API keys must remain server-side.
The frontend should never directly receive:
ABUSEIPDB_API_KEY
NVD_API_KEY

📂 Project Structure
HACTM/
│
├── backend/
│   │
│   ├── src/
│   │   └── hactm/
│   │       │
│   │       ├── api/
│   │       │   ├── routers/
│   │       │   └── schemas/
│   │       │
│   │       ├── cli/
│   │       │
│   │       ├── core/
│   │       │
│   │       ├── eval/
│   │       │
│   │       ├── evaluation/
│   │       │
│   │       ├── feedback/
│   │       │
│   │       ├── fusion/
│   │       │
│   │       ├── graph/
│   │       │
│   │       ├── identity/
│   │       │   └── detectors/
│   │       │
│   │       ├── ingestion/
│   │       │   ├── datasets/
│   │       │   └── loaders/
│   │       │
│   │       ├── memory/
│   │       │
│   │       ├── network/
│   │       │   ├── detectors/
│   │       │   ├── features/
│   │       │   └── ml_ids/
│   │       │
│   │       ├── orchestration/
│   │       │
│   │       ├── phishing/
│   │       │   └── detectors/
│   │       │
│   │       ├── reliability/
│   │       │
│   │       ├── research/
│   │       │
│   │       ├── services/
│   │       │   └── threat_intelligence/
│   │       │
│   │       ├── storage/
│   │       │   └── repositories/
│   │       │
│   │       ├── temporal/
│   │       │
│   │       ├── transaction/
│   │       │   └── detectors/
│   │       │
│   │       ├── uba/
│   │       │   └── detectors/
│   │       │
│   │       └── zerotrust/
│   │
│   ├── data/
│   │   └── raw/
│   │
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── ...
│
├── data/
│   └── raw/
│       └── network/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── benchmarks/
│
├── docs/
│
├── scripts/
│
├── .env.example
├── .gitignore
└── README.md

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
Machine Learning & AI
- Scikit-learn
- Machine Learning
- Deep Learning
- NLP
- Transformer Models
- Anomaly Detection
- Graph Analysis
Security
- Intrusion Detection
- Phishing Detection
- User Behavior Analytics
- Identity Security
- Fraud Detection
- Threat Intelligence
- Zero Trust
- Micro-Segmentation
⚙️ Installation
1. Clone the Repository
git clone https://github.com/asif-visionary/HACTM.git
cd HACTM

🐍 Backend Setup
cd backend

Windows
py -m venv .venv
.venv\Scripts\activate

Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

Install Dependencies
pip install -r requirements.txt

⚛️ Frontend Setup
Open another terminal:
cd frontend
npm install
npm run dev

The Vite development URL will be displayed in the terminal.
🔑 Environment Variables
Create a .env file from:
.env.example

Example configuration:
ABUSEIPDB_API_KEY=
ABUSEIPDB_BASE_URL=

NVD_API_KEY=
NVD_BASE_URL=

NVD_API_TIMEOUT=15
ABUSEIPDB_API_TIMEOUT=10

Never commit the real .env file.

📥 Dataset Installation
The raw datasets are intentionally excluded from GitHub.
After cloning:
Linux / macOS
mkdir -p data/raw/network
mkdir -p backend/data/raw/network

Windows PowerShell
New-Item -ItemType Directory -Force data/raw/network
New-Item -ItemType Directory -Force backend/data/raw/network

Place the downloaded datasets according to the dataset loader expected by the project.
Example:
data/
└── raw/
    └── network/
        └── bot_iot/
            ├── data_1.csv
            ├── data_2.csv
            ├── ...
            └── data_63.csv

The same principle applies to other datasets.
🚫 Why the Datasets Are in .gitignore
Large raw datasets should not be committed directly to GitHub.
For example, individual BoT-IoT CSV files in the development environment can exceed 200 MB.
Therefore, HACTM separates:
Source Code
     ↓
GitHub Repository

from:
Large Research Data
     ↓
Local / External Dataset Storage

The repository ignores paths such as:
data/raw/network/bot_iot/
backend/data/raw/network/

The datasets remain available locally for experiments while Git tracks the application source code.
🧪 Testing
HACTM contains:
tests/
├── unit/
├── integration/
└── benchmarks/

Run:
pytest

Testing should cover:
- Data validation
- Dataset loaders
- Feature extraction
- Agent outputs
- Evidence normalization
- Evidence fusion
- Risk calculation
- External intelligence failures
- Duplicate evidence
- Calibration
- API behavior
- Policy decisions
📊 Evaluation Metrics
HACTM should not be evaluated using accuracy alone.
Detection Metrics
- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- PR-AUC
- False Positive Rate
- False Negative Rate
Calibration Metrics
- Expected Calibration Error
- Brier Score
- Calibration Error
- Coverage
- AUSE
Reliability Metrics
- Agent Availability
- Latency
- Failure Rate
- Resource Usage
Adaptive Orchestration
- Agent Invocation Count
- Detection Performance
- Inference Cost
- Latency
- Evidence Quality
Security Enforcement
- Containment Time
- Blast Radius
- Policy Effectiveness
- Segmentation Violations
- False Positive Rate
- False Negative Rate
🔬 Research Evaluation
HACTM is designed to investigate several research hypotheses.
H1 — Adaptive Agent Selection
Can risk-, uncertainty-, reliability- and cost-aware agent selection reduce unnecessary agent invocations while maintaining detection performance?
H2 — Reliability-Aware Fusion
Can reliability- and uncertainty-aware evidence fusion reduce incorrect decisions compared with simple unweighted fusion?
H3 — Cross-Session Memory
Can historical and cross-session evidence improve detection of multi-stage attacks?
H4 — Adaptive Micro-Segmentation
Can dynamic context-aware segmentation reduce lateral attack reach compared with static segmentation?
H5 — Closed-Loop Security
Can enforcement telemetry improve subsequent risk assessment and policy adaptation?
These are research hypotheses, not claimed experimental results.

💡 Research Positioning & Novelty
HACTM does not claim that individual technologies such as:
- IDS
- Phishing Detection
- UBA
- 2FA
- Biometric Verification
- Fraud Detection
- Graph Reasoning
- Uncertainty Calibration
- Zero Trust
- Micro-Segmentation
are individually novel.
The research direction focuses on the coordination mechanism between heterogeneous security systems.
Heterogeneous Evidence
        ↓
Reliability
        ↓
Uncertainty
        ↓
Historical Context
        ↓
Adaptive Agent Selection
        ↓
Cross-Domain Fusion
        ↓
Dynamic Security Context
        ↓
Cyber Risk
        ↓
Adaptive Enforcement
        ↓
Telemetry
        ↓
Reassessment

The research positioning emphasizes:
Reliability- and uncertainty-aware adaptive evidence orchestration

rather than claiming novelty for each underlying security technology.
🧭 Development Roadmap
PHASE 1
Foundation & Common Data Model
        ↓
PHASE 2
Data Ingestion & Preprocessing
        ↓
PHASE 3
Specialized Security Agents
        ↓
PHASE 4
Security Evidence & Local Fusion
        ↓
PHASE 5
Evidence Memory
        ↓
PHASE 6
Reliability & Uncertainty
        ↓
PHASE 7
Regional Orchestration
        ↓
PHASE 8
Global Adaptive Orchestration
        ↓
PHASE 9
Risk Assessment
        ↓
PHASE 10
Adaptive Policy
        ↓
PHASE 11
Micro-Segmentation
        ↓
PHASE 12
Telemetry & Feedback
        ↓
PHASE 13
Evaluation & Research

🖥️ Dashboard
The HACTM dashboard is designed to provide visibility into:
Security Events
      ↓
Evidence Explorer
      ↓
Agent Results
      ↓
Risk Assessment
      ↓
Policy Decisions
      ↓
Security Context
      ↓
Threat Intelligence
      ↓
Historical Evidence

Possible dashboard information includes:
- Unified cyber risk
- Agent status
- Security events
- Risk distribution
- Evidence sources
- Confidence
- Uncertainty
- Threat categories
- Policy decisions
- Historical events
- Agent reliability
- Threat intelligence
📄 Security Reporting
HACTM can generate structured security reports containing:
- Executive summary
- Security events
- Evidence
- Risk assessment
- Agent contributions
- Context
- Threat intelligence
- Policy decisions
- Enforcement actions
- Recommendations
- Historical evidence
Reporting Flow
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
Report

🔄 Complete HACTM Closed Loop
┌─────────────────────────────┐
│        DATA SOURCES         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│      DATA PREPROCESSING     │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     SPECIALIZED AGENTS      │
│                             │
│ Network | Phishing | UBA    │
│ Identity | Transaction      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│      SECURITY EVIDENCE      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│      LOCAL EVIDENCE FUSION  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│   RELIABILITY + UNCERTAINTY │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│       EVIDENCE MEMORY       │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     REGIONAL ORCHESTRATOR   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│      GLOBAL ORCHESTRATOR    │
│                             │
│ Agent Selection             │
│ Evidence Fusion             │
│ Graph Reasoning             │
│ Temporal Reasoning          │
│ Explainability              │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│        CYBER RISK           │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│      POLICY DECISION        │
│                             │
│ ALLOW | MONITOR | VERIFY    │
│ QUARANTINE | BLOCK          │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     MICRO-SEGMENTATION      │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│     TELEMETRY & FEEDBACK    │
└──────────────┬──────────────┘
               │
               └──────────→ REASSESS

🔮 Future Enhancements
Planned research directions include:
- Advanced adaptive agent selection
- More robust uncertainty estimation
- Concept-drift detection
- Adversarial robustness
- Improved graph reasoning
- Cross-session attack reasoning
- Advanced AI-agent security
- More threat-intelligence providers
- Real-time streaming
- Distributed deployment
- Kubernetes deployment
- SDN integration
- Cloud security integration
- Automated remediation
- Advanced policy learning
- Continuous model recalibration
⚠️ Ethical Use & Disclaimer
HACTM is intended strictly for:
- Educational purposes
- Cybersecurity research
- Academic projects
- Security experimentation
- Authorized security assessments
- Laboratory environments
- Controlled testing
Do not use HACTM to monitor, scan, attack, enumerate, or interfere with systems, networks, accounts, applications, or data without explicit authorization.
The project must only be used against systems and datasets for which you have appropriate permission.
The authors are not responsible for misuse of this software.
👨‍💻 Author
Mohamed Asif
Cybersecurity Enthusiast | Security Researcher | Developer
GitHub:
https://github.com/asif-visionary
📜 License
Add the selected open-source license to:
LICENSE

For example:
MIT License

Select and add the license that matches the intended distribution and usage of the project.

⭐ Support
If HACTM is useful for:
- Cybersecurity research
- Academic experimentation
- Security engineering
- Multi-agent security research
- Digital trust research
consider giving the repository a ⭐.
🛡️ HACTM
        HIERARCHICAL ADAPTIVE
          CYBER TRUST MESH

                  │
                  ▼

     ┌──────────────────────────┐
     │   MULTI-DOMAIN EVIDENCE  │
     └────────────┬─────────────┘
                  ↓
     ┌──────────────────────────┐
     │    SPECIALIZED AGENTS    │
     │                          │
     │ Network                  │
     │ Phishing                 │
     │ UBA                      │
     │ Identity                 │
     │ Transaction              │
     └────────────┬─────────────┘
                  ↓
     ┌──────────────────────────┐
     │     EVIDENCE FUSION      │
     └────────────┬─────────────┘
                  ↓
     ┌──────────────────────────┐
     │ RELIABILITY + UNCERTAINTY│
     └────────────┬─────────────┘
                  ↓
     ┌──────────────────────────┐
     │   ADAPTIVE ORCHESTRATOR  │
     └────────────┬─────────────┘
                  ↓
     ┌──────────────────────────┐
     │        CYBER RISK        │
     └────────────┬─────────────┘
                  ↓
     ┌──────────────────────────┐
     │     ZERO-TRUST POLICY    │
     └────────────┬─────────────┘
                  ↓
     ┌──────────────────────────┐
     │    MICRO-SEGMENTATION    │
     └────────────┬─────────────┘
                  ↓
     ┌──────────────────────────┐
     │    TELEMETRY / FEEDBACK  │
     └────────────┬─────────────┘
                  │
                  └──────→ REASSESS