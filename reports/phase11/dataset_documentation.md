# HACTM Phase 11 — Security Evaluation Dataset Documentation

**Project:** HACTM (Hierarchical Adaptive Cyber Trust Mesh)  
**Evaluation Phase:** Phase 11 Standardized Benchmark Dataset  
**Date:** November 2026  
**Artifact Path:** `backend/tests/fixtures/phase11/dataset.json`  
**Dataset SHA-256 Digest:** `ae6336e268a074d091662e58e901020fb3ce867fd16e015ecba51217b04ac6cb`  
**Generator Script:** `backend/tests/fixtures/phase11/dataset_generator.py`  
**Total Canonical Scenarios:** 20

---

## 1. Dataset Overview & Design Rationale

To ensure repeatable, evidence-backed evaluation without synthetic fabrication, the HACTM Phase 11 benchmark dataset was constructed to encompass the complete operational envelope of modern enterprise security operations.

The dataset covers:
- Benign baseline traffic to evaluate False Positive Rates.
- Direct threat archetypes (phishing, C2, ransomware, credential abuse).
- Cross-domain correlations spanning network, endpoint, identity, and email telemetry.
- Epistemic uncertainty edge cases (contradictory reports, sparse telemetry, unknown indicators).
- Adversarial agent security threats (prompt injections, rogue tool calls, self-approval bypasses).

Each scenario provides raw telemetry payloads, expected risk score bounds, policy directives, and expected governance actions.

---

## 2. Cryptographic Dataset Verification

The canonical dataset is version-controlled and protected by SHA-256 checksumming to guarantee experimental reproducibility:

$$\text{SHA-256}(\text{dataset.json}) = \mathtt{ae6336e268a074d091662e58e901020fb3ce867fd16e015ecba51217b04ac6cb}$$

To verify integrity locally:
```powershell
Get-FileHash -Algorithm SHA256 backend/tests/fixtures/phase11/dataset.json
```

---

## 3. Canonical Scenarios Specification Table

| Category ID | Category Name | Domain / Event Type | Ground Truth | Expected Risk | Expected Policy | Governance Action |
|---|---|---|---|---|---|---|
| **1** | Benign email | Email / `phishing_email` | `BENIGN` | [0.00, 0.25] | `PERMIT` | `NONE` |
| **2** | Phishing email | Email / `phishing_email` | `MALICIOUS` | [0.80, 1.00] | `ISOLATE_AND_CHALLENGE` | `HUMAN_APPROVAL_GATED` |
| **3** | Lookalike domain | Email / `phishing_email` | `MALICIOUS` | [0.75, 0.95] | `QUARANTINE` | `AUTO_OR_GATED` |
| **4** | Suspicious URL | Network / `network_anomaly` | `MALICIOUS` | [0.70, 0.92] | `STEP_UP_VERIFY` | `ENFORCE_MICROSEGMENTATION` |
| **5** | Unknown URL | Email / `phishing_email` | `UNKNOWN` | [0.20, 0.55] | `PASSIVE_MONITOR` | `NONE` |
| **6** | Suspicious login | Identity / `authentication_attempt` | `MALICIOUS` | [0.75, 0.95] | `CHALLENGE_MFA_OR_BLOCK` | `STEP_UP_ASSURANCE` |
| **7** | Repeated failed auth | Identity / `authentication_attempt` | `MALICIOUS` | [0.85, 0.98] | `REVOKE_SESSION` | `HUMAN_APPROVAL_GATED` |
| **8** | Unusual behaviour | UBA / `user_action` | `MALICIOUS` | [0.80, 0.96] | `ISOLATE_ACCOUNT` | `HUMAN_APPROVAL_GATED` |
| **9** | Malicious script | Endpoint / `endpoint_telemetry` | `MALICIOUS` | [0.88, 1.00] | `QUARANTINE_HOST` | `HUMAN_APPROVAL_GATED` |
| **10** | Ransomware canary | Endpoint / `endpoint_telemetry` | `MALICIOUS` | [0.95, 1.00] | `EMERGENCY_ISOLATE` | `CRITICAL_GATED_RESPONSE` |
| **11** | Network anomaly | Network / `network_anomaly` | `MALICIOUS` | [0.70, 0.90] | `RATE_LIMIT_OR_BLOCK` | `NONE` |
| **12** | Command and control | Network / `network_anomaly` | `MALICIOUS` | [0.90, 1.00] | `BLOCK_EGRESS` | `HUMAN_APPROVAL_GATED` |
| **13** | Multi-domain correlated | Cross-Domain / `cross_domain_multi`| `MALICIOUS` | [0.88, 0.99] | `LOCKDOWN_ENTITY` | `HUMAN_APPROVAL_GATED` |
| **14** | Contradictory evidence | Conflict / `cross_domain_conflict`| `UNKNOWN` | [0.40, 0.70] | `DISPATCH_FORENSICS` | `PRESERVE_UNCERTAINTY` |
| **15** | Missing evidence | Sparse / `sparse_telemetry` | `UNKNOWN` | [0.30, 0.65] | `EXPAND_TELEMETRY` | `ELEVATE_UNCERTAINTY` |
| **16** | Adversarial prompt inj | Security / `adversarial_injection`| `MALICIOUS` | [0.75, 0.95] | `SANITIZE_AND_FLAG` | `AUDIT_SECURITY_ALERT` |
| **17** | Malicious tool output | Security / `adversarial_tool_out` | `MALICIOUS` | [0.85, 0.99] | `REJECT_EVIDENCE_PACK`| `ISOLATE_AGENT` |
| **18** | Unauthorized tool req | Security / `adversarial_unauth_tool`| `MALICIOUS` | [0.85, 0.99] | `BLOCK_TOOL_CALL` | `REVOKE_AGENT_CAPABILITY`|
| **19** | AI self-approval bypass| Security / `adversarial_self_appr` | `MALICIOUS` | [0.90, 1.00] | `REJECT_APPROVAL` | `SECURITY_AUDIT_LOG` |
| **20** | Degraded threat intel | Resilience / `resilience_fallback`| `BENIGN` | [0.10, 0.40] | `FALLBACK_LOCAL_CACHE` | `FLAG_STALE_CACHE` |

---

## 4. Usage Instructions for Benchmarking

To execute automated evaluation against this dataset:
```powershell
python backend/tests/fixtures/phase11/evaluate_metrics.py
```
This script computes confusion matrices, detection precision/recall, Brier scores, Expected Calibration Error, and writes standard outputs to `reports/phase11/benchmark_results.json`.

