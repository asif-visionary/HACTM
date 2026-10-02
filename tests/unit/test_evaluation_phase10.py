"""
Unit tests for Evaluation Framework Engine, MetricEngine, and DatasetRegistry.
"""

import pytest
from hactm.evaluation.metric_engine import MetricEngine
from hactm.evaluation.dataset_registry import EvaluationDatasetRegistry
from hactm.evaluation.experiment_runner import ExperimentRunner
from hactm.evaluation.models import ResultStatus, ReportFormat
from hactm.evaluation.report_generator import ReportGenerator


def test_metric_engine_precision_recall_f1():
    prec, status = MetricEngine.calculate_precision(90, 10)
    assert prec == 0.90
    assert status == ResultStatus.COMPLETED

    rec, _ = MetricEngine.calculate_recall(90, 10)
    assert rec == 0.90

    f1, _ = MetricEngine.calculate_f1(prec, rec)
    assert f1 == 0.90

    # Edge cases
    prec_zero, status_zero = MetricEngine.calculate_precision(0, 0)
    assert prec_zero is None
    assert status_zero == ResultStatus.NOT_AVAILABLE


def test_metric_engine_auroc_single_class_edge_case():
    # Single-class dataset (only 1s) must return NOT_AVAILABLE
    auroc, status = MetricEngine.calculate_auroc([1, 1, 1], [0.8, 0.9, 0.7])
    assert auroc is None
    assert status == ResultStatus.NOT_AVAILABLE

    # Multi-class dataset
    auroc_ok, status_ok = MetricEngine.calculate_auroc([1, 1, 0, 0], [0.9, 0.8, 0.2, 0.1])
    assert auroc_ok == 1.0
    assert status_ok == ResultStatus.COMPLETED


def test_metric_engine_ece_calibration():
    ece, status = MetricEngine.calculate_ece([1, 1, 0, 0], [0.9, 0.8, 0.2, 0.1])
    assert ece is not None
    assert status == ResultStatus.COMPLETED
    assert ece <= 0.20


def test_dataset_registry_time_aware_split():
    registry = EvaluationDatasetRegistry()
    samples = [
        {"id": 1, "timestamp": "2026-01-01T00:00:00Z"},
        {"id": 2, "timestamp": "2026-01-02T00:00:00Z"},
        {"id": 3, "timestamp": "2026-01-03T00:00:00Z"},
        {"id": 4, "timestamp": "2026-01-04T00:00:00Z"},
        {"id": 5, "timestamp": "2026-01-05T00:00:00Z"},
    ]
    splits = registry.create_time_aware_split(samples, train_ratio=0.6, val_ratio=0.2)
    assert len(splits["train"]) == 3
    assert splits["split_info"]["data_leakage_protected"]


def test_experiment_runner_master_experiments():
    runner = ExperimentRunner()
    res1 = runner.run_master_experiment("EXP_1_AGENT_DETECTION")
    assert "agent_detection_metrics" in res1["results"]

    res_scale = runner.run_master_experiment("EXP_12_SCALABILITY")
    assert len(res_scale["results"]["scalability_matrix"]) == 6

    res_abl = runner.run_master_experiment("EXP_13_ABLATION")
    assert len(res_abl["results"]["ablation_matrix"]) == 12


def test_report_generator_checksum_and_artifacts():
    generator = ReportGenerator(output_dir="artifacts/test_reports")
    rpt = generator.generate_report("EXP_14_END_TO_END", "Test PDF Report", ReportFormat.PDF, {"f1": 0.962})
    assert rpt.status == "COMPLETED"
    assert rpt.reproducibility_checksum is not None
