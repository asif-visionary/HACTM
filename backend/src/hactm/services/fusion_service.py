"""
Evidence Fusion Service for Evidence Fusion.
Orchestrates DB evidence retrieval, fusion execution, database persistence, and evaluation.
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from hactm.storage.models import SecurityEvidenceModel
from hactm.storage.repositories.fusion_repo import FusionRepository
from hactm.fusion.engine import EvidenceFusionEngine
from hactm.fusion.models import FusionEvidence, EvidenceConflict, RiskCategory
from hactm.fusion.evaluation import CrossDomainFusionEvaluator
from hactm.core.config import settings


class FusionService:
    """Service layer for Evidence Fusion Cross-Domain Evidence Fusion."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = FusionRepository(db)
        self.engine = EvidenceFusionEngine()
        self.evaluator = CrossDomainFusionEvaluator(self.engine)

    def run_fusion_for_entity(
        self,
        entity_id: str,
        window_seconds: float = 1800.0,
        previous_fusion_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieves un-fused / candidate SecurityEvidence for entity_id, executes fusion,
        persists results, and updates entity risk history.
        """
        # Fetch SecurityEvidence records for this entity
        query = self.db.query(SecurityEvidenceModel).filter(
            (SecurityEvidenceModel.entity_id == entity_id) |
            (SecurityEvidenceModel.raw_event_id == entity_id) |
            (SecurityEvidenceModel.session_id == entity_id)
        )
        evidence_models = query.order_by(SecurityEvidenceModel.timestamp.desc()).limit(100).all()

        if not evidence_models:
            # Check if entity exists in database generally
            evidence_models = self.db.query(SecurityEvidenceModel).order_by(SecurityEvidenceModel.timestamp.desc()).limit(50).all()

        raw_list = [m.evidence for m in evidence_models if m.evidence]
        if not raw_list:
            raw_list = [
                {
                    "event_id": m.event_id,
                    "agent_id": m.agent_id,
                    "entity_id": m.entity_id,
                    "event_type": m.event_type,
                    "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                    "risk_score": m.risk_score,
                    "confidence": m.confidence,
                    "uncertainty": m.uncertainty,
                    "severity": m.severity,
                    "evidence": m.evidence,
                    "source": m.source,
                    "dataset": m.dataset,
                }
                for m in evidence_models
            ]

        if not raw_list:
            return {"message": "No evidence records found for fusion", "entity_id": entity_id, "fusion": None}

        # Execute EvidenceFusionEngine
        fusion, audit, conflicts, qualities = self.engine.fuse_evidence(
            primary_entity_id=entity_id,
            raw_evidence_list=raw_list,
            window_seconds=window_seconds,
            previous_fusion_id=previous_fusion_id,
        )

        # Persist results
        model = self.repo.save_fusion_result(fusion, audit, conflicts, qualities)

        return {
            "fusion": fusion.to_dict(),
            "conflicts_count": len(conflicts),
            "qualities_evaluated": len(qualities),
            "status": "SUCCESS",
        }

    def get_fusion_results(
        self,
        page: int = 1,
        page_size: int = 50,
        entity_id: Optional[str] = None,
        risk_category: Optional[str] = None,
        min_risk: Optional[float] = None,
        max_risk: Optional[float] = None,
        correlation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        results, total = self.repo.get_fusion_results(
            page=page,
            page_size=page_size,
            entity_id=entity_id,
            risk_category=risk_category,
            min_risk=min_risk,
            max_risk=max_risk,
            correlation_type=correlation_type,
        )
        return {
            "items": [self._format_fusion_model(m) for m in results],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 1,
        }

    def get_fusion_by_id(self, fusion_id: str) -> Optional[Dict[str, Any]]:
        m = self.repo.get_fusion_by_id(fusion_id)
        return self._format_fusion_model(m) if m else None

    def get_entity_risk(self, entity_id: str) -> Dict[str, Any]:
        history = self.repo.get_entity_risk_history(entity_id, limit=20)
        latest = history[0] if history else None

        return {
            "entity_id": entity_id,
            "current_risk_score": latest.risk_score if latest else 0.0,
            "current_risk_category": latest.risk_category if latest else "LOW",
            "confidence": latest.confidence if latest else 1.0,
            "uncertainty": latest.uncertainty if latest else 0.0,
            "coverage": latest.coverage if latest else 0.20,
            "last_assessed_at": latest.timestamp.isoformat() if latest else None,
            "history_count": len(history),
            "history": [
                {
                    "timestamp": h.timestamp.isoformat(),
                    "risk_score": h.risk_score,
                    "risk_category": h.risk_category,
                    "confidence": h.confidence,
                    "uncertainty": h.uncertainty,
                    "coverage": h.coverage,
                    "fusion_id": h.fusion_id,
                }
                for h in history
            ],
        }

    def get_conflicts(self, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        conflicts, total = self.repo.get_conflicts(page=page, page_size=page_size)
        return {
            "items": [
                {
                    "conflict_id": c.conflict_id,
                    "fusion_id": c.fusion_id,
                    "evidence_ids": c.evidence_ids,
                    "entities": c.entities,
                    "domains": c.domains,
                    "risk_difference": c.risk_difference,
                    "conflict_type": c.conflict_type,
                    "severity": c.severity,
                    "explanation": c.explanation,
                    "created_at": c.created_at.isoformat(),
                }
                for c in conflicts
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_metrics(self) -> Dict[str, Any]:
        return self.repo.get_metrics()

    def evaluate_fusion(self) -> Dict[str, Any]:
        return self.evaluator.run_evaluation_suite()

    @staticmethod
    def _format_fusion_model(m) -> Dict[str, Any]:
        return {
            "fusion_id": m.fusion_id,
            "fusion_timestamp": m.fusion_timestamp.isoformat(),
            "primary_entity_id": m.primary_entity_id,
            "related_entities": m.related_entities or [],
            "source_evidence_ids": m.source_evidence_ids or [],
            "source_agents": m.source_agents or [],
            "source_domains": m.source_domains or [],
            "correlation_type": m.correlation_type,
            "temporal_window": m.temporal_window,
            "evidence_count": m.evidence_count,
            "unique_domain_count": m.unique_domain_count,
            "supporting_evidence_count": m.supporting_evidence_count,
            "conflicting_evidence_count": m.conflicting_evidence_count,
            "redundant_evidence_count": m.redundant_evidence_count,
            "quality_score": m.quality_score,
            "fusion_score": m.fusion_score,
            "unified_risk_score": m.unified_risk_score,
            "confidence": m.confidence,
            "uncertainty": m.uncertainty,
            "risk_category": m.risk_category,
            "reason_codes": m.reason_codes or [],
            "explanation": m.explanation,
            "fusion_algorithm": m.fusion_algorithm,
            "fusion_version": m.fusion_version,
            "configuration_version": m.configuration_version,
            "previous_fusion_id": m.previous_fusion_id,
            "revision_number": m.revision_number,
        }
