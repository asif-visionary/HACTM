"""
Threat Intelligence Service for HACTM.
Unified coordinator managing external threat intelligence providers (AbuseIPDB),
caching, normalization, and SecurityEvidence conversion.
"""

import logging
from typing import Dict, Any, List, Optional

from hactm.core.models import SecurityEvidence
from hactm.services.threat_intelligence.provider import ThreatIntelligenceProvider, NormalizedThreatIntelResult
from hactm.services.threat_intelligence.abuseipdb_service import AbuseIPDBService
from hactm.services.threat_intelligence.evidence_mapper import ThreatIntelEvidenceMapper

logger = logging.getLogger("hactm.threat_intel")


class ThreatIntelligenceService:
    """Unified Threat Intelligence Service managing AbuseIPDB and external evidence providers."""

    def __init__(self, abuseipdb_service: Optional[AbuseIPDBService] = None):
        self.abuseipdb = abuseipdb_service or AbuseIPDBService()
        self._providers: Dict[str, ThreatIntelligenceProvider] = {
            "abuseipdb": self.abuseipdb
        }

    def register_provider(self, name: str, provider: ThreatIntelligenceProvider) -> None:
        """Extensible registry for future external threat intelligence providers."""
        self._providers[name] = provider
        logger.info(f"Registered threat intelligence provider: {name}")

    def check_ip(self, ip_address: str, provider_name: str = "abuseipdb", max_age_days: Optional[int] = None) -> NormalizedThreatIntelResult:
        """Queries specified threat intelligence provider for IP reputation."""
        provider = self._providers.get(provider_name.lower())
        if not provider:
            logger.warning(f"Unknown threat intelligence provider '{provider_name}'. Falling back to AbuseIPDB.")
            provider = self.abuseipdb

        return provider.check_ip(ip_address, max_age_days=max_age_days)

    def get_ip_reputation(self, ip_address: str, max_age_days: Optional[int] = None) -> Dict[str, Any]:
        """Queries AbuseIPDB reputation and returns dictionary schema for API endpoint."""
        res = self.check_ip(ip_address, provider_name="abuseipdb", max_age_days=max_age_days)
        return res.model_dump()

    def get_ip_evidence(self, ip_address: str, entity_id: Optional[str] = None) -> SecurityEvidence:
        """Queries AbuseIPDB and converts normalized result into canonical SecurityEvidence."""
        norm_res = self.check_ip(ip_address, provider_name="abuseipdb")
        return ThreatIntelEvidenceMapper.to_security_evidence(norm_res, entity_id=entity_id)

    def get_status(self) -> Dict[str, Any]:
        """Returns configuration and reachability health check for all registered providers."""
        statuses = {}
        for name, provider in self._providers.items():
            statuses[name] = provider.get_status()
        return statuses
