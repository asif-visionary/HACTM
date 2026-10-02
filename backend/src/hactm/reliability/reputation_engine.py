"""
Reliability & Trust Agent Reputation Engine.
Tracks time-aware operational reputation based on validated detections, FPR, FNR, calibration,
stability, drift, data quality, and evaluation coverage.
"""

import math
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from hactm.reliability.models import AgentReputation


class ReputationEngine:
    """Time-Aware Agent Reputation Engine for HACTM Reliability & Trust."""

    def calculate_reputation(
        self,
        agent_id: str,
        historical_precision: float = 0.85,
        historical_recall: float = 0.80,
        stability_score: float = 1.0,
        calibration_score: float = 0.90,
        drift_score: float = 0.0,
        coverage_score: float = 1.0,
        evaluation_count: int = 10,
        previous_reputation: Optional[AgentReputation] = None,
        reputation_version: str = "1.0.0",
    ) -> AgentReputation:
        """
        Calculates time-aware, non-static agent reputation score.
        """
        now = datetime.now(timezone.utc)

        # Base performance score from precision, recall, stability, calibration, coverage
        base_rep = (
            0.30 * historical_precision
            + 0.25 * historical_recall
            + 0.15 * stability_score
            + 0.15 * calibration_score
            + 0.15 * coverage_score
            - 0.20 * drift_score
        )
        base_rep = max(0.05, min(0.99, base_rep))

        # Time-aware smoothing with previous reputation if present
        if previous_reputation:
            # Exponential smoothing factor alpha = 0.30
            alpha = 0.30
            smoothed_score = alpha * base_rep + (1.0 - alpha) * previous_reputation.reputation_score
        else:
            smoothed_score = base_rep

        smoothed_score = max(0.05, min(0.99, round(smoothed_score, 4)))

        # Confidence Interval calculation on reputation
        ci_spread = max(0.05, 0.30 / math.sqrt(max(1, evaluation_count)))
        lower_ci = max(0.0, round(smoothed_score - ci_spread, 4))
        upper_ci = min(1.0, round(smoothed_score + ci_spread, 4))

        rep_id = previous_reputation.agent_id if previous_reputation else agent_id

        return AgentReputation(
            agent_id=agent_id,
            reputation_score=smoothed_score,
            historical_precision=round(historical_precision, 4),
            historical_recall=round(historical_recall, 4),
            stability_score=round(stability_score, 4),
            calibration_score=round(calibration_score, 4),
            drift_score=round(drift_score, 4),
            coverage_score=round(coverage_score, 4),
            last_evaluated_at=now,
            evaluation_count=evaluation_count,
            confidence_interval_lower=lower_ci,
            confidence_interval_upper=upper_ci,
            reputation_version=reputation_version,
            created_at=previous_reputation.created_at if previous_reputation else now,
            updated_at=now,
        )
