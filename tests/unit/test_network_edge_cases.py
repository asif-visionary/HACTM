"""
Comprehensive Edge Case Test Matrix.
Implements rigorous testing for Section 92 requirements across:
- DATA, IP, PORT, PROTOCOL, TIMESTAMP, FLOW, FEATURES, SIGNATURES, ANOMALY MODEL, WINDOWS, DETECTIONS.
"""

import math
from datetime import datetime, timezone, timedelta
import pytest

from hactm.core.constants import SeverityLevel
from hactm.core.errors import HACTMValidationError
from hactm.network.models import NetworkEvent, DetectorType
from hactm.network.normalization import (
    classify_ip,
    clean_numeric,
    normalize_ip,
    normalize_port,
    normalize_protocol,
    normalize_timestamp,
)
from hactm.network.features.extractor import NetworkFeatureExtractor
from hactm.network.detectors.signature import SignatureDetector, evaluate_condition_tree
from hactm.network.detectors.heuristic import HeuristicDetector
from hactm.network.detectors.anomaly import AnomalyDetector


# --- IP EDGE CASES ---
def test_edge_case_ip_matrix():
    # Valid IPv4 & IPv6
    assert normalize_ip("10.0.0.1") == "10.0.0.1"
    assert normalize_ip("2001:db8::1") == "2001:db8::1"

    # Classifications
    assert classify_ip("192.168.0.1") == "PRIVATE"
    assert classify_ip("1.1.1.1") == "PUBLIC"
    assert classify_ip("127.0.0.1") == "LOOPBACK"
    assert classify_ip("239.255.255.250") == "MULTICAST"
    assert classify_ip("169.254.0.1") == "LINK_LOCAL"
    assert classify_ip("0.0.0.0") == "UNSPECIFIED"

    # Invalid & Whitespace
    assert normalize_ip("   192.168.1.1   ") == "192.168.1.1"
    assert normalize_ip("999.999.999.999", strict=False) is None
    assert normalize_ip("", strict=False) is None
    assert normalize_ip("   ", strict=False) is None
    assert normalize_ip("invalid.host.domain", strict=False) is None


# --- PORT EDGE CASES ---
def test_edge_case_port_matrix():
    # Boundaries
    assert normalize_port(0) == 0
    assert normalize_port(1) == 1
    assert normalize_port(65535) == 65535

    # Out of bounds
    assert normalize_port(-1, strict=False) is None
    assert normalize_port(65536, strict=False) is None

    # Strings & Decimals
    assert normalize_port("80") == 80
    assert normalize_port("  443  ") == 443
    assert normalize_port("80.5", strict=False) is None
    assert normalize_port(None, strict=False) is None


# --- PROTOCOL EDGE CASES ---
def test_edge_case_protocol_matrix():
    assert normalize_protocol("TCP") == "TCP"
    assert normalize_protocol("UDP") == "UDP"
    assert normalize_protocol("ICMP") == "ICMP"
    assert normalize_protocol("ICMPv6") == "ICMPv6"
    assert normalize_protocol("SCTP") == "SCTP"
    assert normalize_protocol(6) == "TCP"
    assert normalize_protocol(17) == "UDP"
    assert normalize_protocol("unknown_proto_xyz") == "OTHER"
    assert normalize_protocol(None) == "OTHER"


# --- TIMESTAMP EDGE CASES ---
def test_edge_case_timestamp_matrix():
    # UTC ISO
    ts1 = normalize_timestamp("2026-02-01T12:00:00Z")
    assert ts1.tzinfo == timezone.utc

    # Timezone offset
    ts2 = normalize_timestamp("2026-02-01T14:00:00+02:00")
    assert ts2.tzinfo == timezone.utc
    assert ts2.hour == 12  # Converted to UTC

    # Unix seconds and milliseconds
    ts3 = normalize_timestamp(1700000000)
    assert ts3.tzinfo == timezone.utc
    ts4 = normalize_timestamp(1700000000000)
    assert ts4.tzinfo == timezone.utc

    # Invalid timestamp
    with pytest.raises(ValueError):
        normalize_timestamp("invalid-date-string")


# --- FLOW AND EXTREME VALUES EDGE CASES ---
def test_edge_case_flow_matrix():
    # Zero duration
    extractor = NetworkFeatureExtractor()
    zero_dur_evt = NetworkEvent(
        event_id="EVT-ZD",
        timestamp=datetime.now(timezone.utc),
        src_ip="192.168.1.1",
        dst_ip="10.0.0.1",
        duration=0.0,
        flow_bytes=1000
    )
    features = extractor.extract(zero_dur_evt)
    assert features["duration"] == 0.0
    assert features["bytes_per_second"] == 0.0  # Zero division avoided

    # Extreme and negative values cleaned
    assert clean_numeric(-100, min_val=0.0, default=0.0) == 0.0
    assert clean_numeric(math.nan, default=0.0) == 0.0
    assert clean_numeric(math.inf, default=0.0) == 0.0
    assert clean_numeric(1e18, max_val=1e12) == 1e12


# --- SIGNATURE EDGE CASES ---
def test_edge_case_signatures_matrix():
    context = {"dst_port": 80, "protocol": "TCP"}

    # Unknown operator handles safely without crash
    cond_unknown_op = {"field": "dst_port", "operator": "non_existent_op", "value": 80}
    match, _ = evaluate_condition_tree({"all": [cond_unknown_op]}, context)
    assert match is False

    # Missing field in context
    cond_missing_field = {"field": "unseen_field", "operator": "eq", "value": 10}
    match, _ = evaluate_condition_tree({"all": [cond_missing_field]}, context)
    assert match is False

    # Empty rule
    match, _ = evaluate_condition_tree({}, context)
    assert match is False


# --- WINDOW AND LATE EVENT EDGE CASES ---
def test_edge_case_windows_matrix():
    detector = HeuristicDetector(
        port_scan_window=20,
        port_scan_threshold=5,
        allowed_lateness_seconds=30
    )
    base = datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc)

    # Single event should not crash
    single_evt = NetworkEvent(
        event_id="EVT-1",
        timestamp=base,
        src_ip="192.168.1.50",
        dst_ip="10.0.0.1",
        dst_port=80
    )
    assert detector.detect(single_evt) is None

    # Out of order event
    ooo_evt = NetworkEvent(
        event_id="EVT-2",
        timestamp=base - timedelta(seconds=10),
        src_ip="192.168.1.50",
        dst_ip="10.0.0.1",
        dst_port=81
    )
    assert detector.detect(ooo_evt) is None


# --- ANOMALY MODEL EDGE CASES ---
def test_edge_case_anomaly_matrix():
    detector = AnomalyDetector()

    # Empty training data
    with pytest.raises(HACTMValidationError):
        detector.fit([])

    # Constant feature training data
    base = datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc)
    constant_events = [
        NetworkEvent(
            event_id=f"EVT-C-{i}",
            timestamp=base + timedelta(seconds=i),
            src_ip="192.168.1.1",
            dst_ip="10.0.0.1",
            flow_bytes=1000,
            flow_packets=10,
            duration=1.0
        )
        for i in range(25)
    ]
    meta = detector.fit(constant_events)
    assert meta.status == "ACTIVE"
