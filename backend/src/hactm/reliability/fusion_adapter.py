"""
Reliability & Trust Fusion Adapter.
Integrates Reliability & Trust reliability, calibrated confidence, uncertainty, quality,
disagreement, freshness, and drift state into Evidence Fusion Evidence Fusion weighting.
"""

from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timezone

from hactm.reliability.models import (
    AgentReliabilityRecord,
    EvidenceQuality,
    EvidenceUncertainty,
    DriftRecord,
    DetectorDisagreement,
)


class ReliabilityFusionAdapter:
    """Adapts Evidence Fusion evidence items with Reliability & Trust reliability/uncertainty parameters."""

    def __init__(self):
        pass

    def compute_reliability_aware_weight(
        self,
        evidence_item: Dict[str, Any],
        reliability_record: Optional[AgentReliabilityRecord] = None,
        quality_assessment: Optional[EvidenceQuality] = None,
        uncertainty_record: Optional[EvidenceUncertainty] = None,
        disagreement: Optional[DetectorDisagreement] = None,
        drift_record: Optional[DriftRecord] = None,
        base_weight: float = 1.0,
    ) -> Tuple[float, List[str], Dict[str, Any]]:
        """
        Calculates Reliability & Trust reliability-aware fusion weight and transparent reason codes.
        Formula:
        effective_weight = base_weight * reliability_factor * quality_factor * freshness_factor * relevance_factor * uncertainty_adjustment
        """
        reason_codes = []
        breakdown = {}

        # 1. Reliability Factor
        if reliability_record:
            rel_score = reliability_record.reliability_score
            rel_status = str(reliability_record.reliability_status.value if hasattr(reliability_record.reliability_status, "value") else reliability_record.reliability_status)

            if rel_status == "INSUFFICIENT_DATA":
                rel_factor = 0.50
                reason_codes.append("LOW_SAMPLE_SUPPORT")
            elif rel_status == "DRIFT_OBSERVED":
                rel_factor = rel_score * 0.70
                reason_codes.append("DRIFT_OBSERVED")
            elif rel_status == "CALIBRATION_REQUIRED":
                rel_factor = rel_score * 0.85
                reason_codes.append("CALIBRATION_REQUIRED")
            elif rel_score >= 0.85:
                rel_factor = rel_score
                reason_codes.append("RELIABILITY_HIGH")
            else:
                rel_factor = rel_score
                reason_codes.append("RELIABILITY_REDUCED")
        else:
            rel_factor = 0.75
            reason_codes.append("NO_RELIABILITY_RECORD")

        breakdown["reliability_factor"] = round(rel_factor, 4)

        # 2. Evidence Quality Factor
        if quality_assessment:
            qual_score = quality_assessment.quality_score
            fresh_score = quality_assessment.freshness_score
            qual_factor = qual_score
            fresh_factor = fresh_score

            if qual_score >= 0.85:
                reason_codes.append("QUALITY_HIGH")
            if fresh_score >= 0.90:
                reason_codes.append("FRESH_EVIDENCE")
        else:
            qual_factor = float(evidence_item.get("quality_score", 0.80))
            fresh_factor = 1.0

        breakdown["quality_factor"] = round(qual_factor, 4)
        breakdown["freshness_factor"] = round(fresh_factor, 4)

        # 3. Uncertainty Adjustment Factor
        # High uncertainty reduces evidentiary weight smoothly
        if uncertainty_record:
            unc_score = uncertainty_record.uncertainty_score
        else:
            unc_score = float(evidence_item.get("uncertainty", 0.20))

        if unc_score <= 0.25:
            reason_codes.append("LOW_UNCERTAINTY")

        uncertainty_adj = 1.0 - (0.50 * unc_score)
        breakdown["uncertainty_adjustment"] = round(uncertainty_adj, 4)

        # 4. Detector Disagreement Penalty
        if disagreement and disagreement.disagreement_score > 0.35:
            dis_penalty = 1.0 - (0.30 * disagreement.disagreement_score)
            reason_codes.append("HIGH_DISAGREEMENT")
        else:
            dis_penalty = 1.0

        breakdown["disagreement_penalty"] = round(dis_penalty, 4)

        # 5. Drift Adjustment
        if drift_record and drift_record.drift_detected:
            drift_adj = 0.80
        else:
            drift_adj = 1.0
        breakdown["drift_adjustment"] = round(drift_adj, 4)

        # Effective Composite Weight
        effective_weight = (
            base_weight
            * rel_factor
            * qual_factor
            * fresh_factor
            * uncertainty_adj
            * dis_penalty
            * drift_adj
        )

        effective_weight = max(0.05, min(3.0, round(effective_weight, 4)))
        breakdown["effective_weight"] = effective_weight

        return effective_weight, reason_codes, breakdown
