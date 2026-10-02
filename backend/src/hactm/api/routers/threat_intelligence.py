"""
FastAPI Router for Threat Intelligence API Endpoints.
Exposes endpoints for IP reputation checks (/ip/{ip}), provider health status (/status),
and Threat Intelligence SecurityEvidence generation.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel

from hactm.services.threat_intelligence.threat_intelligence_service import ThreatIntelligenceService
from hactm.services.threat_intelligence.provider import NormalizedThreatIntelResult

router = APIRouter(prefix="/api/v1/threat-intelligence", tags=["External Threat Intelligence"])


@router.get("/status", response_model=Dict[str, Any])
def get_threat_intel_status():
    """Returns configuration and reachability status for external threat intelligence providers."""
    service = ThreatIntelligenceService()
    return service.get_status()


@router.get("/ip/{ip}", response_model=Dict[str, Any])
def get_ip_reputation(
    ip: str,
    max_age_days: Optional[int] = Query(None, description="Max age in days for report query (default 30)")
):
    """Queries external AbuseIPDB threat intelligence provider for IP reputation and returns normalized evidence data."""
    service = ThreatIntelligenceService()
    result = service.check_ip(ip, max_age_days=max_age_days)
    return result.model_dump()


@router.post("/evidence", response_model=Dict[str, Any])
def generate_threat_intel_evidence(
    ip_address: str,
    entity_id: Optional[str] = None
):
    """Queries AbuseIPDB and constructs canonical HACTM SecurityEvidence object."""
    service = ThreatIntelligenceService()
    evidence = service.get_ip_evidence(ip_address, entity_id=entity_id)
    return evidence.model_dump()
