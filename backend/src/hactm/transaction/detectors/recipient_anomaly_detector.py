"""
Recipient & Device Anomaly Detector for Transaction Security Agent.
"""

from typing import Any, Dict, Optional
from hactm.transaction.models import TransactionDetectionResult, TransactionEvent
from hactm.core.constants import risk_score_to_severity


class RecipientAnomalyDetector:
    """Detects new recipient combined with unusual amount or unseen device."""

    def __init__(self, version: str = "1.0.0"):
        self.detector_id = "transaction-recipient-detector"
        self.version = version

    def detect(self, event: TransactionEvent, features: Dict[str, Any]) -> Optional[TransactionDetectionResult]:
        is_new_recip = features.get("is_new_recipient", False)
        is_new_dev = features.get("is_new_device", False)
        ratio = features.get("amount_ratio", 1.0)

        if not is_new_recip:
            return None

        reason_codes = ["TRANSACTION_NEW_RECIPIENT_OBSERVED"]
        explanation_parts = [f"Transfer to new recipient '{event.recipient_id or event.destination_account}'"]
        score = 0.30

        if ratio >= 2.5:
            score += 0.35
            reason_codes.append("TRANSACTION_NEW_RECIPIENT_HIGH_AMOUNT")
            explanation_parts.append(f"Elevated amount ratio ({ratio:.1f}x median) toward new recipient")

        if is_new_dev:
            score += 0.25
            reason_codes.append("TRANSACTION_NEW_DEVICE_AND_RECIPIENT")
            explanation_parts.append("Transaction initiated from new/unrecognized device")

        if score < 0.40:
            return None

        risk_score = min(1.0, score)
        confidence = 0.82
        uncertainty = round(1.0 - confidence, 4)

        return TransactionDetectionResult(
            detection_id=f"det_tx_recip_{event.transaction_id}",
            event_id=event.transaction_id,
            account_id=event.account_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="RECIPIENT_NOVELTY_ANOMALY",
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(risk_score).value,
            explanation="; ".join(explanation_parts),
            features_used={
                "is_new_recipient": is_new_recip,
                "is_new_device": is_new_dev,
                "amount_ratio": ratio,
            },
            detector_version=self.version,
            reason_codes=reason_codes,
        )
