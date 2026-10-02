"""
Unit tests for Adaptive Memory & Graph Adaptive Evidence Memory.
"""

from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hactm.storage.database import Base
from hactm.memory.engine import AdaptiveEvidenceMemory
from hactm.memory.models import MemoryTier, MemoryRetrievalQuery, MemoryImportanceScorer


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_importance_scorer():
    scorer = MemoryImportanceScorer()
    now = datetime.now(timezone.utc)
    # High risk, high confidence, critical severity -> high importance
    score1 = scorer.calculate(
        risk_score=0.9,
        confidence=0.95,
        severity="CRITICAL",
        timestamp=now,
    )
    assert 0.7 <= score1 <= 1.0

    # Low risk, low confidence, low severity -> low importance
    score2 = scorer.calculate(
        risk_score=0.1,
        confidence=0.3,
        severity="LOW",
        timestamp=now - timedelta(hours=20),
    )
    assert score2 < score1


def test_adaptive_memory_store_and_retrieve(db_session):
    mem = AdaptiveEvidenceMemory(db_session)
    now = datetime.now(timezone.utc)

    entry = mem.store(
        evidence_id="ev_001",
        entity_ids=["USER-001"],
        event_type="suspicious_login",
        domain="identity",
        timestamp=now,
        risk_score=0.8,
        confidence=0.9,
        uncertainty=0.1,
        severity="HIGH",
        metadata={"password": "secret_password123", "user_agent": "Mozilla/5.0"},
    )

    assert entry.memory_tier == MemoryTier.HOT
    assert entry.importance_score > 0.5
    # Check privacy redaction
    assert entry.metadata["password"] == "[REDACTED_PRIVACY]"
    assert entry.metadata["user_agent"] == "Mozilla/5.0"

    retrieved = mem.retrieve(MemoryRetrievalQuery(entity_id="USER-001"))
    assert len(retrieved) == 1
    assert retrieved[0].evidence_id == "ev_001"


def test_memory_promotion_and_demotion(db_session):
    mem = AdaptiveEvidenceMemory(db_session)
    now = datetime.now(timezone.utc)

    entry = mem.store(
        evidence_id="ev_002",
        entity_ids=["USER-002"],
        event_type="phishing_click",
        domain="phishing",
        timestamp=now,
        risk_score=0.7,
        confidence=0.8,
        uncertainty=0.1,
    )

    # Demote HOT -> WARM
    ok_dem = mem.demote(entry.memory_id, MemoryTier.WARM, reason="TEST_DEMOTION")
    assert ok_dem is True
    res = mem.repo.get_by_id(entry.memory_id)
    assert res.memory_tier == "WARM"

    # Promote WARM -> HOT
    ok_prom = mem.promote(entry.memory_id, MemoryTier.HOT, reason="TEST_PROMOTION")
    assert ok_prom is True
    res2 = mem.repo.get_by_id(entry.memory_id)
    assert res2.memory_tier == "HOT"


def test_memory_redundancy_deduplication(db_session):
    mem = AdaptiveEvidenceMemory(db_session)
    now = datetime.now(timezone.utc)

    # Ingest same evidence ID twice
    entry1 = mem.store(
        evidence_id="ev_dup_100",
        entity_ids=["USER-100"],
        event_type="network_anomaly",
        domain="network",
        timestamp=now,
        risk_score=0.5,
        confidence=0.8,
        uncertainty=0.1,
    )

    entry2 = mem.store(
        evidence_id="ev_dup_100",
        entity_ids=["USER-100"],
        event_type="network_anomaly",
        domain="network",
        timestamp=now,
        risk_score=0.5,
        confidence=0.8,
        uncertainty=0.1,
    )

    assert entry1.memory_id == entry2.memory_id
    retrieved = mem.retrieve(MemoryRetrievalQuery(entity_id="USER-100"))
    assert len(retrieved) == 1
