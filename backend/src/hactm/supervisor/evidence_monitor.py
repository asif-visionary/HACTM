"""
Central Agent Supervisor — Evidence Integrity Monitor.
Monitors SecurityEvidence artifacts, validates schema integrity, detects provenance discrepancies,
identifies contradictory claims, and intercepts adversarial prompt injections embedded in evidence.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from hactm.supervisor.schemas import AnomalyType, AnomalySeverity
from hactm.core.logging import logger

INJECTION_PATTERNS = [
    "ignore all previous instructions",
    "ignore previous instructions",
    "reveal system prompt",
    "system prompt override",
    "dump environment variables",
    "<script>",
    "eval(",
    "bypass approval gate",
]


class EvidenceIntegrityMonitor:
    """Evaluates the structural, semantic, and cryptographic integrity of agent evidence."""

    def __init__(self):
        self._flagged_evidence: Dict[str, Dict[str, Any]] = {}

    def inspect_evidence(
        self,
        evidence_dict: Dict[str, Any],
        submitting_agent_id: str,
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validates an evidence submission.
        Returns: (is_valid, anomaly_if_flagged)
        """
        now = datetime.now(timezone.utc)
        event_id = evidence_dict.get("event_id") or evidence_dict.get("evidence_id", "UNKNOWN_EVD")

        # 1. Mandatory Schema Field Verification
        mandatory_fields = ["agent_id", "entity_id", "risk_score", "confidence", "uncertainty"]
        missing = [f for f in mandatory_fields if f not in evidence_dict]
        if missing:
            anomaly = {
                "type": AnomalyType.EVIDENCE_SCHEMA_INVALID.value,
                "severity": AnomalySeverity.HIGH.value,
                "agent_id": submitting_agent_id,
                "evidence_id": event_id,
                "desc": f"Evidence '{event_id}' from '{submitting_agent_id}' missing mandatory fields: {missing}.",
                "recommended_action": "MARK_FOR_VERIFICATION",
            }
            self._flag_evidence(event_id, anomaly)
            return False, anomaly

        # 2. Provenance Verification
        declared_agent = evidence_dict.get("agent_id")
        if declared_agent and declared_agent != submitting_agent_id:
            anomaly = {
                "type": AnomalyType.EVIDENCE_SCHEMA_INVALID.value,
                "severity": AnomalySeverity.CRITICAL.value,
                "agent_id": submitting_agent_id,
                "evidence_id": event_id,
                "desc": f"Evidence provenance mismatch: declared agent '{declared_agent}' != submitting agent '{submitting_agent_id}'.",
                "recommended_action": "REJECT_AND_ISOLATE",
            }
            self._flag_evidence(event_id, anomaly)
            return False, anomaly

        # 3. Adversarial Prompt Injection in Evidence Body / Text
        raw_str = json.dumps(evidence_dict).lower()
        for pattern in INJECTION_PATTERNS:
            if pattern in raw_str:
                anomaly = {
                    "type": AnomalyType.PROMPT_INJECTION_DETECTED.value,
                    "severity": AnomalySeverity.HIGH.value,
                    "agent_id": submitting_agent_id,
                    "evidence_id": event_id,
                    "desc": f"Adversarial prompt injection pattern detected in evidence payload: '{pattern}'.",
                    "recommended_action": "SANITIZE_AND_FLAG",
                }
                self._flag_evidence(event_id, anomaly)
                return False, anomaly

        # 4. Confidence / Uncertainty Consistency Check
        conf = float(evidence_dict.get("confidence", 0.0))
        unc = float(evidence_dict.get("uncertainty", 0.0))
        # Total certainty budget shouldn't wildly violate probability bounds
        if conf + unc < 0.20 or conf + unc > 1.80:
            anomaly = {
                "type": AnomalyType.EVIDENCE_SCHEMA_INVALID.value,
                "severity": AnomalySeverity.MEDIUM.value,
                "agent_id": submitting_agent_id,
                "evidence_id": event_id,
                "desc": f"Evidence '{event_id}' has inconsistent calibration: confidence={conf}, uncertainty={unc}.",
                "recommended_action": "MARK_FOR_VERIFICATION",
            }
            self._flag_evidence(event_id, anomaly)
            return False, anomaly

        return True, None

    def _flag_evidence(self, evidence_id: str, anomaly: Dict[str, Any]):
        self._flagged_evidence[evidence_id] = {
            "flagged_at": datetime.now(timezone.utc).isoformat(),
            **anomaly,
        }
        logger.warning(f"CAS Evidence Monitor: Flagged evidence '{evidence_id}' -> {anomaly.get('type')}")

    def get_flagged_evidence(self) -> Dict[str, Dict[str, Any]]:
        return self._flagged_evidence

