# HACTM Phishing Intelligence Agent Documentation

**Agent ID:** `phishing-intelligence-agent`  
**Phase:** Specialized Security Agents Multi-Domain Specialized Security Agents  
**Category:** Email & Messaging Threat Detection  

---

## 1. Overview
The Phishing Intelligence Agent is an offline evidence generation engine designed to analyze inbound messaging telemetry, headers, static plain/HTML text, embedded URLs, and attachment metadata.

### Architectural Principles
- **Offline & Safe:** Does NOT visit external URLs, resolve DNS dynamically, execute attachments, or trigger macro code.
- **Explainable Evidence:** Emits fine-grained `SecurityDetectionResult` and canonical `SecurityEvidence` objects with clear indicators (SPF/DKIM mismatch, urgency language, Punycode/typosquatting URLs, double extensions).
- **Extensible NLP Baseline:** Uses a deterministic TF-IDF + Logistic Regression baseline for reproducible NLP classification while remaining agnostic to future Transformer/BERT models.

---

## 2. Pipeline Architecture
```
Inbound Email Record
         │
         ▼
EmailNormalizationPipeline (Header, Body, URL, Attachment)
         │
         ▼
FeatureExtractor (Header, URL, Attachment, Text Lexicon, NLP vectorizer)
         │
         ├── HeaderAnomalyDetector (SPF/DKIM mismatch, Reply-To anomaly)
         ├── SuspiciousURLDetector (IP hostname, punycode, length, density)
         ├── AttachmentMetadataDetector (Double extensions, executable MIME)
         ├── NLPPhishingDetector (TF-IDF + Logistic Regression)
         ├── SpearPhishingDetector (Personalization & executive targeting)
         └── BECDetector (Urgent financial request + domain similarity)
         │
         ▼
PhishingRiskCalculator (Configurable weighted risk sum)
         │
         ▼
SecurityEvidenceAdapter (Deterministic SecurityEvidence output)
```

---

## 3. Risk Semantics & Calibration
- **Cyber Risk Score (0.0 – 1.0):** Quantitative measure of cyber threat risk based on weighted domain detector scores.
- **Detector Confidence (0.0 – 1.0):** Model/rule certainty regarding feature observations.
- **Baseline Uncertainty (0.0 – 1.0):** Uncalibrated baseline uncertainty estimate based on missing header fields or sparse text content.

---

## 4. Operational Boundaries & Security Limitations
1. **Metadata Only:** Attachment analysis inspects extension, MIME type, size, and optional precomputed hash. No sandboxing or dynamic binary execution is performed.
2. **Offline Analysis:** URL features rely purely on lexical structure. No live HTTP GET/HEAD requests are sent.
3. **No Cross-Agent Fusion:** Produces domain-isolated evidence for Evidence Fusion consumption.
