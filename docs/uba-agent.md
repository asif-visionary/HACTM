# HACTM User Behavior Analytics (UBA) Agent Documentation

**Agent ID:** `uba-agent`  
**Phase:** Specialized Security Agents Multi-Domain Specialized Security Agents  
**Category:** User Activity Baseline & Behavioral Anomaly Detection  

---

## 1. Overview
The User Behavior Analytics (UBA) Agent tracks user actions, session patterns, file resource accesses, privilege usage, and network data transfer volumes to detect insider threat indicators and risk-elevated activities.

### Key Architectural Safeguards
- **Non-Judgmental Terminology:** Uses terms like "behavioral anomaly", "insider-threat indicator", and "risk-elevated activity" rather than assigning definitive malicious intent to human users.
- **`INSUFFICIENT_BASELINE` State:** New users or users with fewer than `min_historical_events` (default: 5) receive `INSUFFICIENT_BASELINE` status with zero false-positive risk inflation.
- **Bounded Storage:** Profile baselines maintain running statistics (mean/stddev for login hours, rare resource sets, rare app frequency) with configurable event count caps.

---

## 2. Detection Modules
1. **Temporal Anomaly Detector:** Identifies off-hours activity deviations relative to user-specific normal login hours and day-of-week baselines.
2. **Resource Access Anomaly Detector:** Flags accesses to rare or previously unseen high-sensitivity files, administrative tools, or peer-group resources.
3. **Data Exfiltration Detector:** Monitors anomalous data transfer volumes (robust z-score on bytes transferred) and high file movement rates.
4. **Statistical Anomaly Detector:** Employs Median Absolute Deviation (MAD) / Isolation Forest logic over multi-dimensional activity features.

---

## 3. Profile Management & Peer Baseline
- **User Profile Baseline:** Stores established normal login hours, source IPs, device IDs, application usage frequencies, and data transfer metrics per user.
- **Peer Group Baseline:** Compares individual access habits against organizational department or role peers when peer-group metadata is supplied.
