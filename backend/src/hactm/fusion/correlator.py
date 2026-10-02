"""
Cross-Domain Evidence Correlator for Evidence Fusion Fusion.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from hactm.fusion.models import CorrelationType


class CrossDomainEvidenceCorrelator:
    """Correlates evidence items across entities, sessions, time windows, and multi-domain patterns."""

    def __init__(self, default_window_seconds: float = 1800.0):
        self.default_window_seconds = default_window_seconds

    def correlate_entities(self, primary_entity_id: str, evidence_list: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str], CorrelationType]:
        """
        Filters and correlates evidence items related to primary_entity_id.
        Supported relationships:
            - Exact entity_id match (ENTITY_MATCH)
            - Same session_id (SESSION_MATCH)
            - Same correlation_id (CORRELATION_ID_MATCH)
            - Explicit account_id, device_id, IP context
        """
        correlated_evidence = []
        related_entities = set()
        primary_correlation_type = CorrelationType.ENTITY_MATCH

        for item in evidence_list:
            ent = item.get("entity_id")
            session = item.get("session_id")
            corr_id = item.get("correlation_id")
            evidence_data = item.get("evidence", {}) or {}

            matched = False

            if ent == primary_entity_id:
                matched = True
                primary_correlation_type = CorrelationType.ENTITY_MATCH
            elif session and session == primary_entity_id:
                matched = True
                primary_correlation_type = CorrelationType.SESSION_MATCH
            elif corr_id and corr_id == primary_entity_id:
                matched = True
                primary_correlation_type = CorrelationType.CORRELATION_ID_MATCH
            elif evidence_data.get("user_id") == primary_entity_id or evidence_data.get("account_id") == primary_entity_id:
                matched = True
                primary_correlation_type = CorrelationType.ENTITY_MATCH
            elif evidence_data.get("device_id") == primary_entity_id:
                matched = True
                primary_correlation_type = CorrelationType.SHARED_DEVICE
            elif evidence_data.get("source_ip") == primary_entity_id or evidence_data.get("src_ip") == primary_entity_id:
                matched = True
                primary_correlation_type = CorrelationType.SHARED_IP

            if matched:
                correlated_evidence.append(item)
                if ent and ent != primary_entity_id:
                    related_entities.add(ent)
                if evidence_data.get("user_id") and evidence_data.get("user_id") != primary_entity_id:
                    related_entities.add(evidence_data.get("user_id"))
                if evidence_data.get("account_id") and evidence_data.get("account_id") != primary_entity_id:
                    related_entities.add(evidence_data.get("account_id"))

        return correlated_evidence, list(related_entities), primary_correlation_type

    def correlate_temporal(
        self,
        evidence_list: List[Dict[str, Any]],
        window_seconds: float = None,
        reference_time: Optional[datetime] = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Filters evidence items within the temporal correlation window relative to reference_time.
        Computes max temporal distance in seconds.
        """
        if window_seconds is None:
            window_seconds = self.default_window_seconds

        if reference_time is None:
            reference_time = datetime.now(timezone.utc)
        elif reference_time.tzinfo is None:
            reference_time = reference_time.replace(tzinfo=timezone.utc)

        temporally_correlated = []
        max_delta = 0.0

        for item in evidence_list:
            ts = item.get("timestamp")
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    continue

            if isinstance(ts, datetime):
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)

                delta = abs((reference_time - ts).total_seconds())
                if delta <= window_seconds:
                    item["temporal_distance_seconds"] = delta
                    temporally_correlated.append(item)
                    if delta > max_delta:
                        max_delta = delta

        return temporally_correlated, max_delta

    def detect_cross_domain_patterns(self, evidence_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifies cross-domain correlation patterns (e.g., Phishing -> Auth Anomaly -> Transaction Anomaly).
        Returns pattern matches as MULTI_DOMAIN_SECURITY_PATTERN (NOT CONFIRMED_ATTACK_CHAIN).
        """
        domains_present = set(item.get("domain", "generic") for item in evidence_list)
        patterns = []

        # Declarative pattern: PHISH_AUTH_TX
        if {"phishing", "identity", "transaction"}.issubset(domains_present):
            patterns.append({
                "pattern_id": "PHISH_AUTH_TX",
                "pattern_name": "Multi-Domain Security Sequence (Phishing + Auth Anomaly + Transaction Anomaly)",
                "domains": ["phishing", "identity", "transaction"],
                "classification": "MULTI_DOMAIN_SECURITY_PATTERN",
                "explanation": "Independent security evidence observed across Phishing, Identity, and Transaction domains within correlation window.",
            })
        elif {"phishing", "identity"}.issubset(domains_present):
            patterns.append({
                "pattern_id": "PHISH_AUTH",
                "pattern_name": "Phishing & Authentication Sequence",
                "domains": ["phishing", "identity"],
                "classification": "MULTI_DOMAIN_SECURITY_PATTERN",
                "explanation": "Independent evidence observed across Phishing and Identity domains.",
            })
        elif {"identity", "transaction"}.issubset(domains_present):
            patterns.append({
                "pattern_id": "AUTH_TX",
                "pattern_name": "Authentication & Transaction Sequence",
                "domains": ["identity", "transaction"],
                "classification": "MULTI_DOMAIN_SECURITY_PATTERN",
                "explanation": "Independent evidence observed across Identity and Transaction domains.",
            })
        elif {"network", "identity"}.issubset(domains_present):
            patterns.append({
                "pattern_id": "NET_AUTH",
                "pattern_name": "Network & Identity Sequence",
                "domains": ["network", "identity"],
                "classification": "MULTI_DOMAIN_SECURITY_PATTERN",
                "explanation": "Independent evidence observed across Network and Identity domains.",
            })

        return patterns
