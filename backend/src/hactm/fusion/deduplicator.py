"""
Evidence Deduplication Engine for Evidence Fusion Fusion.
"""

from typing import List, Dict, Any, Tuple


class EvidenceDeduplicationEngine:
    """Identifies and handles duplicate or redundant evidence across agents/detectors."""

    def deduplicate(self, evidence_list: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], int]:
        """
        Deduplicates evidence list.
        Returns:
            deduplicated_list: Unique primary evidence records
            redundant_list: Duplicates identified
            redundant_count: Number of redundant evidence items
        """
        seen_keys = {}
        deduplicated = []
        redundant = []

        for item in evidence_list:
            # Deterministic similarity key: entity + event_type + source_record_id (or event_id)
            source_rec = item.get("source_record_id") or item.get("raw_event_id") or item.get("event_id")
            entity = item.get("entity_id", "")
            event_type = item.get("event_type", "")
            agent = item.get("agent_id", "")

            # Exact key
            key = f"{entity}|{event_type}|{source_rec}|{agent}"

            if key in seen_keys:
                # Compare quality/risk score: keep highest risk/quality item as primary
                existing = seen_keys[key]
                if item.get("risk_score", 0) > existing.get("risk_score", 0):
                    redundant.append(existing)
                    seen_keys[key] = item
                else:
                    redundant.append(item)
            else:
                seen_keys[key] = item

        deduplicated = list(seen_keys.values())
        return deduplicated, redundant, len(redundant)
