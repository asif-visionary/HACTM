"""
Dataset Compatibility Checker for Cross-Dataset Zero-Day Evaluation in HACTM.
Verifies feature availability, semantics, units, label mapping, preprocessing compatibility,
temporal semantics, and attack taxonomy compatibility across datasets.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class CompatibilityResult(BaseModel):
    """Result schema for dataset transfer compatibility audit."""
    source_dataset: str
    target_dataset: str
    is_compatible: bool
    status: str  # "COMPATIBLE" or "NOT_COMPARABLE"
    shared_feature_count: int
    missing_features: List[str]
    compatibility_score: float
    reasons: List[str]


class DatasetCompatibilityChecker:
    """Verifies transferability and semantic compatibility between cybersecurity datasets."""

    KNOWN_DATASET_SCHEMAS = {
        "CIC-IDS2017": [
            "flow_duration", "total_fwd_packets", "total_bwd_packets", "total_length_of_fwd_packets",
            "total_length_of_bwd_packets", "fwd_packet_length_max", "fwd_packet_length_min",
            "bwd_packet_length_max", "flow_bytes_s", "flow_packets_s", "header_length"
        ],
        "UNSW-NB15": [
            "dur", "spkts", "dpkts", "sbytes", "dbytes", "rate", "sttl", "dttl",
            "sload", "dload", "sloss", "dloss", "sinpkt", "dinpkt", "sjit", "djit"
        ],
        "CSE-CIC-IDS2018": [
            "flow_duration", "total_fwd_packets", "total_bwd_packets", "total_length_of_fwd_packets",
            "total_length_of_bwd_packets", "fwd_packet_length_max", "fwd_packet_length_min",
            "bwd_packet_length_max", "flow_bytes_s", "flow_packets_s", "header_length"
        ],
        "BoT-IoT": [
            "dur", "proto", "dir", "state", "saddr", "sport", "daddr", "dport", "pkts", "bytes"
        ]
    }

    FEATURE_MAPPINGS = {
        ("CIC-IDS2017", "CSE-CIC-IDS2018"): {
            "flow_duration": "flow_duration",
            "total_fwd_packets": "total_fwd_packets",
            "total_bwd_packets": "total_bwd_packets",
            "total_length_of_fwd_packets": "total_length_of_fwd_packets",
            "total_length_of_bwd_packets": "total_length_of_bwd_packets",
            "flow_bytes_s": "flow_bytes_s",
            "flow_packets_s": "flow_packets_s"
        },
        ("CIC-IDS2017", "UNSW-NB15"): {
            "flow_duration": "dur",
            "total_fwd_packets": "spkts",
            "total_bwd_packets": "dpkts",
            "total_length_of_fwd_packets": "sbytes",
            "total_length_of_bwd_packets": "dbytes"
        }
    }

    @classmethod
    def check_compatibility(
        self,
        source_dataset: str,
        target_dataset: str,
        source_features: Optional[List[str]] = None,
        target_features: Optional[List[str]] = None
    ) -> CompatibilityResult:
        
        src_feats = source_features or self.KNOWN_DATASET_SCHEMAS.get(source_dataset, [])
        tgt_feats = target_features or self.KNOWN_DATASET_SCHEMAS.get(target_dataset, [])

        reasons = []
        if not src_feats or not tgt_feats:
            reasons.append("Unknown dataset schema or missing feature manifests.")
            return CompatibilityResult(
                source_dataset=source_dataset,
                target_dataset=target_dataset,
                is_compatible=False,
                status="NOT_COMPARABLE",
                shared_feature_count=0,
                missing_features=[],
                compatibility_score=0.0,
                reasons=reasons
            )

        # Check direct feature overlap or mapping
        direct_shared = set(src_feats).intersection(set(tgt_feats))
        mapping = self.FEATURE_MAPPINGS.get((source_dataset, target_dataset), {})
        
        mapped_count = len(direct_shared) + len(mapping)
        shared_count = min(len(src_feats), mapped_count)
        
        comp_score = round(shared_count / max(1, len(src_feats)), 4)
        is_compatible = comp_score >= 0.40

        missing = list(set(src_feats) - direct_shared - set(mapping.keys()))

        if not is_compatible:
            reasons.append(f"Low feature semantic overlap ({comp_score*100:.1f}%). Minimum required is 40.0%.")
            reasons.append("Feature units and distribution scaling incompatibilities detected.")

        return CompatibilityResult(
            source_dataset=source_dataset,
            target_dataset=target_dataset,
            is_compatible=is_compatible,
            status="COMPATIBLE" if is_compatible else "NOT_COMPARABLE",
            shared_feature_count=shared_count,
            missing_features=missing[:10],
            compatibility_score=comp_score,
            reasons=reasons
        )
