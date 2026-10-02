"""
JSON Dataset Loader for HACTM.
Supports standard JSON arrays, nested data wrappers, and single-record objects.
"""

import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple, Union

from hactm.ingestion.loaders.base import BaseDatasetLoader


class JSONLoader(BaseDatasetLoader):
    """
    Loads JSON records from a JSON file.
    Supports top-level array, or objects containing an array under 'data', 'records', 'events', or 'evidence'.
    """
    def stream_batches(
        self, batch_size: int = 1000
    ) -> Generator[List[Tuple[int, Dict[str, Any]]], None, None]:
        if self.file_path.stat().st_size == 0:
            return

        with open(self.file_path, mode="r", encoding="utf-8", errors="replace") as f:
            try:
                data = json.load(f)
            except Exception as e:
                raise ValueError(f"Malformed JSON file {self.file_path.name}: {e}")

        records: List[Dict[str, Any]] = []
        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            for key in ["data", "records", "events", "evidence", "items"]:
                if key in data and isinstance(data[key], list):
                    records = data[key]
                    break
            if not records:
                records = [data]
        else:
            raise ValueError(f"Unexpected JSON root type: {type(data)}")

        batch: List[Tuple[int, Dict[str, Any]]] = []
        for idx, rec in enumerate(records, start=1):
            if isinstance(rec, dict):
                batch.append((idx, rec))
            else:
                batch.append((idx, {"raw_value": rec}))

            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch
