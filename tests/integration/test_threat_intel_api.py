"""
Integration tests for Threat Intelligence FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from hactm.api.app import app

client = TestClient(app)


def test_threat_intel_status_endpoint():
    response = client.get("/api/v1/threat-intelligence/status")
    assert response.status_code == 200
    data = response.json()
    assert "abuseipdb" in data
    assert "configured" in data["abuseipdb"]
    assert "reachable" in data["abuseipdb"]


def test_threat_intel_private_ip_endpoint():
    response = client.get("/api/v1/threat-intelligence/ip/192.168.1.1")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "abuseipdb"
    assert data["status"] == "skipped_private_ip"
    assert data["is_public_ip"] is False
    assert data["abuse_confidence_score"] == 0.0


def test_threat_intel_evidence_endpoint():
    response = client.post(
        "/api/v1/threat-intelligence/evidence?ip_address=10.0.0.5&entity_id=ip:10.0.0.5"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "abuseipdb"
    assert data["event_type"] == "THREAT_INTELLIGENCE"
    assert data["entity_id"] == "ip:10.0.0.5"
