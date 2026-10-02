"""
Unit tests for NetworkDataLoader and Network Evaluation metrics.
Tests Sections 4, 5, 41, 42, 43, 44 of Network Security Agent.
"""

from pathlib import Path
from hactm.network.loader import NetworkDataLoader
from hactm.network.evaluation import evaluate_detections
from hactm.network.models import NetworkDetectionResult, NetworkEvent, DetectorType
from hactm.core.constants import SeverityLevel
from datetime import datetime, timezone


def test_network_data_loader_csv(tmp_path: Path):
    loader = NetworkDataLoader()
    sample_csv = tmp_path / "test_flow.csv"
    sample_csv.write_text(
        "timestamp,src_ip,dst_ip,src_port,dst_port,protocol,duration,flow_bytes,flow_packets\n"
        "2026-02-01T12:00:00Z,192.168.1.5,10.0.0.1,50000,80,TCP,0.5,1000,10\n"
        "2026-02-01T12:00:01Z,192.168.1.6,10.0.0.1,50001,443,TCP,0.8,2000,15\n"
    )

    batches = list(loader.load_from_file(sample_csv, batch_size=10))
    assert len(batches) == 1
    events = batches[0]
    assert len(events) == 2
    assert events[0].src_ip == "192.168.1.5"
    assert events[0].dst_port == 80
    assert events[0].protocol == "TCP"
    assert events[1].flow_bytes == 2000


def test_network_evaluation_metrics_calculation():
    # 2 true positives, 1 false positive, 2 true negatives, 1 false negative
    base_time = datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc)
    events = [
        NetworkEvent(event_id="EVT-1", timestamp=base_time, src_ip="1.1.1.1", dst_ip="2.2.2.2", label="attack"),
        NetworkEvent(event_id="EVT-2", timestamp=base_time, src_ip="1.1.1.2", dst_ip="2.2.2.2", label="attack"),
        NetworkEvent(event_id="EVT-3", timestamp=base_time, src_ip="1.1.1.3", dst_ip="2.2.2.2", label="attack"),  # FN
        NetworkEvent(event_id="EVT-4", timestamp=base_time, src_ip="1.1.1.4", dst_ip="2.2.2.2", label="benign"),  # FP
        NetworkEvent(event_id="EVT-5", timestamp=base_time, src_ip="1.1.1.5", dst_ip="2.2.2.2", label="benign"),
        NetworkEvent(event_id="EVT-6", timestamp=base_time, src_ip="1.1.1.6", dst_ip="2.2.2.2", label="benign"),
    ]

    detections = [
        NetworkDetectionResult(
            detection_id="D-1", event_id="EVT-1", detector_type=DetectorType.SIGNATURE,
            detector_id="SIG1", detector_version="1.0", category="test", risk_score=0.9,
            confidence=0.9, uncertainty=0.1, severity=SeverityLevel.HIGH, explanation="test",
            timestamp=base_time
        ),
        NetworkDetectionResult(
            detection_id="D-2", event_id="EVT-2", detector_type=DetectorType.HEURISTIC,
            detector_id="HEUR1", detector_version="1.0", category="test", risk_score=0.8,
            confidence=0.8, uncertainty=0.2, severity=SeverityLevel.HIGH, explanation="test",
            timestamp=base_time
        ),
        NetworkDetectionResult(
            detection_id="D-4", event_id="EVT-4", detector_type=DetectorType.ANOMALY,
            detector_id="ANOM1", detector_version="1.0", category="test", risk_score=0.7,
            confidence=0.7, uncertainty=0.3, severity=SeverityLevel.MEDIUM, explanation="test",
            timestamp=base_time
        ),
    ]

    metrics = evaluate_detections(events, detections)
    assert metrics.total_evaluated == 6
    assert metrics.true_positives == 2
    assert metrics.false_positives == 1
    assert metrics.true_negatives == 2
    assert metrics.false_negatives == 1
    assert round(metrics.precision, 2) == 0.67  # 2 / (2 + 1)
    assert round(metrics.recall, 2) == 0.67     # 2 / (2 + 1)
    assert metrics.roc_auc is not None
    assert metrics.pr_auc is not None
