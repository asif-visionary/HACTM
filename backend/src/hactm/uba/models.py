"""
User Behavior Analytics (UBA) Data Models.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hactm.core.agent_base import SecurityDetectionResult


class UbaEvent(BaseModel):
    event_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    source_ip: Optional[str] = None
    action: str = Field(default="access")
    resource: Optional[str] = None
    resource_type: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = Field(default=0, ge=0)
    application: Optional[str] = None
    authentication_status: Optional[str] = "SUCCESS"
    privilege_level: Optional[str] = "USER"
    location: Optional[str] = None
    bytes_transferred: Optional[int] = Field(default=0, ge=0)
    peer_group: Optional[str] = None


class UserProfile(BaseModel):
    user_id: str
    peer_group: Optional[str] = None
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_count: int = 0
    normal_login_hours: List[int] = Field(default_factory=list)
    known_devices: List[str] = Field(default_factory=list)
    known_ips: List[str] = Field(default_factory=list)
    known_applications: List[str] = Field(default_factory=list)
    typical_resources: List[str] = Field(default_factory=list)
    avg_bytes_transferred: float = 0.0
    max_bytes_transferred: float = 0.0
    is_insufficient_baseline: bool = True


class UbaDetectionResult(SecurityDetectionResult):
    """UBA specific detection result wrapper."""
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
        is_insufficient_baseline: bool = False,
    ):
        super().__init__(
            detection_id=detection_id,
            event_id=event_id,
            agent_id="uba-agent",
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
        self.is_insufficient_baseline = is_insufficient_baseline
