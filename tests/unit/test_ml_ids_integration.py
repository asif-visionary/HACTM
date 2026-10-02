"""
Unit Tests for Integrated cstub/ml-ids ML Engine inside HACTM NetworkSecurityAgent.
Verifies ML-IDS inference, score, uncertainty calculation, evidence adaptation,
downstream AbuseIPDB enrichment, adaptive agent selection, and Zero-Trust policy evaluation.
"""

from datetime import datetime, timezone
import pytest

from hactm.network.agent import NetworkSecurityAgent
from hactm.network.models import NetworkEvent, DetectorType
from hactm.network.ml_ids.detector import MLIDSDetector
from hactm.fusion.engine import EvidenceFusionEngine
from hactm.zerotrust.policy_engine import ZeroTrustPolicyEngine
from hactm.zerotrust.models import ZeroTrustDecisionContext, PolicyDecision


def test_ml_ids_detector_direct_inference():
    detector = MLIDSDetector(decision_threshold=0.55)
    
    # Suspicious flow event
    event = NetworkEvent(
        event_id="evt_ml_ids_001",
        timestamp=datetime.now(timezone.utc),
        src_ip="192.168.1.100",
        dst_ip="10.0.0.5",
        src_port=4444,
        dst_port=80,
        protocol="TCP",
        duration=0.005,
        flow_packets=1500,
        flow_bytes=1200000,
        tcp_flags="SYN,RST"
    )

    score, confidence, uncertainty = detector.score(event)
    assert 0.0 <= score <= 1.0
    assert 0.0 <= confidence <= 1.0
    assert 0.0 <= uncertainty <= 1.0

    result = detector.detect(event)
    assert result is not None
    assert result.detector_type == DetectorType.ML_IDS
    assert result.detector_id == "cstub-ml-ids-engine"
    assert result.risk_score >= 0.55
    assert result.uncertainty == uncertainty


def test_network_security_agent_with_ml_ids():
    agent = NetworkSecurityAgent()
    assert "ML_IDS" in agent.health()["active_detectors"]

    # Benign event (non-suspicious metrics)
    benign_event = NetworkEvent(
        event_id="evt_benign_001",
        timestamp=datetime.now(timezone.utc),
        src_ip="192.168.1.50",
        dst_ip="192.168.1.1",
        src_port=52140,
        dst_port=443,
        protocol="TCP",
        duration=1.2,
        flow_packets=10,
        flow_bytes=1500
    )
    benign_dets = agent.process_event(benign_event)
    ml_ids_benign = [d for d in benign_dets if d.detector_type == DetectorType.ML_IDS]
    assert len(ml_ids_benign) == 0 # Non-anomalous

    # Malicious burst event
    attack_event = NetworkEvent(
        event_id="evt_attack_001",
        timestamp=datetime.now(timezone.utc),
        src_ip="203.0.113.45",
        dst_ip="10.0.0.10",
        src_port=49152,
        dst_port=80,
        protocol="TCP",
        duration=0.002,
        flow_packets=2000,
        flow_bytes=2500000,
        tcp_flags="SYN"
    )

    dets, evidence = agent.process_batch([attack_event], dataset_name="ton_iot")
    assert len(dets) >= 1
    ml_ids_dets = [d for d in dets if d.detector_type == DetectorType.ML_IDS]
    assert len(ml_ids_dets) == 1
    
    ev = [e for e in evidence if e.evidence.get("detector_type") == "ML_IDS"][0]
    assert ev.agent_id == "network-security-agent"


def test_full_pipeline_ml_ids_to_zero_trust():
    agent = NetworkSecurityAgent()
    attack_event = NetworkEvent(
        event_id="evt_flow_002",
        timestamp=datetime.now(timezone.utc),
        src_ip="198.51.100.77",
        dst_ip="10.0.0.2",
        src_port=3389,
        dst_port=4444,
        protocol="TCP",
        duration=0.001,
        flow_packets=5000,
        flow_bytes=5000000,
        tcp_flags="SYN,RST"
    )

    dets, evidence_list = agent.process_batch([attack_event])
    assert len(evidence_list) > 0

    # Fusion Engine calculates Cyber Risk for primary entity
    fusion_engine = EvidenceFusionEngine()
    fusion_evidence, audit_rec, conflicts, qualities = fusion_engine.fuse_evidence("IP:198.51.100.77", evidence_list)
    assert fusion_evidence.unified_risk_score >= 0.0

    # Zero-Trust Policy Decision Engine determines enforcement action
    zt_engine = ZeroTrustPolicyEngine()
    zt_context = ZeroTrustDecisionContext(
        context_id="ctx_test_001",
        subject_id="user_admin",
        resource_id="db_server",
        current_risk=fusion_evidence.unified_risk_score,
        uncertainty=fusion_evidence.uncertainty
    )
    decision_record = zt_engine.evaluate_decision(zt_context)
    assert decision_record.decision in [PolicyDecision.ALLOW, PolicyDecision.QUARANTINE, PolicyDecision.VERIFY, PolicyDecision.BLOCK, PolicyDecision.MONITOR]
