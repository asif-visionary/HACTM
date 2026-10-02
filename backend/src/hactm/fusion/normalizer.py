"""
Evidence Normalizer for Cross-Agent Fusion.
"""

from typing import Dict, Any, List


class CrossDomainEvidenceNormalizer:
    """Normalizes domain SecurityEvidence objects for cross-domain fusion."""

    def normalize(self, evidence_item: Any) -> Dict[str, Any]:
        """Normalizes a SecurityEvidence object or dict into a standard fusion item dictionary."""
        if hasattr(evidence_item, "to_dict"):
            data = evidence_item.to_dict()
        elif hasattr(evidence_item, "__dict__"):
            data = vars(evidence_item)
        elif isinstance(evidence_item, dict):
            data = dict(evidence_item)
        else:
            raise ValueError(f"Unsupported evidence item type: {type(evidence_item)}")

        # Ensure mandatory fields exist with safe defaults
        normalized = {
            "event_id": str(data.get("event_id", "")),
            "agent_id": str(data.get("agent_id", "unknown-agent")),
            "entity_id": str(data.get("entity_id", "UNKNOWN")),
            "event_type": str(data.get("event_type", "GENERIC_SECURITY_EVENT")),
            "timestamp": data.get("timestamp"),
            "risk_score": float(data.get("risk_score", 0.0)),
            "confidence": float(data.get("confidence", 1.0)),
            "uncertainty": float(data.get("uncertainty", 0.0)),
            "severity": str(data.get("severity", "LOW")).upper(),
            "evidence": data.get("evidence", {}),
            "source": data.get("source"),
            "dataset": data.get("dataset"),
            "session_id": data.get("session_id"),
            "correlation_id": data.get("correlation_id"),
            "model_version": data.get("model_version"),
            "detector_version": data.get("detector_version"),
            "schema_version": data.get("schema_version", "1.0.0"),
            "raw_event_id": data.get("raw_event_id"),
            "source_record_id": data.get("source_record_id"),
        }

        # Map agent ID to domain classification
        normalized["domain"] = self.map_agent_to_domain(normalized["agent_id"])
        return normalized

    @staticmethod
    def map_agent_to_domain(agent_id: str) -> str:
        agent = agent_id.lower()
        if "network" in agent:
            return "network"
        elif "phishing" in agent:
            return "phishing"
        elif "uba" in agent or "behavior" in agent:
            return "uba"
        elif "identity" in agent or "auth" in agent:
            return "identity"
        elif "transaction" in agent or "payment" in agent:
            return "transaction"
        return "generic"
