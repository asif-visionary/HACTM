"""
Data structures and models for the Attack Evidence Graph.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    EVIDENCE = "Evidence"
    USER = "User"
    ACCOUNT = "Account"
    DEVICE = "Device"
    IP = "IP"
    EMAIL = "Email"
    DOMAIN = "Domain"
    URL = "URL"
    TRANSACTION = "Transaction"
    APPLICATION = "Application"
    SERVER = "Server"
    SESSION = "Session"


class EdgeType(str, Enum):
    OBSERVED_BY = "OBSERVED_BY"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    SENT_TO = "SENT_TO"
    AUTHENTICATED_FROM = "AUTHENTICATED_FROM"
    EXECUTED_ON = "EXECUTED_ON"
    INVOLVED_IN = "INVOLVED_IN"
    OCCURRED_BEFORE = "OCCURRED_BEFORE"
    OCCURRED_AFTER = "OCCURRED_AFTER"
    SHARES_ENTITY = "SHARES_ENTITY"
    SHARES_SESSION = "SHARES_SESSION"
    SHARES_ACCOUNT = "SHARES_ACCOUNT"
    SHARES_DEVICE = "SHARES_DEVICE"
    TEMPORALLY_RELATED = "TEMPORALLY_RELATED"
    SUPPORTS = "SUPPORTS"
    CONFLICTS_WITH = "CONFLICTS_WITH"


class GraphNode(BaseModel):
    """Node in the Attack Evidence Graph representing entities or observed evidence."""
    node_id: str
    node_type: NodeType
    canonical_id: str
    display_name: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphEdge(BaseModel):
    """Directed edge linking graph nodes with evidence provenance."""
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: EdgeType
    confidence: float = 1.0
    weight: float = 1.0
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_count: int = 1
    evidence_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Subgraph(BaseModel):
    """Bounded subgraph returned for entity-centric queries."""
    center_node_id: str
    k_hop: int
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int
    truncated: bool = False


class AttackChainStage(BaseModel):
    stage_index: int
    evidence_id: str
    domain: str
    event_type: str
    timestamp: datetime
    entity_id: str
    stage_confidence: float = 1.0


class AttackChainCandidate(BaseModel):
    """Detected attack-chain candidate from graph and temporal sequence reasoning."""
    chain_id: str
    pattern_id: str
    primary_entity_id: str
    stages: List[AttackChainStage]
    stage_count: int
    matched_stage_count: int
    completeness: float  # [0.0, 1.0]
    confidence: float    # [0.0, 1.0]
    start_time: datetime
    end_time: datetime
    status: str = "CANDIDATE"  # PARTIAL, CANDIDATE, INVALIDATED, EXPIRED
    explanation: str
    pattern_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
