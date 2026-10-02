"""
Pattern matcher for detecting multi-stage attack-chain candidates.
"""

import os
import uuid
import yaml
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from hactm.graph.models import AttackChainCandidate, AttackChainStage
from hactm.graph.repository import GraphRepository
from hactm.temporal.engine import TemporalEvidenceEngine


class GraphPatternMatcher:
    """Evaluates declarative attack sequence patterns against historical evidence memory and graph context."""

    def __init__(self, session: Optional[Session] = None, patterns_path: Optional[str] = None):
        self.session = session
        self.repo = GraphRepository(session) if session else None
        self.temporal_engine = TemporalEvidenceEngine(session)
        self.patterns: List[Dict[str, Any]] = []

        if patterns_path and os.path.exists(patterns_path):
            self.load_patterns(patterns_path)

    def load_patterns(self, path: str):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            self.patterns = cfg.get("patterns", [])
        except Exception:
            pass

    def evaluate_evidence_sequence(
        self,
        events: List[Dict[str, Any]],
        primary_entity_id: str,
    ) -> List[AttackChainCandidate]:
        """Evaluates declarative attack sequence patterns against observed evidence items."""
        if not events:
            return []

        # Event time order
        ordered = self.temporal_engine.order_events(events)

        # False correlation check: Ensure events share the primary entity
        filtered_events = []
        for ev in ordered:
            ent_id = ev.get("entity_id")
            rel_ents = ev.get("related_entities") or []
            if ent_id == primary_entity_id or primary_entity_id in rel_ents:
                filtered_events.append(ev)

        if len(filtered_events) < 2:
            return []

        candidates = []
        for pat in self.patterns:
            pattern_id = pat.get("pattern_id", "PATTERN_UNK")
            seq_expected = pat.get("sequence", [])
            max_gap = pat.get("max_gap_seconds", 3600)
            min_domains = pat.get("minimum_domains", 2)

            matched_stages: List[AttackChainStage] = []
            matched_domains = set()

            # Sequential domain pattern matching
            exp_idx = 0
            for ev in filtered_events:
                ev_dom = ev.get("domain", "").lower()
                if exp_idx < len(seq_expected):
                    target_dom = seq_expected[exp_idx].lower()
                    if ev_dom == target_dom:
                        ev_id = ev.get("event_id") or ev.get("evidence_id") or f"ev_{exp_idx}"
                        ts = ev.get("timestamp")
                        if isinstance(ts, str):
                            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if ts and ts.tzinfo is None:
                            ts = ts.replace(tzinfo=timezone.utc)

                        stg = AttackChainStage(
                            stage_index=exp_idx + 1,
                            evidence_id=ev_id,
                            domain=ev.get("domain", "unknown"),
                            event_type=ev.get("event_type", "unknown"),
                            timestamp=ts or datetime.now(timezone.utc),
                            entity_id=primary_entity_id,
                            stage_confidence=ev.get("confidence", 1.0),
                        )
                        matched_stages.append(stg)
                        matched_domains.add(ev_dom)
                        exp_idx += 1

            if len(matched_stages) >= 2 and len(matched_domains) >= min_domains:
                completeness = round(len(matched_stages) / float(len(seq_expected)), 2)
                start_time = matched_stages[0].timestamp
                end_time = matched_stages[-1].timestamp
                time_span = max(0.0, (end_time - start_time).total_seconds())

                if time_span <= max_gap * len(seq_expected):
                    avg_conf = sum(s.stage_confidence for s in matched_stages) / len(matched_stages)
                    cand_conf = round(min(1.0, avg_conf * (0.5 + 0.5 * completeness)), 2)

                    status = "CANDIDATE" if completeness >= 1.0 else "PARTIAL"
                    chain_id = f"chain_{uuid.uuid4().hex[:12]}"

                    exp_lines = [
                        f"ATTACK-CHAIN CANDIDATE: {pat.get('name')}",
                        f"Pattern ID: {pattern_id}",
                        f"Primary Entity: {primary_entity_id}",
                        f"Matched Stages ({len(matched_stages)}/{len(seq_expected)}):",
                    ]
                    for s in matched_stages:
                        exp_lines.append(f"  Stage {s.stage_index} [{s.domain}]: {s.event_type} at {s.timestamp.isoformat()}")
                    exp_lines.append(f"Time Window: {round(time_span/60.0, 1)} minutes")
                    exp_lines.append(f"Completeness: {int(completeness*100)}%, Confidence: {cand_conf}")

                    cand = AttackChainCandidate(
                        chain_id=chain_id,
                        pattern_id=pattern_id,
                        primary_entity_id=primary_entity_id,
                        stages=matched_stages,
                        stage_count=len(seq_expected),
                        matched_stage_count=len(matched_stages),
                        completeness=completeness,
                        confidence=cand_conf,
                        start_time=start_time,
                        end_time=end_time,
                        status=status,
                        explanation="\n".join(exp_lines),
                    )
                    candidates.append(cand)

                    if self.repo:
                        self.repo.store_attack_chain(cand)

        return candidates
