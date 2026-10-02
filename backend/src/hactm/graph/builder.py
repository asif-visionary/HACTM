"""
GraphBuilder constructs and manages the Attack Evidence Graph.
"""

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session

from hactm.graph.models import (
    NodeType,
    EdgeType,
    GraphNode,
    GraphEdge,
    Subgraph,
)
from hactm.graph.repository import GraphRepository


class GraphBuilder:
    """Constructs graph nodes and edges from Security Evidence with strict entity deduplication."""

    def __init__(self, session: Session):
        self.session = session
        self.repo = GraphRepository(session)

    def create_nodes(self, evidence: Dict[str, Any]) -> List[GraphNode]:
        """Extracts and constructs canonical entity and evidence nodes."""
        nodes = []
        now = datetime.now(timezone.utc)
        ev_id = evidence.get("event_id") or evidence.get("evidence_id") or f"ev_{uuid.uuid4().hex[:8]}"

        # 1. Evidence Node
        ev_node = GraphNode(
            node_id=f"node_ev_{ev_id}",
            node_type=NodeType.EVIDENCE,
            canonical_id=ev_id,
            display_name=f"Evidence {ev_id[:10]}",
            attributes={
                "domain": evidence.get("domain", "unknown"),
                "risk_score": evidence.get("risk_score", 0.0),
                "confidence": evidence.get("confidence", 1.0),
                "event_type": evidence.get("event_type", "unknown"),
            },
            first_seen=now,
            last_seen=now,
        )
        nodes.append(ev_node)
        self.repo.upsert_node(ev_node)

        # 2. Primary Entity Node
        entity_id = evidence.get("entity_id")
        if entity_id:
            ent_type = NodeType.USER
            if "acc" in entity_id.lower():
                ent_type = NodeType.ACCOUNT
            elif "dev" in entity_id.lower():
                ent_type = NodeType.DEVICE
            elif "ip" in entity_id.lower():
                ent_type = NodeType.IP

            ent_node = GraphNode(
                node_id=f"node_{ent_type.value.lower()}_{entity_id}",
                node_type=ent_type,
                canonical_id=entity_id,
                display_name=f"{ent_type.value}: {entity_id}",
                attributes={"entity_id": entity_id},
                first_seen=now,
                last_seen=now,
            )
            nodes.append(ent_node)
            self.repo.upsert_node(ent_node)

        # 3. Additional attributes/telemetry entities (IP, Email, Device, etc.)
        ev_data = evidence.get("evidence", {}) or {}
        ip_val = ev_data.get("ip_address") or ev_data.get("src_ip") or ev_data.get("source_ip")
        if ip_val:
            ip_node = GraphNode(
                node_id=f"node_ip_{ip_val}",
                node_type=NodeType.IP,
                canonical_id=str(ip_val),
                display_name=f"IP: {ip_val}",
                attributes={"ip": ip_val},
                first_seen=now,
                last_seen=now,
            )
            nodes.append(ip_node)
            self.repo.upsert_node(ip_node)

        email_val = ev_data.get("email") or ev_data.get("sender") or ev_data.get("recipient")
        if email_val:
            email_node = GraphNode(
                node_id=f"node_email_{email_val}",
                node_type=NodeType.EMAIL,
                canonical_id=str(email_val),
                display_name=f"Email: {email_val}",
                attributes={"email": email_val},
                first_seen=now,
                last_seen=now,
            )
            nodes.append(email_node)
            self.repo.upsert_node(email_node)

        return nodes

    def create_edges(self, evidence: Dict[str, Any], nodes: List[GraphNode]) -> List[GraphEdge]:
        """Constructs relationships linking evidence node to entity nodes."""
        edges = []
        ev_node = next((n for n in nodes if n.node_type == NodeType.EVIDENCE), None)
        if not ev_node:
            return []

        ev_id = evidence.get("event_id") or evidence.get("evidence_id") or "ev"
        now = datetime.now(timezone.utc)

        for target in nodes:
            if target.node_id == ev_node.node_id:
                continue

            edge_type = EdgeType.OBSERVED_BY
            if target.node_type in (NodeType.USER, NodeType.ACCOUNT):
                edge_type = EdgeType.INVOLVED_IN
            elif target.node_type == NodeType.IP:
                edge_type = EdgeType.AUTHENTICATED_FROM
            elif target.node_type == NodeType.DEVICE:
                edge_type = EdgeType.EXECUTED_ON

            # Deterministic Edge ID for deduplication
            edge_id = f"edge_{ev_node.node_id}_to_{target.node_id}_{edge_type.value}"

            edge = GraphEdge(
                edge_id=edge_id,
                source_node_id=ev_node.node_id,
                target_node_id=target.node_id,
                edge_type=edge_type,
                confidence=evidence.get("confidence", 1.0),
                weight=1.0,
                first_seen=now,
                last_seen=now,
                evidence_count=1,
                evidence_ids=[ev_id],
            )
            edges.append(edge)
            self.repo.upsert_edge(edge)

        return edges

    def add_evidence(self, evidence: Dict[str, Any]) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """Processes single security evidence entry and updates graph structure."""
        nodes = self.create_nodes(evidence)
        edges = self.create_edges(evidence, nodes)
        return nodes, edges

    def get_subgraph(self, node_id: str, k_hop: int = 2, max_nodes: int = 200) -> Subgraph:
        return self.repo.get_subgraph(center_node_id=node_id, k_hop=k_hop, max_nodes=max_nodes)

    def get_entity_neighbors(self, entity_id: str, k_hop: int = 2) -> Subgraph:
        node_id = f"node_user_{entity_id}"
        existing = self.repo.get_node(node_id)
        if not existing:
            node_id = f"node_account_{entity_id}"
        return self.get_subgraph(node_id=node_id, k_hop=k_hop)

    def get_temporal_subgraph(self, entity_id: str, time_window_seconds: float = 86400.0) -> Subgraph:
        return self.get_entity_neighbors(entity_id=entity_id, k_hop=2)

    def remove_expired_edges(self, max_age_days: int = 30) -> int:
        """Removes edges older than retention period."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        deleted = self.session.query(GraphEdgeModel).filter(GraphEdgeModel.last_seen < cutoff).delete()
        self.session.commit()
        return deleted
