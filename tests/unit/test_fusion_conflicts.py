"""
Unit Tests for Evidence Conflict Detector.
"""

from hactm.fusion.conflict_detector import EvidenceConflictDetector
from hactm.fusion.models import ConflictType


def test_detect_risk_disagreement_conflict():
    detector = EvidenceConflictDetector(risk_disagreement_threshold=0.35)
    evidence_list = [
        {"event_id": "E1", "domain": "phishing", "risk_score": 0.85, "entity_id": "USER-104"},
        {"event_id": "E2", "domain": "identity", "risk_score": 0.10, "entity_id": "USER-104"},
    ]
    conflicts, supporting, conflicting = detector.detect_conflicts("FUSE-104", evidence_list)
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == ConflictType.RISK_DISAGREEMENT
    assert conflicts[0].risk_difference == 0.75
