"""
Evidence Fusion Cross-Domain Evidence Fusion Data Models and Enums.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional


class CorrelationType(str, Enum):
    ENTITY_MATCH = "ENTITY_MATCH"
    SESSION_MATCH = "SESSION_MATCH"
    CORRELATION_ID_MATCH = "CORRELATION_ID_MATCH"
    TEMPORAL_PROXIMITY = "TEMPORAL_PROXIMITY"
    DOMAIN_RELATION = "DOMAIN_RELATION"
    EVENT_SEQUENCE = "EVENT_SEQUENCE"
    CONTEXT_MATCH = "CONTEXT_MATCH"
    SHARED_DEVICE = "SHARED_DEVICE"
    SHARED_ACCOUNT = "SHARED_ACCOUNT"
    SHARED_IP = "SHARED_IP"
    SHARED_TRANSACTION = "SHARED_TRANSACTION"


class ConflictType(str, Enum):
    RISK_DISAGREEMENT = "RISK_DISAGREEMENT"
    CLASSIFICATION_DISAGREEMENT = "CLASSIFICATION_DISAGREEMENT"
    TEMPORAL_INCONSISTENCY = "TEMPORAL_INCONSISTENCY"
    ENTITY_AMBIGUITY = "ENTITY_AMBIGUITY"
    DATA_QUALITY_CONFLICT = "DATA_QUALITY_CONFLICT"


class RiskCategory(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class EvidenceQualityAssessment:
    quality_id: str
    evidence_id: str
    completeness_score: float  # [0, 1]
    provenance_score: float    # [0, 1]
    freshness_score: float     # [0, 1]
    validity_score: float      # [0, 1]
    quality_score: float       # Overall quality score [0, 1]
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quality_id": self.quality_id,
            "evidence_id": self.evidence_id,
            "completeness_score": self.completeness_score,
            "provenance_score": self.provenance_score,
            "freshness_score": self.freshness_score,
            "validity_score": self.validity_score,
            "quality_score": self.quality_score,
            "evaluated_at": self.evaluated_at.isoformat(),
        }


@dataclass
class EvidenceConflict:
    conflict_id: str
    fusion_id: str
    evidence_ids: List[str]
    entities: List[str]
    domains: List[str]
    risk_difference: float
    conflict_type: ConflictType
    severity: str  # LOW, MEDIUM, HIGH
    explanation: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "fusion_id": self.fusion_id,
            "evidence_ids": self.evidence_ids,
            "entities": self.entities,
            "domains": self.domains,
            "risk_difference": self.risk_difference,
            "conflict_type": self.conflict_type.value if isinstance(self.conflict_type, Enum) else self.conflict_type,
            "severity": self.severity,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class EvidenceCoverage:
    expected_domains: List[str]
    available_domains: List[str]
    missing_domains: List[str]
    evidence_count: int
    coverage_ratio: float  # available_domains / expected_domains

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expected_domains": self.expected_domains,
            "available_domains": self.available_domains,
            "missing_domains": self.missing_domains,
            "evidence_count": self.evidence_count,
            "coverage_ratio": self.coverage_ratio,
        }


@dataclass
class FusionAuditRecord:
    audit_id: str
    fusion_id: str
    input_evidence_ids: List[str]
    deduplicated_evidence_ids: List[str]
    excluded_evidence_ids: List[str]
    conflict_ids: List[str]
    weights: Dict[str, float]
    quality_scores: Dict[str, float]
    correlation_results: Dict[str, Any]
    risk_result: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "fusion_id": self.fusion_id,
            "input_evidence_ids": self.input_evidence_ids,
            "deduplicated_evidence_ids": self.deduplicated_evidence_ids,
            "excluded_evidence_ids": self.excluded_evidence_ids,
            "conflict_ids": self.conflict_ids,
            "weights": self.weights,
            "quality_scores": self.quality_scores,
            "correlation_results": self.correlation_results,
            "risk_result": self.risk_result,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class FusionEvidence:
    fusion_id: str
    fusion_timestamp: datetime
    primary_entity_id: str
    related_entities: List[str]
    source_evidence_ids: List[str]
    source_agents: List[str]
    source_domains: List[str]
    correlation_type: CorrelationType
    temporal_window: float
    evidence_count: int
    unique_domain_count: int
    supporting_evidence_count: int
    conflicting_evidence_count: int
    redundant_evidence_count: int
    quality_score: float
    fusion_score: float
    unified_risk_score: float  # [0.0, 1.0]
    confidence: float          # [0.0, 1.0]
    uncertainty: float         # [0.0, 1.0]
    risk_category: RiskCategory
    reason_codes: List[str]
    explanation: str
    fusion_algorithm: str = "weighted_contextual_baseline"
    fusion_version: str = "1.0.0"
    configuration_version: str = "1.0.0"
    previous_fusion_id: Optional[str] = None
    revision_number: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fusion_id": self.fusion_id,
            "fusion_timestamp": self.fusion_timestamp.isoformat(),
            "primary_entity_id": self.primary_entity_id,
            "related_entities": self.related_entities,
            "source_evidence_ids": self.source_evidence_ids,
            "source_agents": self.source_agents,
            "source_domains": self.source_domains,
            "correlation_type": self.correlation_type.value if isinstance(self.correlation_type, Enum) else self.correlation_type,
            "temporal_window": self.temporal_window,
            "evidence_count": self.evidence_count,
            "unique_domain_count": self.unique_domain_count,
            "supporting_evidence_count": self.supporting_evidence_count,
            "conflicting_evidence_count": self.conflicting_evidence_count,
            "redundant_evidence_count": self.redundant_evidence_count,
            "quality_score": self.quality_score,
            "fusion_score": self.fusion_score,
            "unified_risk_score": self.unified_risk_score,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "risk_category": self.risk_category.value if isinstance(self.risk_category, Enum) else self.risk_category,
            "reason_codes": self.reason_codes,
            "explanation": self.explanation,
            "fusion_algorithm": self.fusion_algorithm,
            "fusion_version": self.fusion_version,
            "configuration_version": self.configuration_version,
            "previous_fusion_id": self.previous_fusion_id,
            "revision_number": self.revision_number,
        }
