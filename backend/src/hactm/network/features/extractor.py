"""
Network Feature Extraction Engine.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Extracts flow, directional, temporal, and protocol feature vectors from NetworkEvent.
Applies rigorous validation against NaN, Infinity, negative values, and zero-duration divisions.
"""

import math
from typing import Any, Dict, List, Optional
import numpy as np

from hactm.core.errors import HACTMValidationError
from hactm.network.models import IPClassification, NetworkEvent

FEATURE_SCHEMA_VERSION = "1.0.0"

CANONICAL_FEATURE_NAMES = [
    "duration",
    "flow_bytes",
    "flow_packets",
    "forward_bytes",
    "backward_bytes",
    "forward_packets",
    "backward_packets",
    "bytes_per_second",
    "packets_per_second",
    "forward_ratio",
    "forward_packet_ratio",
    "average_packet_size",
    "is_well_known_port",
    "is_ephemeral_port",
    "protocol_tcp",
    "protocol_udp",
    "protocol_icmp",
    "src_is_private",
    "dst_is_private",
]


class NetworkFeatureExtractor:
    """
    Extracts numerical feature dictionaries and matrices for signature, heuristic, and anomaly detectors.
    """
    def __init__(self, selected_features: Optional[List[str]] = None):
        self.features = selected_features or CANONICAL_FEATURE_NAMES
        self.schema_version = FEATURE_SCHEMA_VERSION

    def extract(self, event: NetworkEvent) -> Dict[str, float]:
        """Convenience alias for extract_features."""
        return self.extract_features(event)

    def extract_features(self, event: NetworkEvent) -> Dict[str, float]:
        """
        Extracts a dictionary of numerical features for a single NetworkEvent.
        Guarantees finite float outputs with zero division protection.
        """
        duration = max(0.0, float(event.duration or 0.0))
        flow_bytes = max(0, float(event.flow_bytes or 0))
        flow_packets = max(0, float(event.flow_packets or 0))
        fwd_bytes = max(0, float(event.forward_bytes or 0))
        bwd_bytes = max(0, float(event.backward_bytes or 0))
        fwd_pkts = max(0, float(event.forward_packets or 0))
        bwd_pkts = max(0, float(event.backward_packets or 0))

        # Rates (with zero duration guard)
        bytes_per_second = (flow_bytes / duration) if duration > 0.0 else 0.0
        packets_per_second = (flow_packets / duration) if duration > 0.0 else 0.0

        # Ratios (with zero division guard)
        total_dir_bytes = fwd_bytes + bwd_bytes
        forward_ratio = (fwd_bytes / total_dir_bytes) if total_dir_bytes > 0 else (1.0 if flow_bytes > 0 else 0.0)

        total_dir_pkts = fwd_pkts + bwd_pkts
        forward_packet_ratio = (fwd_pkts / total_dir_pkts) if total_dir_pkts > 0 else (1.0 if flow_packets > 0 else 0.0)

        average_packet_size = (flow_bytes / flow_packets) if flow_packets > 0 else 0.0

        # Port classifications
        dst_port = event.dst_port or 0
        is_well_known = 1.0 if 0 < dst_port <= 1024 else 0.0
        is_ephemeral = 1.0 if dst_port >= 49152 else 0.0

        # Protocols
        proto = event.protocol.upper()
        proto_tcp = 1.0 if proto == "TCP" else 0.0
        proto_udp = 1.0 if proto == "UDP" else 0.0
        proto_icmp = 1.0 if proto in ["ICMP", "ICMPV6"] else 0.0

        # IP Scopes
        src_priv = 1.0 if event.src_ip_classification == IPClassification.PRIVATE else 0.0
        dst_priv = 1.0 if event.dst_ip_classification == IPClassification.PRIVATE else 0.0

        all_features = {
            "duration": duration,
            "flow_bytes": flow_bytes,
            "flow_packets": flow_packets,
            "forward_bytes": fwd_bytes,
            "backward_bytes": bwd_bytes,
            "forward_packets": fwd_pkts,
            "backward_packets": bwd_pkts,
            "bytes_per_second": bytes_per_second,
            "packets_per_second": packets_per_second,
            "forward_ratio": forward_ratio,
            "forward_packet_ratio": forward_packet_ratio,
            "average_packet_size": average_packet_size,
            "is_well_known_port": is_well_known,
            "is_ephemeral_port": is_ephemeral,
            "protocol_tcp": proto_tcp,
            "protocol_udp": proto_udp,
            "protocol_icmp": proto_icmp,
            "src_is_private": src_priv,
            "dst_is_private": dst_priv,
        }

        # Filter and validate against NaN / Inf
        extracted: Dict[str, float] = {}
        for f in self.features:
            val = all_features.get(f, 0.0)
            if math.isnan(val) or math.isinf(val):
                val = 0.0
            extracted[f] = float(val)

        return extracted

    def to_vector(self, event: NetworkEvent) -> np.ndarray:
        """Extracts a 1D NumPy array in canonical feature order."""
        feature_dict = self.extract_features(event)
        return np.array([feature_dict[name] for name in self.features], dtype=np.float64)

    def to_matrix(self, events: List[NetworkEvent]) -> np.ndarray:
        """Extracts a 2D NumPy array (N samples, D features) for batch training or inference."""
        if not events:
            return np.empty((0, len(self.features)), dtype=np.float64)
        return np.array([self.to_vector(e) for e in events], dtype=np.float64)
