# HACTM Identity & Authentication Agent Documentation

**Agent ID:** `identity-authentication-agent`  
**Phase:** Specialized Security Agents Multi-Domain Specialized Security Agents  
**Category:** Authentication & Credential Security Telemetry  

---

## 1. Overview
The Identity & Authentication Agent processes login events, 2FA/MFA outcomes, device association shifts, session anomalies, and credential abuse indicators to detect account takeover risk.

### Strict Security & Privacy Invariants
- **No Secret Storage:** NEVER records passwords, session tokens, OTP values, API keys, or raw biometrics.
- **Biometric Outcomes Only:** Stores boolean status flags (`biometric_verified`, `biometric_failed`, `biometric_not_available`) without raw facial or fingerprint data.
- **Geographic Heuristics:** Computes Haversine velocity for impossible-travel anomalies ONLY when explicit geographic coordinates are provided. No unsafe IP-to-location guessing.

---

## 2. Detection Logic
1. **Credential Abuse Detector:** Identifies brute-force velocity spikes and failure-to-success transition patterns.
2. **Account Takeover Detector:** Correlates novel IP/device occurrences with login failures and password reset events.
3. **MFA Anomaly Detector:** Flags repeated 2FA prompt rejections, 2FA bypass indicators, or unexpected MFA failure sequences.
4. **Impossible Travel Detector:** Measures physical travel velocity ($km/h$) between consecutive logins from distinct geographic locations. Velocity exceeding $800\,km/h$ flags `possible_impossible_travel`.
