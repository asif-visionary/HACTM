"""
Integration tests for IngestionPipeline, Idempotency, and Quarantine policies.
"""

from pathlib import Path
import pytest

from hactm.core.constants import IngestionPolicy
from hactm.core.errors import HACTMValidationError
from hactm.ingestion.pipeline import IngestionPipeline
from hactm.storage.models import IngestionErrorModel, SecurityEvidenceModel


def test_idempotent_ingestion(db_session, tmp_path):
    pipeline = IngestionPipeline(db_session)

    records = [
        {
            "event_id": "EVT-IDEMP-001",
            "agent_id": "AGENT-01",
            "entity_id": "IP:192.168.1.1",
            "event_type": "NETWORK",
            "timestamp": "2026-10-01T10:00:00Z",
            "risk_score": 0.5,
            "confidence": 0.9,
            "uncertainty": 0.1,
            "evidence": {"port": 80},
        },
        {
            "event_id": "EVT-IDEMP-002",
            "agent_id": "AGENT-01",
            "entity_id": "USER:alice",
            "event_type": "AUTHENTICATION",
            "timestamp": "2026-10-01T10:05:00Z",
            "risk_score": 0.2,
            "confidence": 0.95,
            "uncertainty": 0.05,
            "evidence": {"auth": "ok"},
        },
    ]

    # Run 1: Should insert 2 records
    res1 = pipeline.ingest_records(records, source_name="idemp_test", policy=IngestionPolicy.QUARANTINE_INVALID)
    assert res1.inserted == 2
    assert res1.duplicates == 0
    assert res1.invalid == 0

    # Run 2: Ingest exact same records -> Must NOT duplicate evidence
    res2 = pipeline.ingest_records(records, source_name="idemp_test", policy=IngestionPolicy.QUARANTINE_INVALID)
    assert res2.inserted == 0
    assert res2.duplicates == 2
    assert res2.invalid == 0

    # Verify total records in DB is strictly 2
    total_in_db = db_session.query(SecurityEvidenceModel).count()
    assert total_in_db == 2


def test_quarantine_invalid_policy(db_session, tmp_path):
    pipeline = IngestionPipeline(db_session)

    records = [
        {
            "event_id": "EVT-VALID-01",
            "agent_id": "AGENT-01",
            "entity_id": "HOST:srv-01",
            "event_type": "SYSTEM",
            "timestamp": "2026-10-01T10:00:00Z",
            "risk_score": 0.4,
            "confidence": 0.8,
            "uncertainty": 0.2,
            "evidence": {},
        },
        {
            "event_id": "EVT-INVALID-RISK",
            "agent_id": "AGENT-01",
            "event_type": "NETWORK",
            "timestamp": "2026-10-01T10:00:00Z",
            "risk_score": 2.5,  # Out of bounds!
            "evidence": {},
        },
        {
            "event_id": "",  # Missing event_id!
            "agent_id": "AGENT-01",
            "event_type": "NETWORK",
            "timestamp": "2026-10-01T10:00:00Z",
            "risk_score": 0.5,
            "evidence": {},
        },
    ]

    res = pipeline.ingest_records(records, source_name="quarantine_test", policy=IngestionPolicy.QUARANTINE_INVALID)
    assert res.inserted == 1
    assert res.invalid == 2
    assert res.quarantined == 2

    # Verify error entries in database
    errors = db_session.query(IngestionErrorModel).all()
    assert len(errors) == 2


def test_strict_policy_aborts_on_invalid(db_session):
    pipeline = IngestionPipeline(db_session)

    records = [
        {
            "event_id": "EVT-FAIL-01",
            "agent_id": "AGENT-01",
            "event_type": "NETWORK",
            "timestamp": "2026-10-01T10:00:00Z",
            "risk_score": 9.9,  # Invalid
        }
    ]

    with pytest.raises(HACTMValidationError):
        pipeline.ingest_records(records, source_name="strict_test", policy=IngestionPolicy.STRICT)


def test_sample_files_ingestion(db_session):
    """Verifies that the synthetic sample files ingest cleanly and quarantine expected invalid records."""
    pipeline = IngestionPipeline(db_session)

    csv_path = Path("data/sample/sample_evidence.csv")
    if csv_path.exists():
        res_csv = pipeline.ingest_file(csv_path, policy=IngestionPolicy.QUARANTINE_INVALID)
        assert res_csv.inserted > 0
        assert res_csv.quarantined > 0  # Expected due to invalid rows embedded for testing

    json_path = Path("data/sample/sample_evidence.json")
    if json_path.exists():
        res_json = pipeline.ingest_file(json_path, policy=IngestionPolicy.QUARANTINE_INVALID)
        assert res_json.inserted > 0

    jsonl_path = Path("data/sample/sample_evidence.jsonl")
    if jsonl_path.exists():
        res_jsonl = pipeline.ingest_file(jsonl_path, policy=IngestionPolicy.QUARANTINE_INVALID)
        assert res_jsonl.inserted > 0
        assert res_jsonl.quarantined >= 1  # Malformed line isolated
