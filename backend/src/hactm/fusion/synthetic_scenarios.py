"""
Synthetic Scenario Generators for Evidence Fusion Engine Evaluation.
Constructs controlled multi-domain evidence streams, negative scenarios, and false correlation tests.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple


class FusionSyntheticScenarioGenerator:
    """Generates controlled synthetic cross-domain evidence sets for research evaluation."""

    @staticmethod
    def generate_scenario_1_single_domain(entity_id: str = "USER-101") -> List[Dict[str, Any]]:
        """Scenario 1: Single domain evidence (Phishing only)."""
        now = datetime.now(timezone.utc)
        return [{
            "event_id": "EV-PHISH-001",
            "agent_id": "phishing-intelligence-agent",
            "entity_id": entity_id,
            "event_type": "SUSPICIOUS_EMAIL",
            "timestamp": now.isoformat(),
            "risk_score": 0.82,
            "confidence": 0.90,
            "uncertainty": 0.10,
            "severity": "HIGH",
            "evidence": {"sender": "attacker@evil.com", "subject": "Urgent Security Verification"},
            "source": "synthetic_email_loader",
            "dataset": "synthetic_evidence_fusion",
        }]

    @staticmethod
    def generate_scenario_2_two_domain(entity_id: str = "USER-102") -> List[Dict[str, Any]]:
        """Scenario 2: Two domain correlated evidence (Phishing + Identity)."""
        now = datetime.now(timezone.utc)
        return [
            {
                "event_id": "EV-PHISH-002",
                "agent_id": "phishing-intelligence-agent",
                "entity_id": entity_id,
                "event_type": "SUSPICIOUS_EMAIL",
                "timestamp": (now - timedelta(minutes=10)).isoformat(),
                "risk_score": 0.85,
                "confidence": 0.92,
                "uncertainty": 0.08,
                "severity": "HIGH",
                "evidence": {"url": "http://login-verify-fake.com"},
            },
            {
                "event_id": "EV-AUTH-002",
                "agent_id": "identity-authentication-agent",
                "entity_id": entity_id,
                "event_type": "NEW_DEVICE_LOGIN",
                "timestamp": now.isoformat(),
                "risk_score": 0.78,
                "confidence": 0.88,
                "uncertainty": 0.12,
                "severity": "HIGH",
                "evidence": {"device_id": "DEV-UNKNOWN-99", "source_ip": "198.51.100.45"},
            }
        ]

    @staticmethod
    def generate_scenario_3_three_domain(entity_id: str = "USER-103") -> List[Dict[str, Any]]:
        """Scenario 3: Three domain correlated sequence (Phishing + Identity + Transaction)."""
        now = datetime.now(timezone.utc)
        return [
            {
                "event_id": "EV-PHISH-003",
                "agent_id": "phishing-intelligence-agent",
                "entity_id": entity_id,
                "event_type": "SUSPICIOUS_EMAIL",
                "timestamp": (now - timedelta(minutes=15)).isoformat(),
                "risk_score": 0.88,
                "confidence": 0.93,
                "uncertainty": 0.07,
                "severity": "HIGH",
                "evidence": {"subject": "Urgent Bank Wire Verification"},
            },
            {
                "event_id": "EV-AUTH-003",
                "agent_id": "identity-authentication-agent",
                "entity_id": entity_id,
                "event_type": "FAILED_LOGIN_SPIKE",
                "timestamp": (now - timedelta(minutes=8)).isoformat(),
                "risk_score": 0.82,
                "confidence": 0.89,
                "uncertainty": 0.11,
                "severity": "HIGH",
                "evidence": {"failed_attempts": 12},
            },
            {
                "event_id": "EV-TX-003",
                "agent_id": "transaction-security-agent",
                "entity_id": entity_id,
                "event_type": "ANOMALOUS_TRANSACTION",
                "timestamp": now.isoformat(),
                "risk_score": 0.91,
                "confidence": 0.95,
                "uncertainty": 0.05,
                "severity": "CRITICAL",
                "evidence": {"amount": 48500.0, "recipient_id": "RECP-UNSEEN-88"},
            }
        ]

    @staticmethod
    def generate_scenario_4_conflicting(entity_id: str = "USER-104") -> List[Dict[str, Any]]:
        """Scenario 4: Conflicting evidence (High Phishing vs Low Auth)."""
        now = datetime.now(timezone.utc)
        return [
            {
                "event_id": "EV-PHISH-004",
                "agent_id": "phishing-intelligence-agent",
                "entity_id": entity_id,
                "event_type": "SUSPICIOUS_EMAIL",
                "timestamp": (now - timedelta(minutes=5)).isoformat(),
                "risk_score": 0.85,
                "confidence": 0.90,
                "uncertainty": 0.10,
                "severity": "HIGH",
                "evidence": {"subject": "Credential Update Request"},
            },
            {
                "event_id": "EV-AUTH-004",
                "agent_id": "identity-authentication-agent",
                "entity_id": entity_id,
                "event_type": "NORMAL_LOGIN",
                "timestamp": now.isoformat(),
                "risk_score": 0.10,
                "confidence": 0.95,
                "uncertainty": 0.05,
                "severity": "LOW",
                "evidence": {"authentication_status": "SUCCESS", "two_factor_used": "HARDWARE_KEY"},
            }
        ]

    @staticmethod
    def generate_scenario_5_redundant(entity_id: str = "USER-105") -> List[Dict[str, Any]]:
        """Scenario 5: Redundant evidence (3 network detectors observing same underlying flow)."""
        now = datetime.now(timezone.utc)
        return [
            {
                "event_id": "EV-NET-005-A",
                "agent_id": "network-security-agent",
                "entity_id": entity_id,
                "event_type": "PORT_SCAN",
                "timestamp": now.isoformat(),
                "risk_score": 0.75,
                "confidence": 0.85,
                "uncertainty": 0.15,
                "severity": "MEDIUM",
                "source_record_id": "FLOW-REC-9999",
                "raw_event_id": "FLOW-REC-9999",
            },
            {
                "event_id": "EV-NET-005-B",
                "agent_id": "network-security-agent",
                "entity_id": entity_id,
                "event_type": "PORT_SCAN",
                "timestamp": now.isoformat(),
                "risk_score": 0.72,
                "confidence": 0.82,
                "uncertainty": 0.18,
                "severity": "MEDIUM",
                "source_record_id": "FLOW-REC-9999",
                "raw_event_id": "FLOW-REC-9999",
            },
            {
                "event_id": "EV-NET-005-C",
                "agent_id": "network-security-agent",
                "entity_id": entity_id,
                "event_type": "PORT_SCAN",
                "timestamp": now.isoformat(),
                "risk_score": 0.74,
                "confidence": 0.84,
                "uncertainty": 0.16,
                "severity": "MEDIUM",
                "source_record_id": "FLOW-REC-9999",
                "raw_event_id": "FLOW-REC-9999",
            }
        ]

    @staticmethod
    def generate_false_correlation_unrelated_entities() -> Tuple[str, List[Dict[str, Any]]]:
        """Negative Scenario D/E: High-risk events occurring within 1 minute but involving distinct entities."""
        now = datetime.now(timezone.utc)
        evidence = [
            {
                "event_id": "EV-UNREL-1",
                "agent_id": "phishing-intelligence-agent",
                "entity_id": "USER-ALPHA",
                "event_type": "SUSPICIOUS_EMAIL",
                "timestamp": now.isoformat(),
                "risk_score": 0.88,
                "confidence": 0.90,
                "severity": "HIGH",
            },
            {
                "event_id": "EV-UNREL-2",
                "agent_id": "identity-authentication-agent",
                "entity_id": "USER-BETA",
                "event_type": "NEW_DEVICE_LOGIN",
                "timestamp": now.isoformat(),
                "risk_score": 0.85,
                "confidence": 0.90,
                "severity": "HIGH",
            },
            {
                "event_id": "EV-UNREL-3",
                "agent_id": "transaction-security-agent",
                "entity_id": "ACCOUNT-GAMMA",
                "event_type": "ANOMALOUS_TRANSACTION",
                "timestamp": now.isoformat(),
                "risk_score": 0.90,
                "confidence": 0.95,
                "severity": "CRITICAL",
            }
        ]
        return "USER-ALPHA", evidence
