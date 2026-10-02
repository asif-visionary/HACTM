"""
CSV Dataset Loader for HACTM.
Handles:
- Missing file check
- Empty files
- UTF-8 with BOM (utf-8-sig)
- Quoted CSV fields
- Embedded JSON strings inside cells
- Unicode characters
- Memory-efficient batching without loading entire file
"""

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from hactm.ingestion.loaders.base import BaseDatasetLoader


def _try_parse_embedded_json(val: str) -> Any:
    """Safely unpacks JSON dict/list if a CSV cell contains structured JSON."""
    s = val.strip()
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except Exception:
            return val
    return val


class CSVLoader(BaseDatasetLoader):
    """
    Streams CSV records in configurable batches.
    """
    def stream_batches(
        self, batch_size: int = 1000
    ) -> Generator[List[Tuple[int, Dict[str, Any]]], None, None]:
        if self.file_path.stat().st_size == 0:
            return

        with open(self.file_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return

            batch: List[Tuple[int, Dict[str, Any]]] = []
            row_idx = 1  # 1 is header, first data row is 2

            for raw_row in reader:
                row_idx += 1
                record: Dict[str, Any] = {}
                for k, v in raw_row.items():
                    if k is not None:
                        clean_k = k.strip()
                        if isinstance(v, str):
                            record[clean_k] = _try_parse_embedded_json(v)
                        else:
                            record[clean_k] = v

                batch.append((row_idx, record))

                if len(batch) >= batch_size:
                    yield batch
                    batch = []

            if batch:
                yield batch
