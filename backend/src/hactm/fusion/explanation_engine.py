"""
Fusion Explanation Engine for Evidence Fusion.
Generates explainable, evidence-traceable rationale without making unproven causal claims.
"""

from typing import List, Dict, Any, Tuple
from hactm.fusion.models import EvidenceConflict, EvidenceCoverage, RiskCategory


class FusionExplanationEngine:
    """Generates human-readable, provenance-linked explanations for fusion decisions."""

    def generate_explanation(
        self,
        unified_risk: float,
        risk_category: RiskCategory,
        primary_entity_id: str,
        supporting_evidence: List[Dict[str, Any]],
        conflicting_evidence: List[Dict[str, Any]],
        conflicts: List[EvidenceConflict],
        coverage: EvidenceCoverage,
        patterns: List[Dict[str, Any]]
    ) -> Tuple[List[str], str]:
        """
        Generates reason codes and detailed markdown explanation text.
        Returns:
            reason_codes: List[str]
            explanation_text: str
        """
        reason_codes = []
        explanation_lines = []

        explanation_lines.append(f"UNIFIED CYBER RISK: {unified_risk:.2f} ({risk_category.value})")
        explanation_lines.append(f"Target Entity: {primary_entity_id}")
        explanation_lines.append("")

        # 1. Multi-Domain Patterns & Supporting Evidence
        if supporting_evidence:
            explanation_lines.append("Supporting Security Evidence:")
            domains_seen = set()
            for ev in supporting_evidence:
                ev_id = ev.get("event_id", "UNKNOWN")
                dom = ev.get("domain", "generic")
                r = ev.get("risk_score", 0.0)
                sev = ev.get("severity", "LOW")
                agent = ev.get("agent_id", "unknown-agent")
                event_type = ev.get("event_type", "SECURITY_EVENT")

                domains_seen.add(dom)
                reason_code = f"EVIDENCE_{dom.upper()}_{sev}_{ev_id}"
                reason_codes.append(reason_code)

                explanation_lines.append(
                    f"  - [{ev_id}] ({dom.upper()} / {agent}): {event_type} evaluated with risk {r:.2f} ({sev})."
                )

        # 2. Temporal & Cross-Domain Sequence Relationships
        if patterns:
            explanation_lines.append("")
            explanation_lines.append("Cross-Domain Sequence Correlations:")
            for p in patterns:
                reason_codes.append(f"PATTERN_{p['pattern_id']}")
                explanation_lines.append(
                    f"  - Pattern {p['pattern_id']}: {p['explanation']} (Temporally correlated, not causal)."
                )

        # 3. Evidence Conflicts
        if conflicts:
            explanation_lines.append("")
            explanation_lines.append("Evidence Conflicts Identified:")
            for c in conflicts:
                reason_codes.append(f"CONFLICT_{c.conflict_type.value if hasattr(c.conflict_type, 'value') else c.conflict_type}")
                explanation_lines.append(f"  - Conflict ({c.conflict_type}): {c.explanation}")

        # 4. Domain Coverage
        explanation_lines.append("")
        explanation_lines.append(
            f"Evidence Coverage: {len(coverage.available_domains)} / {len(coverage.expected_domains)} expected domains "
            f"({coverage.coverage_ratio * 100:.1f}% coverage)."
        )
        if coverage.missing_domains:
            explanation_lines.append(f"  - Missing domain telemetry: {', '.join(coverage.missing_domains)}")

        explanation_text = "\n".join(explanation_lines)
        return reason_codes, explanation_text
