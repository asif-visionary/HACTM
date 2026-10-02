"""
AbuseIPDB Threat Intelligence API v2 Provider Implementation for HACTM.
Handles IP validation (RFC1918 filtering), API key authentication, HTTP GET queries,
caching, rate limiting, and failure isolation.
"""

import time
import json
import logging
import ipaddress
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from hactm.core.config import settings
from hactm.services.threat_intelligence.provider import ThreatIntelligenceProvider, NormalizedThreatIntelResult

logger = logging.getLogger("hactm.threat_intel.abuseipdb")


class AbuseIPDBService(ThreatIntelligenceProvider):
    """AbuseIPDB API v2 External Threat Intelligence Evidence Provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_age_days: Optional[int] = None,
        reliability: Optional[float] = None,
        cache_ttl_seconds: int = 86400  # 24 hours
    ):
        self.api_key = api_key if api_key is not None else settings.ABUSEIPDB_API_KEY
        self.base_url = (base_url or settings.ABUSEIPDB_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.ABUSEIPDB_API_TIMEOUT
        self.max_age_days = max_age_days or settings.ABUSEIPDB_MAX_AGE_DAYS
        self.reliability = reliability if reliability is not None else settings.ABUSEIPDB_RELIABILITY
        self.enabled = settings.ABUSEIPDB_ENABLED
        self.cache_ttl = cache_ttl_seconds

        # In-memory TTL cache: (ip, max_age_days) -> (NormalizedThreatIntelResult, cached_timestamp)
        self._cache: Dict[Tuple[str, int], Tuple[NormalizedThreatIntelResult, float]] = {}

        # Rate limiting state
        self._rate_limited_until: float = 0.0

    def is_public_ip(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """Validates IP address and checks if it is a public, routable IP."""
        try:
            ip_obj = ipaddress.ip_address(ip_address.strip())
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                return False, "PRIVATE_OR_RESERVED_IP"
            return True, None
        except ValueError:
            return False, "INVALID_IP_FORMAT"

    def check_ip(self, ip_address: str, max_age_days: Optional[int] = None) -> NormalizedThreatIntelResult:
        """Queries AbuseIPDB API for IP reputation evidence."""
        effective_max_age = max_age_days or self.max_age_days
        cache_key = (ip_address.strip(), effective_max_age)
        now = time.time()

        # 1. IP Validation & Private RFC1918 Filtering
        is_pub, reason = self.is_public_ip(ip_address)
        if not is_pub:
            logger.debug(f"Skipping AbuseIPDB lookup for non-public IP '{ip_address}': {reason}")
            return NormalizedThreatIntelResult(
                provider="abuseipdb",
                indicator_type="ip",
                indicator=ip_address,
                abuse_confidence_score=0.0,
                total_reports=0,
                source_reliability=1.0,
                uncertainty=0.0,
                status="skipped_private_ip",
                error_type=reason,
                is_public_ip=False
            )

        # 2. Check In-Memory TTL Cache
        if cache_key in self._cache:
            cached_res, cached_ts = self._cache[cache_key]
            if now - cached_ts < self.cache_ttl:
                logger.debug(f"AbuseIPDB cache hit for IP '{ip_address}'")
                res_copy = cached_res.model_copy()
                res_copy.status = "cached"
                return res_copy

        # 3. Check configuration and rate limiting status
        if not self.enabled:
            return NormalizedThreatIntelResult(
                provider="abuseipdb",
                indicator=ip_address,
                status="unconfigured",
                error_type="PROVIDER_DISABLED",
                source_reliability=self.reliability,
                uncertainty=1.0 - self.reliability
            )

        if not self.api_key or self.api_key.strip() == "":
            logger.warning("AbuseIPDB API key is not configured. Returning unconfigured status.")
            return NormalizedThreatIntelResult(
                provider="abuseipdb",
                indicator=ip_address,
                status="unconfigured",
                error_type="MISSING_API_KEY",
                source_reliability=self.reliability,
                uncertainty=1.0 - self.reliability
            )

        # Fallback to cache if currently rate-limited
        if now < self._rate_limited_until:
            if cache_key in self._cache:
                cached_res, _ = self._cache[cache_key]
                res_copy = cached_res.model_copy()
                res_copy.status = "cached"
                return res_copy
            return NormalizedThreatIntelResult(
                provider="abuseipdb",
                indicator=ip_address,
                status="unavailable",
                error_type="RATE_LIMITED",
                source_reliability=self.reliability,
                uncertainty=1.0 - self.reliability
            )

        # 4. Execute HTTP GET Request to AbuseIPDB v2 /check
        url = f"{self.base_url}/check?ipAddress={urllib.parse.quote(ip_address)}&maxAgeInDays={effective_max_age}&verbose=true"
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "Key": self.api_key
        })

        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                t1 = time.perf_counter()
                latency_ms = (t1 - t0) * 1000.0

                if response.status == 200:
                    body = json.loads(response.read().decode('utf-8'))
                    data = body.get("data", {})

                    abuse_score = float(data.get("abuseConfidenceScore", 0))
                    total_reports = int(data.get("totalReports", 0))
                    country = data.get("countryCode")
                    usage_type = data.get("usageType")
                    isp = data.get("isp")
                    domain = data.get("domain")
                    last_reported = data.get("lastReportedAt")
                    is_whitelisted = bool(data.get("isWhitelisted", False))

                    result = NormalizedThreatIntelResult(
                        provider="abuseipdb",
                        indicator_type="ip",
                        indicator=ip_address,
                        abuse_confidence_score=abuse_score,
                        total_reports=total_reports,
                        country_code=country,
                        usage_type=usage_type,
                        isp=isp,
                        domain=domain,
                        last_reported_at=last_reported,
                        is_whitelisted=is_whitelisted,
                        source_reliability=self.reliability,
                        uncertainty=round(float(1.0 - self.reliability), 4),
                        observed_at=datetime.now(timezone.utc).isoformat(),
                        status="success",
                        is_public_ip=True,
                        raw_details={
                            "latency_ms": round(latency_ms, 2),
                            "ip_version": data.get("ipVersion")
                        }
                    )

                    # Store in cache
                    self._cache[cache_key] = (result, now)
                    logger.info(f"AbuseIPDB lookup successful for '{ip_address}': abuse_score={abuse_score}, reports={total_reports} ({latency_ms:.1f}ms)")
                    return result

        except urllib.error.HTTPError as e:
            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000.0
            error_code = e.code

            if error_code == 429:
                self._rate_limited_until = now + 60.0  # 60s cooldown
                retry_after = e.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    self._rate_limited_until = now + float(retry_after)
                logger.warning(f"AbuseIPDB API Rate limit exceeded (429). Cooldown until {self._rate_limited_until}")
                error_type = "RATE_LIMITED"
            elif error_code in [401, 403]:
                logger.error(f"AbuseIPDB Authentication failure (HTTP {error_code}). Check API key.")
                error_type = "UNAUTHORIZED"
            elif error_code == 400:
                error_type = "BAD_REQUEST"
            else:
                error_type = f"HTTP_{error_code}"

            return NormalizedThreatIntelResult(
                provider="abuseipdb",
                indicator=ip_address,
                status="unconfigured" if error_code in [401, 403] else "unavailable",
                error_type=error_type,
                source_reliability=self.reliability,
                uncertainty=1.0 - self.reliability,
                raw_details={"http_code": error_code, "latency_ms": round(latency_ms, 2)}
            )

        except (urllib.error.URLError, TimeoutError, OSError) as e:
            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000.0
            logger.warning(f"AbuseIPDB connection error for '{ip_address}': {e}")
            return NormalizedThreatIntelResult(
                provider="abuseipdb",
                indicator=ip_address,
                status="unavailable",
                error_type="CONNECTION_FAILURE",
                source_reliability=self.reliability,
                uncertainty=1.0 - self.reliability,
                raw_details={"latency_ms": round(latency_ms, 2)}
            )

        return NormalizedThreatIntelResult(
            provider="abuseipdb",
            indicator=ip_address,
            status="unavailable",
            error_type="UNKNOWN_FAILURE",
            source_reliability=self.reliability,
            uncertainty=1.0 - self.reliability
        )

    def check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Convenience method returning raw dict schema required by API endpoint."""
        res = self.check_ip(ip_address)
        return res.model_dump()

    def get_status(self) -> Dict[str, Any]:
        """Returns AbuseIPDB health & configuration status."""
        configured = bool(self.api_key and self.api_key.strip())
        return {
            "provider": "abuseipdb",
            "enabled": self.enabled,
            "configured": configured,
            "reachable": configured and time.time() >= self._rate_limited_until,
            "base_url": self.base_url,
            "max_age_days": self.max_age_days,
            "reliability": self.reliability,
            "cached_entries": len(self._cache)
        }
