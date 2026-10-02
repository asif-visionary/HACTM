"""
Unit tests for Temporal Evidence Engine.
"""

from datetime import datetime, timezone, timedelta
import pytest

from hactm.temporal.engine import TemporalEvidenceEngine
from hactm.temporal.models import TemporalRelationshipType


def test_temporal_event_ordering():
    engine = TemporalEvidenceEngine()
    now = datetime.now(timezone.utc)

    ev1 = {"event_id": "ev1", "timestamp": (now + timedelta(minutes=10)).isoformat()}
    ev2 = {"event_id": "ev2", "timestamp": now.isoformat()}
    ev3 = {"event_id": "ev3", "timestamp": (now + timedelta(minutes=5)).isoformat()}

    ordered = engine.order_events([ev1, ev2, ev3])
    ordered_ids = [e["event_id"] for e in ordered]
    assert ordered_ids == ["ev2", "ev3", "ev1"]


def test_temporal_distance_and_classification():
    engine = TemporalEvidenceEngine()
    now = datetime.now(timezone.utc)

    ev1 = {"event_id": "e1", "timestamp": now}
    ev2 = {"event_id": "e2", "timestamp": now + timedelta(minutes=15)}

    dist = engine.calculate_temporal_distance(ev1, ev2)
    assert dist == 900.0

    rel = engine.classify_relationship(ev1, ev2, window_seconds=1800.0)
    assert rel.relationship_type == TemporalRelationshipType.WITHIN_WINDOW


def test_temporal_sequence_and_burst_detection():
    engine = TemporalEvidenceEngine()
    now = datetime.now(timezone.utc)

    events = [
        {"event_id": "e1", "domain": "phishing", "timestamp": now},
        {"event_id": "e2", "domain": "identity", "timestamp": now + timedelta(minutes=5)},
        {"event_id": "e3", "domain": "transaction", "timestamp": now + timedelta(minutes=12)},
    ]

    sequences = engine.detect_sequences(events, max_gap_seconds=1800.0)
    assert len(sequences) >= 1
    assert "phishing" in sequences[0].domains
    assert "identity" in sequences[0].domains

    # Test burst detection
    burst_events = [
        {"event_id": f"b{i}", "timestamp": now + timedelta(seconds=i*2)}
        for i in range(6)
    ]
    bursts = engine.detect_bursts(burst_events, burst_window_seconds=60.0, min_events=5)
    assert len(bursts) == 1
    assert bursts[0]["event_count"] == 6
