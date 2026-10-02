"""
Reliability & Trust Uncertainty Engine & Detector Disagreement Analysis.
Calculates uncertainty scores (0-1) across aleatoric, epistemic, detector disagreement,
evidence incompleteness, and OOD proxy indicators.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from hactm.reliability.models import EvidenceUncertainty, DetectorDisagreement


class UncertaintyEngine:
    """Core Uncertainty and Disagreement Analysis Engine for Reliability & Trust."""

    def __init__(self, disagreement_threshold: float = 0.35):
        self.disagreement_threshold = disagreement_threshold

    def calculate_evidence_uncertainty(
        self,
        evidence_id: str,
        agent_id: str,
        detector_id: Optional[str] = None,
        confidence: float = 0.8,
        features_used: Optional[Dict[str, Any]] = None,
        missing_fields: Optional[List[str]] = None,
        disagreement_score: float = 0.0,
        model_version: str = "1.0.0",
        uncertainty_type: str = "PROXY",
    ) -> EvidenceUncertainty:
        """
        Calculates composite uncertainty score based on confidence gap, missing fields,
        feature sparsity, and detector disagreement.
        """
        features_used = features_used or {}
        missing_fields = missing_fields or []

        # 1. Epistemic / Confidence Gap Factor (higher when confidence is mid-range ~ 0.5)
        # Confidence near 0.5 indicates maximum model uncertainty
        conf_distance_from_certainty = 1.0 - abs(confidence - 0.5) * 2.0  # 1.0 if conf=0.5, 0.0 if conf=1.0 or 0.0
        confidence_uncertainty = max(0.0, min(1.0, 1.0 - confidence))

        # 2. Evidence Incompleteness Factor
        missing_count = len(missing_fields)
        incompleteness_factor = min(1.0, missing_count * 0.20)

        # 3. Feature Sparsity (OOD indicator proxy)
        num_features = len(features_used)
        if num_features < 3:
            sparsity_factor = 0.40
        elif num_features < 6:
            sparsity_factor = 0.20
        else:
            sparsity_factor = 0.05

        # 4. Detector Disagreement Contribution
        disagreement_contrib = max(0.0, min(1.0, disagreement_score))

        # Composite weighted uncertainty score
        composite_score = (
            0.35 * confidence_uncertainty
            + 0.25 * incompleteness_factor
            + 0.15 * sparsity_factor
            + 0.25 * disagreement_contrib
        )
        uncertainty_score = max(0.0, min(1.0, composite_score))

        factors = {
            "confidence": confidence,
            "confidence_uncertainty": round(confidence_uncertainty, 4),
            "missing_fields": missing_fields,
            "incompleteness_factor": round(incompleteness_factor, 4),
            "feature_count": num_features,
            "sparsity_factor": round(sparsity_factor, 4),
            "disagreement_score": round(disagreement_score, 4),
        }

        unc_id = f"unc-{uuid.uuid4().hex[:12]}"
        return EvidenceUncertainty(
            uncertainty_id=unc_id,
            evidence_id=evidence_id,
            agent_id=agent_id,
            detector_id=detector_id,
            uncertainty_score=round(uncertainty_score, 4),
            uncertainty_type=uncertainty_type,
            source="composite_uncertainty_evaluator",
            calculation_method="entropy_disagreement_composite",
            contributing_factors=factors,
            model_version=model_version,
            created_at=datetime.now(timezone.utc),
        )

    def analyze_detector_disagreement(
        self,
        event_id: str,
        entity_id: str,
        detections: List[Dict[str, Any]],
    ) -> DetectorDisagreement:
        """
        Analyzes multi-detector predictions for a single event/entity.
        Calculates risk variance, confidence variance, categorical disagreement,
        and overall disagreement score.
        """
        if not detections:
            return DetectorDisagreement(
                disagreement_id=f"dis-{uuid.uuid4().hex[:12]}",
                event_id=event_id,
                entity_id=entity_id,
                detector_count=0,
                participating_detectors=[],
                risk_scores={},
                confidence_scores={},
                risk_variance=0.0,
                confidence_variance=0.0,
                categorical_disagreement=False,
                disagreement_score=0.0,
                explanation="No detector outputs to evaluate.",
                created_at=datetime.now(timezone.utc),
            )

        detector_ids = []
        risk_map = {}
        conf_map = {}
        severities = []

        for d in detections:
            det_name = d.get("detector_id") or d.get("detector_type") or d.get("agent_id") or f"det-{len(detector_ids)}"
            r = float(d.get("risk_score", 0.0))
            c = float(d.get("confidence", 0.8))
            sev = str(d.get("severity", "LOW")).upper()

            detector_ids.append(det_name)
            risk_map[det_name] = r
            conf_map[det_name] = c
            severities.append(sev)

        detector_count = len(detections)
        risk_vals = list(risk_map.values())
        conf_vals = list(conf_map.values())

        # Variance calculations
        mean_risk = sum(risk_vals) / float(detector_count)
        mean_conf = sum(conf_vals) / float(detector_count)

        if detector_count > 1:
            risk_var = sum((x - mean_risk) ** 2 for x in risk_vals) / float(detector_count - 1)
            conf_var = sum((x - mean_conf) ** 2 for x in conf_vals) / float(detector_count - 1)
            risk_range = max(risk_vals) - min(risk_vals)
        else:
            risk_var = 0.0
            conf_var = 0.0
            risk_range = 0.0

        # Categorical disagreement check (e.g. HIGH vs LOW)
        distinct_severities = set(severities)
        categorical_disagreement = len(distinct_severities) > 1 and ("HIGH" in distinct_severities or "CRITICAL" in distinct_severities) and ("LOW" in distinct_severities)

        # Composite disagreement score (0 to 1)
        # Normalize range (0-1) and variance
        disagreement_score = max(0.0, min(1.0, (risk_range * 0.70) + (math.sqrt(risk_var) * 0.30)))

        explanation_parts = []
        if risk_range > self.disagreement_threshold:
            explanation_parts.append(f"Significant risk range delta of {risk_range:.2f} across {detector_count} detectors.")
        if categorical_disagreement:
            explanation_parts.append(f"Categorical severity disagreement observed ({', '.join(distinct_severities)}).")
        if not explanation_parts:
            explanation_parts.append(f"Detectors show strong consensus with low risk range of {risk_range:.2f}.")

        dis_id = f"dis-{uuid.uuid4().hex[:12]}"
        return DetectorDisagreement(
            disagreement_id=dis_id,
            event_id=event_id,
            entity_id=entity_id,
            detector_count=detector_count,
            participating_detectors=detector_ids,
            risk_scores=risk_map,
            confidence_scores=conf_map,
            risk_variance=round(risk_var, 4),
            confidence_variance=round(conf_var, 4),
            categorical_disagreement=categorical_disagreement,
            disagreement_score=round(disagreement_score, 4),
            explanation=" ".join(explanation_parts),
            created_at=datetime.now(timezone.utc),
        )
