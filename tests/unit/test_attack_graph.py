"""
Unit tests for Attack Evidence Graph and Pattern Matcher.
"""

from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hactm.storage.database import Base
from hactm.graph.builder import GraphBuilder
from hactm.graph.pattern_matcher import GraphPatternMatcher
from hactm.graph.models import NodeType, EdgeType


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_graph_node_and_edge_creation(db_session):
    builder = GraphBuilder(db_session)
    now = datetime.now(timezone.utc)

    ev_data = {
        "event_id": "ev_graph_1",
        "entity_id": "USER-999",
        "domain": "phishing",
        "risk_score": 0.85,
        "confidence": 0.9,
        "evidence": {"ip_address": "192.168.1.100", "email": "victim@company.com"},
        "timestamp": now,
    }

    nodes, edges = builder.add_evidence(ev_data)
    assert len(nodes) >= 3  # Evidence + User + IP + Email
    assert len(edges) >= 2  # Evidence -> User, Evidence -> IP, etc.

    # Bounded subgraph query
    sub = builder.get_entity_neighbors(entity_id="USER-999", k_hop=2)
    assert sub.total_nodes >= 2
    assert sub.truncated is False


def test_pattern_matcher_attack_chain_detection():
    matcher = GraphPatternMatcher(patterns_path="configs/attack_patterns.yaml")
    now = datetime.now(timezone.utc)

    # Coordinated 3-stage attack sequence
    events = [
        {"event_id": "ev1", "entity_id": "USER-100", "domain": "phishing", "event_type": "phishing_link_clicked", "timestamp": now, "confidence": 0.9},
        {"event_id": "ev2", "entity_id": "USER-100", "domain": "identity", "event_type": "new_device_login", "timestamp": now + timedelta(minutes=10), "confidence": 0.85},
        {"event_id": "ev3", "entity_id": "USER-100", "domain": "transaction", "event_type": "unusual_transfer", "timestamp": now + timedelta(minutes=25), "confidence": 0.95},
    ]

    candidates = matcher.evaluate_evidence_sequence(events, primary_entity_id="USER-100")
    assert len(candidates) >= 1
    c = candidates[0]
    assert c.pattern_id == "PHISH_AUTH_TRANSACTION"
    assert c.completeness == 1.0
    assert c.confidence > 0.8
    assert "ATTACK-CHAIN CANDIDATE" in c.explanation


def test_false_correlation_prevention():
    matcher = GraphPatternMatcher(patterns_path="configs/attack_patterns.yaml")
    now = datetime.now(timezone.utc)

    # Events from DIFFERENT entities should NOT trigger attack chain candidate for USER-A
    events = [
        {"event_id": "ev1", "entity_id": "USER-A", "domain": "phishing", "event_type": "phishing_link_clicked", "timestamp": now},
        {"event_id": "ev2", "entity_id": "USER-B", "domain": "identity", "event_type": "new_device_login", "timestamp": now + timedelta(minutes=10)},
        {"event_id": "ev3", "entity_id": "USER-C", "domain": "transaction", "event_type": "unusual_transfer", "timestamp": now + timedelta(minutes=25)},
    ]

    candidates = matcher.evaluate_evidence_sequence(events, primary_entity_id="USER-A")
    assert len(candidates) == 0  # Differing entities prevented false correlation
