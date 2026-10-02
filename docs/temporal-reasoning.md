# Temporal Evidence Reasoning & Correlation (HACTM Adaptive Memory & Graph)

## Overview
The Temporal Evidence Engine evaluates event-time relationships, sequence order, bursts, and cross-session correlations across separate user sessions.

## Key Relationships Supported
- `BEFORE`: Event A occurred prior to Event B.
- `AFTER`: Event A occurred following Event B.
- `SIMULTANEOUS`: Time delta $\Delta t < 1$ second.
- `WITHIN_WINDOW`: Delta $\Delta t \le \text{configured window}$ (default 30m).
- `BURST`: $\ge 5$ high-frequency events within 60 seconds.
- `GAP`: Significant temporal delay ($\ge 12$ hours) between related security events.
- `REPEATED`: High-frequency repetition of identical detector signatures.

## Event-Time & Late Event Handling
- All temporal ordering relies on true event timestamps (`timestamp`), never database insertion time.
- Late-arriving events produce auditable `TemporalRevision` records rather than silently mutating prior analysis.
