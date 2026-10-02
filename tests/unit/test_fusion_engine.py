"""
Unit Tests for Evidence Fusion Engine.
"""

from datetime import datetime, timezone
from hactm.fusion.engine import EvidenceFusionEngine
from hactm.fusion.synthetic_scenarios import FusionSyntheticScenarioGenerator


def test_fuse_evidence_three_domain_scenario():
    engine = EvidenceFusionEngine()
    sc3 = FusionSyntheticScenarioGenerator.generate_scenario_3_three_domain("USER-103")
    fusion, audit, conflicts, qualities = engine.fuse_evidence("USER-103", sc3)

    assert fusion.primary_entity_id == "USER-103"
    assert fusion.evidence_count == 3
    assert fusion.unique_domain_count == 3
    assert fusion.unified_risk_score > 0.85
    assert fusion.confidence > 0.70
    assert "UNIFIED CYBER RISK" in fusion.explanation
    assert len(qualities) == 3


def test_fuse_evidence_deduplication():
    engine = EvidenceFusionEngine()
    sc5 = FusionSyntheticScenarioGenerator.generate_scenario_5_redundant("USER-105")
    fusion, audit, conflicts, qualities = engine.fuse_evidence("USER-105", sc5)

    assert fusion.evidence_count == 1
    assert fusion.redundant_evidence_count == 2
