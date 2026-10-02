"""
Transaction Security Data Models.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hactm.core.agent_base import SecurityDetectionResult


class TransactionEvent(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    account_id: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    amount: float
    currency: str = Field(default="USD")
    merchant_id: Optional[str] = None
    merchant_category: Optional[str] = None
    recipient_id: Optional[str] = None
    source_account: Optional[str] = None
    destination_account: Optional[str] = None
    transaction_type: str = Field(default="PAYMENT")  # PAYMENT, TRANSFER, REFUND, CHARGEBACK, CANCEL
    channel: Optional[str] = Field(default="WEB")
    location: Optional[Dict[str, Any]] = None
    status: str = Field(default="COMPLETED")


class TransactionDetectionResult(SecurityDetectionResult):
    """Transaction specific detection result wrapper."""
    def __init__(
        self,
        detection_id: str,
        event_id: str,
        account_id: str,
        detector_type: str,
        detector_id: str,
        category: str,
        risk_score: float,
        confidence: float,
        uncertainty: float,
        severity: str,
        explanation: str,
        features_used: Dict[str, Any],
        detector_version: str = "1.0.0",
        reason_codes: Optional[List[str]] = None,
        model_version: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        processing_time_ms: float = 0.0,
    ):
        super().__init__(
            detection_id=detection_id,
            event_id=event_id,
            agent_id="transaction-security-agent",
            detector_type=detector_type,
            detector_id=detector_id,
            category=category,
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=severity,
            explanation=explanation,
            features_used=features_used,
            detector_version=detector_version,
            reason_codes=reason_codes,
            model_version=model_version,
            timestamp=timestamp,
            processing_time_ms=processing_time_ms,
        )
        self.account_id = account_id
