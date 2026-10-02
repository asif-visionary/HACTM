"""
Common Security Agents REST API Router.
Specialized Security Agents — Heterogeneous Multi-Domain Agent Management.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.network_service import NetworkService
from hactm.services.phishing_service import PhishingService
from hactm.services.uba_service import UbaService
from hactm.services.identity_service import IdentityService
from hactm.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/v1/agents", tags=["Security Agents"])


def _get_agent_services(db: Session) -> Dict[str, Any]:
    return {
        "network-security-agent": NetworkService(db),
        "phishing-intelligence-agent": PhishingService(db),
        "uba-agent": UbaService(db),
        "identity-authentication-agent": IdentityService(db),
        "transaction-security-agent": TransactionService(db),
    }


@router.get("")
def list_all_agents(db: Session = Depends(get_db)):
    services = _get_agent_services(db)
    agents_summary = []
    for agent_id, svc in services.items():
        h = svc.agent.health()
        agents_summary.append({
            "agent_id": agent_id,
            "version": h.get("version", "1.0.0"),
            "status": h.get("status", "OPERATIONAL"),
            "events_processed": h.get("events_processed", 0),
            "detections_generated": h.get("detections_generated", 0),
            "average_latency_ms": h.get("average_latency_ms", 0.0),
            "active_detectors": h.get("active_detectors", []),
        })
    return agents_summary


@router.get("/{agent_id}")
def get_agent_detail(agent_id: str, db: Session = Depends(get_db)):
    services = _get_agent_services(db)
    if agent_id not in services:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    svc = services[agent_id]
    h = svc.agent.health()

    limitations = {
        "network-security-agent": "Offline packet/flow analysis; requires signature and heuristic windowing.",
        "phishing-intelligence-agent": "Offline email analysis; does not visit external URLs or run dynamic attachment sandboxes.",
        "uba-agent": "Requires minimum 5 historical user events for statistical baseline; returns INSUFFICIENT_BASELINE for new users.",
        "identity-authentication-agent": "Analyzes auth telemetry only; does not implement real 2FA/biometric identity providers.",
        "transaction-security-agent": "Detection only; does not execute transactions, transfer funds, or freeze financial accounts.",
    }

    methods = {
        "network-security-agent": "Signature matching, sliding window scan heuristics, and Isolation Forest flow anomaly detection.",
        "phishing-intelligence-agent": "Header analysis, URL structure features, double-extension detection, and TF-IDF NLP classification.",
        "uba-agent": "Bounded historical profile baseline, temporal windowing, data movement thresholding, and robust z-score.",
        "identity-authentication-agent": "Brute-force velocity windowing, ATO success-after-failure heuristic, and Haversine impossible travel.",
        "transaction-security-agent": "Burst velocity tracking, robust amount deviation z-score, and recipient novelty correlation.",
    }

    return {
        "agent_id": agent_id,
        "version": h.get("version", "1.0.0"),
        "status": h.get("status", "OPERATIONAL"),
        "events_processed": h.get("events_processed", 0),
        "detections_generated": h.get("detections_generated", 0),
        "errors_count": h.get("errors_count", 0),
        "average_latency_ms": h.get("average_latency_ms", 0.0),
        "model_version": h.get("model_version", "1.0.0"),
        "active_detectors": h.get("active_detectors", []),
        "detection_method": methods.get(agent_id, "Specialized domain threat detection engine."),
        "current_limitations": limitations.get(agent_id, "Domain evidence generation only."),
    }


@router.get("/{agent_id}/health")
def get_agent_health(agent_id: str, db: Session = Depends(get_db)):
    services = _get_agent_services(db)
    if agent_id not in services:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return services[agent_id].agent.health()
