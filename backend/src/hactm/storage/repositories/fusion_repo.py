"""
Database Repository for Evidence Fusion Fusion Persistence & Queries.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from hactm.storage.models import (
    FusionResultModel,
    FusionInputModel,
    EvidenceConflictModel,
    FusionAuditModel,
    RiskHistoryModel,
    EvidenceQualityModel,
)
from hactm.fusion.models import (
    FusionEvidence,
    FusionAuditRecord,
    EvidenceConflict,
    EvidenceQualityAssessment,
)


class FusionRepository:
    """Handles CRUD operations for Evidence Fusion cross-domain fusion records."""

    def __init__(self, db: Session):
        self.db = db

    def save_fusion_result(
        self,
        fusion: FusionEvidence,
        audit: FusionAuditRecord,
        conflicts: List[EvidenceConflict],
        qualities: List[EvidenceQualityAssessment]
    ) -> FusionResultModel:
        """Persists complete FusionEvidence, FusionInputs, Conflicts, Audit, and RiskHistory."""
        # 1. Fusion Result Model
        fusion_model = FusionResultModel(
            fusion_id=fusion.fusion_id,
            fusion_timestamp=fusion.fusion_timestamp,
            primary_entity_id=fusion.primary_entity_id,
            related_entities=fusion.related_entities,
            source_evidence_ids=fusion.source_evidence_ids,
            source_agents=fusion.source_agents,
            source_domains=fusion.source_domains,
            correlation_type=fusion.correlation_type.value if hasattr(fusion.correlation_type, 'value') else str(fusion.correlation_type),
            temporal_window=fusion.temporal_window,
            evidence_count=fusion.evidence_count,
            unique_domain_count=fusion.unique_domain_count,
            supporting_evidence_count=fusion.supporting_evidence_count,
            conflicting_evidence_count=fusion.conflicting_evidence_count,
            redundant_evidence_count=fusion.redundant_evidence_count,
            quality_score=fusion.quality_score,
            fusion_score=fusion.fusion_score,
            unified_risk_score=fusion.unified_risk_score,
            confidence=fusion.confidence,
            uncertainty=fusion.uncertainty,
            risk_category=fusion.risk_category.value if hasattr(fusion.risk_category, 'value') else str(fusion.risk_category),
            reason_codes=fusion.reason_codes,
            explanation=fusion.explanation,
            fusion_algorithm=fusion.fusion_algorithm,
            fusion_version=fusion.fusion_version,
            configuration_version=fusion.configuration_version,
            previous_fusion_id=fusion.previous_fusion_id,
            revision_number=fusion.revision_number,
        )
        self.db.add(fusion_model)
        self.db.flush()

        # 2. Fusion Inputs
        for ev_id in fusion.source_evidence_ids:
            weight = audit.weights.get(ev_id, 1.0)
            input_model = FusionInputModel(
                fusion_id=fusion.fusion_id,
                evidence_id=ev_id,
                agent_id="unknown",  # Populated from evidence
                domain="unknown",
                role="SUPPORTING",
                weight=weight,
                contribution=round(fusion.unified_risk_score * weight, 4),
            )
            self.db.add(input_model)

        # 3. Conflicts
        for c in conflicts:
            conflict_model = EvidenceConflictModel(
                conflict_id=c.conflict_id,
                fusion_id=fusion.fusion_id,
                evidence_ids=c.evidence_ids,
                entities=c.entities,
                domains=c.domains,
                risk_difference=c.risk_difference,
                conflict_type=c.conflict_type.value if hasattr(c.conflict_type, 'value') else str(c.conflict_type),
                severity=c.severity,
                explanation=c.explanation,
                created_at=c.created_at,
            )
            self.db.add(conflict_model)

        # 4. Audit Record
        audit_model = FusionAuditModel(
            audit_id=audit.audit_id,
            fusion_id=fusion.fusion_id,
            input_evidence_ids=audit.input_evidence_ids,
            deduplicated_evidence_ids=audit.deduplicated_evidence_ids,
            excluded_evidence_ids=audit.excluded_evidence_ids,
            conflict_ids=audit.conflict_ids,
            weights=audit.weights,
            quality_scores=audit.quality_scores,
            correlation_results=audit.correlation_results,
            risk_result=audit.risk_result,
            timestamp=audit.timestamp,
        )
        self.db.add(audit_model)

        # 5. Risk History
        history_model = RiskHistoryModel(
            entity_id=fusion.primary_entity_id,
            timestamp=fusion.fusion_timestamp,
            risk_score=fusion.unified_risk_score,
            risk_category=fusion.risk_category.value if hasattr(fusion.risk_category, 'value') else str(fusion.risk_category),
            confidence=fusion.confidence,
            uncertainty=fusion.uncertainty,
            coverage=round(fusion.unique_domain_count / 5.0, 4),
            fusion_id=fusion.fusion_id,
        )
        self.db.add(history_model)

        # 6. Quality Assessments
        for q in qualities:
            qual_model = EvidenceQualityModel(
                quality_id=q.quality_id,
                evidence_id=q.evidence_id,
                completeness_score=q.completeness_score,
                provenance_score=q.provenance_score,
                freshness_score=q.freshness_score,
                validity_score=q.validity_score,
                quality_score=q.quality_score,
                evaluated_at=q.evaluated_at,
            )
            self.db.add(qual_model)

        self.db.commit()
        self.db.refresh(fusion_model)
        return fusion_model

    def get_fusion_results(
        self,
        page: int = 1,
        page_size: int = 50,
        entity_id: Optional[str] = None,
        risk_category: Optional[str] = None,
        min_risk: Optional[float] = None,
        max_risk: Optional[float] = None,
        correlation_type: Optional[str] = None
    ) -> Tuple[List[FusionResultModel], int]:
        """Retrieves paginated fusion results with optional filters."""
        query = self.db.query(FusionResultModel)

        if entity_id:
            query = query.filter(FusionResultModel.primary_entity_id == entity_id)
        if risk_category:
            query = query.filter(FusionResultModel.risk_category == risk_category.upper())
        if min_risk is not None:
            query = query.filter(FusionResultModel.unified_risk_score >= min_risk)
        if max_risk is not None:
            query = query.filter(FusionResultModel.unified_risk_score <= max_risk)
        if correlation_type:
            query = query.filter(FusionResultModel.correlation_type == correlation_type)

        total = query.count()
        offset = (page - 1) * page_size
        results = query.order_by(FusionResultModel.fusion_timestamp.desc()).offset(offset).limit(page_size).all()
        return results, total

    def get_fusion_by_id(self, fusion_id: str) -> Optional[FusionResultModel]:
        """Retrieves a single fusion result by fusion_id."""
        return self.db.query(FusionResultModel).filter(FusionResultModel.fusion_id == fusion_id).first()

    def get_entity_risk_history(self, entity_id: str, limit: int = 50) -> List[RiskHistoryModel]:
        """Retrieves risk evolution history for an entity."""
        return (
            self.db.query(RiskHistoryModel)
            .filter(RiskHistoryModel.entity_id == entity_id)
            .order_by(RiskHistoryModel.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_conflicts(self, page: int = 1, page_size: int = 50) -> Tuple[List[EvidenceConflictModel], int]:
        """Retrieves evidence conflicts."""
        query = self.db.query(EvidenceConflictModel)
        total = query.count()
        offset = (page - 1) * page_size
        conflicts = query.order_by(EvidenceConflictModel.created_at.desc()).offset(offset).limit(page_size).all()
        return conflicts, total

    def get_metrics(self) -> Dict[str, Any]:
        """Calculates aggregate Evidence Fusion fusion metrics."""
        total_fusions = self.db.query(FusionResultModel).count()
        total_conflicts = self.db.query(EvidenceConflictModel).count()
        high_risk_fusions = self.db.query(FusionResultModel).filter(FusionResultModel.unified_risk_score >= 0.60).count()
        
        avg_risk = 0.0
        avg_coverage = 0.0
        if total_fusions > 0:
            avg_risk = self.db.query(FusionResultModel).with_entities(FusionResultModel.unified_risk_score).all()
            avg_risk = sum(r[0] for r in avg_risk) / total_fusions
            
            domain_counts = self.db.query(FusionResultModel).with_entities(FusionResultModel.unique_domain_count).all()
            avg_coverage = sum(c[0] for c in domain_counts) / (total_fusions * 5.0)

        return {
            "total_fusions": total_fusions,
            "high_risk_fusions": high_risk_fusions,
            "total_conflicts": total_conflicts,
            "average_unified_risk": round(avg_risk, 4),
            "average_domain_coverage": round(avg_coverage, 4),
        }
