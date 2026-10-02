generate the .md broo for hactm
# 🛡️ HACTM — Hierarchical Adaptive Cyber Trust Mesh

### A Reliability- and Uncertainty-Aware Multi-Agent Architecture for Cross-Domain Threat Detection and Adaptive Zero-Trust Security

> **From isolated security alerts to adaptive, evidence-driven cyber trust.**

---

## 📌 What is HACTM?

**HACTM (Hierarchical Adaptive Cyber Trust Mesh)** is a research-oriented cybersecurity architecture that combines security information from multiple domains and converts it into a unified, context-aware security decision.

Instead of treating every security alert independently, HACTM connects evidence from:

- 🌐 Network Security
- 📧 Phishing & Email Security
- 👤 User Behavior Analytics (UBA)
- 🔐 Identity & Authentication
- 💳 Transaction Security
- 🤖 AI-Agent Security
- 🌍 External Threat Intelligence

The findings from these security areas are converted into a common **Security Evidence** format.

HACTM then uses:

- Evidence Fusion
- Evidence Memory
- Reliability
- Uncertainty
- Temporal Reasoning
- Graph Reasoning
- Security Context
- Adaptive Agent Selection
- Regional Orchestration
- Global Orchestration
- Cyber-Risk Assessment
- Adaptive Policy
- Micro-Segmentation
- Telemetry & Feedback

to make security decisions.

---

# 🎯 Core Problem

Modern organizations generate security alerts from many independent systems.

```text
                         ORGANIZATION
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
    Network IDS          Email Security       Identity
          │                   │                   │
          ▼                   ▼                   ▼
    Network Alert        Phishing Alert      Login Alert

          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
        UBA               Transactions        Endpoint
          │                   │                   │
          ▼                   ▼                   ▼
    Behavior Alert        Fraud Alert        EDR Alert
The problem is that these alerts may be generated independently.

For example:

Suspicious Login
       +
Phishing Email
       +
Abnormal Network Traffic
       +
Unusual User Behavior
       +
Suspicious Transaction
       +
Previous Suspicious Activity
       ↓
Higher Contextual Risk
A single alert may not be enough to understand the actual security situation.

HACTM's approach
HACTM correlates these different signals and asks:

Are these events related, how trustworthy is the evidence, how certain are we, what happened previously, and what security action should happen next?

🧠 HACTM Core Idea
Raw Security Data
        ↓
Security Events
        ↓
Normalized Security Data
        ↓
Specialized Security Agents
        ↓
Security Evidence
        ↓
Local Evidence Fusion
        ↓
Evidence Memory
        ↓
Reliability + Uncertainty
        ↓
Regional Orchestration
        ↓
Global Adaptive Orchestration
        ↓
Temporal + Graph + Context Reasoning
        ↓
Cyber Risk
        ↓
Adaptive Policy
        ↓
Security Enforcement
        ↓
Telemetry
        ↓
New Evidence
        ↓
Reassessment
        ↺
The result is a continuous security feedback loop rather than a one-time detection process.

🏗️ Complete HACTM Architecture
                         ┌──────────────────────────────┐
                         │      MULTI-DOMAIN DATA       │
                         │ Network • Email • Identity   │
                         │ UBA • Transactions • AI • TI │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │       DATA INGESTION         │
                         │   Normalize • Validate       │
                         │   Extract • Enrich           │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │     SPECIALIZED AGENTS       │
                         │ Network • Phishing • UBA     │
                         │ Identity • Transaction • AI  │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │     SECURITY EVIDENCE        │
                         │       + LOCAL FUSION         │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │       EVIDENCE MEMORY        │
                         │ Current • Recent • Historical│
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │   RELIABILITY + UNCERTAINTY  │
                         │ Trustworthiness • Confidence │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │   REGIONAL ORCHESTRATION     │
                         │ Local / Site / Edge Analysis │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │ GLOBAL ADAPTIVE ORCHESTRATOR │
                         │ Context • Time • Graph • Risk│
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │       CYBER RISK             │
                         │      LOW • MEDIUM • HIGH     │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │      ADAPTIVE POLICY         │
                         │ Allow • Monitor • Verify     │
                         │ Quarantine • Block           │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │   MICRO-SEGMENTATION         │
                         │ Firewall • SDN • Cloud • K8s │
                         └──────────────┬───────────────┘
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │     TELEMETRY & FEEDBACK     │
                         │ Observe • Measure • Reassess │
                         └──────────────┬───────────────┘
                                        │
                                        └──────────────────↺
                                             NEW EVIDENCE
🔄 Complete End-to-End HACTM Flow
<div align="center">

┌────────────────────────────────────────────────────────────────────┐
│                         REAL-WORLD ACTIVITY                        │
│ Users • Devices • Applications • Network • Email • Transactions    │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 1. MULTI-DOMAIN DATA SOURCES                                       │
│ Collect security information from different security domains       │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 2. DATA INGESTION & PREPROCESSING                                  │
│ Collect → Normalize → Validate → Resolve → Extract → Enrich        │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 3. SPECIALIZED SECURITY AGENTS                                     │
│ Network | Phishing | UBA | Identity | Transaction | AI | TI        │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 4. SECURITY EVIDENCE & LOCAL FUSION                                │
│ Convert findings into common evidence and correlate locally        │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 5. EVIDENCE MEMORY                                                 │
│ Current + Recent + Historical + Cross-Session Evidence             │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 6. RELIABILITY & UNCERTAINTY                                       │
│ Evaluate evidence trustworthiness and prediction uncertainty       │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 7. REGIONAL ORCHESTRATION                                          │
│ Combine and reason over evidence within local environments         │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 8. GLOBAL ADAPTIVE ORCHESTRATION                                   │
│ Context + History + Time + Graph + Risk + Agent Selection          │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 9. CYBER RISK ASSESSMENT                                           │
│ Generate unified contextual cyber risk                             │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 10. ADAPTIVE POLICY                                                │
│ ALLOW | MONITOR | VERIFY | QUARANTINE | BLOCK                      │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 11. ADAPTIVE MICRO-SEGMENTATION                                    │
│ Apply restrictions to users, workloads, networks or assets         │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────┐
│ 12. TELEMETRY & FEEDBACK                                           │
│ Observe enforcement → Measure → Generate evidence → Reassess       │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
                                    └───────────────────────────────↺
</div>
📚 Layer-by-Layer Architecture
1️⃣ Layer 1 — Multi-Domain Data Sources
Purpose
HACTM starts by collecting information from different security domains.

Data Sources
<div align="center">

                         SECURITY DATA
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
     NETWORK                EMAIL                IDENTITY
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
      UBA                TRANSACTION             AI
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    THREAT INTELLIGENCE
</div>
Network
Possible sources:

CIC-IDS2017
CSE-CIC-IDS2018
UNSW-NB15
BoT-IoT
ToN-IoT
NetFlow
PCAP
DNS Logs
Firewall Logs
IDS/IPS Logs
Email & Phishing
Possible sources:

Phishing email datasets
SpamAssassin
Enron
PhishTank
Recent phishing datasets
Endpoint
Possible sources:

Windows Logs
Linux Logs
Endpoint Telemetry
Process Events
File Events
Registry Events
EDR Data
Identity
Possible sources:

LANL Authentication Data
NIST FRTE/FATE
FERET
Synthetic 2FA Data
Transactions
Possible sources:

ULB Credit Card Fraud
Synthetic Transaction Data
Company-Bank Network Data
E-commerce / Banking Data
Uniswap Transaction Data
AI-Agent Security
Possible sources:

CSTM-Bench
Cross-session attack scenarios
Benign-hard scenarios
AI-agent misuse scenarios
Prompt/agent attack scenarios
Threat Intelligence
Possible sources:

MISP Galaxy
PhishTank
OSINT feeds
NVD
AbuseIPDB
Main Features
Multi-domain visibility
Multiple security data sources
External intelligence integration
Support for heterogeneous security information
2️⃣ Layer 2 — Data Ingestion & Preprocessing
Raw data cannot directly enter the orchestration system.

HACTM first converts it into a common structure.
<div align="center">



                         RAW DATA
                            │
                            ▼
                       COLLECTION
                            │
                            ▼
                      NORMALIZATION
                            │
                            ▼
                         PARSING
                            │
                            ▼
                   SCHEMA VALIDATION
                            │
                            ▼
                   ENTITY RESOLUTION
                            │
                            ▼
                   FEATURE EXTRACTION
                            │
                            ▼
                  TIME SYNCHRONIZATION
                            │
                            ▼
                  THREAT INTELLIGENCE
                      ENRICHMENT
                            │
                            ▼
                    CONTEXT ENRICHMENT
                            │
                            ▼
                PREPROCESSED SECURITY DATA

</div>
Entity Resolution
HACTM can associate events with:

User
Device
IP Address
Account
Application
Workload
Transaction
Main Features
Data normalization
Schema validation
Entity resolution
Feature extraction
Time synchronization
Threat-intelligence enrichment
Context enrichment
Output
Raw Security Data
        ↓
Clean + Structured + Enriched Security Data
3️⃣ Layer 3 — Specialized Security Agents
This layer performs domain-specific analysis.
<div align="center">


                         SECURITY DATA
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       NETWORK AGENT     PHISHING AGENT      UBA AGENT
             │                 │                 │
             ▼                 ▼                 ▼
       IDENTITY AGENT    TRANSACTION AGENT   AI / TI AGENT
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ▼
                     SECURITY FINDINGS

</div>
🌐 Network Security Agent
Purpose
Detect suspicious network activity.
<div align="center">

Analysis
Network Traffic
       ↓
Flow Analysis
       ↓
Signature Detection
       ↓
Anomaly Detection
       ↓
Behavior Analysis
       ↓
Network Finding

</div>
Can detect
Network anomalies
Intrusion
Suspicious traffic
Zero-day-like behavior
Lateral movement
East-west traffic
Micro-segmentation violations
Possible model families
Signature-based detection
Random Forest
Gradient Boosting
Isolation Forest
Neural-network-based anomaly detection
Autoencoders
HACTM is model-agnostic. These are possible implementations, not a claim that one fixed model is the final model.

📧 Phishing Intelligence Agent
Purpose
Analyze emails and URLs for phishing-related threats.

<div align="center">

Email
  ↓
NLP
  ↓
Text Representation
  ↓
Email Classification
  ↓
URL Analysis
  ↓
Sender / Attachment Analysis
  ↓
Phishing Evidence

</div>

Can analyze
Email content
URLs
Sender reputation
Attachments
Generic phishing
Spear phishing
Business Email Compromise
Possible models
TF-IDF + classical classifier
Transformer-based classifiers
URL feature models
Hybrid email + URL models
👤 User Behavior Analytics Agent
Purpose
Understand whether user activity differs from normal behavior.

User Activity
      ↓
Behavior Profile
      ↓
Historical Comparison
      ↓
Deviation Detection
      ↓
Privilege Analysis
      ↓
Abnormal Behavior
      ↓
Risk Evidence
Can detect
Insider-threat indicators
Abnormal activity
Privilege abuse
Unusual data movement
Behavioral deviations
Possible approaches
Statistical anomaly detection
Clustering
Isolation Forest
Sequence models
Behavioral profiling
Graph-based behavior analysis
🔐 Identity Agent
Purpose
Evaluate authentication and identity-related security.

Login
  ↓
Authentication Analysis
  ↓
Device Trust
  ↓
Time / Location
  ↓
MFA / 2FA
  ↓
Login Behavior
  ↓
Identity Risk
Features
Authentication pattern analysis
2FA verification
Biometric verification
Device trust
Time/location analysis
Login anomaly detection
The identity layer is not represented as one single ML model. It combines security mechanisms and behavioral analysis.

💳 Transaction Security Agent
Purpose
Identify suspicious or fraudulent transactions.

Transaction
     ↓
Transaction Features
     ↓
Anomaly Detection
     ↓
Fraud Analysis
     ↓
Graph Analysis
     ↓
Money-Flow Analysis
     ↓
Transaction Risk
Features
Fraud classification
Anomaly detection
Graph analysis
Transaction-network analysis
Money-flow analysis
🤖 AI-Agent Security
Purpose
Analyze security risks involving AI-agent environments.

Areas
Cross-session attacks
Benign-hard scenarios
AI-agent misuse
Prompt/agent attack scenarios
Multi-session attack behavior
🌍 Threat Intelligence Agent
Purpose
Add external security intelligence to HACTM evidence.

External Intelligence
        ↓
Indicator Extraction
        ↓
Normalization
        ↓
Entity Matching
        ↓
Threat Intelligence Evidence
Possible sources include:

MISP Galaxy
PhishTank
NVD
AbuseIPDB
OSINT feeds
4️⃣ Layer 4 — Security Evidence & Local Fusion
Different agents produce different findings.

HACTM converts them into a common SecurityEvidence representation.

Network Finding
       +
Phishing Finding
       +
Identity Finding
       +
UBA Finding
       +
Transaction Finding
       ↓
┌──────────────────────────────┐
│      SECURITY EVIDENCE       │
└──────────────────────────────┘
       ↓
┌──────────────────────────────┐
│     LOCAL EVIDENCE FUSION    │
└──────────────────────────────┘
       ↓
Correlated Security Evidence
SecurityEvidence
Conceptual fields include:

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
External intelligence can additionally provide:

source_provider
source_type
indicator_type
indicator
reliability
observed_at
expires_at
normalization_version
Main Features
Common evidence format
Cross-agent correlation
Local risk
Confidence
Uncertainty
Security context
Evidence traceability
5️⃣ Layer 5 — Dynamic Security Context
HACTM needs to understand who or what the evidence belongs to.

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
Example
Entity: User-101

        ↓

Identity: Employee

        ↓

Tags:
TRUSTED
PRIVILEGED
HIGH_RISK

        ↓

Group:
Finance

        ↓

Zone:
Critical Application

        ↓

Dependencies:
Database + Payment System
Possible Security Tags
TRUSTED
HIGH_RISK
COMPROMISED
PRIVILEGED
THIRD_PARTY
CRITICAL
Possible Security Zones
User
Application
Database
IoT
Admin
Third-Party
Why it matters
The same event can have different consequences depending on the affected entity.

6️⃣ Layer 6 — Evidence Memory
HACTM maintains relevant historical information.

                         CURRENT EVENT
                              │
                              ▼
                        RECENT EVENTS
                              │
                              ▼
                     HISTORICAL EVENTS
                              │
                              ▼
                       ENTITY HISTORY
                              │
                              ▼
                     CROSS-SESSION DATA
                              │
                              ▼
                      EVIDENCE MEMORY
Main Features
Current evidence
Recent evidence
Historical evidence
Entity history
Cross-session reasoning
Attack progression
Previous suspicious behavior
Example
Phishing Email
      ↓
Credential Compromise
      ↓
Suspicious Login
      ↓
Abnormal Network Traffic
      ↓
Privilege Abuse
      ↓
Suspicious Transaction
HACTM can use these relationships to understand a developing security situation.

7️⃣ Layer 7 — Reliability & Uncertainty
HACTM separates reliability, confidence, and uncertainty.

Reliability
Reliability asks:

How trustworthy is this security agent?

Agent Performance
       +
False Positive Rate
       +
False Negative Rate
       +
Availability
       +
Latency
       +
Historical Performance
       ↓
AGENT RELIABILITY
Uncertainty
Uncertainty asks:

How certain is this particular prediction?

Prediction
    ↓
Confidence
    ↓
Uncertainty
    ↓
Calibration
    ↓
Calibrated Evidence
Possible calibration approaches
Temperature Scaling
Isotonic Regression
Conformal Prediction
Possible evaluation metrics
Expected Calibration Error (ECE)
Brier Score
Calibration Error
Empirical Coverage
AUSE
Types of uncertainty
Predictive uncertainty
Epistemic uncertainty
Aleatoric uncertainty
Confidence intervals
8️⃣ Layer 8 — Regional Orchestration
Regional orchestration combines evidence within a local or regional environment.

                 LOCAL SECURITY EVIDENCE
                           │
                           ▼
                REGIONAL ORCHESTRATOR
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
     Temporal           Graph              Context
     Analysis          Analysis            Analysis
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                    REGIONAL RISK
Main Features
Local evidence correlation
Regional risk
Temporal relationships
Graph relationships
Cross-site reasoning
Local security context
9️⃣ Layer 9 — Global Adaptive Orchestration
This is the central coordination layer.

The global orchestrator is not simply another classifier.

It combines multiple types of information.

                           EVIDENCE
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
      RISK              UNCERTAINTY             RELIABILITY
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              ▼
                       HISTORICAL DATA
                              │
                              ▼
                       SECURITY CONTEXT
                              │
                              ▼
                   TEMPORAL RELATIONSHIPS
                              │
                              ▼
                     GRAPH RELATIONSHIPS
                              │
                              ▼
                    INVESTIGATION COST
                              │
                              ▼
                  GLOBAL ORCHESTRATOR
It considers
Current risk
Evidence uncertainty
Agent reliability
Historical evidence
Security context
Temporal relationships
Graph relationships
Investigation cost
🎯 Adaptive Agent Selection
HACTM can decide whether additional analysis is required.

                 CURRENT SECURITY STATE
                           │
                           ▼
                 ┌───────────────────┐
                 │ Should more       │
                 │ analysis happen?  │
                 └─────────┬─────────┘
                           │
                    ┌──────┴──────┐
                    │             │
                   YES            NO
                    │             │
                    ▼             ▼
             Select Agent      Continue
                    │
                    ▼
             New Evidence
                    │
                    └───────────────→ Fusion
Example
Suspicious Email
      ↓
Phishing Agent
      ↓
Risk increases
      ↓
Identity Agent selected
      ↓
Suspicious Login
      ↓
Network Agent selected
      ↓
Abnormal Traffic
      ↓
Risk increases
This makes the architecture adaptive instead of forcing every agent to analyze every event.

🕒 Temporal Reasoning
Temporal reasoning understands when events happened and how they relate over time.

T1
Phishing Email
      ↓
T2
Credential Activity
      ↓
T3
Suspicious Login
      ↓
T4
Network Anomaly
      ↓
T5
Privilege Abuse
      ↓
T6
Suspicious Transaction
Instead of treating six events as independent alerts, HACTM can reason about their sequence.

🕸️ Graph Reasoning
HACTM can represent relationships between entities.

                    ┌───────────┐
                    │   USER    │
                    └─────┬─────┘
                          │
                          ▼
                    ┌───────────┐
                    │  DEVICE   │
                    └─────┬─────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │   APP    │ │ ACCOUNT  │ │ NETWORK  │
        └────┬─────┘ └────┬─────┘ └──────────┘
             │            │
             └──────┬─────┘
                    ▼
             ┌──────────────┐
             │ TRANSACTION  │
             └──────────────┘
Possible graphs
User-device-application graph
Communication graph
Transaction graph
Attack evidence graph
Purpose
Understand relationships, not just individual events.

🔟 Layer 10 — Cyber Risk Assessment
All important evidence is combined to produce a unified cyber-risk assessment.

Evidence
   +
Context
   +
History
   +
Reliability
   +
Uncertainty
   +
Temporal Reasoning
   +
Graph Reasoning
   ↓
┌──────────────────────────────┐
│       CYBER RISK ENGINE      │
└──────────────┬───────────────┘
               ↓
       ┌───────┼───────┐
       ▼       ▼       ▼
      LOW    MEDIUM   HIGH
Example
Phishing Evidence       → HIGH
Identity Evidence       → HIGH
Network Evidence        → MEDIUM
UBA Evidence            → HIGH
Transaction Evidence    → HIGH
Historical Evidence     → HIGH
Agent Reliability       → HIGH
Uncertainty             → MEDIUM

              ↓

       UNIFIED CYBER RISK
1️⃣1️⃣ Layer 11 — Adaptive Policy
The risk assessment is converted into a security action.

                        CYBER RISK
                            │
                            ▼
                     POLICY ENGINE
                            │
       ┌────────────┬──────┼──────┬────────────┐
       ▼            ▼      ▼      ▼            ▼
    ┌──────┐   ┌────────┐ ┌──────┐ ┌──────────┐ ┌───────┐
    │ALLOW │   │MONITOR │ │VERIFY│ │QUARANTINE│ │ BLOCK │
    └──────┘   └────────┘ └──────┘ └──────────┘ └───────┘
ALLOW
Normal access.

MONITOR
Allow access while increasing monitoring.

VERIFY
Request additional verification such as:

2FA
Biometrics
Additional authentication
QUARANTINE
Restrict the entity or move it into an isolated environment.

BLOCK
Deny access and trigger a security response.

1️⃣2️⃣ Layer 12 — Adaptive Micro-Segmentation
Risk-driven decisions can affect the network or workload environment.

                       CYBER RISK
                           │
                           ▼
                       POLICY
                           │
                           ▼
                     ENFORCEMENT
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
    FIREWALL               SDN             CLOUD
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                     KUBERNETES
                           │
                           ▼
                   SECURITY ZONES
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
Goal
Reduce lateral movement
Restrict access
Limit blast radius
Isolate compromised entities
1️⃣3️⃣ Layer 13 — Telemetry & Feedback
HACTM does not stop after making a decision.

It observes the result.

                     POLICY DECISION
                            │
                            ▼
                       ENFORCEMENT
                            │
                            ▼
                         TELEMETRY
                            │
                            ▼
                      OBSERVE RESULT
                            │
                            ▼
                  MEASURE EFFECTIVENESS
                            │
                            ▼
                      NEW EVIDENCE
                            │
                            ▼
                      REASSESS RISK
                            │
                            ▼
                  UPDATE POLICY / AGENT
                            │
                            └──────────────↺
Telemetry can include
Allow events
Deny events
Reject events
Segmentation violations
Reachable assets
Blast radius
Containment time
False-positive rate
False-negative rate
Agent performance
Why it matters
The result of enforcement becomes new evidence.

This creates the adaptive feedback loop.

🔁 Complete Closed-Loop Model
                         ┌──────────────────────┐
                         │     DATA SOURCES     │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │     PREPROCESSING    │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │  SPECIALIZED AGENTS  │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ SECURITY EVIDENCE    │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │   LOCAL FUSION       │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │  EVIDENCE MEMORY     │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ RELIABILITY +        │
                         │ UNCERTAINTY          │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ REGIONAL             │
                         │ ORCHESTRATION        │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ GLOBAL ADAPTIVE      │
                         │ ORCHESTRATION        │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ TEMPORAL + GRAPH +   │
                         │ CONTEXT REASONING    │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │     CYBER RISK       │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │   POLICY ENGINE      │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │    ENFORCEMENT       │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │ MICRO-SEGMENTATION   │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │      TELEMETRY       │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │    NEW EVIDENCE      │
                         └──────────┬───────────┘
                                    ↓
                         ┌──────────────────────┐
                         │     REASSESSMENT     │
                         └──────────┬───────────┘
                                    │
                                    └──────────────↺
🔥 HACTM Example — Complete Attack Scenario
Consider an employee receiving a phishing email.

                    PHISHING EMAIL
                          │
                          ▼
                  PHISHING AGENT
                          │
                          ▼
                Suspicious Email
                          │
                          ▼
                 SECURITY EVIDENCE
                          │
                          ▼
                  EVIDENCE MEMORY
                          │
                          ▼
              Identity Agent Selected
                          │
                          ▼
                Suspicious Login
                          │
                          ▼
               NETWORK AGENT SELECTED
                          │
                          ▼
                Abnormal Traffic
                          │
                          ▼
                  UBA AGENT SELECTED
                          │
                          ▼
                 Abnormal Behavior
                          │
                          ▼
             TRANSACTION AGENT SELECTED
                          │
                          ▼
                Suspicious Transaction
                          │
                          ▼
                  EVIDENCE FUSION
                          │
                          ▼
             TEMPORAL + GRAPH CONTEXT
                          │
                          ▼
              RELIABILITY + UNCERTAINTY
                          │
                          ▼
                GLOBAL ORCHESTRATOR
                          │
                          ▼
                    CYBER RISK
                          │
                          ▼
                     HIGH RISK
                          │
                          ▼
                  POLICY DECISION
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
              VERIFY          QUARANTINE
                                   │
                                   ▼
                          MICRO-SEGMENTATION
                                   │
                                   ▼
                                TELEMETRY
                                   │
                                   ▼
                            NEW EVIDENCE
                                   │
                                   ▼
                              REASSESS
                                   ↺
What a traditional system may see
Phishing Alert
Login Alert
Network Alert
Behavior Alert
Transaction Alert
What HACTM tries to understand
        These events may belong to
              the same entity
                    and
        may represent one developing
             security incident.
🧩 HACTM Security Evidence Model
The common evidence representation allows different agents to communicate.

┌─────────────────────────────────────────────┐
│              SECURITY EVIDENCE              │
├─────────────────────────────────────────────┤
│ Event ID                                    │
│ Agent ID                                    │
│ Entity ID                                   │
│ Event Type                                  │
│ Timestamp                                   │
│ Risk Score                                  │
│ Confidence                                  │
│ Uncertainty                                 │
│ Evidence                                    │
│ Security Tags                               │
│ Security Group                              │
│ Security Zone                               │
│ Model Version                               │
└─────────────────────────────────────────────┘
External threat intelligence may additionally include:

Source Provider
Source Type
Indicator Type
Indicator
Reliability
Observed At
Expires At
Normalization Version
🧠 HACTM Reasoning Model
HACTM combines several forms of reasoning.

                       SECURITY EVIDENCE
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
      CONTEXT              TEMPORAL              GRAPH
      REASONING            REASONING            REASONING
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                       HISTORICAL MEMORY
                              │
                              ▼
                    RELIABILITY + UNCERTAINTY
                              │
                              ▼
                        CYBER RISK
Context Reasoning
Understands:

Who
What device
Which application
Which asset
Which group
Which security zone
Temporal Reasoning
Understands:

What happened first
What happened next
How events evolved
Graph Reasoning
Understands:

User-device relationships
Application relationships
Communication relationships
Transaction relationships
Attack relationships
🎯 HACTM Key Features
Feature	What it does
🌐 Multi-Domain Security	Combines network, email, identity, UBA, transaction and AI-agent evidence
🧩 Evidence Fusion	Correlates different security signals
🛡️ Reliability Awareness	Considers historical agent performance
📐 Uncertainty Awareness	Separates confidence from uncertainty
🧠 Evidence Memory	Maintains relevant historical evidence
🕒 Temporal Reasoning	Understands event sequences
🕸️ Graph Reasoning	Understands relationships between entities
🎯 Adaptive Agent Selection	Dynamically selects additional analysis
🌍 Regional Orchestration	Combines evidence within local environments
🌐 Global Orchestration	Performs cross-domain reasoning
🚦 Adaptive Policy	Converts risk into security actions
🧱 Micro-Segmentation	Enables risk-driven isolation
🔁 Telemetry Feedback	Uses enforcement results as new evidence
🔎 Explainability	Records contributing evidence and reasoning context
🌍 Threat Intelligence	Integrates external intelligence
📄 Security Reporting	Produces structured security reports
🧠 Models & Detection Techniques
HACTM is model-agnostic at the architecture level.

The architecture defines what each agent should accomplish.

Different models can be evaluated depending on:

Dataset
Implementation
Detection requirement
Research experiment
Therefore, the documentation distinguishes between:

Detection techniques
Model families
Possible implementations
Research/planned models
Actual experimental models
Exact model assignments should only be claimed when actually implemented and evaluated.

Network Agent
Network Data
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
Possible approaches:

Signature-based detection
Random Forest
Gradient Boosting
Isolation Forest
Neural-network anomaly detection
Autoencoders
Phishing Agent
Email
  ↓
NLP
  ↓
Text Representation
  ↓
Classification
  ↓
URL / Sender / Attachment Analysis
  ↓
SecurityEvidence
Possible approaches:

TF-IDF + classical classifier
Transformer-based classifiers
URL feature models
Hybrid email + URL models
UBA Agent
User Activity
      ↓
Behavior Profile
      ↓
Historical Comparison
      ↓
Deviation Detection
      ↓
Risk Evidence
Possible approaches:

Statistical anomaly detection
Clustering
Isolation Forest
Sequence models
Behavioral profiling
Graph-based behavior analysis
Identity Agent
Possible techniques:

Authentication pattern analysis
2FA verification
Biometric verification
Device trust
Time/location analysis
Login anomaly detection
Transaction Agent
Possible techniques:

Fraud classification
Anomaly detection
Graph analysis
Transaction-network analysis
Money-flow analysis
📊 Dataset → Model → Evidence Pipeline
                    DATASET
                       │
                       ▼
                DATASET LOADER
                       │
                       ▼
              SCHEMA VALIDATION
                       │
                       ▼
                    CLEANING
                       │
                       ▼
              FEATURE ENGINEERING
                       │
                       ▼
                MODEL / DETECTOR
                       │
                       ▼
                  PREDICTION
                       │
                       ▼
                  CONFIDENCE
                       │
                       ▼
                 UNCERTAINTY
                       │
                       ▼
                  RELIABILITY
                       │
                       ▼
                SECURITY EVIDENCE
                       │
                       ▼
                EVIDENCE FUSION
🗃️ Dataset Strategy
Large raw datasets should not be committed directly to the public repository.

Example datasets may include:

data/raw/network/bot_iot/
backend/data/raw/network/
The dataset strategy separates:

Raw Dataset
     ↓
Loader
     ↓
Preprocessing
     ↓
Model
     ↓
Evidence
Large datasets should remain outside the Git repository when appropriate.

🖥️ HACTM Dashboard
The dashboard provides visibility into the complete security process.

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
Dashboard information can include
Unified cyber risk
Agent status
Security events
Risk distribution
Evidence sources
Confidence
Uncertainty
Threat categories
Policy decisions
Historical events
Agent reliability
Threat intelligence
📄 Security Reporting
HACTM can generate structured security reports.

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
Reports can contain:

Executive summary
Security events
Evidence
Risk assessment
Agent contributions
Security context
Threat intelligence
Policy decisions
Enforcement actions
Recommendations
Historical evidence
🏗️ Project Structure
HACTM/
│
├── backend/
│   ├── src/
│   │   └── hactm/
│   │       ├── api/
│   │       │   ├── routers/
│   │       │   └── schemas/
│   │       │
│   │       ├── cli/
│   │       ├── core/
│   │       ├── eval/
│   │       ├── evaluation/
│   │       ├── feedback/
│   │       ├── fusion/
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
│   │       ├── phishing/
│   │       │   └── detectors/
│   │       ├── reliability/
│   │       ├── research/
│   │       │
│   │       ├── services/
│   │       │   └── threat_intelligence/
│   │       │
│   │       ├── storage/
│   │       │   └── repositories/
│   │       │
│   │       ├── temporal/
│   │       ├── transaction/
│   │       │   └── detectors/
│   │       ├── uba/
│   │       │   └── detectors/
│   │       └── zerotrust/
│   │
│   └── data/
│       └── raw/
│
├── frontend/
│   ├── src/
│   └── public/
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
├── scripts/
│
├── .env.example
├── .gitignore
└── README.md
⚙️ Technology Stack
Area	Technology
Backend	Python
API	FastAPI
Database	SQLite
ORM	SQLAlchemy
Frontend	React
Language	TypeScript
Build Tool	Vite
Styling	Tailwind CSS
Visualization	Chart.js / Recharts
ML	scikit-learn
NLP	NLP / Transformer-based approaches
Detection	Signature + Anomaly Detection
Reasoning	Temporal + Graph Analysis
Security	IDS + Phishing + UBA + Identity + Fraud
Enforcement	Zero Trust + Micro-Segmentation
🚀 Installation
Clone the Repository
git clone https://github.com/asif-visionary/HACTM.git
cd HACTM

Backend Setup
cd backend

Windows
py -m venv .venv
.venv\Scripts\activate

Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Frontend Setup
cd frontend
npm install
npm run dev

🔐 Environment Configuration
Create the environment configuration from:

.env.example
Possible configuration values include:

ABUSEIPDB_API_KEY=
ABUSEIPDB_BASE_URL=
ABUSEIPDB_API_TIMEOUT=10

NVD_API_KEY=
NVD_BASE_URL=
NVD_API_TIMEOUT=15
Security Rule
Never expose API keys or other secrets to the frontend.

Never commit:

.env
API keys
Passwords
Tokens
Private credentials
Sensitive datasets
🧪 Testing
Run the test suite:

pytest

Testing areas include:

Unit Tests
    ↓
Integration Tests
    ↓
Benchmarks
    ↓
Evaluation
📈 Evaluation
HACTM can evaluate different parts of the architecture.

Detection
Accuracy
Precision
Recall
F1
False-positive rate
False-negative rate
Reliability
Historical performance
Availability
Agent reliability
Latency
Uncertainty
ECE
Brier Score
Calibration Error
Empirical Coverage
AUSE
Enforcement
Containment time
Blast radius
Reachable assets
Segmentation violations
System Behavior
Agent selection
Evidence fusion
Risk decisions
Policy effectiveness
Feedback behavior
🗺️ Development Roadmap
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
🔬 Research Positioning
HACTM's research positioning focuses on:

Reliability- and uncertainty-aware adaptive evidence orchestration.

The architecture does not claim novelty for every individual security technology.

Instead, the research focus is on how multiple security signals can be:

Collected
   ↓
Normalized
   ↓
Analyzed
   ↓
Fused
   ↓
Evaluated for Reliability
   ↓
Evaluated for Uncertainty
   ↓
Remembered
   ↓
Reasoned Across Time and Relationships
   ↓
Adaptively Orchestrated
   ↓
Converted into Risk
   ↓
Converted into Security Action
   ↓
Verified Through Feedback
🔐 Security & Privacy
HACTM should follow secure development practices.

Never commit
.env files
API keys
Passwords
Authentication tokens
Private credentials
Sensitive datasets
Proprietary information
Large or sensitive datasets should remain outside the public repository when required.

🎯 HACTM in Simple Words
If someone is completely new to HACTM, the entire architecture can be understood as:

                         WHAT IS HAPPENING?
                                │
                                ▼
                         COLLECT DATA
                                │
                                ▼
                      UNDERSTAND EACH SIGNAL
                                │
                                ▼
                       COMBINE THE EVIDENCE
                                │
                                ▼
                      CHECK PAST ACTIVITY
                                │
                                ▼
                    CHECK TRUST + UNCERTAINTY
                                │
                                ▼
                     UNDERSTAND RELATIONSHIPS
                                │
                                ▼
                         CALCULATE RISK
                                │
                                ▼
                       CHOOSE AN ACTION
                                │
                                ▼
                       PROTECT THE SYSTEM
                                │
                                ▼
                        OBSERVE THE RESULT
                                │
                                ▼
                         LEARN FROM IT
                                │
                                └──────────────↺
In one sentence:
HACTM connects security signals from different domains, understands their context and history, combines them into trustworthy evidence, calculates cyber risk, takes an adaptive security action, and continuously reassesses the environment using feedback.

🛡️ Final HACTM Model
                  ┌─────────────────────────────────┐
                  │       MULTI-DOMAIN WORLD        │
                  │                                 │
                  │ Network • Email • Identity      │
                  │ UBA • Transactions • AI • TI   │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │     INGESTION & PREPROCESSING   │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │       SPECIALIZED AGENTS        │
                  │                                 │
                  │ Network | Phishing | UBA        │
                  │ Identity | Transaction | AI/TI │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │       SECURITY EVIDENCE         │
                  │          + LOCAL FUSION          │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │         EVIDENCE MEMORY         │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │     RELIABILITY + UNCERTAINTY   │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │      REGIONAL ORCHESTRATION     │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │    GLOBAL ADAPTIVE ORCHESTRATOR │
                  │                                 │
                  │ Context • Time • Graph • Risk  │
                  │ Agent Selection • History      │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │         CYBER RISK              │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │       ADAPTIVE POLICY           │
                  │                                 │
                  │ ALLOW | MONITOR | VERIFY       │
                  │ QUARANTINE | BLOCK             │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │      MICRO-SEGMENTATION         │
                  │                                 │
                  │ Firewall | SDN | Cloud | K8s   │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │       TELEMETRY & FEEDBACK      │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │          NEW EVIDENCE            │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │          REASSESSMENT            │
                  └────────────────┬────────────────┘
                                   │
                                   └────────────────↺
👨‍💻 Author
Mohamed Asif

GitHub:
https://github.com/asif-visionary

📜 License
Add the project license selected for the repository.