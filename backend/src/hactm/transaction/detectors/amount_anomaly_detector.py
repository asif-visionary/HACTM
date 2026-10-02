"""
Amount Anomaly Detector for Transaction Security Agent.
"""

from typing import Any, Dict, Optional
from hactm.transaction.models import TransactionDetectionResult, TransactionEvent
from hactm.core.constants import risk_score_to_severity


class AmountAnomalyDetector:
    """Detects transaction amount deviations vs historical account baseline."""

    def __init__(self, zscore_threshold: float = 3.0, version: str = "1.0.0"):
        self.detector_id = "transaction-amount-detector"
        self.version = version
        self.zscore_threshold = zscore_threshold

    def detect(self, event: TransactionEvent, features: Dict[str, Any]) -> Optional[TransactionDetectionResult]:
        ratio = features.get("amount_ratio", 1.0)
        z_score = features.get("z_score", 0.0)
        hist_count = features.get("history_count", 0)

        # Requires minimum 3 historical transactions for accurate statistical baseline
        if hist_count < 3:
            if event.amount > 10_000.0:
                score = 0.50
                return TransactionDetectionResult(
                    detection_id=f"det_tx_amt_{event.transaction_id}",
                    event_id=event.transaction_id,
                    account_id=event.account_id,
                    detector_type="STATISTICAL",
                    detector_id=self.detector_id,
                    category="HIGH_VALUE_INITIAL_TRANSACTION",
                    risk_score=score,
                    confidence=0.60,
                    uncertainty=0.40,
                    severity=risk_score_to_severity(score).value,
                    explanation=f"High-value initial transaction ({event.currency} {event.amount:,.2f}) on account with sparse history",
                    features_used={"amount": event.amount, "history_count": hist_count},
                    detector_version=self.version,
                    reason_codes=["TRANSACTION_HIGH_INITIAL_VALUE"],
                )
            return None

        if ratio < 3.5 and z_score < self.zscore_threshold:
            return None

        score = min(1.0, 0.40 + min(0.55, (ratio / 10.0)))
        confidence = 0.86
        uncertainty = round(1.0 - confidence, 4)

        return TransactionDetectionResult(
            detection_id=f"det_tx_amt_{event.transaction_id}",
            event_id=event.transaction_id,
            account_id=event.account_id,
            detector_type="STATISTICAL",
            detector_id=self.detector_id,
            category="TRANSACTION_AMOUNT_ANOMALY",
            risk_score=score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(score).value,
            explanation=f"Transaction amount ({event.currency} {event.amount:,.2f}) is {ratio:.1f}x above historical account median",
            features_used={
                "amount": event.amount,
                "amount_median": features.get("amount_median"),
                "amount_ratio": ratio,
                "z_score": z_score,
            },
            detector_version=self.version,
            reason_codes=["TRANSACTION_AMOUNT_DEVIATION_HIGH"],
        )
