"""
Unified Network Security Dataset Ingestion & Processing Pipeline.
Adapts ToN-IoT and BoT-IoT into HACTM Normalized Network Events.
Supports chunking, feature normalization, temporal & cross-dataset splits.
"""

import os
import csv
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Generator, Tuple, Optional

logger = logging.getLogger("hactm.datasets.network")


class NetworkDatasetPipeline:
    """Ingests ToN-IoT and BoT-IoT datasets into HACTM Network Events."""

    def __init__(self, base_data_dir: Optional[Path] = None):
        self.base_dir = base_data_dir or Path(__file__).resolve().parents[5] / "data"
        self.raw_dir = self.base_dir / "raw" / "network"
        self.processed_dir = self.base_dir / "processed" / "network"
        self.splits_dir = self.base_dir / "splits" / "network"
        
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.splits_dir.mkdir(parents=True, exist_ok=True)

    def process_ton_iot(self, max_records: Optional[int] = None) -> Dict[str, Any]:
        """Ingests ToN-IoT train_test_network.csv into normalized HACTM events."""
        ton_file = self.raw_dir / "ton_iot" / "train_test_network.csv"
        if not ton_file.exists():
            raise FileNotFoundError(f"ToN-IoT file not found at {ton_file}")

        events = []
        attack_types = set()

        with open(ton_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Clean BOM if present in first field
                src_ip = row.get("\ufeffsrc_ip", row.get("src_ip", "0.0.0.0"))
                event = {
                    "event_id": f"ton_iot_{count}",
                    "timestamp": row.get("duration", "0.0"),
                    "source_ip": src_ip,
                    "destination_ip": row.get("dst_ip", "0.0.0.0"),
                    "source_port": int(row.get("src_port", 0)) if row.get("src_port", "0").isdigit() else 0,
                    "destination_port": int(row.get("dst_port", 0)) if row.get("dst_port", "0").isdigit() else 0,
                    "protocol": row.get("proto", "tcp").lower(),
                    "service": row.get("service", "-"),
                    "packet_features": {
                        "src_bytes": float(row.get("src_bytes", 0)) if row.get("src_bytes", "0").replace('.', '', 1).isdigit() else 0.0,
                        "dst_bytes": float(row.get("dst_bytes", 0)) if row.get("dst_bytes", "0").replace('.', '', 1).isdigit() else 0.0,
                        "src_pkts": int(row.get("src_pkts", 0)) if row.get("src_pkts", "0").isdigit() else 0,
                        "dst_pkts": int(row.get("dst_pkts", 0)) if row.get("dst_pkts", "0").isdigit() else 0,
                    },
                    "attack_category": row.get("type", "normal"),
                    "label": int(row.get("label", 0)) if row.get("label", "0").isdigit() else 0,
                    "dataset_source": "ton_iot"
                }
                events.append(event)
                attack_types.add(event["attack_category"])
                count += 1
                if max_records and count >= max_records:
                    break

        out_file = self.processed_dir / "ton_iot_processed.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)

        # Generate splits (80% train, 10% val, 10% test)
        n = len(events)
        train_idx = int(n * 0.8)
        val_idx = int(n * 0.9)

        splits = {
            "train": events[:train_idx],
            "validation": events[train_idx:val_idx],
            "test": events[val_idx:]
        }
        with open(self.splits_dir / "ton_iot_split.json", "w", encoding="utf-8") as f:
            json.dump({k: len(v) for k, v in splits.items()}, f, indent=2)

        return {
            "dataset": "ToN-IoT",
            "total_processed": len(events),
            "attack_types": sorted(list(attack_types)),
            "output_file": str(out_file)
        }

    def process_bot_iot(self, max_records_per_file: int = 2000) -> Dict[str, Any]:
        """Ingests BoT-IoT CSV subsets into normalized HACTM events."""
        bot_files = list((self.raw_dir / "bot_iot").glob("*.csv"))
        if not bot_files:
            raise FileNotFoundError("No BoT-IoT CSV files found.")

        events = []
        categories = set()
        count = 0

        for b_file in bot_files[:5]:  # Process up to 5 CSV files for dev subset
            with open(b_file, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                file_count = 0
                for row in reader:
                    cat = row.get("category", "Normal").strip()
                    event = {
                        "event_id": f"bot_iot_{count}",
                        "timestamp": row.get("stime", "0.0"),
                        "source_ip": row.get("saddr", "0.0.0.0"),
                        "destination_ip": row.get("daddr", "0.0.0.0"),
                        "source_port": int(row.get("sport", 0)) if row.get("sport", "0").isdigit() else 0,
                        "destination_port": int(row.get("dport", 0)) if row.get("dport", "0").isdigit() else 0,
                        "protocol": row.get("proto", "tcp").lower(),
                        "packet_features": {
                            "pkts": int(row.get("pkts", 0)) if row.get("pkts", "0").isdigit() else 0,
                            "bytes": int(row.get("bytes", 0)) if row.get("bytes", "0").isdigit() else 0,
                            "rate": float(row.get("rate", 0)) if row.get("rate", "0").replace('.', '', 1).isdigit() else 0.0,
                            "dur": float(row.get("dur", 0)) if row.get("dur", "0").replace('.', '', 1).isdigit() else 0.0,
                        },
                        "attack_category": cat,
                        "label": int(row.get("attack", 0)) if row.get("attack", "0").isdigit() else 0,
                        "dataset_source": "bot_iot"
                    }
                    events.append(event)
                    categories.add(cat)
                    count += 1
                    file_count += 1
                    if max_records_per_file and file_count >= max_records_per_file:
                        break

        out_file = self.processed_dir / "bot_iot_processed.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)

        # Generate splits
        n = len(events)
        train_idx = int(n * 0.8)
        val_idx = int(n * 0.9)

        splits = {
            "train": events[:train_idx],
            "validation": events[train_idx:val_idx],
            "test": events[val_idx:]
        }
        with open(self.splits_dir / "bot_iot_split.json", "w", encoding="utf-8") as f:
            json.dump({k: len(v) for k, v in splits.items()}, f, indent=2)

        return {
            "dataset": "BoT-IoT",
            "total_processed": len(events),
            "attack_categories": sorted(list(categories)),
            "output_file": str(out_file)
        }
