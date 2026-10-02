"""
Evidence Fusion Engine for Evidence Fusion.
Orchestrates cross-domain normalisation, quality evaluation, deduplication, correlation,
conflict detection, weighting, risk aggregation, explanation, and FusionEvidence generation.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional

from hactm.fusion.models import (
    FusionEvidence,
    EvidenceQualityAssessment,
    EvidenceConflict,
    EvidenceCoverage,
    FusionAuditRecord,
    CorrelationType,
    RiskCategory,
)
from hactm.fusion.normalizer import CrossDomainEvidenceNormalizer
from hactm.fusion.quality_evaluator import EvidenceQualityEvaluator
from hactm.fusion.deduplicator import EvidenceDeduplicationEngine
from hactm.fusion.correlator import CrossDomainEvidenceCorrelator
from hactm.fusion.conflict_detector import EvidenceConflictDetector
from hactm.fusion.weight_calculator import EvidenceWeightCalculator
from hactm.fusion.risk_calculator import UnifiedRiskCalculator
from hactm.fusion.explanation_engine import FusionExplanationEngine


class EvidenceFusionEngine:
    """Core Evidence Fusion Cross-Domain Evidence Fusion Engine."""

    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = {}

        fusion_cfg = config.get("fusion", {})
        self.algorithm = fusion_cfg.get("algorithm", "weighted_contextual_baseline")
        self.version = fusion_cfg.get("version", "1.0.0")
        self.config_version = fusion_cfg.get("configuration_version", "1.0.0")

        freshness_cfg = fusion_cfg.get("freshness", {})
        fresh_sec = freshness_cfg.get("fresh_seconds", 300.0)
        recent_sec = freshness_cfg.get("recent_seconds", 3600.0)
        stale_sec = freshness_cfg.get("stale_seconds", 86400.0)

        temp_cfg = fusion_cfg.get("temporal_windows", {})
        default_window = temp_cfg.get("default_window_seconds", 1800.0)

        weights_cfg = fusion_cfg.get("weights")
        risk_thresh = fusion_cfg.get("risk_categories")
        expected_doms = fusion_cfg.get("coverage", {}).get("expected_domains")
        conflict_thresh = fusion_cfg.get("conflicts", {}).get("risk_disagreement_threshold", 0.35)
        diminishing_factor = fusion_cfg.get("saturation", {}).get("diminishing_returns_factor", 0.60)

        self.normalizer = CrossDomainEvidenceNormalizer()
        self.quality_evaluator = EvidenceQualityEvaluator(
            fresh_seconds=fresh_sec, recent_seconds=recent_sec, stale_seconds=stale_sec
        )
        self.deduplicator = EvidenceDeduplicationEngine()
        self.correlator = CrossDomainEvidenceCorrelator(default_window_seconds=default_window)
        self.conflict_detector = EvidenceConflictDetector(risk_disagreement_threshold=conflict_thresh)
        self.weight_calculator = EvidenceWeightCalculator(config_weights=weights_cfg)
        self.risk_calculator = UnifiedRiskCalculator(
            diminishing_returns_factor=diminishing_factor,
            expected_domains=expected_doms,
            risk_thresholds=risk_thresh,
        )
        self.explanation_engine = FusionExplanationEngine()

    def normalize_evidence(self, raw_evidence_list: List[Any]) -> List[Dict[str, Any]]:
        """Normalizes a list of evidence items into standard dictionaries."""
        return [self.normalizer.normalize(e) for e in raw_evidence_list]

    def validate_evidence(self, normalized_item: Dict[str, Any]) -> bool:
        """Validates mandatory fields on a normalized evidence item."""
        if not normalized_item.get("event_id"):
            return False
        if not normalized_item.get("entity_id"):
            return False
        if not normalized_item.get("agent_id"):
            return False
        return True

    def assess_quality(self, normalized_evidence_list: List[Dict[str, Any]]) -> List[EvidenceQualityAssessment]:
        """Calculates quality scores for all normalized evidence items."""
        return [self.quality_evaluator.evaluate(e) for e in normalized_evidence_list]

    def deduplicate(self, evidence_list: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
        """Identifies and removes duplicate or redundant evidence."""
        return self.deduplicator.deduplicate(evidence_list)

    def correlate_entities(
        self, primary_entity_id: str, evidence_list: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[str], CorrelationType]:
        """Correlates evidence items against primary_entity_id."""
        return self.correlator.correlate_entities(primary_entity_id, evidence_list)

    def correlate_temporal(
        self, evidence_list: List[Dict[str, Any]], window_seconds: float = None, reference_time: datetime = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """Filters evidence items within the temporal correlation window."""
        return self.correlator.correlate_temporal(evidence_list, window_seconds, reference_time)

    def detect_conflicts(
        self, fusion_id: str, evidence_list: List[Dict[str, Any]]
    ) -> Tuple[List[EvidenceConflict], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Detects risk and classification disagreement conflicts across evidence items."""
        return self.conflict_detector.detect_conflicts(fusion_id, evidence_list)

    def calculate_weights(
        self,
        evidence_list: List[Dict[str, Any]],
        quality_assessments: List[EvidenceQualityAssessment],
        unique_domain_count: int
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Calculates fusion weights for each evidence item."""
        qual_map = {q.evidence_id: q.quality_score for q in quality_assessments}
        domain_diversity_score = min(1.0, unique_domain_count / 3.0)

        weighted_list = []
        for item in evidence_list:
            ev_id = item.get("event_id")
            qual = qual_map.get(ev_id, 0.5)
            w = self.weight_calculator.calculate_weight(
                evidence_item=item,
                quality_score=qual,
                relevance_score=1.0,
                domain_diversity_score=domain_diversity_score,
            )
            weighted_list.append((item, w))
        return weighted_list

    def fuse_evidence(
        self,
        primary_entity_id: str,
        raw_evidence_list: List[Any],
        window_seconds: float = None,
        previous_fusion_id: Optional[str] = None
    ) -> Tuple[FusionEvidence, FusionAuditRecord, List[EvidenceConflict], List[EvidenceQualityAssessment]]:
        """
        Executes complete Evidence Fusion evidence fusion pipeline.
        Returns:
            fusion_evidence: FusionEvidence object
            audit_record: FusionAuditRecord object
            conflicts: List of EvidenceConflict objects
            quality_assessments: List of EvidenceQualityAssessment objects
        """
        fusion_id = f"fuse-{uuid.uuid4().hex[:12]}"
        fusion_ts = datetime.now(timezone.utc)

        # 1. Normalization & Validation
        normalized = self.normalize_evidence(raw_evidence_list)
        valid = [e for e in normalized if self.validate_evidence(e)]

        # 2. Quality Assessment
        qualities = self.assess_quality(valid)
        qual_dict = {q.evidence_id: q.quality_score for q in qualities}

        # 3. Deduplication
        deduped, redundant, redundant_count = self.deduplicate(valid)
        deduped_ids = [e["event_id"] for e in deduped]

        # 4. Entity Correlation
        entity_correlated, related_entities, corr_type = self.correlate_entities(primary_entity_id, deduped)

        # 5. Temporal Correlation
        temp_correlated, temporal_window = self.correlate_temporal(
            entity_correlated, window_seconds=window_seconds, reference_time=fusion_ts
        )

        # 6. Pattern Detection
        patterns = self.correlator.detect_cross_domain_patterns(temp_correlated)

        # 7. Conflict Analysis
        conflicts, supporting, conflicting = self.detect_conflicts(fusion_id, temp_correlated)

        # 8. Domains & Coverage
        source_agents = list(set(e.get("agent_id") for e in temp_correlated if e.get("agent_id")))
        source_domains = list(set(e.get("domain") for e in temp_correlated if e.get("domain")))
        unique_domain_count = len(source_domains)
        coverage = self.risk_calculator.calculate_coverage(temp_correlated)

        # 9. Weight Calculation
        weighted_evidence = self.calculate_weights(temp_correlated, qualities, unique_domain_count)
        weights_dict = {item.get("event_id"): w for item, w in weighted_evidence}

        # 10. Risk Calculation
        unified_risk, fusion_score, risk_category = self.risk_calculator.calculate_unified_risk(weighted_evidence)

        # 11. Confidence & Uncertainty Calculation
        quality_score_values = [qual_dict.get(e.get("event_id"), 0.5) for e in temp_correlated]
        quality_score_avg = sum(quality_score_values) / len(quality_score_values) if quality_score_values else 0.0

        confidence, uncertainty = self.risk_calculator.calculate_confidence_and_uncertainty(
            evidence_list=temp_correlated,
            quality_scores=quality_score_values,
            coverage=coverage,
            conflict_count=len(conflicts),
        )

        # 12. Explanation Engine
        reason_codes, explanation = self.explanation_engine.generate_explanation(
            unified_risk=unified_risk,
            risk_category=risk_category,
            primary_entity_id=primary_entity_id,
            supporting_evidence=supporting,
            conflicting_evidence=conflicting,
            conflicts=conflicts,
            coverage=coverage,
            patterns=patterns,
        )

        # Build FusionEvidence result object
        source_ids = [e["event_id"] for e in temp_correlated]

        fusion_evidence = FusionEvidence(
            fusion_id=fusion_id,
            fusion_timestamp=fusion_ts,
            primary_entity_id=primary_entity_id,
            related_entities=related_entities,
            source_evidence_ids=source_ids,
            source_agents=source_agents,
            source_domains=source_domains,
            correlation_type=corr_type,
            temporal_window=temporal_window,
            evidence_count=len(temp_correlated),
            unique_domain_count=unique_domain_count,
            supporting_evidence_count=len(supporting),
            conflicting_evidence_count=len(conflicting),
            redundant_evidence_count=redundant_count,
            quality_score=round(quality_score_avg, 4),
            fusion_score=fusion_score,
            unified_risk_score=unified_risk,
            confidence=confidence,
            uncertainty=uncertainty,
            risk_category=risk_category,
            reason_codes=reason_codes,
            explanation=explanation,
            fusion_algorithm=self.algorithm,
            fusion_version=self.version,
            configuration_version=self.config_version,
            previous_fusion_id=previous_fusion_id,
            revision_number=2 if previous_fusion_id else 1,
        )

        # Build Audit Record
        audit_record = FusionAuditRecord(
            audit_id=f"audit-{uuid.uuid4().hex[:12]}",
            fusion_id=fusion_id,
            input_evidence_ids=[e["event_id"] for e in valid],
            deduplicated_evidence_ids=deduped_ids,
            excluded_evidence_ids=[e["event_id"] for e in valid if e["event_id"] not in source_ids],
            conflict_ids=[c.conflict_id for c in conflicts],
            weights=weights_dict,
            quality_scores=qual_dict,
            correlation_results={
                "primary_entity_id": primary_entity_id,
                "related_entities": related_entities,
                "correlation_type": corr_type.value if hasattr(corr_type, "value") else corr_type,
                "patterns": patterns,
                "coverage": coverage.to_dict(),
            },
            risk_result=unified_risk,
            timestamp=fusion_ts,
        )

        return fusion_evidence, audit_record, conflicts, qualities
