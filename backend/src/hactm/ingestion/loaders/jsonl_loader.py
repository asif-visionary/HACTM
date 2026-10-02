"""
JSONL (JSON Lines) Dataset Loader for HACTM.
Streams records line-by-line for high throughput and zero memory bloat.
Handles malformed lines according to ingestion policy.
"""

import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Tuple, Union

from hactm.ingestion.loaders.base import BaseDatasetLoader


class JSONLLoader(BaseDatasetLoader):
    """
    Streams JSONL records line by line in configurable batch sizes.
    """
    def stream_batches(
        self, batch_size: int = 1000
    ) -> Generator[List[Tuple[int, Dict[str, Any]]], None, None]:
        if self.file_path.stat().st_size == 0:
            return

        with open(self.file_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
            batch: List[Tuple[int, Dict[str, Any]]] = []
            for line_idx, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue

                try:
                    record = json.loads(clean_line)
                    if isinstance(record, dict):
                        batch.append((line_idx, record))
                    else:
                        batch.append((line_idx, {"raw_value": record}))
                except json.JSONDecodeError as e:
                    # Provide record indicating malformed line for pipeline quarantine / policy handling
                    batch.append((line_idx, {"__malformed_json_error__": str(e), "__raw_line__": clean_line}))

                if len(batch) >= batch_size:
                    yield batch
                    batch = []

            if batch:
                yield batch
