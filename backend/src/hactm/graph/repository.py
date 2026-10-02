"""
Repository for Attack Evidence Graph database operations.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func, or_

from hactm.storage.models import (
    GraphNodeModel,
    GraphEdgeModel,
    GraphEdgeEvidenceModel,
    AttackChainCandidateModel,
    AttackChainStageModel,
)
from hactm.graph.models import (
    GraphNode,
    GraphEdge,
    NodeType,
    EdgeType,
    Subgraph,
    AttackChainCandidate,
    AttackChainStage,
)


class GraphRepository:
    """Relational persistence layer for Attack Evidence Graph nodes and edges."""

    def __init__(self, session: Session):
        self.session = session

    def upsert_node(self, node: GraphNode) -> GraphNodeModel:
        existing = self.session.query(GraphNodeModel).filter_by(node_id=node.node_id).first()
        if existing:
            existing.last_seen = node.last_seen
            existing.attributes = node.attributes
            existing.updated_at = datetime.now(timezone.utc)
            model_obj = existing
        else:
            model_obj = GraphNodeModel(
                node_id=node.node_id,
                node_type=node.node_type.value if isinstance(node.node_type, NodeType) else str(node.node_type),
                canonical_id=node.canonical_id,
                display_name=node.display_name,
                attributes=node.attributes,
                first_seen=node.first_seen,
                last_seen=node.last_seen,
                created_at=node.created_at,
                updated_at=node.updated_at,
            )
            self.session.add(model_obj)
        self.session.commit()
        return model_obj

    def upsert_edge(self, edge: GraphEdge) -> GraphEdgeModel:
        existing = self.session.query(GraphEdgeModel).filter_by(edge_id=edge.edge_id).first()
        if existing:
            existing.last_seen = edge.last_seen
            existing.evidence_count += 1
            existing.confidence = edge.confidence
            model_obj = existing
        else:
            model_obj = GraphEdgeModel(
                edge_id=edge.edge_id,
                source_node_id=edge.source_node_id,
                target_node_id=edge.target_node_id,
                edge_type=edge.edge_type.value if isinstance(edge.edge_type, EdgeType) else str(edge.edge_type),
                confidence=edge.confidence,
                weight=edge.weight,
                first_seen=edge.first_seen,
                last_seen=edge.last_seen,
                evidence_count=edge.evidence_count,
                created_at=edge.created_at,
            )
            self.session.add(model_obj)

        self.session.commit()

        # Save evidence provenance links
        for ev_id in edge.evidence_ids:
            ev_link = GraphEdgeEvidenceModel(
                edge_id=edge.edge_id,
                evidence_id=ev_id,
                confidence=edge.confidence,
                timestamp=datetime.now(timezone.utc),
            )
            self.session.add(ev_link)
        self.session.commit()
        return model_obj

    def get_node(self, node_id: str) -> Optional[GraphNodeModel]:
        return self.session.query(GraphNodeModel).filter_by(node_id=node_id).first()

    def get_edge(self, edge_id: str) -> Optional[GraphEdgeModel]:
        return self.session.query(GraphEdgeModel).filter_by(edge_id=edge_id).first()

    def get_subgraph(
        self,
        center_node_id: str,
        k_hop: int = 2,
        max_nodes: int = 200,
        max_edges: int = 500,
    ) -> Subgraph:
        """Traverses graph up to k-hop distance with cycle prevention and node/edge caps."""
        k_hop = min(max(1, k_hop), 4)  # Clamp k-hop between 1 and 4

        visited_nodes: Set[str] = {center_node_id}
        current_frontier: Set[str] = {center_node_id}
        collected_edges: List[GraphEdgeModel] = []

        for _ in range(k_hop):
            if not current_frontier or len(visited_nodes) >= max_nodes:
                break
            next_frontier: Set[str] = set()
            edges = self.session.query(GraphEdgeModel).filter(
                or_(
                    GraphEdgeModel.source_node_id.in_(list(current_frontier)),
                    GraphEdgeModel.target_node_id.in_(list(current_frontier)),
                )
            ).limit(max_edges).all()

            for edge in edges:
                if edge not in collected_edges:
                    collected_edges.append(edge)
                neighbor = edge.target_node_id if edge.source_node_id in current_frontier else edge.source_node_id
                if neighbor not in visited_nodes:
                    visited_nodes.add(neighbor)
                    next_frontier.add(neighbor)
                    if len(visited_nodes) >= max_nodes:
                        break
            current_frontier = next_frontier

        # Fetch Node objects
        nodes_models = self.session.query(GraphNodeModel).filter(GraphNodeModel.node_id.in_(list(visited_nodes))).all()

        node_objs = [
            GraphNode(
                node_id=m.node_id,
                node_type=NodeType(m.node_type) if m.node_type in [e.value for e in NodeType] else NodeType.EVIDENCE,
                canonical_id=m.canonical_id,
                display_name=m.display_name,
                attributes=m.attributes or {},
                first_seen=m.first_seen,
                last_seen=m.last_seen,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in nodes_models
        ]

        edge_objs = [
            GraphEdge(
                edge_id=m.edge_id,
                source_node_id=m.source_node_id,
                target_node_id=m.target_node_id,
                edge_type=EdgeType(m.edge_type) if m.edge_type in [e.value for e in EdgeType] else EdgeType.ASSOCIATED_WITH,
                confidence=m.confidence,
                weight=m.weight,
                first_seen=m.first_seen,
                last_seen=m.last_seen,
                evidence_count=m.evidence_count,
            )
            for m in collected_edges
        ]

        truncated = len(visited_nodes) >= max_nodes or len(collected_edges) >= max_edges

        return Subgraph(
            center_node_id=center_node_id,
            k_hop=k_hop,
            nodes=node_objs,
            edges=edge_objs,
            total_nodes=len(node_objs),
            total_edges=len(edge_objs),
            truncated=truncated,
        )

    def store_attack_chain(self, chain: AttackChainCandidate) -> AttackChainCandidateModel:
        existing = self.session.query(AttackChainCandidateModel).filter_by(chain_id=chain.chain_id).first()
        if not existing:
            chain_obj = AttackChainCandidateModel(
                chain_id=chain.chain_id,
                pattern_id=chain.pattern_id,
                primary_entity_id=chain.primary_entity_id,
                stage_count=chain.stage_count,
                matched_stage_count=chain.matched_stage_count,
                completeness=chain.completeness,
                confidence=chain.confidence,
                start_time=chain.start_time,
                end_time=chain.end_time,
                status=chain.status,
                explanation=chain.explanation,
                pattern_version=chain.pattern_version,
                created_at=chain.created_at,
            )
            self.session.add(chain_obj)

            for stg in chain.stages:
                stg_obj = AttackChainStageModel(
                    chain_id=chain.chain_id,
                    stage_index=stg.stage_index,
                    evidence_id=stg.evidence_id,
                    domain=stg.domain,
                    event_type=stg.event_type,
                    timestamp=stg.timestamp,
                    entity_id=stg.entity_id,
                    stage_confidence=stg.stage_confidence,
                )
                self.session.add(stg_obj)

            self.session.commit()
            return chain_obj
        return existing
