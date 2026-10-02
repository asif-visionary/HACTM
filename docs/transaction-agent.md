# HACTM Transaction Security Agent Documentation

**Agent ID:** `transaction-security-agent`  
**Phase:** Specialized Security Agents Multi-Domain Specialized Security Agents  
**Category:** Financial & Transaction Fraud Telemetry  

---

## 1. Overview
The Transaction Security Agent evaluates transaction stream telemetry to identify unusual payment amounts, high transaction velocity, recipient novelty, and payment channel anomalies.

### Safety Invariants
- **Detection Only:** The agent operates strictly as an offline evidence generator. It does NOT transfer funds, modify account balances, freeze consumer accounts, or interface with payment gateways.
- **Privacy Enforcement:** Payment card numbers, CVVs, PINs, and banking credentials are strictly excluded from event models.

---

## 2. Detection Logic
1. **Transaction Velocity Detector:** Detects sudden bursts of transactions within a short time window (e.g. 25 transactions within 2 minutes) yielding `transaction_velocity_anomaly`.
2. **Amount Anomaly Detector:** Calculates robust z-score metrics based on historical median and Median Absolute Deviation (MAD) for account transaction amounts.
3. **Recipient Novelty Detector:** Identifies first-time transfer recipients combined with elevated amount or off-hours timing indicators.
