"""
Weight Calculator for Evidence Fusion Fusion.
"""

from typing import Dict, Any, List


class EvidenceWeightCalculator:
    """Calculates fusion weights for evidence items based on quality, confidence, freshness, and relevance."""

    def __init__(self, config_weights: Dict[str, float] = None):
        if config_weights is None:
            config_weights = {
                "confidence_weight": 0.25,
                "quality_weight": 0.20,
                "relevance_weight": 0.20,
                "freshness_weight": 0.10,
                "diversity_weight": 0.10,
                "severity_weight": 0.15,
            }
        self.validate_weights(config_weights)
        self.config_weights = config_weights

    @staticmethod
    def validate_weights(weights: Dict[str, float]) -> None:
        """Validates that configured weights are within [0, 1]."""
        for k, v in weights.items():
            if not isinstance(v, (int, float)):
                raise ValueError(f"Weight {k} must be a number, got {type(v)}")
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"Weight {k} must be between 0.0 and 1.0, got {v}")

    def calculate_weight(
        self,
        evidence_item: Dict[str, Any],
        quality_score: float,
        relevance_score: float = 1.0,
        domain_diversity_score: float = 1.0
    ) -> float:
        """
        Calculates individual evidence weight.
        Formula:
            weight = w_conf * conf + w_qual * qual + w_rel * rel + w_fresh * fresh + w_div * div + w_sev * sev
        """
        conf = float(evidence_item.get("confidence", 1.0))
        qual = float(quality_score)
        rel = float(relevance_score)
        div = float(domain_diversity_score)

        # Freshness approximation from quality or timestamp
        fresh = float(evidence_item.get("freshness_score", qual))

        # Severity numerical mapping
        sev_str = str(evidence_item.get("severity", "LOW")).upper()
        sev_map = {"CRITICAL": 1.0, "HIGH": 0.8, "MEDIUM": 0.5, "LOW": 0.2, "INFO": 0.1}
        sev = sev_map.get(sev_str, 0.2)

        w = self.config_weights

        weight = (
            w["confidence_weight"] * conf +
            w["quality_weight"] * qual +
            w["relevance_weight"] * rel +
            w["freshness_weight"] * fresh +
            w["diversity_weight"] * div +
            w["severity_weight"] * sev
        )

        return round(max(0.01, min(1.0, weight)), 4)
