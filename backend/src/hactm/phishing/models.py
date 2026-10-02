"""
Phishing Intelligence Domain Data Models.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hactm.core.agent_base import SecurityDetectionResult
from hactm.core.constants import SeverityLevel


class AttachmentMetadata(BaseModel):
    filename: Optional[str] = None
    extension: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = Field(default=0, ge=0)
    hash: Optional[str] = None
    is_archive: bool = False
    is_double_extension: bool = False


class UrlFeature(BaseModel):
    url: str
    length: int = 0
    hostname_length: int = 0
    path_length: int = 0
    num_subdomains: int = 0
    num_query_params: int = 0
    is_ip_hostname: bool = False
    is_https: bool = False
    is_punycode: bool = False
    special_char_density: float = 0.0
    domain_mismatch: bool = False


class PhishingEmailEvent(BaseModel):
    message_id: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = ""
    body: Optional[str] = ""
    headers: Optional[Dict[str, Any]] = Field(default_factory=dict)
    urls: List[str] = Field(default_factory=list)
    attachments: List[AttachmentMetadata] = Field(default_factory=list)
    sender_domain: Optional[str] = None
    reply_to: Optional[str] = None
    return_path: Optional[str] = None
    authentication_results: Optional[Dict[str, Any]] = Field(default_factory=dict)  # spf, dkim, dmarc
    source_ip: Optional[str] = None


class PhishingDetectionResult(SecurityDetectionResult):
    """Phishing specific detection result wrapper."""
    def __init__(
        self,
        detection_id: str,
        event_id: str,
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
        is_spear_phishing: bool = False,
        is_bec: bool = False,
        matched_rules: Optional[List[str]] = None,
    ):
        super().__init__(
            detection_id=detection_id,
            event_id=event_id,
            agent_id="phishing-intelligence-agent",
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
            matched_rules=matched_rules,
        )
        self.is_spear_phishing = is_spear_phishing
        self.is_bec = is_bec
