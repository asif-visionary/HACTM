"""
Temporal Evidence Engine.
Analyzes event-time temporal relationships, sequence order, bursts, gaps, and cross-session correlation.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session

from hactm.temporal.models import (
    TemporalRelationshipType,
    TemporalRelationship,
    TemporalRevision,
    SequencePatternMatch,
)
from hactm.storage.models import TemporalRelationshipModel


class TemporalEvidenceEngine:
    """Core engine for event-time processing and temporal correlation analysis."""

    def __init__(self, session: Optional[Session] = None):
        self.session = session

    def order_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Orders security events by event timestamp (not DB insertion time)."""
        def get_ts(ev: Dict[str, Any]) -> datetime:
            ts = ev.get("timestamp")
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                except ValueError:
                    ts = datetime.now(timezone.utc)
            if ts is None:
                ts = datetime.now(timezone.utc)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            return ts

        return sorted(events, key=get_ts)

    def calculate_temporal_distance(self, event1: Dict[str, Any], event2: Dict[str, Any]) -> float:
        """Calculates exact delta in seconds between two events."""
        ordered = self.order_events([event1, event2])
        ts1 = ordered[0].get("timestamp")
        ts2 = ordered[1].get("timestamp")
        if isinstance(ts1, str):
            ts1 = datetime.fromisoformat(ts1.replace("Z", "+00:00"))
        if isinstance(ts2, str):
            ts2 = datetime.fromisoformat(ts2.replace("Z", "+00:00"))
        if ts1.tzinfo is None:
            ts1 = ts1.replace(tzinfo=timezone.utc)
        if ts2.tzinfo is None:
            ts2 = ts2.replace(tzinfo=timezone.utc)
        return max(0.0, (ts2 - ts1).total_seconds())

    def classify_relationship(self, event1: Dict[str, Any], event2: Dict[str, Any], window_seconds: float = 1800.0) -> TemporalRelationship:
        """Classifies pairwise temporal relationship between two events."""
        ev1_id = event1.get("event_id") or event1.get("evidence_id") or "ev1"
        ev2_id = event2.get("event_id") or event2.get("evidence_id") or "ev2"

        dist = self.calculate_temporal_distance(event1, event2)

        if dist < 1.0:
            rel_type = TemporalRelationshipType.SIMULTANEOUS
        elif dist <= window_seconds:
            rel_type = TemporalRelationshipType.WITHIN_WINDOW
        elif dist > 43200:  # 12h+ gap
            rel_type = TemporalRelationshipType.GAP
        else:
            rel_type = TemporalRelationshipType.BEFORE

        rel_id = f"trel_{uuid.uuid4().hex[:12]}"
        rel = TemporalRelationship(
            relationship_id=rel_id,
            source_evidence_id=ev1_id,
            target_evidence_id=ev2_id,
            relationship_type=rel_type,
            time_difference_seconds=dist,
            confidence=1.0 if dist <= window_seconds else 0.8,
        )

        if self.session:
            model_obj = TemporalRelationshipModel(
                relationship_id=rel_id,
                source_evidence_id=ev1_id,
                target_evidence_id=ev2_id,
                relationship_type=rel_type.value,
                time_difference_seconds=dist,
                confidence=rel.confidence,
                created_at=datetime.now(timezone.utc),
            )
            self.session.add(model_obj)
            self.session.commit()

        return rel

    def detect_sequences(
        self,
        events: List[Dict[str, Any]],
        max_gap_seconds: float = 3600.0,
        expected_domains: Optional[List[str]] = None,
    ) -> List[SequencePatternMatch]:
        """Detects ordered cross-domain event sequences."""
        ordered = self.order_events(events)
        if len(ordered) < 2:
            return []

        matches = []
        for i in range(len(ordered) - 1):
            seq = [ordered[i]]
            for j in range(i + 1, len(ordered)):
                dist = self.calculate_temporal_distance(seq[-1], ordered[j])
                if dist <= max_gap_seconds:
                    seq.append(ordered[j])
                else:
                    break

            if len(seq) >= 2:
                domains = [e.get("domain") or "unknown" for e in seq]
                unique_domains = list(set(domains))
                if expected_domains:
                    # Check if expected domains match subset
                    domain_match = all(d in unique_domains for d in expected_domains)
                    if not domain_match:
                        continue

                ev_ids = [e.get("event_id") or e.get("evidence_id") or str(idx) for idx, e in enumerate(seq)]
                first_ts = seq[0].get("timestamp")
                last_ts = seq[-1].get("timestamp")
                if isinstance(first_ts, str):
                    first_ts = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
                if isinstance(last_ts, str):
                    last_ts = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
                span = max(0.0, (last_ts - first_ts).total_seconds())

                sessions = {e.get("session_id") for e in seq if e.get("session_id")}
                is_cross_session = len(sessions) > 1

                matches.append(
                    SequencePatternMatch(
                        sequence_id=f"seq_{uuid.uuid4().hex[:12]}",
                        entity_id=seq[0].get("entity_id", "unknown"),
                        event_ids=ev_ids,
                        domains=domains,
                        time_span_seconds=span,
                        pattern_name=f"Sequence_{len(unique_domains)}Domains",
                        confidence=min(1.0, 0.5 + (len(unique_domains) * 0.2)),
                        is_cross_session=is_cross_session,
                    )
                )

        return matches

    def detect_gaps(self, events: List[Dict[str, Any]], gap_threshold_seconds: float = 3600.0) -> List[Dict[str, Any]]:
        """Identifies significant temporal gaps between consecutive events."""
        ordered = self.order_events(events)
        gaps = []
        for i in range(len(ordered) - 1):
            dist = self.calculate_temporal_distance(ordered[i], ordered[i + 1])
            if dist >= gap_threshold_seconds:
                gaps.append({
                    "previous_event_id": ordered[i].get("event_id") or ordered[i].get("evidence_id"),
                    "next_event_id": ordered[i + 1].get("event_id") or ordered[i + 1].get("evidence_id"),
                    "gap_seconds": dist,
                    "gap_hours": round(dist / 3600.0, 2),
                    "relationship": TemporalRelationshipType.GAP.value,
                })
        return gaps

    def detect_repeated_activity(self, events: List[Dict[str, Any]], window_seconds: float = 1800.0) -> Dict[str, Any]:
        """Detects repeated event types within temporal window."""
        ordered = self.order_events(events)
        counts = {}
        for ev in ordered:
            evt_type = ev.get("event_type", "unknown")
            counts[evt_type] = counts.get(evt_type, 0) + 1

        repeated = {k: v for k, v in counts.items() if v > 1}
        return {
            "has_repeated_activity": len(repeated) > 0,
            "repeated_event_types": repeated,
            "total_events": len(events),
        }

    def detect_bursts(self, events: List[Dict[str, Any]], burst_window_seconds: float = 60.0, min_events: int = 5) -> List[Dict[str, Any]]:
        """Detects rapid bursts of events within short timeframes."""
        ordered = self.order_events(events)
        bursts = []
        i = 0
        while i < len(ordered):
            window = [ordered[i]]
            j = i + 1
            while j < len(ordered):
                dist = self.calculate_temporal_distance(ordered[i], ordered[j])
                if dist <= burst_window_seconds:
                    window.append(ordered[j])
                    j += 1
                else:
                    break
            if len(window) >= min_events:
                bursts.append({
                    "start_time": window[0].get("timestamp"),
                    "end_time": window[-1].get("timestamp"),
                    "event_count": len(window),
                    "event_ids": [e.get("event_id") or e.get("evidence_id") for e in window],
                })
                i = j
            else:
                i += 1
        return bursts

    def detect_longitudinal_patterns(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyzes multi-day or weekly temporal patterns for an entity."""
        ordered = self.order_events(events)
        if not ordered:
            return {"pattern_detected": False, "span_days": 0}

        first_ts = ordered[0].get("timestamp")
        last_ts = ordered[-1].get("timestamp")
        if isinstance(first_ts, str):
            first_ts = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
        if isinstance(last_ts, str):
            last_ts = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
        if first_ts.tzinfo is None:
            first_ts = first_ts.replace(tzinfo=timezone.utc)
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)

        span_days = max(0.0, (last_ts - first_ts).total_seconds() / 86400.0)
        return {
            "pattern_detected": span_days >= 1.0,
            "span_days": round(span_days, 2),
            "event_count": len(events),
            "events_per_day": round(len(events) / max(span_days, 1.0), 2),
        }

    def handle_late_event(self, previous_result_id: str, new_event: Dict[str, Any], reason: str) -> TemporalRevision:
        """Handles late-arriving evidence deterministically via explicit revision log."""
        ev_id = new_event.get("event_id") or new_event.get("evidence_id") or "new_ev"
        rev = TemporalRevision(
            revision_id=f"rev_{uuid.uuid4().hex[:12]}",
            previous_result_id=previous_result_id,
            new_event_id=ev_id,
            revision_reason=reason,
        )
        return rev
