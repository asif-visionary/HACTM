"""
False-Alarm, Missing-Data, and Adversarial-Input Safeguards for HACTM.
Provides explicit uncertainty calibration, missing data handling, contradictory evidence preservation,
and prompt injection defense.
"""

from typing import Dict, List, Any, Optional, Tuple
from hactm.core.logging import logger


class EvidenceSafeguardsEngine:
    """Core reliability and resilience safeguards engine."""

    def handle_missing_data(
        self,
        evidence_items: List[Dict[str, Any]],
        required_fields: List[str],
    ) -> Dict[str, Any]:
        """
        Validates evidence items for missing fields.
        CRITICAL RULE: Missing evidence is NEVER treated as safety.
        Missing data increases predictive uncertainty and applies an uncertainty penalty.
        """
        valid_items = []
        missing_reports = []
        total_missing_count = 0

        for item in evidence_items:
            item_missing = [f for f in required_fields if f not in item or item[f] is None]
            if item_missing:
                total_missing_count += len(item_missing)
                missing_reports.append({
                    "event_id": item.get("event_id", "UNKNOWN"),
                    "missing_fields": item_missing,
                })
            else:
                valid_items.append(item)

        # Compute uncertainty penalty: more missing required fields -> higher uncertainty
        missing_penalty = min(0.50, total_missing_count * 0.15)

        return {
            "valid_evidence_count": len(valid_items),
            "missing_reports": missing_reports,
            "has_missing_data": total_missing_count > 0,
            "uncertainty_penalty": missing_penalty,
            "message": f"Processed {len(evidence_items)} items. Found missing fields in {len(missing_reports)} items. Applied uncertainty penalty: +{missing_penalty:.2f}" if total_missing_count > 0 else "All required evidence fields present.",
        }

    def process_contradictory_evidence(
        self,
        evidence_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Preserves contradictory evidence rather than discarding it without explanation.
        Categorizes items into supporting vs. contradicting based on risk thresholds or agent claims.
        """
        supporting = []
        contradicting = []

        for item in evidence_items:
            risk = item.get("risk_score", 0.0)
            confidence = item.get("confidence", 0.5)
            # High risk or explicit threat indicator -> supporting threat hypothesis
            if risk >= 0.50 and confidence >= 0.40:
                supporting.append(item)
            else:
                # Low risk or benign signal -> contradicting threat hypothesis
                contradicting.append(item)

        conflict_level = 0.0
        if supporting and contradicting:
            # High contradiction if both strong supporting and strong contradicting evidence exist
            conflict_level = min(1.0, (len(supporting) * len(contradicting)) / ((len(evidence_items) / 2) ** 2 or 1))

        return {
            "supporting_count": len(supporting),
            "contradicting_count": len(contradicting),
            "supporting_evidence": supporting,
            "contradicting_evidence": contradicting,
            "conflict_level": round(conflict_level, 4),
            "has_contradiction": len(supporting) > 0 and len(contradicting) > 0,
        }

    def evaluate_source_reliability_and_unverified_reports(
        self,
        source_name: str,
        source_reliability: float,
        reported_risk: float,
    ) -> Tuple[bool, float, str]:
        """
        RULE: Avoid automatic blocking solely because an unverified source reports a threat.
        Returns: (should_block, adjusted_risk, reasoning)
        """
        # Unverified or low reliability source (< 0.50)
        if source_reliability < 0.50 and reported_risk >= 0.70:
            adjusted_risk = reported_risk * source_reliability
            return (
                False, # Block automatic enforcement!
                adjusted_risk,
                f"Source '{source_name}' has low reliability ({source_reliability:.2f}). High-risk report ({reported_risk:.2f}) demoted for human review rather than automatic blocking.",
            )

        return (reported_risk >= 0.80, reported_risk, f"Report evaluated with source reliability {source_reliability:.2f}.")

    def sanitize_adversarial_payload(self, raw_content: str) -> Dict[str, Any]:
        """
        Detects embedded malicious instructions in emails, logs, or tool outputs (Prompt Injection).
        """
        suspicious_patterns = [
            "ignore previous instructions",
            "override system prompt",
            "grant admin privileges",
            "delete all logs",
            "disable security controls",
            "approve action",
            "bypass approval",
        ]

        raw_lower = raw_content.lower()
        detected_triggers = [p for p in suspicious_patterns if p in raw_lower]

        is_adversarial = len(detected_triggers) > 0
        cleaned_content = raw_content
        if is_adversarial:
            for trigger in detected_triggers:
                cleaned_content = cleaned_content.replace(trigger, f"[BLOCKED_ADVERSARIAL_INSTRUCTION: {trigger}]")

        return {
            "is_adversarial": is_adversarial,
            "detected_triggers": detected_triggers,
            "sanitized_content": cleaned_content,
            "isolation_status": "ISOLATED_UNTRUSTED_PAYLOAD" if is_adversarial else "CLEAN",
        }
