"""
Identity & Authentication Security Data Models.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hactm.core.agent_base import SecurityDetectionResult


class IdentityEvent(BaseModel):
    authentication_event_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str = Field(..., min_length=1)
    account_id: Optional[str] = None
    device_id: Optional[str] = None
    source_ip: Optional[str] = None
    location: Optional[Dict[str, Any]] = None  # e.g., {"lat": 37.77, "lon": -122.41, "country": "US", "city": "SF"}
    authentication_method: str = Field(default="PASSWORD")
    authentication_status: str = Field(default="SUCCESS")  # SUCCESS, FAILED
    failure_reason: Optional[str] = None
    two_factor_used: Optional[str] = None  # OTP, APP, KEY, NONE
    two_factor_result: Optional[str] = None  # SUCCESS, FAILED, TIMEOUT, BYPASS, UNAVAILABLE
    session_id: Optional[str] = None
    biometric_verification_result: Optional[str] = None  # verified, failed, not_available (metadata only)
    device_fingerprint: Optional[str] = None


class IdentityDetectionResult(SecurityDetectionResult):
    """Identity specific detection result wrapper."""
    def __init__(
        self,
        detection_id: str,
        event_id: str,
        user_id: str,
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
            agent_id="identity-authentication-agent",
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
        self.user_id = user_id
