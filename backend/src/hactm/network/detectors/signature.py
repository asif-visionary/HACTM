"""
Safe Structured Signature-Based Detection Engine.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Evaluates structured JSON condition trees without eval() or exec().
"""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from hactm.core.constants import SeverityLevel
from hactm.core.logging import logger
from hactm.network.detectors.base import BaseDetector
from hactm.network.models import DetectorType, NetworkDetectionResult, NetworkEvent


def _safe_compare(left: Any, operator: str, right: Any) -> bool:
    """
    Safely executes primitive relational comparisons without eval/exec.
    """
    if left is None:
        return False

    op = operator.lower().strip()

    # Numeric conversions if both can be float
    if isinstance(right, (int, float)) and not isinstance(left, (int, float)):
        try:
            left = float(left)
        except (ValueError, TypeError):
            return False

    try:
        if op == "eq":
            if isinstance(left, str) and isinstance(right, str):
                return left.strip().lower() == right.strip().lower()
            return left == right
        elif op == "neq":
            if isinstance(left, str) and isinstance(right, str):
                return left.strip().lower() != right.strip().lower()
            return left != right
        elif op == "gt":
            return float(left) > float(right)
        elif op == "gte":
            return float(left) >= float(right)
        elif op == "lt":
            return float(left) < float(right)
        elif op == "lte":
            return float(left) <= float(right)
        elif op == "in":
            if isinstance(right, (list, tuple, set)):
                if isinstance(left, str):
                    return any(str(item).lower() == left.lower() for item in right)
                return left in right
            return False
        elif op == "contains":
            if isinstance(left, (list, tuple, set, str)):
                return str(right).lower() in str(left).lower()
            return False
        elif op == "regex":
            return bool(re.search(str(right), str(left), re.IGNORECASE))
    except (TypeError, ValueError):
        return False

    return False


def evaluate_condition_tree(conditions: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Recursively evaluates an AST of conditions against context dictionary.
    Returns (is_matched: bool, matched_reasons: List[str]).
    """
    if not conditions:
        return False, []

    reasons: List[str] = []

    # AND combinator ('all')
    if "all" in conditions:
        for cond in conditions["all"]:
            matched, sub_reasons = evaluate_condition_tree(cond, context)
            if not matched:
                return False, []
            reasons.extend(sub_reasons)
        return True, reasons

    # OR combinator ('any')
    if "any" in conditions:
        for cond in conditions["any"]:
            matched, sub_reasons = evaluate_condition_tree(cond, context)
            if matched:
                return True, sub_reasons
        return False, []

    # NOT combinator ('not')
    if "not" in conditions:
        matched, sub_reasons = evaluate_condition_tree(conditions["not"], context)
        if not matched:
            return True, ["Condition negation satisfied"]
        return False, []

    # Terminal Leaf Condition: {"field": ..., "operator": ..., "value": ...}
    field = conditions.get("field")
    operator = conditions.get("operator")
    target_val = conditions.get("value")

    if not field or not operator:
        return False, []

    actual_val = context.get(field)
    if _safe_compare(actual_val, operator, target_val):
        desc = f"{field} ({actual_val}) {operator} {target_val}"
        return True, [desc]

    return False, []


class SignatureDetector(BaseDetector):
    """
    Deterministic rule and signature evaluation engine.
    """
    detector_type = DetectorType.SIGNATURE
    detector_id = "network-signature-engine"
    detector_version = "1.0.0"

    def __init__(self, signatures_file: Optional[Union[str, Path]] = None):
        self.signatures: List[Dict[str, Any]] = []
        candidates = []
        if signatures_file:
            candidates.append(Path(signatures_file))
            candidates.append(Path("backend") / signatures_file)
            candidates.append(Path(__file__).resolve().parents[4] / signatures_file)
            candidates.append(Path(__file__).resolve().parents[3] / signatures_file)

        candidates.extend([
            Path("backend/configs/network_signatures.json"),
            Path("configs/network_signatures.json"),
            Path(__file__).resolve().parents[4] / "configs" / "network_signatures.json",
            Path(__file__).resolve().parents[3] / "configs" / "network_signatures.json",
        ])

        found_path = None
        for cand in candidates:
            if cand.exists():
                found_path = cand
                break

        if found_path:
            self.load_signatures(found_path)
        else:
            logger.warning("Signature file not found, checked candidates")

    def load_signatures(self, file_path: Union[str, Path]) -> None:
        p = Path(file_path)
        if not p.exists():
            logger.warning(f"Signature file not found: {p}")
            return

        try:
            with open(p, "r", encoding="utf-8") as f:
                raw_sigs = json.load(f)
            # Deduplicate by signature_id and filter enabled
            seen_ids = set()
            loaded = []
            for s in raw_sigs:
                sid = s.get("signature_id")
                if sid and sid not in seen_ids and s.get("enabled", True):
                    seen_ids.add(sid)
                    loaded.append(s)
            self.signatures = loaded
            logger.info(f"Loaded {len(self.signatures)} active network signatures from {p.name}")
        except Exception as e:
            logger.error(f"Failed to load signatures from {p}: {e}")

    def detect(self, event: NetworkEvent) -> Optional[NetworkDetectionResult]:
        t0 = time.perf_counter()

        # Build execution context for signature conditions
        context = {
            "event_id": event.event_id,
            "src_ip": event.src_ip,
            "dst_ip": event.dst_ip,
            "src_port": event.src_port,
            "dst_port": event.dst_port,
            "protocol": event.protocol,
            "duration": event.duration,
            "flow_bytes": event.flow_bytes,
            "flow_packets": event.flow_packets,
            "forward_bytes": event.forward_bytes,
            "backward_bytes": event.backward_bytes,
            "tcp_flags": event.tcp_flags,
            "connection_state": event.connection_state,
            "flow_rate": event.flow_rate,
            "packet_rate": event.packet_rate,
            "src_ip_classification": event.src_ip_classification.value if event.src_ip_classification else None,
            "dst_ip_classification": event.dst_ip_classification.value if event.dst_ip_classification else None,
        }

        # Check all signatures
        for sig in self.signatures:
            matched, matched_reasons = evaluate_condition_tree(sig.get("conditions", {}), context)
            if matched:
                elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)
                sig_id = sig["signature_id"]
                name = sig.get("name", sig_id)
                confidence = float(sig.get("confidence", 0.90))
                risk = float(sig.get("risk_score", 0.70))
                severity_str = sig.get("severity", "HIGH")

                explanation = (
                    f"Signature Match [{sig_id} - {name}]: "
                    f"{'; '.join(matched_reasons)}. {sig.get('description', '')}"
                )

                return NetworkDetectionResult(
                    detection_id=f"DET-SIG-{sig_id}-{event.event_id}",
                    event_id=event.event_id,
                    detector_type=DetectorType.SIGNATURE,
                    detector_id=self.detector_id,
                    detector_version=self.detector_version,
                    category=sig.get("category", "Signature Detection"),
                    risk_score=risk,
                    confidence=confidence,
                    uncertainty=round(max(0.0, 1.0 - confidence), 4),
                    severity=SeverityLevel[severity_str.upper()] if severity_str.upper() in SeverityLevel.__members__ else SeverityLevel.HIGH,
                    reason_codes=[f"SIG_MATCH_{sig_id}"],
                    explanation=explanation,
                    features_used={k: context[k] for k in ["dst_port", "protocol", "flow_bytes", "flow_rate", "packet_rate"] if context.get(k) is not None},
                    timestamp=datetime.now(timezone.utc),
                    signature_id=sig_id,
                    processing_time_ms=elapsed_ms,
                    src_ip=event.src_ip,
                    dst_ip=event.dst_ip,
                )

        return None
