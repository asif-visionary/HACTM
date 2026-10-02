"""
Evidence Conflict Detector for Evidence Fusion Fusion.
"""

import uuid
from typing import List, Dict, Any, Tuple
from hactm.fusion.models import EvidenceConflict, ConflictType


class EvidenceConflictDetector:
    """Detects conflicts between evidence items from different domains."""

    def __init__(self, risk_disagreement_threshold: float = 0.35):
        self.risk_disagreement_threshold = risk_disagreement_threshold

    def detect_conflicts(
        self,
        fusion_id: str,
        evidence_list: List[Dict[str, Any]]
    ) -> Tuple[List[EvidenceConflict], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detects evidence conflicts.
        Returns:
            conflicts: List of EvidenceConflict objects
            supporting_evidence: Evidence items supporting the main risk trend
            conflicting_evidence: Evidence items contradicting the main risk trend
        """
        if not evidence_list:
            return [], [], []

        # Group by domain
        domain_risks = {}
        for item in evidence_list:
            dom = item.get("domain", "generic")
            if dom not in domain_risks:
                domain_risks[dom] = []
            domain_risks[dom].append(item)

        conflicts = []
        supporting = []
        conflicting = []

        # Calculate average risk per domain
        domain_avg_risk = {
            dom: sum(i.get("risk_score", 0.0) for i in items) / len(items)
            for dom, items in domain_risks.items()
        }

        risks = list(domain_avg_risk.values())
        if not risks:
            return [], evidence_list, []

        max_risk = max(risks)
        min_risk = min(risks)
        diff = max_risk - min_risk

        # Check for RISK_DISAGREEMENT across domains
        if len(domain_avg_risk) > 1 and diff >= self.risk_disagreement_threshold:
            high_domains = [dom for dom, r in domain_avg_risk.items() if r >= (max_risk - 0.15)]
            low_domains = [dom for dom, r in domain_avg_risk.items() if r <= (min_risk + 0.15)]

            high_ev_ids = [i.get("event_id") for dom in high_domains for i in domain_risks[dom]]
            low_ev_ids = [i.get("event_id") for dom in low_domains for i in domain_risks[dom]]

            explanation = (
                f"Evidence risk disagreement detected across domains. "
                f"High-risk domain(s) {', '.join(high_domains)} (avg risk {max_risk:.2f}) "
                f"contrast with low-risk domain(s) {', '.join(low_domains)} (avg risk {min_risk:.2f})."
            )

            conflict = EvidenceConflict(
                conflict_id=f"conf-{uuid.uuid4().hex[:12]}",
                fusion_id=fusion_id,
                evidence_ids=high_ev_ids + low_ev_ids,
                entities=list(set(i.get("entity_id") for i in evidence_list if i.get("entity_id"))),
                domains=list(domain_risks.keys()),
                risk_difference=round(diff, 4),
                conflict_type=ConflictType.RISK_DISAGREEMENT,
                severity="MEDIUM" if diff < 0.6 else "HIGH",
                explanation=explanation,
            )
            conflicts.append(conflict)

            # Categorize supporting vs conflicting evidence relative to overall median risk
            median_risk = sum(risks) / len(risks)
            for item in evidence_list:
                if abs(item.get("risk_score", 0.0) - median_risk) <= self.risk_disagreement_threshold / 2:
                    supporting.append(item)
                else:
                    conflicting.append(item)
        else:
            supporting = list(evidence_list)

        return conflicts, supporting, conflicting
