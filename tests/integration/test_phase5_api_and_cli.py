"""
Integration tests for Adaptive Memory & Graph API endpoints and CLI commands.
"""

import pytest
from fastapi.testclient import TestClient

from hactm.api.app import app
from hactm.storage.database import init_db


@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as c:
        yield c


def test_memory_api_endpoints(client):
    res_h = client.get("/api/v1/memory/health")
    assert res_h.status_code == 200
    assert "status" in res_h.json()

    res_e = client.get("/api/v1/memory/evidence")
    assert res_e.status_code == 200
    assert "entries" in res_e.json()

    res_t = client.get("/api/v1/memory/transitions")
    assert res_t.status_code == 200
    assert isinstance(res_t.json(), list)

    res_a = client.get("/api/v1/memory/access-log")
    assert res_a.status_code == 200
    assert isinstance(res_a.json(), list)


def test_graph_and_temporal_api_endpoints(client):
    res_c = client.get("/api/v1/graph/attack-chains")
    assert res_c.status_code == 200
    assert isinstance(res_c.json(), list)

    res_p = client.get("/api/v1/temporal/patterns")
    assert res_p.status_code == 200
    assert "patterns" in res_p.json()


def test_adaptive_memory_evaluation_api_endpoint(client):
    res_ev = client.get("/api/v1/adaptive_memory/evaluate")
    assert res_ev.status_code == 200
    data = res_ev.json()
    assert data["status"] == "COMPLETED"
    assert "baseline_comparison" in data
    assert "ablation_studies" in data
    assert "Proposed_AdaptiveMemory" in data["baseline_comparison"]
