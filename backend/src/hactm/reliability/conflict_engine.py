"""
Reliability & Trust Conflict & Missing Evidence Handler.
Implements missing evidence tracking (coverage gaps) and multi-agent evidence conflict diagnostic tracking.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from hactm.reliability.models import (
    ConflictRecord,
    MissingEvidenceRecord,
)


class ConflictEngine:
    """Missing Evidence and Cross-Domain Conflict Analysis Engine."""

    def __init__(self, risk_conflict_threshold: float = 0.35):
        self.risk_conflict_threshold = risk_conflict_threshold

    def evaluate_missing_evidence(
        self,
        entity_id: str,
        expected_agents: List[str],
        present_agents: List[str],
        expected_domains: Optional[List[str]] = None,
        window_start: Optional[datetime] = None,
        window_end: Optional[datetime] = None,
    ) -> List[MissingEvidenceRecord]:
        """
        Identifies missing security agents/domains without treating absence as safe evidence.
        Produces explicit MissingEvidenceRecords with coverage_gap = True.
        """
        now = datetime.now(timezone.utc)
        w_start = window_start or now
        w_end = window_end or now

        missing_records = []
        present_set = set(present_agents)
        total_expected = len(expected_agents) if expected_agents else 1

        for idx, agent in enumerate(expected_agents):
            if agent not in present_set:
                domain = (expected_domains[idx] if (expected_domains and idx < len(expected_domains)) else "unknown_domain")
                rec_id = f"missing-{uuid.uuid4().hex[:12]}"
                gap_record = MissingEvidenceRecord(
                    record_id=rec_id,
                    entity_id=entity_id,
                    expected_agent=agent,
                    expected_domain=domain,
                    missing_agent=agent,
                    reason="No telemetry or detection evidence generated within window",
                    window_start=w_start,
                    window_end=w_end,
                    coverage_impact=round(1.0 / float(total_expected), 4),
                    coverage_gap=True,
                    created_at=now,
                )
                missing_records.append(gap_record)

        return missing_records

    def diagnose_evidence_conflicts(
        self,
        entity_id: str,
        evidence_items: List[Dict[str, Any]],
    ) -> Optional[ConflictRecord]:
        """
        Identifies and diagnoses conflict causes across multi-domain evidence items.
        Prevents silent averaging by explicitly logging ConflictRecord.
        """
        if not evidence_items or len(evidence_items) < 2:
            return None

        risks = []
        ev_ids = []
        timestamps = []
        quality_scores = []

        for e in evidence_items:
            ev_id = e.get("event_id") or e.get("evidence_id")
            if ev_id:
                ev_ids.append(str(ev_id))
            risks.append(float(e.get("risk_score", 0.0)))
            q = float(e.get("quality_score", 1.0)) if "quality_score" in e else 1.0
            quality_scores.append(q)

            ts = e.get("timestamp")
            if isinstance(ts, datetime):
                timestamps.append(ts)

        min_r = min(risks)
        max_r = max(risks)
        risk_range_delta = max_r - min_r

        if risk_range_delta < self.risk_conflict_threshold:
            return None

        # Diagnose likely conflict causes
        likely_causes = []

        # 1. Check timestamp difference (Different observation windows)
        if len(timestamps) >= 2:
            time_span_seconds = abs((max(timestamps) - min(timestamps)).total_seconds())
            if time_span_seconds > 900:  # 15 minutes
                likely_causes.append("DIFFERENT_OBSERVATION_WINDOWS")

        # 2. Check quality variation (Incomplete evidence)
        if max(quality_scores) - min(quality_scores) > 0.30:
            likely_causes.append("INCOMPLETE_EVIDENCE")

        # 3. Model stale or drift
        has_drift = any(e.get("drift_detected", False) for e in evidence_items)
        if has_drift:
            likely_causes.append("STALE_MODEL")

        if not likely_causes:
            likely_causes.append("GENUINE_AMBIGUITY")

        c_id = f"cnf-{uuid.uuid4().hex[:12]}"
        return ConflictRecord(
            conflict_id=c_id,
            evidence_ids=ev_ids,
            entity_id=entity_id,
            conflict_type="RISK_DISAGREEMENT",
            risk_range={"min_risk": round(min_r, 4), "max_risk": round(max_r, 4), "delta": round(risk_range_delta, 4)},
            disagreement_score=round(risk_range_delta, 4),
            likely_causes=likely_causes,
            resolution_status="OPEN",
            resolution_method=None,
            created_at=datetime.now(timezone.utc),
        )
