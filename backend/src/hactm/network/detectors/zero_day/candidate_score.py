"""
Zero-Day Candidate Score, Agent Disagreement Tracker, and Zero-Day Escalation Policy for HACTM.

Implements HACTM design mechanisms for unknown attack candidate evaluation, cross-agent disagreement tracking,
and controlled zero-day escalation policy mapping.
"""

import math
import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ZeroDayCandidateScoreConfig(BaseModel):
    """Configuration weights for ZeroDayCandidateScore."""
    w1_anomaly_score: float = 0.25
    w2_uncertainty: float = 0.20
    w3_novelty: float = 0.15
    w4_temporal_deviation: float = 0.15
    w5_contextual_deviation: float = 0.10
    w6_agent_disagreement: float = 0.15


class ZeroDayCandidateResult(BaseModel):
    """Structured Zero-Day Candidate Score breakdown."""
    event_id: str
    candidate_score: float = Field(..., ge=0.0, le=1.0)
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    uncertainty: float = Field(..., ge=0.0, le=1.0)
    novelty_indicator: float = Field(..., ge=0.0, le=1.0)
    temporal_deviation: float = Field(..., ge=0.0, le=1.0)
    contextual_deviation: float = Field(..., ge=0.0, le=1.0)
    agent_disagreement: float = Field(..., ge=0.0, le=1.0)
    weights_used: Dict[str, float]
    zero_day_category: str = "protocol_network_stack" # Taxonomy metadata


class AgentDisagreementResult(BaseModel):
    """Structured metrics for cross-agent disagreement."""
    mean_score: float
    variance: float
    max_min_difference: float
    entropy: float
    pairwise_disagreement: float
    confidence_weighted_disagreement: float
    agent_count: int


class AgentDisagreementTracker:
    """Calculates cross-agent disagreement features to feed into HACTM evidence fusion."""

    @staticmethod
    def calculate(agent_scores: List[Dict[str, Any]]) -> AgentDisagreementResult:
        """
        agent_scores format:
        [
            {"agent_id": "network", "score": 0.88, "confidence": 0.90},
            {"agent_id": "uba", "score": 0.21, "confidence": 0.70},
            ...
        ]
        """
        if not agent_scores:
            return AgentDisagreementResult(
                mean_score=0.0,
                variance=0.0,
                max_min_difference=0.0,
                entropy=0.0,
                pairwise_disagreement=0.0,
                confidence_weighted_disagreement=0.0,
                agent_count=0
            )

        scores = [float(a.get("score", 0.0)) for a in agent_scores]
        confidences = [float(a.get("confidence", 1.0)) for a in agent_scores]
        n = len(scores)

        mean_val = float(np.mean(scores))
        var_val = float(np.var(scores))
        max_min_diff = float(max(scores) - min(scores))

        # Categorical entropy approximation across 5 score bins [0-0.2, 0.2-0.4, ...]
        bins = [0] * 5
        for s in scores:
            bin_idx = min(4, int(s * 5))
            bins[bin_idx] += 1
        probs = [b / n for b in bins if b > 0]
        entropy_val = float(-sum(p * math.log2(p) for p in probs))

        # Pairwise mean absolute disagreement
        if n > 1:
            pairwise_sum = sum(abs(scores[i] - scores[j]) for i in range(n) for j in range(i + 1, n))
            pairwise_dis = float(pairwise_sum / (n * (n - 1) / 2.0))
        else:
            pairwise_dis = 0.0

        # Confidence-weighted disagreement
        weighted_diffs = []
        for i in range(n):
            for j in range(i + 1, n):
                weight = confidences[i] * confidences[j]
                diff = abs(scores[i] - scores[j])
                weighted_diffs.append(weight * diff)
        
        cw_dis = float(np.mean(weighted_diffs)) if weighted_diffs else 0.0

        return AgentDisagreementResult(
            mean_score=round(mean_val, 4),
            variance=round(var_val, 4),
            max_min_difference=round(max_min_diff, 4),
            entropy=round(entropy_val, 4),
            pairwise_disagreement=round(pairwise_dis, 4),
            confidence_weighted_disagreement=round(cw_dis, 4),
            agent_count=n
        )


class ZeroDayCandidateScoreCalculator:
    """Computes composite HACTM Zero-Day Candidate Score (Z)."""

    def __init__(self, config: Optional[ZeroDayCandidateScoreConfig] = None):
        self.config = config or ZeroDayCandidateScoreConfig()

    def calculate(
        self,
        event_id: str,
        anomaly_score: float,
        uncertainty: float,
        novelty_indicator: float,
        temporal_deviation: float,
        contextual_deviation: float,
        agent_disagreement: float,
        zero_day_category: str = "protocol_network_stack"
    ) -> ZeroDayCandidateResult:
        cfg = self.config
        
        # Linear combination of design components
        raw_z = (
            cfg.w1_anomaly_score * anomaly_score +
            cfg.w2_uncertainty * uncertainty +
            cfg.w3_novelty * novelty_indicator +
            cfg.w4_temporal_deviation * temporal_deviation +
            cfg.w5_contextual_deviation * contextual_deviation +
            cfg.w6_agent_disagreement * agent_disagreement
        )
        total_weights = (
            cfg.w1_anomaly_score + cfg.w2_uncertainty + cfg.w3_novelty +
            cfg.w4_temporal_deviation + cfg.w5_contextual_deviation + cfg.w6_agent_disagreement
        )
        
        z_norm = raw_z / total_weights if total_weights > 0 else 0.0
        candidate_score = max(0.0, min(1.0, float(z_norm)))

        return ZeroDayCandidateResult(
            event_id=event_id,
            candidate_score=round(candidate_score, 4),
            anomaly_score=round(anomaly_score, 4),
            uncertainty=round(uncertainty, 4),
            novelty_indicator=round(novelty_indicator, 4),
            temporal_deviation=round(temporal_deviation, 4),
            contextual_deviation=round(contextual_deviation, 4),
            agent_disagreement=round(agent_disagreement, 4),
            weights_used={
                "w1_anomaly_score": cfg.w1_anomaly_score,
                "w2_uncertainty": cfg.w2_uncertainty,
                "w3_novelty": cfg.w3_novelty,
                "w4_temporal_deviation": cfg.w4_temporal_deviation,
                "w5_contextual_deviation": cfg.w5_contextual_deviation,
                "w6_agent_disagreement": cfg.w6_agent_disagreement
            },
            zero_day_category=zero_day_category
        )


class ZeroDayEscalationPolicy:
    """
    Controlled zero-day candidate escalation mechanism mapping risk, uncertainty,
    and candidate score to dynamic Zero-Trust response actions.
    """

    @staticmethod
    def evaluate_escalation(
        candidate_result: ZeroDayCandidateResult,
        known_class_confidence: float,
        entity_criticality: float = 0.50,
        policy_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        z_score = candidate_result.candidate_score
        unc = candidate_result.uncertainty
        
        # Policy rules: ALLOW, MONITOR, VERIFY, 2FA, RESTRICT, QUARANTINE, BLOCK
        action = "ALLOW"
        reason = "Low anomaly and low zero-day candidate score."

        if z_score >= 0.85 and entity_criticality >= 0.70:
            action = "QUARANTINE"
            reason = "Critical asset zero-day candidate detected with extreme novelty and high candidate score."
        elif z_score >= 0.80:
            action = "BLOCK" if unc < 0.40 else "RESTRICT"
            reason = f"High zero-day candidate score ({z_score:.2f}). Action determined by uncertainty level ({unc:.2f})."
        elif z_score >= 0.65:
            action = "RESTRICT" if entity_criticality >= 0.50 else "2FA"
            reason = f"Moderate-high zero-day candidate score ({z_score:.2f}). Mandatory identity re-verification."
        elif z_score >= 0.45 or unc > 0.50:
            action = "VERIFY"
            reason = f"Elevated uncertainty or candidate score. Triggering additional security agent investigation."
        elif z_score >= 0.25:
            action = "MONITOR"
            reason = "Slight anomaly observed. Enabling enhanced telemetry logging."

        return {
            "event_id": candidate_result.event_id,
            "action": action,
            "reason": reason,
            "candidate_score": z_score,
            "uncertainty": unc,
            "known_class_confidence": known_class_confidence,
            "entity_criticality": entity_criticality,
            "zero_day_category": candidate_result.zero_day_category,
            "escalation_triggered": action in ["VERIFY", "2FA", "RESTRICT", "QUARANTINE", "BLOCK"]
        }
