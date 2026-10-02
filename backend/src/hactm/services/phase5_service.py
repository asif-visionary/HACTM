"""
Adaptive Memory & Graph Orchestrator Service.
Coordinates Adaptive Evidence Memory, Temporal Engine, Attack Evidence Graph, and Evidence Fusion Fusion context enrichment.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from hactm.memory.engine import AdaptiveEvidenceMemory
from hactm.memory.models import MemoryRetrievalQuery, MemoryTier
from hactm.temporal.engine import TemporalEvidenceEngine
from hactm.graph.builder import GraphBuilder
from hactm.graph.pattern_matcher import GraphPatternMatcher
from hactm.graph.models import AttackChainCandidate, Subgraph
from hactm.storage.models import TemporalFusionContextModel


class AdaptiveMemoryService:
    """Integrated Adaptive Memory & Graph service for bounded historical memory, temporal reasoning, and graph context."""

    def __init__(self, session: Session, config_dir: str = "configs"):
        self.session = session
        self.memory = AdaptiveEvidenceMemory(
            session=session,
            config_path=f"{config_dir}/evidence_memory.yaml",
        )
        self.temporal_engine = TemporalEvidenceEngine(session=session)
        self.graph_builder = GraphBuilder(session=session)
        self.pattern_matcher = GraphPatternMatcher(
            session=session,
            patterns_path=f"{config_dir}/attack_patterns.yaml",
        )

    def process_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests evidence into memory, updates graph, detects temporal sequences & attack chains."""
        ev_id = evidence.get("event_id") or evidence.get("evidence_id") or f"ev_{uuid.uuid4().hex[:8]}"
        ent_id = evidence.get("entity_id", "unknown_entity")
        domain = evidence.get("domain", "network")
        event_type = evidence.get("event_type", "anomaly")
        risk_score = float(evidence.get("risk_score", 0.5))
        confidence = float(evidence.get("confidence", 1.0))
        uncertainty = float(evidence.get("uncertainty", 0.0))
        severity = evidence.get("severity", "LOW")

        ts = evidence.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if ts is None:
            ts = datetime.now(timezone.utc)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        # 1. Store in Adaptive Evidence Memory
        mem_entry = self.memory.store(
            evidence_id=ev_id,
            entity_ids=[ent_id],
            event_type=event_type,
            domain=domain,
            timestamp=ts,
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=severity,
            source_dataset=evidence.get("dataset"),
            agent_id=evidence.get("agent_id"),
            detector_id=evidence.get("detector_id"),
            metadata=evidence.get("evidence"),
        )

        # 2. Update Attack Evidence Graph
        nodes, edges = self.graph_builder.add_evidence(evidence)

        # 3. Retrieve Historical Context for Entity
        hist_entries = self.memory.get_history(entity_id=ent_id)

        # Convert memory entries to dicts for temporal & pattern matching
        hist_events = []
        for h in hist_entries:
            hist_events.append({
                "event_id": h.evidence_id,
                "entity_id": ent_id,
                "domain": h.domain,
                "event_type": h.event_type,
                "timestamp": h.timestamp,
                "risk_score": h.risk_score,
                "confidence": h.confidence,
                "session_id": h.metadata.get("session_id"),
            })

        # 4. Temporal Analysis
        seq_matches = self.temporal_engine.detect_sequences(hist_events)

        # 5. Attack Chain Pattern Matching
        candidates = self.pattern_matcher.evaluate_evidence_sequence(
            events=hist_events,
            primary_entity_id=ent_id,
        )

        # 6. Construct Bounded TemporalFusionContext for Evidence Fusion
        ctx_id = f"ctx_{uuid.uuid4().hex[:12]}"
        hist_ids = [h.evidence_id for h in hist_entries if h.evidence_id != ev_id]
        graph_node_ids = [n.node_id for n in nodes]
        graph_edge_ids = [e.edge_id for e in edges]
        cand_dicts = [c.dict() for c in candidates]

        coverage = min(1.0, len(hist_entries) / 10.0)
        completeness = max((c.completeness for c in candidates), default=1.0)

        ctx_model = TemporalFusionContextModel(
            context_id=ctx_id,
            current_evidence_id=ev_id,
            historical_evidence_ids=hist_ids,
            graph_node_ids=graph_node_ids,
            graph_edge_ids=graph_edge_ids,
            temporal_relationships=[s.dict() for s in seq_matches],
            attack_chain_candidates=cand_dicts,
            memory_coverage=coverage,
            context_completeness=completeness,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(ctx_model)
        self.session.commit()

        return {
            "memory_id": mem_entry.memory_id,
            "memory_tier": mem_entry.memory_tier.value,
            "importance_score": mem_entry.importance_score,
            "historical_event_count": len(hist_entries),
            "graph_nodes_count": len(nodes),
            "graph_edges_count": len(edges),
            "attack_chain_candidates": cand_dicts,
            "context_id": ctx_id,
            "context_completeness": completeness,
        }

    def get_entity_context(self, entity_id: str) -> Dict[str, Any]:
        """Fetches unified historical memory, graph subgraph, and candidate attack chains for an entity."""
        mem_ctx = self.memory.get_context(entity_id=entity_id, max_events=20)
        subgraph = self.graph_builder.get_entity_neighbors(entity_id=entity_id, k_hop=2)

        hist_entries = self.memory.get_history(entity_id=entity_id)
        hist_events = [
            {
                "event_id": h.evidence_id,
                "entity_id": entity_id,
                "domain": h.domain,
                "event_type": h.event_type,
                "timestamp": h.timestamp,
                "risk_score": h.risk_score,
                "confidence": h.confidence,
            }
            for h in hist_entries
        ]
        candidates = self.pattern_matcher.evaluate_evidence_sequence(
            events=hist_events,
            primary_entity_id=entity_id,
        )

        return {
            "entity_id": entity_id,
            "memory": mem_ctx,
            "subgraph": subgraph.dict(),
            "attack_chain_candidates": [c.dict() for c in candidates],
        }
