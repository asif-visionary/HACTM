"""
Feedback Validation & Quality Assessment Engine for HACTM Closed-Loop Adaptation.
Calculates trust levels, multi-dimensional quality scores, conflict detection, and retractions.
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
import math

from hactm.feedback.models import (
    FeedbackSourceType,
    FeedbackTrustLevel,
    FeedbackQuality,
    ValidationStatus,
    FeedbackEvent,
)


class FeedbackValidator:
    """Validator for determining trust level, multi-dimensional quality score, and conflicts."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.min_usable_quality = self.config.get("min_usable_quality_score", 0.60)

    def determine_trust_level(self, source_type: FeedbackSourceType) -> FeedbackTrustLevel:
        """Maps feedback source type to trust level."""
        if source_type == FeedbackSourceType.GROUND_TRUTH_DATASET:
            return FeedbackTrustLevel.GROUND_TRUTH
        elif source_type in (
            FeedbackSourceType.CONTROLLED_EXPERIMENT,
            FeedbackSourceType.CONTROLLED_ATTACK_EXPERIMENT,
            FeedbackSourceType.SECURITY_TEST_ENVIRONMENT,
        ):
            return FeedbackTrustLevel.CONTROLLED_EXPERIMENT
        elif source_type in (
            FeedbackSourceType.ANALYST_VALIDATION,
            FeedbackSourceType.INCIDENT_INVESTIGATION,
        ):
            return FeedbackTrustLevel.ANALYST_CONFIRMED
        elif source_type in (
            FeedbackSourceType.SUCCESSFUL_2FA,
            FeedbackSourceType.FAILED_2FA,
            FeedbackSourceType.CONFIRMED_PHISHING_REPORT,
            FeedbackSourceType.CONFIRMED_ACCOUNT_COMPROMISE,
            FeedbackSourceType.CONFIRMED_TRANSACTION_FRAUD,
            FeedbackSourceType.CONFIRMED_NETWORK_ATTACK,
            FeedbackSourceType.VERIFIED_POLICY_VIOLATION,
        ):
            return FeedbackTrustLevel.MULTI_SOURCE_VALIDATED
        else:
            return FeedbackTrustLevel.UNRESOLVED

    def calculate_quality(
        self,
        source_type: FeedbackSourceType,
        validation_status: ValidationStatus,
        evidence_count: int,
        delay_seconds: float,
        independent_sources_count: int = 1,
        reproducible: bool = True,
    ) -> FeedbackQuality:
        """Calculates multi-dimensional feedback quality score."""
        # 1. Source reliability
        source_rel_map = {
            FeedbackSourceType.GROUND_TRUTH_DATASET: 1.0,
            FeedbackSourceType.CONTROLLED_EXPERIMENT: 0.95,
            FeedbackSourceType.ANALYST_VALIDATION: 0.85,
            FeedbackSourceType.INCIDENT_INVESTIGATION: 0.90,
            FeedbackSourceType.SUCCESSFUL_2FA: 0.80,
            FeedbackSourceType.FAILED_2FA: 0.80,
            FeedbackSourceType.CONFIRMED_PHISHING_REPORT: 0.90,
            FeedbackSourceType.CONFIRMED_ACCOUNT_COMPROMISE: 0.95,
            FeedbackSourceType.CONFIRMED_TRANSACTION_FRAUD: 0.95,
            FeedbackSourceType.CONFIRMED_NETWORK_ATTACK: 0.90,
            FeedbackSourceType.VERIFIED_POLICY_VIOLATION: 0.85,
        }
        source_reliability = source_rel_map.get(source_type, 0.50)

        # 2. Validation strength
        status_val_map = {
            ValidationStatus.GROUND_TRUTH_CONFIRMED: 1.0,
            ValidationStatus.ANALYST_CONFIRMED: 0.90,
            ValidationStatus.VALIDATED_TRUE_POSITIVE: 0.85,
            ValidationStatus.VALIDATED_FALSE_POSITIVE: 0.85,
            ValidationStatus.VALIDATED_TRUE_NEGATIVE: 0.85,
            ValidationStatus.VALIDATED_FALSE_NEGATIVE: 0.85,
            ValidationStatus.PARTIALLY_VALIDATED: 0.60,
            ValidationStatus.PENDING: 0.30,
            ValidationStatus.UNRESOLVED: 0.20,
            ValidationStatus.FEEDBACK_CONFLICT: 0.10,
            ValidationStatus.RETRACTED: 0.0,
        }
        validation_strength = status_val_map.get(validation_status, 0.30)

        # 3. Evidence completeness (capped at 5 items for max score 1.0)
        evidence_completeness = min(1.0, 0.40 + (evidence_count * 0.12))

        # 4. Temporal proximity (exponential decay based on delay)
        half_life_seconds = 86400.0  # 24 hours
        temporal_proximity = math.exp(-0.693 * (delay_seconds / half_life_seconds))
        temporal_proximity = max(0.1, min(1.0, temporal_proximity))

        # 5. Independence
        independence = min(1.0, 0.50 + (independent_sources_count * 0.25))

        # 6. Consistency & Reproducibility
        consistency = 0.90 if validation_status != ValidationStatus.FEEDBACK_CONFLICT else 0.20
        reproducibility = 1.0 if reproducible else 0.50

        # Weighted aggregate score
        quality_score = (
            (0.25 * source_reliability)
            + (0.25 * validation_strength)
            + (0.15 * evidence_completeness)
            + (0.15 * temporal_proximity)
            + (0.10 * independence)
            + (0.05 * consistency)
            + (0.05 * reproducibility)
        )

        return FeedbackQuality(
            source_reliability=round(source_reliability, 4),
            validation_strength=round(validation_strength, 4),
            evidence_completeness=round(evidence_completeness, 4),
            temporal_proximity=round(temporal_proximity, 4),
            independence=round(independence, 4),
            consistency=round(consistency, 4),
            reproducibility=round(reproducibility, 4),
            feedback_quality_score=round(quality_score, 4),
        )

    def is_usable_feedback(
        self, quality: FeedbackQuality, trust_level: FeedbackTrustLevel, min_threshold: Optional[float] = None
    ) -> bool:
        """Determines if feedback meets requirements for learning updates."""
        threshold = min_threshold or self.min_usable_quality
        if trust_level == FeedbackTrustLevel.UNRESOLVED:
            return False
        return quality.feedback_quality_score >= threshold

    def detect_conflict(self, feedbacks: List[FeedbackEvent]) -> Tuple[bool, Optional[str]]:
        """Detects if multiple feedbacks for the same decision conflict (e.g. TP vs FP)."""
        if len(feedbacks) < 2:
            return False, None

        outcomes = set()
        for fb in feedbacks:
            obs = fb.details.get("observed_outcome")
            if obs:
                outcomes.add(obs)

        if len(outcomes) > 1:
            return True, f"Conflicting observed outcomes reported across feedback: {list(outcomes)}"
        return False, None
