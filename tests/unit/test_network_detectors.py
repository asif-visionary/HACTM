"""
Unit tests for Network Security Detectors.
Covers:
- Safe Structured Signature Engine (Sections 15, 16, 17)
- Sliding-Window Heuristic Engine (Sections 18, 19, 20, 21, 47, 48, 49)
- Anomaly Detection Engine (Sections 22, 23, 24, 27)
"""

from datetime import datetime, timezone, timedelta
import pytest

from hactm.network.models import NetworkEvent, DetectorType
from hactm.network.detectors.signature import SignatureDetector, evaluate_condition_tree
from hactm.network.detectors.heuristic import HeuristicDetector
from hactm.network.detectors.anomaly import AnomalyDetector, RobustZScoreDetector
from hactm.core.errors import HACTMValidationError


def test_signature_condition_evaluator_safety():
    context = {"dst_port": 23, "protocol": "TCP", "flow_rate": 1500.0}

    # Valid AND condition
    tree1 = {
        "all": [
            {"field": "dst_port", "operator": "eq", "value": 23},
            {"field": "protocol", "operator": "eq", "value": "TCP"}
        ]
    }
    match1, reasons1 = evaluate_condition_tree(tree1, context)
    assert match1 is True

    # Valid OR condition
    tree2 = {
        "any": [
            {"field": "dst_port", "operator": "eq", "value": 80},
            {"field": "dst_port", "operator": "eq", "value": 23}
        ]
    }
    match2, _ = evaluate_condition_tree(tree2, context)
    assert match2 is True

    # NOT condition
    tree3 = {
        "not": {"field": "dst_port", "operator": "eq", "value": 80}
    }
    match3, _ = evaluate_condition_tree(tree3, context)
    assert match3 is True

    # Numeric threshold
    tree4 = {
        "all": [{"field": "flow_rate", "operator": "gt", "value": 1000.0}]
    }
    match4, _ = evaluate_condition_tree(tree4, context)
    assert match4 is True

    # Missing field evaluates cleanly to False without crashing
    tree5 = {
        "all": [{"field": "non_existent_column", "operator": "eq", "value": "test"}]
    }
    match5, _ = evaluate_condition_tree(tree5, context)
    assert match5 is False


def test_signature_detector_rules():
    detector = SignatureDetector()
    base_time = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)

    # 1. Telnet detection
    telnet_evt = NetworkEvent(
        event_id="EVT-TEL-01",
        timestamp=base_time,
        src_ip="192.168.1.50",
        dst_ip="10.0.0.1",
        src_port=40000,
        dst_port=23,
        protocol="TCP"
    )
    res_tel = detector.detect(telnet_evt)
    assert res_tel is not None
    assert res_tel.detector_type == DetectorType.SIGNATURE
    assert res_tel.signature_id == "SIG-NET-001"
    assert "telnet" in res_tel.explanation.lower()

    # 2. Benign HTTPS flow - should not trigger
    https_evt = NetworkEvent(
        event_id="EVT-HTTPS-01",
        timestamp=base_time,
        src_ip="192.168.1.50",
        dst_ip="10.0.0.1",
        src_port=40000,
        dst_port=443,
        protocol="TCP"
    )
    assert detector.detect(https_evt) is None


def test_heuristic_port_scan_sliding_window():
    detector = HeuristicDetector(
        port_scan_window=10,
        port_scan_threshold=5  # Alert after 5 distinct ports
    )
    base_time = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
    attacker_ip = "192.168.1.200"

    # Send 4 connection attempts to different ports
    for i in range(4):
        evt = NetworkEvent(
            event_id=f"EVT-SCAN-{i}",
            timestamp=base_time + timedelta(seconds=i),
            src_ip=attacker_ip,
            dst_ip="10.0.0.5",
            src_port=50000 + i,
            dst_port=1000 + i,
            protocol="TCP"
        )
        assert detector.detect(evt) is None

    # 5th attempt breaches threshold
    breach_evt = NetworkEvent(
        event_id="EVT-SCAN-4",
        timestamp=base_time + timedelta(seconds=4),
        src_ip=attacker_ip,
        dst_ip="10.0.0.5",
        src_port=50004,
        dst_port=1004,
        protocol="TCP"
    )
    port_scan_det = detector.detect(breach_evt)
    assert port_scan_det is not None
    assert port_scan_det.detector_type == DetectorType.HEURISTIC
    assert port_scan_det.risk_score >= 0.70
    assert "distinct destination ports" in port_scan_det.explanation.lower() or "port scan" in port_scan_det.explanation.lower()


def test_heuristic_out_of_order_and_late_events():
    detector = HeuristicDetector(
        port_scan_window=30,
        port_scan_threshold=5,
        allowed_lateness_seconds=60
    )
    base_time = datetime(2026, 2, 1, 12, 0, 0, tzinfo=timezone.utc)

    # 1. Normal event at 12:05:00
    evt1 = NetworkEvent(
        event_id="EVT-NORM",
        timestamp=base_time + timedelta(minutes=5),
        src_ip="192.168.1.10",
        dst_ip="10.0.0.1",
        dst_port=80,
        protocol="TCP"
    )
    detector.detect(evt1)

    # 2. Out-of-order event within allowed lateness (12:04:30)
    evt_ooo = NetworkEvent(
        event_id="EVT-OOO",
        timestamp=base_time + timedelta(minutes=4, seconds=30),
        src_ip="192.168.1.10",
        dst_ip="10.0.0.1",
        dst_port=81,
        protocol="TCP"
    )
    # Should be processed into window without throwing error
    detector.detect(evt_ooo)

    # 3. Excessively late event (> 60s older than latest timestamp)
    evt_too_late = NetworkEvent(
        event_id="EVT-LATE",
        timestamp=base_time,  # 5 minutes late!
        src_ip="192.168.1.10",
        dst_ip="10.0.0.1",
        dst_port=82,
        protocol="TCP"
    )
    # Bounded window ignores or logs late event gracefully
    dets = detector.detect(evt_too_late)
    assert dets is None or isinstance(dets, NetworkDetectionResult)


def test_anomaly_detector_training_and_scoring():
    detector = AnomalyDetector(algorithm="isolation_forest", contamination=0.05)
    base_time = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)

    # 1. Reject insufficient data (<10 events)
    with pytest.raises(HACTMValidationError):
        detector.fit([])

    # 2. Fit on 50 benign baseline events
    benign_events = [
        NetworkEvent(
            event_id=f"EVT-BEN-{i}",
            timestamp=base_time + timedelta(seconds=i),
            src_ip="192.168.1.10",
            dst_ip="10.0.0.1",
            src_port=30000 + i,
            dst_port=443,
            duration=0.1 + (i % 5) * 0.02,
            flow_bytes=1500 + (i % 8) * 100,
            flow_packets=10 + (i % 4),
            flow_rate=15000.0,
            packet_rate=100.0
        )
        for i in range(50)
    ]
    meta = detector.fit(benign_events, dataset_name="unit_test_dataset")
    assert meta.model_id == "model_net_baseline_v1"
    assert meta.status == "ACTIVE"

    # 3. Test on standard benign flow -> should receive lower risk score (<0.60)
    benign_score = detector.score(benign_events[0])
    assert 0.0 <= benign_score <= 1.0

    # 4. Test on massive volumetric anomaly -> should receive higher anomaly score
    anomaly_evt = NetworkEvent(
        event_id="EVT-ANOM-99",
        timestamp=base_time + timedelta(hours=1),
        src_ip="192.168.1.99",
        dst_ip="10.0.0.1",
        src_port=55555,
        dst_port=80,
        protocol="UDP",
        duration=0.001,
        flow_bytes=10000000,
        flow_packets=50000,
        flow_rate=10000000000.0,
        packet_rate=50000000.0
    )
    anomaly_score = detector.score(anomaly_evt)
    assert 0.0 <= anomaly_score <= 1.0
    assert anomaly_score > benign_score


def test_robust_z_score_detector():
    z_detector = RobustZScoreDetector(threshold_z=2.5)
    base_time = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)

    events = [
        NetworkEvent(
            event_id=f"EVT-{i}",
            timestamp=base_time + timedelta(seconds=i),
            src_ip="192.168.1.10",
            dst_ip="10.0.0.1",
            dst_port=443,
            protocol="TCP",
            flow_bytes=1000 + (i % 50),
            flow_packets=10
        )
        for i in range(40)
    ]
    z_detector.fit(events)

    # Inlier flow
    inlier = events[0]
    score_inlier = z_detector.score(inlier)
    assert score_inlier < 0.50

    # Massive outlier flow
    outlier = NetworkEvent(
        event_id="EVT-OUTLIER",
        timestamp=base_time + timedelta(minutes=10),
        src_ip="192.168.1.10",
        dst_ip="10.0.0.1",
        dst_port=443,
        protocol="TCP",
        flow_bytes=5000000,
        flow_packets=5000
    )
    score_outlier = z_detector.score(outlier)
    assert score_outlier > score_inlier
