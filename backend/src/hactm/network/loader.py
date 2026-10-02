"""
Network Event Data Loader and Streaming Adapter.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Supports dataset schema mappings from configs/datasets.yaml for:
- CIC-IDS2017
- CSE-CIC-IDS2018
- UNSW-NB15
- BoT-IoT
- ToN-IoT
- Generic Canonical Schema
"""

import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
import yaml

from hactm.core.constants import IngestionPolicy
from hactm.core.errors import HACTMValidationError
from hactm.core.logging import logger
from hactm.ingestion.loaders.base import BaseDatasetLoader
from hactm.ingestion.loaders.csv_loader import CSVLoader
from hactm.ingestion.loaders.json_loader import JSONLoader
from hactm.ingestion.loaders.jsonl_loader import JSONLLoader
from hactm.ingestion.normalization import normalize_timestamp
from hactm.ingestion.pipeline import get_loader_for_file
from hactm.network.models import NetworkEvent
from hactm.network.normalization import (
    normalize_network_protocol,
    sanitize_float_metric,
    sanitize_int_metric,
    validate_and_classify_ip,
    validate_and_normalize_port,
)


class NetworkEventSource(ABC):
    """
    Abstract streaming event source interface (extensible for Kafka/RabbitMQ in future).
    """
    @abstractmethod
    def stream_events(self, batch_size: int = 1000) -> Generator[List[NetworkEvent], None, None]:
        pass


class NetworkDataLoader(NetworkEventSource):
    """
    Loads and normalizes network flow records into canonical NetworkEvent instances.
    """
    def __init__(self, mapping_config_path: Optional[Path] = None):
        cfg_path = mapping_config_path or Path(__file__).resolve().parent.parent.parent.parent / "configs" / "datasets.yaml"
        self.mappings: Dict[str, Dict[str, str]] = {}
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.mappings = data.get("datasets", {})

    def get_mapping(self, dataset_name: Optional[str]) -> Dict[str, str]:
        if not dataset_name:
            return self.mappings.get("canonical", {})
        key = dataset_name.lower().replace("-", "_").replace(" ", "_")
        return self.mappings.get(key, self.mappings.get("canonical", {}))

    def parse_record(
        self,
        raw_record: Dict[str, Any],
        row_id: Optional[str] = None,
        dataset_name: Optional[str] = None,
    ) -> NetworkEvent:
        """
        Transforms a raw flow dictionary into a validated NetworkEvent.
        """
        mapping = self.get_mapping(dataset_name)

        def get_field(canonical_key: str, default_val: Any = None) -> Any:
            mapped_key = mapping.get(canonical_key, canonical_key)
            if mapped_key in raw_record:
                return raw_record[mapped_key]
            # Fallback to direct canonical key
            if canonical_key in raw_record:
                return raw_record[canonical_key]
            return default_val

        # 1. Event ID
        event_id = get_field("event_id")
        if not event_id:
            event_id = f"NET-EVT-{uuid.uuid4().hex[:10].upper()}"
        else:
            event_id = str(event_id).strip()

        # 2. Timestamp
        raw_ts = get_field("timestamp")
        if raw_ts is None:
            raise HACTMValidationError("Network event missing timestamp")
        try:
            ts = normalize_timestamp(raw_ts)
        except Exception as e:
            raise HACTMValidationError(f"Invalid network timestamp '{raw_ts}': {e}")

        # 3. Source IP
        raw_src = get_field("src_ip")
        try:
            src_ip, src_class = validate_and_classify_ip(raw_src)
        except Exception as e:
            raise HACTMValidationError(f"Invalid source IP: {e}")

        # 4. Destination IP
        raw_dst = get_field("dst_ip")
        try:
            dst_ip, dst_class = validate_and_classify_ip(raw_dst)
        except Exception as e:
            raise HACTMValidationError(f"Invalid destination IP: {e}")

        # 5. Ports
        try:
            src_port = validate_and_normalize_port(get_field("src_port"))
            dst_port = validate_and_normalize_port(get_field("dst_port"))
        except ValueError as e:
            raise HACTMValidationError(str(e))

        # 6. Protocol
        proto = normalize_network_protocol(get_field("protocol"))

        # 7. Metrics with bounds and NaN check
        try:
            duration = sanitize_float_metric(get_field("duration"), "duration")
            flow_bytes = sanitize_int_metric(get_field("flow_bytes"), "flow_bytes")
            flow_packets = sanitize_int_metric(get_field("flow_packets"), "flow_packets")
            forward_bytes = sanitize_int_metric(get_field("forward_bytes"), "forward_bytes")
            backward_bytes = sanitize_int_metric(get_field("backward_bytes"), "backward_bytes")
            forward_packets = sanitize_int_metric(get_field("forward_packets"), "forward_packets")
            backward_packets = sanitize_int_metric(get_field("backward_packets"), "backward_packets")
            flow_rate = sanitize_float_metric(get_field("flow_rate"), "flow_rate")
            packet_rate = sanitize_float_metric(get_field("packet_rate"), "packet_rate")
        except ValueError as e:
            raise HACTMValidationError(str(e))

        # 8. If flow_rate or packet_rate missing but duration and bytes exist:
        if flow_rate is None and flow_bytes is not None and duration is not None:
            flow_rate = round(flow_bytes / duration, 2) if duration > 0 else None
        if packet_rate is None and flow_packets is not None and duration is not None:
            packet_rate = round(flow_packets / duration, 2) if duration > 0 else None

        # 9. Ground Truth Label (for evaluation/benchmarking only)
        raw_label = get_field("label")
        label_str = str(raw_label).strip() if raw_label is not None else None

        return NetworkEvent(
            event_id=event_id,
            timestamp=ts,
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=proto,
            duration=duration,
            flow_bytes=flow_bytes,
            flow_packets=flow_packets,
            forward_bytes=forward_bytes,
            backward_bytes=backward_bytes,
            forward_packets=forward_packets,
            backward_packets=backward_packets,
            tcp_flags=str(get_field("tcp_flags")) if get_field("tcp_flags") is not None else None,
            connection_state=str(get_field("connection_state")) if get_field("connection_state") is not None else None,
            flow_rate=flow_rate,
            packet_rate=packet_rate,
            dataset=dataset_name,
            source_record_id=row_id,
            src_ip_classification=src_class,
            dst_ip_classification=dst_class,
            label=label_str,
        )

    def load_from_file(
        self,
        file_path: Union[str, Path],
        dataset_name: Optional[str] = None,
        batch_size: int = 1000,
        policy: IngestionPolicy = IngestionPolicy.QUARANTINE_INVALID,
    ) -> Generator[List[NetworkEvent], None, None]:
        path = Path(file_path)
        loader = get_loader_for_file(path)
        ds_name = dataset_name or path.stem

        for batch in loader.stream_batches(batch_size=batch_size):
            events = []
            for row_idx, raw_rec in batch:
                try:
                    event = self.parse_record(raw_rec, row_id=str(row_idx), dataset_name=ds_name)
                    events.append(event)
                except HACTMValidationError as e:
                    if policy == IngestionPolicy.STRICT:
                        raise e
                    elif policy == IngestionPolicy.QUARANTINE_INVALID:
                        logger.warning(f"Quarantined network event row {row_idx}: {e}")
                    # SKIP_INVALID simply ignores invalid record
                    continue
            if events:
                yield events

    def stream_events(self, batch_size: int = 1000) -> Generator[List[NetworkEvent], None, None]:
        raise NotImplementedError("Use load_from_file or feed events directly")
