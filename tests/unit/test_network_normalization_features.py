"""
Unit tests for Network Telemetry Normalization, Validation, and Feature Extraction.
Tests Sections 7, 8, 9, 10, 11, 12, 13, 14, 51, 52, 53 of Network Security Agent.
"""

import math
from datetime import datetime, timezone
import pytest

from hactm.network.normalization import (
    classify_ip,
    clean_numeric,
    normalize_ip,
    normalize_port,
    normalize_protocol,
    normalize_tcp_flags,
    normalize_timestamp,
)
from hactm.network.features.extractor import NetworkFeatureExtractor
from hactm.network.models import NetworkEvent


def test_ip_classification():
    # IPv4 tests
    assert classify_ip("192.168.1.1") == "PRIVATE"
    assert classify_ip("10.0.0.5") == "PRIVATE"
    assert classify_ip("172.16.5.20") == "PRIVATE"
    assert classify_ip("127.0.0.1") == "LOOPBACK"
    assert classify_ip("8.8.8.8") == "PUBLIC"
    assert classify_ip("224.0.0.1") == "MULTICAST"
    assert classify_ip("169.254.1.1") == "LINK_LOCAL"
    assert classify_ip("0.0.0.0") == "UNSPECIFIED"

    # IPv6 tests
    assert classify_ip("::1") == "LOOPBACK"
    assert classify_ip("fe80::1") == "LINK_LOCAL"
    assert classify_ip("ff02::1") == "MULTICAST"
    assert classify_ip("2607:f8b0:4005:805::200e") == "PUBLIC"

    # Invalid IPs
    assert classify_ip("999.999.1.1") == "INVALID"
    assert classify_ip("abc.def.ghi.jkl") == "INVALID"
    assert classify_ip("") == "INVALID"
    assert classify_ip(None) == "INVALID"


def test_ip_normalization():
    assert normalize_ip("  192.168.1.50  ") == "192.168.1.50"
    assert normalize_ip("2001:0db8:0000:0000:0000:ff00:0042:8329") == "2001:db8::ff00:42:8329"
    assert normalize_ip("invalid-ip", strict=False) is None

    with pytest.raises(ValueError):
        normalize_ip("999.999.1.1", strict=True)


def test_port_normalization():
    # Valid ports
    assert normalize_port(0) == 0
    assert normalize_port(80) == 80
    assert normalize_port("443") == 443
    assert normalize_port("  8080 ") == 8080
    assert normalize_port(65535) == 65535

    # Invalid ports
    assert normalize_port(-1, strict=False) is None
    assert normalize_port(65536, strict=False) is None
    assert normalize_port("abc", strict=False) is None
    assert normalize_port("80.5", strict=False) is None

    with pytest.raises(ValueError):
        normalize_port(-10, strict=True)


def test_protocol_normalization():
    # Standard string protocols
    assert normalize_protocol("tcp") == "TCP"
    assert normalize_protocol("  UDP ") == "UDP"
    assert normalize_protocol("icmp") == "ICMP"
    assert normalize_protocol("icmpv6") == "ICMPv6"
    assert normalize_protocol("sctp") == "SCTP"

    # Numeric protocol IDs
    assert normalize_protocol(6) == "TCP"
    assert normalize_protocol("6") == "TCP"
    assert normalize_protocol(17) == "UDP"
    assert normalize_protocol(1) == "ICMP"
    assert normalize_protocol(58) == "ICMPv6"
    assert normalize_protocol(132) == "SCTP"

    # Unknown
    assert normalize_protocol("custom_proto_99") == "OTHER"
    assert normalize_protocol(None) == "OTHER"


def test_timestamp_normalization():
    # ISO strings
    dt1 = normalize_timestamp("2026-02-01T12:00:00Z")
    assert dt1.tzinfo == timezone.utc
    assert dt1.hour == 12

    # Unix timestamp
    dt2 = normalize_timestamp(1700000000)
    assert dt2.tzinfo == timezone.utc

    # Malformed timestamp
    with pytest.raises(ValueError):
        normalize_timestamp("not-a-timestamp")


def test_clean_numeric_nan_inf_guards():
    assert clean_numeric(math.nan, default=0.0) == 0.0
    assert clean_numeric(math.inf, default=0.0) == 0.0
    assert clean_numeric(-math.inf, default=0.0) == 0.0
    assert clean_numeric(-5.0, min_val=0.0, default=0.0) == 0.0
    assert clean_numeric(100.0, max_val=50.0) == 50.0
    assert clean_numeric(25.0) == 25.0


def test_tcp_flags_normalization():
    assert normalize_tcp_flags("syn,ack") == "SYN,ACK"
    assert normalize_tcp_flags(0x12) == "SYN,ACK"
    assert normalize_tcp_flags(None) is None


def test_feature_extraction_canonical():
    extractor = NetworkFeatureExtractor()
    event = NetworkEvent(
        event_id="EVT-TEST-001",
        timestamp=datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc),
        src_ip="192.168.1.100",
        dst_ip="10.0.0.1",
        src_port=49152,
        dst_port=443,
        protocol="TCP",
        duration=2.0,
        flow_bytes=2048,
        flow_packets=10,
        forward_bytes=1024,
        backward_bytes=1024,
        forward_packets=5,
        backward_packets=5,
        tcp_flags="SYN,ACK",
        flow_rate=1024.0,
        packet_rate=5.0
    )

    features = extractor.extract(event)
    assert "duration" in features
    assert "bytes_per_second" in features
    assert "packets_per_second" in features
    assert "forward_ratio" in features
    assert features["duration"] == 2.0
    assert features["bytes_per_second"] == 1024.0
    assert features["packets_per_second"] == 5.0
    assert features["forward_ratio"] == 0.5


def test_feature_extraction_zero_duration_guard():
    extractor = NetworkFeatureExtractor()
    event = NetworkEvent(
        event_id="EVT-TEST-002",
        timestamp=datetime(2026, 2, 1, 10, 0, 0, tzinfo=timezone.utc),
        src_ip="192.168.1.100",
        dst_ip="10.0.0.1",
        src_port=49152,
        dst_port=80,
        protocol="TCP",
        duration=0.0,  # Zero duration flow
        flow_bytes=100,
        flow_packets=2
    )

    features = extractor.extract(event)
    assert features["duration"] == 0.0
    # Avoid division by zero: rate defaults to 0.0 safely
    assert features["bytes_per_second"] == 0.0
    assert features["packets_per_second"] == 0.0
