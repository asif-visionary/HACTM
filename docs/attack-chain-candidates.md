# Attack-Chain Candidate Detection (HACTM Adaptive Memory & Graph)

## Overview
Adaptive Memory & Graph detects multi-stage attack-chain candidates across correlated temporal domain evidence using declarative pattern specifications (`configs/attack_patterns.yaml`).

## Declarative Pattern Specification
Example pattern:
```yaml
pattern_id: PHISH_AUTH_TRANSACTION
sequence:
  - phishing
  - identity
  - transaction
max_gap_seconds: 3600
required_relationship: same_user_or_account
minimum_domains: 2
```

## Candidate Completeness & Explanation
- **Completeness**: Ratio of matched sequence stages observed ($\text{Completeness} \in [0.0, 1.0]$).
- **Status**: `CANDIDATE` if completeness = 100%, `PARTIAL` if intermediate stages observed.
- **False Correlation Prevention**: Prevents linking events belonging to unrelated entities or events connected solely via shared corporate NAT/VPN egress IPs.
