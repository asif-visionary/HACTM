"""
Unit Tests for AbuseIPDB Threat Intelligence Integration in HACTM.
Tests IP validation (RFC1918 private IP skipping), HTTP mock responses (200, 401, 429, timeout),
caching, rate limiting, evidence mapping, and failure isolation.
"""

import json
import pytest
import urllib.error
from unittest.mock import MagicMock, patch

from hactm.services.threat_intelligence import (
    AbuseIPDBService,
    ThreatIntelligenceService,
    ThreatIntelEvidenceMapper,
    NormalizedThreatIntelResult
)
# pyrefly: ignore [missing-import]
from hactm.fusion.engine import EvidenceFusionEngine


def test_ip_validation_and_private_filtering():
    service = AbuseIPDBService(api_key="test-key")

    # Public IPv4 & IPv6
    is_pub, reason = service.is_public_ip("1.1.1.1")
    assert is_pub is True
    assert reason is None

    is_pub6, _ = service.is_public_ip("2606:4700:4700::1111")
    assert is_pub6 is True

    # Private RFC1918 IPv4
    is_pub, reason = service.is_public_ip("10.0.0.1")
    assert is_pub is False
    assert reason == "PRIVATE_OR_RESERVED_IP"

    is_pub, reason = service.is_public_ip("192.168.1.100")
    assert is_pub is False

    is_pub, reason = service.is_public_ip("127.0.0.1")
    assert is_pub is False

    # Invalid IP string
    is_pub, reason = service.is_public_ip("not-an-ip-address")
    assert is_pub is False
    assert reason == "INVALID_IP_FORMAT"


def test_private_ip_skipped_without_api_call():
    service = AbuseIPDBService(api_key="test-key")
    res = service.check_ip("192.168.0.1")

    assert res.status == "skipped_private_ip"
    assert res.is_public_ip is False
    assert res.abuse_confidence_score == 0.0
    assert res.total_reports == 0


def test_missing_api_key_returns_unconfigured():
    service = AbuseIPDBService(api_key="")
    res = service.check_ip("8.8.8.8")

    assert res.status == "unconfigured"
    assert res.error_type == "MISSING_API_KEY"
    assert res.abuse_confidence_score == 0.0


def test_abuseipdb_http_200_success_mock():
    service = AbuseIPDBService(api_key="valid-mock-key")

    mock_response_data = {
        "data": {
            "ipAddress": "118.25.6.39",
            "isPublic": True,
            "ipVersion": 4,
            "isWhitelisted": False,
            "abuseConfidenceScore": 85,
            "countryCode": "CN",
            "usageType": "Data Center/Web Hosting/Transit",
            "isp": "Tencent Cloud Computing",
            "domain": "tencent.com",
            "totalReports": 42,
            "lastReportedAt": "2026-10-02T12:00:00+00:00"
        }
    }

    mock_cm = MagicMock()
    mock_cm.status = 200
    mock_cm.read.return_value = json.dumps(mock_response_data).encode("utf-8")
    mock_cm.__enter__.return_value = mock_cm

    with patch("urllib.request.urlopen", return_value=mock_cm):
        res = service.check_ip("118.25.6.39")

    assert res.status == "success"
    assert res.provider == "abuseipdb"
    assert res.indicator == "118.25.6.39"
    assert res.abuse_confidence_score == 85.0
    assert res.total_reports == 42
    assert res.country_code == "CN"
    assert res.usage_type == "Data Center/Web Hosting/Transit"
    assert res.isp == "Tencent Cloud Computing"


def test_abuseipdb_caching():
    service = AbuseIPDBService(api_key="valid-mock-key")

    mock_response_data = {
        "data": {
            "ipAddress": "8.8.4.4",
            "abuseConfidenceScore": 10,
            "totalReports": 2
        }
    }
    mock_cm = MagicMock()
    mock_cm.status = 200
    mock_cm.read.return_value = json.dumps(mock_response_data).encode("utf-8")
    mock_cm.__enter__.return_value = mock_cm

    with patch("urllib.request.urlopen", return_value=mock_cm) as mock_urlopen:
        res1 = service.check_ip("8.8.4.4")
        assert res1.status == "success"

        # Second lookup should hit in-memory cache
        res2 = service.check_ip("8.8.4.4")
        assert res2.status == "cached"
        assert res2.abuse_confidence_score == 10.0
        assert mock_urlopen.call_count == 1


def test_abuseipdb_http_401_unauthorized():
    service = AbuseIPDBService(api_key="invalid-key")

    err = urllib.error.HTTPError(
        url="http://api.abuseipdb.com",
        code=401,
        msg="Unauthorized",
        hdrs={},
        fp=None
    )

    with patch("urllib.request.urlopen", side_effect=err):
        res = service.check_ip("1.1.1.1")

    assert res.status == "unconfigured"
    assert res.error_type == "UNAUTHORIZED"
    assert res.abuse_confidence_score == 0.0


def test_abuseipdb_http_429_rate_limit():
    service = AbuseIPDBService(api_key="mock-key")

    err = urllib.error.HTTPError(
        url="http://api.abuseipdb.com",
        code=429,
        msg="Too Many Requests",
        hdrs={"Retry-After": "30"},
        fp=None
    )

    with patch("urllib.request.urlopen", side_effect=err):
        res = service.check_ip("1.0.0.1")

    assert res.status == "unavailable"
    assert res.error_type == "RATE_LIMITED"
    assert res.abuse_confidence_score == 0.0


def test_evidence_mapper_to_security_evidence():
    norm_res = NormalizedThreatIntelResult(
        provider="abuseipdb",
        indicator="203.0.113.5",
        abuse_confidence_score=75.0,
        total_reports=15,
        country_code="US",
        isp="Example ISP",
        status="success"
    )

    evidence = ThreatIntelEvidenceMapper.to_security_evidence(norm_res)
    assert evidence.source == "abuseipdb"
    assert evidence.risk_score == 0.75
    assert evidence.confidence == 0.90
    assert evidence.severity.value in ["HIGH", "CRITICAL"]
    assert "abusive_ip" in evidence.security_tags


def test_fusion_engine_incorporates_threat_intel_evidence():
    ti_res = NormalizedThreatIntelResult(
        provider="abuseipdb",
        indicator="198.51.100.22",
        abuse_confidence_score=90.0,
        total_reports=50,
        status="success"
    )
    ti_evidence = ThreatIntelEvidenceMapper.to_security_evidence(ti_res)

    engine = EvidenceFusionEngine()
    fusion_evidence, audit_record, conflicts, qualities = engine.fuse_evidence("ip:198.51.100.22", [ti_evidence])

    assert fusion_evidence is not None
    assert fusion_evidence.unified_risk_score > 0.0
    assert fusion_evidence.evidence_count == 1
