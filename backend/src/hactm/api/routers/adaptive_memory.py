"""
FastAPI Router for Adaptive Memory & Graph: Adaptive Memory, Attack Evidence Graph, and Temporal Correlation.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.phase5_service import AdaptiveMemoryService
from hactm.memory.models import MemoryRetrievalQuery, MemoryTier
from hactm.storage.models import (
    EvidenceMemoryModel,
    MemoryAccessLogModel,
    MemoryTransitionLogModel,
    GraphNodeModel,
    GraphEdgeModel,
    AttackChainCandidateModel,
)
from hactm.eval.adaptive_memory_eval import AdaptiveMemoryEvaluator

router = APIRouter(prefix="/api/v1", tags=["Adaptive Memory & Graph - Memory, Temporal & Graph"])


# ============================================================
# MEMORY API ENDPOINTS
# ============================================================

@router.get("/memory/health")
def get_memory_health(db: Session = Depends(get_db)):
    svc = AdaptiveMemoryService(db)
    return svc.memory.health()


@router.get("/memory/evidence")
def list_memory_evidence(
    entity_id: Optional[str] = None,
    domain: Optional[str] = None,
    tier: Optional[str] = None,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    svc = AdaptiveMemoryService(db)
    q_tier = MemoryTier(tier.upper()) if tier and tier.upper() in ["HOT", "WARM", "COLD"] else None
    query = MemoryRetrievalQuery(
        entity_id=entity_id,
        domain=domain,
        memory_tier=q_tier,
        max_results=limit,
    )
    entries = svc.memory.retrieve(query, requesting_component="api_router")
    return {"count": len(entries), "entries": [e.dict() for e in entries]}


@router.get("/memory/evidence/{memory_id}")
def get_memory_entry(memory_id: str, db: Session = Depends(get_db)):
    svc = AdaptiveMemoryService(db)
    entry = svc.memory.repo.get_by_id(memory_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Memory entry '{memory_id}' not found")
    svc.memory.repo.log_access(memory_id, requesting_component="api_router", reason="DIRECT_LOOKUP")
    return {
        "memory_id": entry.memory_id,
        "evidence_id": entry.evidence_id,
        "entity_ids": entry.entity_ids or [],
        "event_type": entry.event_type,
        "domain": entry.domain,
        "timestamp": entry.timestamp.isoformat(),
        "risk_score": entry.risk_score,
        "confidence": entry.confidence,
        "uncertainty": entry.uncertainty,
        "importance_score": entry.importance_score,
        "memory_tier": entry.memory_tier,
        "access_count": entry.access_count,
        "last_accessed_at": entry.last_accessed_at.isoformat(),
        "created_at": entry.created_at.isoformat(),
        "expires_at": entry.expires_at.isoformat() if entry.expires_at else None,
        "retrieval_count": entry.retrieval_count,
        "summary": entry.summary,
        "metadata": entry.metadata_json or {},
    }


@router.get("/memory/context/{entity_id}")
def get_entity_memory_context(entity_id: str, db: Session = Depends(get_db)):
    svc = AdaptiveMemoryService(db)
    return svc.get_entity_context(entity_id)


@router.post("/memory/retrieve")
def post_memory_retrieve(query: MemoryRetrievalQuery, db: Session = Depends(get_db)):
    svc = AdaptiveMemoryService(db)
    entries = svc.memory.retrieve(query, requesting_component="api_post_query")
    return {"count": len(entries), "entries": [e.dict() for e in entries]}


@router.get("/memory/transitions")
def get_memory_transitions(limit: int = Query(default=50, le=200), db: Session = Depends(get_db)):
    rows = db.query(MemoryTransitionLogModel).order_by(MemoryTransitionLogModel.timestamp.desc()).limit(limit).all()
    return [
        {
            "transition_id": r.transition_id,
            "memory_id": r.memory_id,
            "previous_tier": r.previous_tier,
            "new_tier": r.new_tier,
            "reason": r.reason,
            "importance_score": r.importance_score,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in rows
    ]


@router.get("/memory/access-log")
def get_memory_access_log(limit: int = Query(default=50, le=200), db: Session = Depends(get_db)):
    rows = db.query(MemoryAccessLogModel).order_by(MemoryAccessLogModel.access_time.desc()).limit(limit).all()
    return [
        {
            "log_id": r.log_id,
            "memory_id": r.memory_id,
            "query_id": r.query_id,
            "reason": r.reason,
            "retrieval_rank": r.retrieval_rank,
            "requesting_component": r.requesting_component,
            "access_time": r.access_time.isoformat(),
        }
        for r in rows
    ]


# ============================================================
# ATTACK EVIDENCE GRAPH API ENDPOINTS
# ============================================================

@router.get("/graph/nodes/{node_id}")
def get_graph_node(node_id: str, db: Session = Depends(get_db)):
    svc = AdaptiveMemoryService(db)
    node = svc.graph_builder.repo.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Graph node '{node_id}' not found")
    return {
        "node_id": node.node_id,
        "node_type": node.node_type,
        "canonical_id": node.canonical_id,
        "display_name": node.display_name,
        "attributes": node.attributes or {},
        "first_seen": node.first_seen.isoformat(),
        "last_seen": node.last_seen.isoformat(),
    }


@router.get("/graph/subgraph/{node_id}")
def get_graph_subgraph(
    node_id: str,
    k_hop: int = Query(default=2, ge=1, le=4),
    max_nodes: int = Query(default=200, le=500),
    db: Session = Depends(get_db),
):
    svc = AdaptiveMemoryService(db)
    subgraph = svc.graph_builder.get_subgraph(node_id=node_id, k_hop=k_hop, max_nodes=max_nodes)
    return subgraph.dict()


@router.get("/graph/paths")
def get_graph_paths(
    source_node_id: str,
    target_node_id: str,
    db: Session = Depends(get_db),
):
    svc = AdaptiveMemoryService(db)
    subgraph = svc.graph_builder.get_subgraph(node_id=source_node_id, k_hop=3)
    return {
        "source": source_node_id,
        "target": target_node_id,
        "path_found": target_node_id in [n.node_id for n in subgraph.nodes],
        "subgraph": subgraph.dict(),
    }


@router.get("/graph/attack-chains")
def get_attack_chains(
    entity_id: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(AttackChainCandidateModel)
    if entity_id:
        q = q.filter(AttackChainCandidateModel.primary_entity_id == entity_id)
    chains = q.order_by(AttackChainCandidateModel.created_at.desc()).limit(limit).all()
    return [
        {
            "chain_id": c.chain_id,
            "pattern_id": c.pattern_id,
            "primary_entity_id": c.primary_entity_id,
            "stage_count": c.stage_count,
            "matched_stage_count": c.matched_stage_count,
            "completeness": c.completeness,
            "confidence": c.confidence,
            "start_time": c.start_time.isoformat(),
            "end_time": c.end_time.isoformat(),
            "status": c.status,
            "explanation": c.explanation,
            "created_at": c.created_at.isoformat(),
        }
        for c in chains
    ]


# ============================================================
# TEMPORAL ANALYSIS API ENDPOINTS
# ============================================================

@router.get("/temporal/timeline/{entity_id}")
def get_temporal_timeline(entity_id: str, db: Session = Depends(get_db)):
    svc = AdaptiveMemoryService(db)
    ctx = svc.get_entity_context(entity_id)
    return ctx


@router.get("/temporal/patterns")
def get_temporal_patterns(db: Session = Depends(get_db)):
    svc = AdaptiveMemoryService(db)
    return {"patterns": svc.pattern_matcher.patterns}


# ============================================================
# RESEARCH LAB EVALUATION ENDPOINT
# ============================================================

@router.get("/adaptive_memory/evaluate")
def run_adaptive_memory_evaluation(db: Session = Depends(get_db)):
    evaluator = AdaptiveMemoryEvaluator(db)
    baselines = evaluator.run_baseline_comparison()
    ablations = evaluator.run_ablation_study()
    return {
        "status": "COMPLETED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "baseline_comparison": baselines,
        "ablation_studies": ablations,
    }
