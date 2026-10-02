"""
cstub/ml-ids Preprocessing & Feature Pipeline Adapter.
Attribution: https://github.com/cstub/ml-ids (MIT License, Christoph Stumpf)
"""

import math
import numpy as np
from typing import Dict, Any, List, Optional
from hactm.network.models import NetworkEvent


class MLIDSPreprocessor:
    """Preprocesses HACTM NetworkEvents into cstub/ml-ids flow feature vectors."""

    def __init__(self):
        self.feature_names = [
            "flow_duration", "tot_fwd_pkts", "tot_bwd_pkts", "totlen_fwd_pkts", "totlen_bwd_pkts",
            "fwd_pkt_len_mean", "bwd_pkt_len_mean", "flow_byts_s", "flow_pkts_s", "pkt_len_mean",
            "pkt_len_std", "syn_flag_cnt", "rst_flag_cnt", "ack_flag_cnt", "psh_flag_cnt"
        ]

    def extract_features(self, event: NetworkEvent) -> np.ndarray:
        """Transforms a HACTM NetworkEvent into a 15-dimensional cstub/ml-ids flow vector."""
        duration = max(0.001, float(event.duration or 0.01))
        fwd_pkts = float(event.forward_packets or (event.flow_packets / 2 if event.flow_packets else 1))
        bwd_pkts = float(event.backward_packets or (event.flow_packets / 2 if event.flow_packets else 0))
        tot_pkts = max(1.0, fwd_pkts + bwd_pkts)

        fwd_bytes = float(event.forward_bytes or (event.flow_bytes / 2 if event.flow_bytes else 64))
        bwd_bytes = float(event.backward_bytes or (event.flow_bytes / 2 if event.flow_bytes else 0))
        tot_bytes = fwd_bytes + bwd_bytes

        fwd_pkt_mean = fwd_bytes / max(1.0, fwd_pkts)
        bwd_pkt_mean = bwd_bytes / max(1.0, bwd_pkts)
        pkt_len_mean = tot_bytes / tot_pkts

        flow_byts_s = float(event.flow_rate or (tot_bytes / duration))
        flow_pkts_s = float(event.packet_rate or (tot_pkts / duration))

        flags = str(event.tcp_flags or "").upper()
        syn = 1.0 if "SYN" in flags else 0.0
        rst = 1.0 if "RST" in flags else 0.0
        ack = 1.0 if "ACK" in flags else 0.0
        psh = 1.0 if "PSH" in flags else 0.0

        vector = [
            duration * 1e6, # microseconds
            fwd_pkts,
            bwd_pkts,
            fwd_bytes,
            bwd_bytes,
            fwd_pkt_mean,
            bwd_pkt_mean,
            flow_byts_s,
            flow_pkts_s,
            pkt_len_mean,
            pkt_len_mean * 0.2, # std estimate
            syn,
            rst,
            ack,
            psh
        ]
        return np.array(vector, dtype=np.float32)
