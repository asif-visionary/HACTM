"""
Integration tests for Evaluation Framework, Scalability, and Reports API Endpoints.
"""

import pytest
import uuid
from fastapi.testclient import TestClient

from hactm.api.app import app
from hactm.storage.database import init_db

init_db()
client = TestClient(app)


def test_api_evaluation_datasets():
    response = client.get("/api/v1/evaluation/datasets")
    assert response.status_code == 200
    datasets = response.json()["datasets"]
    assert len(datasets) >= 5


def test_api_evaluation_experiments_and_runs():
    exp_res = client.get("/api/v1/evaluation/experiments")
    assert exp_res.status_code == 200
    exps = exp_res.json()["experiments"]
    assert len(exps) >= 7

    run_res = client.post("/api/v1/evaluation/experiments/run?experiment_id=EXP_14_END_TO_END&workload_size=1000")
    assert run_res.status_code == 200
    assert run_res.json()["status"] == "COMPLETED"


def test_api_evaluation_metrics_and_matrices():
    metrics_res = client.get("/api/v1/evaluation/metrics")
    assert metrics_res.status_code == 200
    assert "overall_f1" in metrics_res.json()["detection"]

    scale_res = client.get("/api/v1/evaluation/scalability")
    assert scale_res.status_code == 200
    assert len(scale_res.json()["scalability_matrix"]) == 6

    abl_res = client.get("/api/v1/evaluation/ablations")
    assert abl_res.status_code == 200
    assert len(abl_res.json()["ablation_matrix"]) == 12

    base_res = client.get("/api/v1/evaluation/baselines")
    assert base_res.status_code == 200
    assert len(base_res.json()["baselines"]) == 9


def test_api_reports_generation_and_export():
    uid = uuid.uuid4().hex[:6]
    gen_res = client.post(f"/api/v1/reports/generate?experiment_id=EXP_14_END_TO_END&title=TestReport_{uid}&format=JSON")
    assert gen_res.status_code == 200
    rpt = gen_res.json()
    assert rpt["status"] == "COMPLETED"
    assert rpt["reproducibility_checksum"] is not None

    # Export report file
    rid = rpt["report_id"]
    exp_res = client.get(f"/api/v1/reports/{rid}/export")
    assert exp_res.status_code == 200
