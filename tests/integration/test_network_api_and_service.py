"""
Integration tests for Network Security Agent API endpoints and NetworkService.
Tests Section 64, 65, 73, 74, 88.
"""

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from hactm.api.app import app
from hactm.storage.database import SessionLocal, init_db


@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client


def test_network_health_endpoint(client):
    res = client.get("/api/v1/network/health")
    assert res.status_code == 200
    data = res.json().get("data", res.json())
    assert data["status"] in ["OPERATIONAL", "DEGRADED"]
    assert "events_processed" in data
    assert "active_detectors" in data


def test_network_config_endpoint(client):
    res = client.get("/api/v1/network/config")
    assert res.status_code == 200
    data = res.json().get("data", res.json())
    assert "port_scan" in data or "network" in data or "version" in data


def test_network_detect_single_event_endpoint(client):
    event_payload = {
        "event_id": "API-TEST-NET-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": "192.168.1.100",
        "dst_ip": "10.0.0.5",
        "src_port": 49152,
        "dst_port": 23,  # Cleartext Telnet trigger
        "protocol": "TCP",
        "duration": 0.05,
        "flow_bytes": 120,
        "flow_packets": 2
    }

    res = client.post("/api/v1/network/detect", json={"events": [event_payload], "persist": True})
    assert res.status_code in [200, 201]
    body = res.json()
    data = body.get("data", body)
    detections = data.get("detections", data) if isinstance(data, dict) else data
    assert len(detections) >= 1
    assert detections[0]["signature_id"] == "SIG-NET-001" or "telnet" in detections[0]["explanation"].lower()
    assert detections[0]["detector_type"] == "SIGNATURE"
    det_id = detections[0]["detection_id"]

    # Verify retrieval by ID
    get_res = client.get(f"/api/v1/network/detections/{det_id}")
    assert get_res.status_code == 200
    det_data = get_res.json().get("data", get_res.json())
    assert det_data["detection_id"] == det_id


def test_network_events_and_detections_pagination(client):
    events_res = client.get("/api/v1/network/events?page=1&page_size=10")
    assert events_res.status_code == 200
    ev_data = events_res.json()
    assert "data" in ev_data
    assert "pagination" in ev_data or "meta" in ev_data

    dets_res = client.get("/api/v1/network/detections?page=1&page_size=10")
    assert dets_res.status_code == 200
    det_data = dets_res.json()
    assert "data" in det_data
    assert "pagination" in det_data or "meta" in det_data


def test_network_metrics_endpoint(client):
    res = client.get("/api/v1/network/metrics")
    assert res.status_code == 200
    data = res.json().get("data", res.json())
    assert "total_network_events" in data
    assert "total_detections" in data
    assert "high_risk_detections" in data
    assert "categories" in data


def test_network_models_listing_and_activation(client):
    res = client.get("/api/v1/network/models")
    assert res.status_code == 200
    body = res.json()
    models = body.get("data", body)
    assert isinstance(models, list)
    if len(models) > 0:
        model_id = models[0]["model_id"]
        act_res = client.post(f"/api/v1/network/models/{model_id}/activate")
        assert act_res.status_code in [200, 201]
        act_data = act_res.json().get("data", act_res.json())
        assert act_data.get("success") is True


def test_detection_feedback(client):
    # Detect an event first to have a valid detection_id
    event_payload = {
        "event_id": "API-TEST-FEEDBACK-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_ip": "192.168.1.101",
        "dst_ip": "10.0.0.5",
        "src_port": 49153,
        "dst_port": 23,
        "protocol": "TCP"
    }
    det_res = client.post("/api/v1/network/detect", json={"events": [event_payload], "persist": True})
    data = det_res.json().get("data", det_res.json())
    detections = data.get("detections", data) if isinstance(data, dict) else data
    det_id = detections[0]["detection_id"]

    # Submit feedback
    fb_payload = {
        "detection_id": det_id,
        "label": "TRUE_POSITIVE",
        "analyst_note": "Verified unauthorized telnet attempt in lab testing."
    }
    fb_res = client.post(f"/api/v1/network/detections/{det_id}/feedback", json=fb_payload)
    assert fb_res.status_code in [200, 201]
    fb_data = fb_res.json().get("data", fb_res.json())
    assert fb_data["label"] == "TRUE_POSITIVE"
