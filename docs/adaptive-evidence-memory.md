# Adaptive Evidence Memory Architecture (HACTM Adaptive Memory & Graph)

## Overview
Adaptive Evidence Memory provides HACTM with persistent, bounded, temporally aware security context. Rather than indefinitely retaining raw events or operating in a session-local memoryless fashion, Adaptive Memory & Graph implements a tiered, importance-aware memory lifecycle.

```
CURRENT SECURITY EVIDENCE
          │
          ▼
   EVIDENCE INGESTION
          │
          ▼
   MEMORY CLASSIFICATION
          │
    ┌─────┼─────┐
    ▼     ▼     ▼
   HOT   WARM   COLD
 MEMORY MEMORY MEMORY
    │     │     │
    └─────┼─────┘
          ▼
 ADAPTIVE MEMORY RETRIEVAL
```

## Memory Tiers
1. **HOT MEMORY**: Recent high-value evidence ($\le 15$ minutes, max 10,000 entries).
2. **WARM MEMORY**: Retained historical security evidence ($\le 24$ hours, max 100,000 entries).
3. **COLD MEMORY**: Archived evidence references (30-day retention).

## Importance Scoring Algorithm
Memory entries are assigned a transparent importance score $S_{\text{imp}} \in [0.0, 1.0]$:

$$S_{\text{imp}} = \frac{w_{\text{risk}} \cdot R + w_{\text{confidence}} \cdot C + w_{\text{severity}} \cdot S + w_{\text{recency}} \cdot T + w_{\text{relevance}} \cdot L}{w_{\text{risk}} + w_{\text{confidence}} + w_{\text{severity}} + w_{\text{recency}} + w_{\text{relevance}}}$$

Default weights:
- $w_{\text{risk}} = 0.35$
- $w_{\text{confidence}} = 0.25$
- $w_{\text{severity}} = 0.20$
- $w_{\text{recency}} = 0.10$
- $w_{\text{relevance}} = 0.10$

## Auditing and Privacy Controls
- **Transitions**: Auditable logging of `HOT -> WARM`, `WARM -> HOT` promotions, and `WARM -> COLD` demotions.
- **Privacy Controls**: Mandatory redacting of sensitive credential fields (`password`, `otp`, `auth_token`, `raw_biometrics`, `card_number`).
- **Redundancy**: Deduplicated logical storage using evidence fingerprinting.
