"""
Evidence Quality Assessment Evaluator for Evidence Fusion Fusion.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from hactm.fusion.models import EvidenceQualityAssessment


class EvidenceQualityEvaluator:
    """Evaluates individual evidence quality based on completeness, provenance, freshness, and validity."""

    def __init__(self, fresh_seconds: float = 300.0, recent_seconds: float = 3600.0, stale_seconds: float = 86400.0):
        self.fresh_seconds = fresh_seconds
        self.recent_seconds = recent_seconds
        self.stale_seconds = stale_seconds

    def evaluate(self, normalized_evidence: Dict[str, Any], current_time: datetime = None) -> EvidenceQualityAssessment:
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        evidence_id = normalized_evidence.get("event_id", str(uuid.uuid4()))

        # 1. Completeness Score
        required_fields = ["event_id", "agent_id", "entity_id", "event_type", "timestamp", "risk_score", "severity"]
        optional_fields = ["evidence", "source", "dataset", "session_id", "correlation_id", "model_version"]
        
        present_req = sum(1 for f in required_fields if normalized_evidence.get(f) is not None)
        present_opt = sum(1 for f in optional_fields if normalized_evidence.get(f) is not None)
        
        completeness_score = (present_req / len(required_fields)) * 0.7 + (present_opt / len(optional_fields)) * 0.3

        # 2. Provenance Score
        provenance_count = sum(1 for key in ["agent_id", "source", "dataset", "model_version", "detector_version", "source_record_id"]
                               if normalized_evidence.get(key) is not None)
        provenance_score = min(1.0, provenance_count / 5.0)

        # 3. Freshness Score
        ts = normalized_evidence.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                ts = current_time

        if isinstance(ts, datetime):
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            delta = (current_time - ts).total_seconds()
            if delta < 0:
                delta = 0  # Clock skew or future timestamp

            if delta <= self.fresh_seconds:
                freshness_score = 1.0
            elif delta <= self.recent_seconds:
                freshness_score = 0.85
            elif delta <= self.stale_seconds:
                freshness_score = 0.50
            else:
                freshness_score = 0.20
        else:
            freshness_score = 0.50

        # 4. Validity Score
        validity_score = 1.0
        risk = normalized_evidence.get("risk_score", 0.0)
        confidence = normalized_evidence.get("confidence", 1.0)
        uncertainty = normalized_evidence.get("uncertainty", 0.0)

        if not (0.0 <= risk <= 1.0):
            validity_score -= 0.3
        if not (0.0 <= confidence <= 1.0):
            validity_score -= 0.2
        if not (0.0 <= uncertainty <= 1.0):
            validity_score -= 0.2
        validity_score = max(0.0, validity_score)

        # Overall Quality Score
        quality_score = (
            0.30 * completeness_score +
            0.25 * provenance_score +
            0.25 * freshness_score +
            0.20 * validity_score
        )
        quality_score = round(max(0.0, min(1.0, quality_score)), 4)

        return EvidenceQualityAssessment(
            quality_id=f"qual-{uuid.uuid4().hex[:12]}",
            evidence_id=evidence_id,
            completeness_score=round(completeness_score, 4),
            provenance_score=round(provenance_score, 4),
            freshness_score=round(freshness_score, 4),
            validity_score=round(validity_score, 4),
            quality_score=quality_score,
            evaluated_at=current_time,
        )
