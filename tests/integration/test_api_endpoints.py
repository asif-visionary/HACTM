"""
API integration tests for all Foundation endpoints.
"""

from fastapi import status


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "HACTM" in data["service"]


def test_create_and_get_evidence(client):
    payload = {
        "event_id": "EVT-API-001",
        "agent_id": "AGENT-NET",
        "entity_id": "IP:10.0.0.1",
        "event_type": "NETWORK",
        "timestamp": "2026-10-01T15:00:00Z",
        "risk_score": 0.82,
        "confidence": 0.90,
        "uncertainty": 0.10,
        "evidence": {"port": 443, "proto": "tcp"},
    }

    # Create evidence
    post_res = client.post("/api/v1/evidence", json=payload)
    assert post_res.status_code == status.HTTP_201_CREATED
    body = post_res.json()
    assert body["data"]["event_id"] == "EVT-API-001"
    assert body["data"]["severity"] == "CRITICAL"

    # Get evidence by ID
    get_res = client.get("/api/v1/evidence/EVT-API-001")
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.json()["data"]["event_id"] == "EVT-API-001"

    # Duplicate creation error handling
    dup_res = client.post("/api/v1/evidence", json=payload)
    assert dup_res.status_code == status.HTTP_409_CONFLICT
    assert dup_res.json()["error"]["code"] == "DUPLICATE_ERROR"


def test_evidence_pagination_and_filtering(client):
    # Seed 5 items with varying risk scores
    for i in range(1, 6):
        client.post(
            "/api/v1/evidence",
            json={
                "event_id": f"EVT-FILTER-{i}",
                "agent_id": "AGENT-01",
                "entity_id": f"IP:192.168.1.{i}",
                "event_type": "NETWORK" if i % 2 == 0 else "AUTHENTICATION",
                "timestamp": f"2026-10-01T10:0{i}:00Z",
                "risk_score": i * 0.18,  # 0.18, 0.36, 0.54, 0.72, 0.90
                "confidence": 0.9,
                "uncertainty": 0.1,
                "evidence": {},
            },
        )

    # Test pagination
    p_res = client.get("/api/v1/evidence?page=1&page_size=2")
    assert p_res.status_code == status.HTTP_200_OK
    p_data = p_res.json()
    assert len(p_data["data"]) == 2
    assert p_data["pagination"]["total"] == 5
    assert p_data["pagination"]["page"] == 1
    assert p_data["pagination"]["page_size"] == 2

    # Test filter by event_type
    f_res = client.get("/api/v1/evidence?event_type=AUTHENTICATION")
    assert f_res.status_code == status.HTTP_200_OK
    assert all(e["event_type"] == "AUTHENTICATION" for e in f_res.json()["data"])

    # Test filter by min_risk
    r_res = client.get("/api/v1/evidence?min_risk=0.7")
    assert r_res.status_code == status.HTTP_200_OK
    assert all(e["risk_score"] >= 0.7 for e in r_res.json()["data"])


def test_entities_endpoint(client):
    client.post(
        "/api/v1/evidence",
        json={
            "event_id": "EVT-ENT-001",
            "agent_id": "AGENT-01",
            "entity_id": "USER:security_analyst",
            "event_type": "AUTHENTICATION",
            "timestamp": "2026-10-01T12:00:00Z",
            "risk_score": 0.2,
            "confidence": 0.9,
            "uncertainty": 0.1,
            "evidence": {},
        },
    )

    res = client.get("/api/v1/entities")
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["pagination"]["total"] >= 1

    detail_res = client.get("/api/v1/entities/USER:security_analyst")
    assert detail_res.status_code == status.HTTP_200_OK
    entity_data = detail_res.json()["data"]
    assert entity_data["entity_id"] == "USER:security_analyst"
    assert len(entity_data["associated_evidence"]) == 1


def test_metrics_and_timeline_endpoints(client):
    client.post(
        "/api/v1/evidence",
        json={
            "event_id": "EVT-METRIC-01",
            "agent_id": "AGENT-01",
            "entity_id": "IP:192.168.1.50",
            "event_type": "NETWORK",
            "timestamp": "2026-10-01T14:00:00Z",
            "risk_score": 0.95,
            "confidence": 0.95,
            "uncertainty": 0.05,
            "evidence": {},
        },
    )

    overview_res = client.get("/api/v1/metrics/overview")
    assert overview_res.status_code == status.HTTP_200_OK
    m_data = overview_res.json()["data"]
    assert m_data["total_events"] >= 1
    assert m_data["high_risk_events"] >= 1
    assert "CRITICAL" in m_data["risk_distribution"]

    timeline_res = client.get("/api/v1/metrics/timeline")
    assert timeline_res.status_code == status.HTTP_200_OK
    assert len(timeline_res.json()["data"]) >= 1


def test_evidence_report_generation(client):
    client.post(
        "/api/v1/evidence",
        json={
            "event_id": "EVT-REP-01",
            "agent_id": "AGENT-REP",
            "entity_id": "IP:10.0.0.99",
            "event_type": "NETWORK",
            "source": "AuditFirewall",
            "timestamp": "2026-10-01T16:00:00Z",
            "risk_score": 0.75,
            "confidence": 0.9,
            "uncertainty": 0.1,
            "evidence": {},
        },
    )

    report_payload = {
        "source": "AuditFirewall",
        "min_risk": 0.5,
    }
    rep_res = client.post("/api/v1/reports/evidence", json=report_payload)
    assert rep_res.status_code == status.HTTP_200_OK
    rep_data = rep_res.json()["data"]
    assert rep_data["evidence_count"] >= 1
    assert rep_data["summary"]["pdf_export_status"] == "AVAILABLE"


def test_not_found_and_validation_errors(client):
    # Not found
    nf_res = client.get("/api/v1/evidence/NON_EXISTENT_ID")
    assert nf_res.status_code == status.HTTP_404_NOT_FOUND
    assert nf_res.json()["error"]["code"] == "NOT_FOUND"

    # Schema validation error
    val_res = client.post("/api/v1/evidence", json={"bad_field": 123})
    assert val_res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert val_res.json()["error"]["code"] == "VALIDATION_ERROR"
