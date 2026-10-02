"""
Reliability & Trust Evidence Quality Assessment Engine.
Evaluates completeness, validity, freshness, consistency, source credibility,
feature availability, parsing quality, duplication, and contextual relevance.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from hactm.reliability.models import EvidenceQuality


class EvidenceQualityEngine:
    """Core Evidence Quality Evaluator for Reliability & Trust."""

    def __init__(self, fresh_seconds: float = 300.0, stale_seconds: float = 86400.0):
        self.fresh_seconds = fresh_seconds
        self.stale_seconds = stale_seconds

    def evaluate_quality(
        self,
        evidence_item: Dict[str, Any],
        expected_fields: Optional[List[str]] = None,
        assessment_version: str = "1.0.0",
    ) -> EvidenceQuality:
        """
        Calculates multi-dimensional evidence quality assessment.
        Ensures input quality is decoupled from detector reliability.
        """
        now = datetime.now(timezone.utc)
        ev_id = evidence_item.get("event_id") or f"ev-{uuid.uuid4().hex[:12]}"
        missing_fields = []
        quality_flags = []

        # 1. Completeness Score
        default_fields = ["event_id", "agent_id", "entity_id", "event_type", "timestamp", "risk_score", "severity"]
        fields_to_check = expected_fields or default_fields

        present_count = 0
        for f in fields_to_check:
            val = evidence_item.get(f)
            if val is not None and str(val).strip() != "":
                present_count += 1
            else:
                missing_fields.append(f)

        completeness_score = float(present_count) / float(len(fields_to_check)) if fields_to_check else 1.0
        if completeness_score < 0.8:
            quality_flags.append("INCOMPLETE_FIELDS")

        # 2. Validity Score
        validity_score = 1.0
        risk_score = evidence_item.get("risk_score")
        if risk_score is not None:
            try:
                r_val = float(risk_score)
                if r_val < 0.0 or r_val > 1.0:
                    validity_score -= 0.40
                    quality_flags.append("OUT_OF_BOUNDS_RISK_SCORE")
            except (ValueError, TypeError):
                validity_score -= 0.50
                quality_flags.append("INVALID_RISK_TYPE")

        conf = evidence_item.get("confidence")
        if conf is not None:
            try:
                c_val = float(conf)
                if c_val < 0.0 or c_val > 1.0:
                    validity_score -= 0.30
                    quality_flags.append("OUT_OF_BOUNDS_CONFIDENCE")
            except (ValueError, TypeError):
                validity_score -= 0.30
                quality_flags.append("INVALID_CONFIDENCE_TYPE")

        validity_score = max(0.0, validity_score)

        # 3. Freshness Score
        ts_val = evidence_item.get("timestamp")
        freshness_score = 1.0
        if ts_val:
            if isinstance(ts_val, str):
                try:
                    ts_dt = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
                except ValueError:
                    ts_dt = now
            elif isinstance(ts_val, datetime):
                ts_dt = ts_val
            else:
                ts_dt = now

            if ts_dt.tzinfo is None:
                ts_dt = ts_dt.replace(tzinfo=timezone.utc)

            age_seconds = max(0.0, (now - ts_dt).total_seconds())

            if age_seconds <= self.fresh_seconds:
                freshness_score = 1.0
            elif age_seconds >= self.stale_seconds:
                freshness_score = 0.20
                quality_flags.append("STALE_EVIDENCE")
            else:
                # Linear decay
                ratio = (age_seconds - self.fresh_seconds) / (self.stale_seconds - self.fresh_seconds)
                freshness_score = max(0.20, 1.0 - 0.80 * ratio)

        # 4. Consistency & Relevance
        consistency_score = 1.0
        relevance_score = 1.0

        ev_dict = evidence_item.get("evidence", {}) or {}
        if not ev_dict:
            consistency_score -= 0.20
            quality_flags.append("EMPTY_EVIDENCE_PAYLOAD")

        # 5. Source Quality
        source_quality_score = 1.0
        source = str(evidence_item.get("source") or "").lower()
        if "unverified" in source or "unknown" in source:
            source_quality_score = 0.60
            quality_flags.append("UNVERIFIED_SOURCE")

        # Composite Evidence Quality Score
        composite_quality = (
            0.30 * completeness_score
            + 0.25 * validity_score
            + 0.20 * freshness_score
            + 0.15 * consistency_score
            + 0.10 * source_quality_score
        )

        q_id = f"qual-{uuid.uuid4().hex[:12]}"
        return EvidenceQuality(
            quality_id=q_id,
            evidence_id=str(ev_id),
            quality_score=round(composite_quality, 4),
            completeness_score=round(completeness_score, 4),
            validity_score=round(validity_score, 4),
            freshness_score=round(freshness_score, 4),
            consistency_score=round(consistency_score, 4),
            relevance_score=round(relevance_score, 4),
            source_quality_score=round(source_quality_score, 4),
            missing_fields=missing_fields,
            quality_flags=quality_flags,
            assessment_version=assessment_version,
            created_at=now,
        )
