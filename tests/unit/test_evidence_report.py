"""
Unit tests for Structured Evidence Report Generation & PDF / JSON Exports.
"""

import pytest
from fastapi.testclient import TestClient
from hactm.api.app import app

client = TestClient(app)


def test_generate_evidence_report_no_filters():
    response = client.post("/api/v1/reports/evidence", json={})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    report = data["data"]
    assert report["title"] == "Structured Security Evidence Report"
    assert "report_id" in report
    assert report["report_id"].startswith("RPT-EVD-")
    assert "summary" in report
    assert "records" in report
    assert report["summary"]["pdf_export_status"] == "AVAILABLE"


def test_generate_evidence_report_valid_filters():
    payload = {
        "event_type": "NETWORK",
        "min_risk": 0.5
    }
    response = client.post("/api/v1/reports/evidence", json=payload)
    assert response.status_code == 200
    report = response.json()["data"]
    assert report["filters"]["event_type"] == "NETWORK"
    assert report["filters"]["min_risk"] == 0.5
    for r in report["records"]:
        assert r["event_type"] == "NETWORK"
        assert r["risk_score"] >= 0.5


def test_generate_evidence_report_invalid_min_risk():
    payload = {"min_risk": 1.5}
    response = client.post("/api/v1/reports/evidence", json=payload)
    assert response.status_code == 400 or response.status_code == 422
    assert "Minimum Cyber Risk" in response.text or "less than or equal to 1" in response.text


def test_export_evidence_pdf():
    payload = {"min_risk": 0.3}
    response = client.post("/api/v1/reports/evidence/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
