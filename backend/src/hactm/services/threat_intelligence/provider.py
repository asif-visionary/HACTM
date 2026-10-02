"""
Abstract Threat Intelligence Provider Interface and Normalized Result Schema.
Defines ThreatIntelligenceProvider ABC and NormalizedThreatIntelResult schema for HACTM.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class NormalizedThreatIntelResult(BaseModel):
    """Normalized internal representation of external threat intelligence IP reputation."""
    provider: str = "abuseipdb"
    indicator_type: str = "ip"
    indicator: str
    abuse_confidence_score: float = Field(default=0.0, ge=0.0, le=100.0)
    total_reports: int = 0
    country_code: Optional[str] = None
    usage_type: Optional[str] = None
    isp: Optional[str] = None
    domain: Optional[str] = None
    last_reported_at: Optional[str] = None
    is_whitelisted: bool = False
    source_reliability: float = Field(default=0.85, ge=0.0, le=1.0)
    uncertainty: float = Field(default=0.15, ge=0.0, le=1.0)
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "success"  # "success", "cached", "skipped_private_ip", "unconfigured", "unavailable"
    error_type: Optional[str] = None
    is_public_ip: bool = True
    raw_details: Optional[Dict[str, Any]] = None


class ThreatIntelligenceProvider(ABC):
    """Abstract Base Class for External Threat Intelligence Providers."""

    @abstractmethod
    def check_ip(self, ip_address: str, max_age_days: Optional[int] = None) -> NormalizedThreatIntelResult:
        """Queries IP reputation and returns normalized threat intelligence result."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Returns provider reachability and configuration status."""
        pass
