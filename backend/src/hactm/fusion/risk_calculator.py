"""
Unified Cyber Risk & Uncertainty Calculator for Evidence Fusion Fusion.
"""

from typing import List, Dict, Any, Tuple
from hactm.fusion.models import RiskCategory, EvidenceCoverage


class UnifiedRiskCalculator:
    """Calculates Unified Cyber Risk Score, Confidence, Uncertainty, and Evidence Coverage."""

    def __init__(
        self,
        diminishing_returns_factor: float = 0.60,
        expected_domains: List[str] = None,
        risk_thresholds: Dict[str, float] = None
    ):
        self.diminishing_returns_factor = diminishing_returns_factor
        self.expected_domains = expected_domains or [
            "network-security-agent",
            "phishing-intelligence-agent",
            "uba-agent",
            "identity-authentication-agent",
            "transaction-security-agent"
        ]
        self.risk_thresholds = risk_thresholds or {
            "low_max": 0.24,
            "moderate_max": 0.49,
            "high_max": 0.74,
            "critical_min": 0.75,
        }

    def calculate_unified_risk(
        self,
        evidence_with_weights: List[Tuple[Dict[str, Any], float]]
    ) -> Tuple[float, float, RiskCategory]:
        """
        Calculates Unified Cyber Risk Score [0.0, 1.0] using bounded probabilistic-style aggregation
        with diminishing returns for repeated evidence.
        Returns:
            unified_risk_score: float [0.0, 1.0]
            fusion_score: float raw weighted score
            risk_category: RiskCategory
        """
        if not evidence_with_weights:
            return 0.0, 0.0, RiskCategory.LOW

        # Group evidence by domain to apply diminishing returns per domain
        domain_groups: Dict[str, List[Tuple[Dict[str, Any], float]]] = {}
        for item, weight in evidence_with_weights:
            dom = item.get("domain", "generic")
            if dom not in domain_groups:
                domain_groups[dom] = []
            domain_groups[dom].append((item, weight))

        domain_scores = []
        for dom, items in domain_groups.items():
            # Sort items by risk * weight descending
            sorted_items = sorted(items, key=lambda x: x[0].get("risk_score", 0.0) * x[1], reverse=True)
            
            # Diminishing returns: score = r1*w1 + 0.6*r2*w2 + 0.6^2*r3*w3 ...
            dom_score = 0.0
            weight_sum = 0.0
            factor = 1.0
            for itm, w in sorted_items:
                r = float(itm.get("risk_score", 0.0))
                dom_score += r * w * factor
                weight_sum += w * factor
                factor *= self.diminishing_returns_factor

            norm_dom_score = dom_score / weight_sum if weight_sum > 0 else 0.0
            domain_scores.append(norm_dom_score)

        # Bounded probabilistic union across domains: 1 - prod(1 - S_dom)
        # Prevents 10 medium evidence items from automatically becoming 1.0 risk simply due to count.
        prob_union = 1.0
        for s in domain_scores:
            prob_union *= (1.0 - max(0.0, min(0.99, s)))

        unified_risk = round(1.0 - prob_union, 4)
        unified_risk = max(0.0, min(1.0, unified_risk))

        # Raw fusion score (weighted arithmetic average for comparison/audit)
        total_weight = sum(w for _, w in evidence_with_weights)
        total_weighted_risk = sum(float(item.get("risk_score", 0.0)) * w for item, w in evidence_with_weights)
        fusion_score = round(total_weighted_risk / total_weight, 4) if total_weight > 0 else 0.0

        risk_category = self.categorize_risk(unified_risk)
        return unified_risk, fusion_score, risk_category

    def categorize_risk(self, risk_score: float) -> RiskCategory:
        if risk_score >= self.risk_thresholds.get("critical_min", 0.75):
            return RiskCategory.CRITICAL
        elif risk_score >= 0.50:
            return RiskCategory.HIGH
        elif risk_score >= 0.25:
            return RiskCategory.MODERATE
        return RiskCategory.LOW

    def calculate_coverage(self, evidence_list: List[Dict[str, Any]]) -> EvidenceCoverage:
        """Calculates domain coverage ratio and identifies missing domains."""
        available_agents = set(item.get("agent_id", "") for item in evidence_list if item.get("agent_id"))
        
        expected_set = set(self.expected_domains)
        available = list(expected_set.intersection(available_agents))
        missing = list(expected_set.difference(available_agents))

        coverage_ratio = round(len(available) / len(expected_set), 4) if expected_set else 1.0

        return EvidenceCoverage(
            expected_domains=self.expected_domains,
            available_domains=available,
            missing_domains=missing,
            evidence_count=len(evidence_list),
            coverage_ratio=coverage_ratio,
        )

    def calculate_confidence_and_uncertainty(
        self,
        evidence_list: List[Dict[str, Any]],
        quality_scores: List[float],
        coverage: EvidenceCoverage,
        conflict_count: int
    ) -> Tuple[float, float]:
        """
        Calculates Fusion Confidence and Baseline Uncertainty.
        Confidence increases with source confidence, quality, coverage, and domain agreement.
        Uncertainty increases with missing domains, conflicts, sparse evidence, and detector uncertainty.
        """
        if not evidence_list:
            return 0.50, 0.50

        avg_source_confidence = sum(float(i.get("confidence", 1.0)) for i in evidence_list) / len(evidence_list)
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5

        # Fusion confidence combines source confidence, quality, and domain coverage
        confidence = (0.45 * avg_source_confidence) + (0.35 * avg_quality) + (0.20 * coverage.coverage_ratio)
        if conflict_count > 0:
            confidence *= max(0.60, 1.0 - (0.15 * conflict_count))

        confidence = round(max(0.05, min(0.99, confidence)), 4)

        # Baseline uncertainty increases when coverage is low or conflicts exist
        avg_source_uncertainty = sum(float(i.get("uncertainty", 0.0)) for i in evidence_list) / len(evidence_list)
        coverage_uncertainty = 1.0 - coverage.coverage_ratio
        conflict_uncertainty = min(0.40, conflict_count * 0.20)

        uncertainty = (0.40 * avg_source_uncertainty) + (0.40 * coverage_uncertainty) + (0.20 * conflict_uncertainty)
        uncertainty = round(max(0.01, min(0.99, uncertainty)), 4)

        return confidence, uncertainty
