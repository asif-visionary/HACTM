"""
Velocity Detector for Transaction Security Agent.
"""

from typing import Any, Dict, Optional
from hactm.transaction.models import TransactionDetectionResult, TransactionEvent
from hactm.core.constants import risk_score_to_severity


class VelocityDetector:
    """Detects rapid transaction velocity anomalies within short time windows."""

    def __init__(self, max_threshold: int = 5, version: str = "1.0.0"):
        self.detector_id = "transaction-velocity-detector"
        self.version = version
        self.max_threshold = max_threshold

    def detect(self, event: TransactionEvent, features: Dict[str, Any]) -> Optional[TransactionDetectionResult]:
        vel_cnt = features.get("recent_velocity_count", 0)
        if vel_cnt < self.max_threshold:
            return None

        score = min(1.0, 0.45 + min(0.50, (vel_cnt - self.max_threshold) * 0.10))
        confidence = 0.88
        uncertainty = round(1.0 - confidence, 4)

        return TransactionDetectionResult(
            detection_id=f"det_tx_vel_{event.transaction_id}",
            event_id=event.transaction_id,
            account_id=event.account_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="TRANSACTION_VELOCITY_ANOMALY",
            risk_score=score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(score).value,
            explanation=f"Transaction velocity anomaly: {vel_cnt} rapid transactions executed within 2-minute window for account '{event.account_id}'",
            features_used={
                "recent_velocity_count": vel_cnt,
                "velocity_threshold": self.max_threshold,
            },
            detector_version=self.version,
            reason_codes=["TRANSACTION_HIGH_VELOCITY_BURST"],
        )
