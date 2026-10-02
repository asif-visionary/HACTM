# Attack Evidence Graph Schema & Traversal (HACTM Adaptive Memory & Graph)

## Overview
The Attack Evidence Graph models observed relationships between entities (Users, Accounts, Devices, IPs, Emails) and Security Evidence.

## Graph Schema
- **Nodes**: `Evidence`, `User`, `Account`, `Device`, `IP`, `Email`, `Domain`, `URL`, `Transaction`, `Application`, `Server`, `Session`.
- **Edges**: `OBSERVED_BY`, `ASSOCIATED_WITH`, `SENT_TO`, `AUTHENTICATED_FROM`, `EXECUTED_ON`, `INVOLVED_IN`, `OCCURRED_BEFORE`, `OCCURRED_AFTER`, `SHARES_ENTITY`, `SHARES_SESSION`, `SHARES_ACCOUNT`, `SHARES_DEVICE`, `TEMPORALLY_RELATED`, `SUPPORTS`, `CONFLICTS_WITH`.

## Query Safety & Bounded Traversal
- Default traversal depth $k = 2$, maximum allowed $k = 4$.
- Cycle tracking prevents infinite loops on cyclic entity graphs (User $\rightarrow$ Device $\rightarrow$ IP $\rightarrow$ User).
- Max node limits (default 200) prevent RAM exhaustion during entity-centered subgraph queries.
- Relational tables (`graph_nodes`, `graph_edges`, `graph_edge_evidence`) provide initial persistence.
