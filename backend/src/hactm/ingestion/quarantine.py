"""
Data Quarantine Manager.
Isolates records that fail validation, schema constraints, or parsing into
local quarantine storage and logs lineage for research auditability.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from hactm.core.config import settings
from hactm.core.logging import logger


class QuarantineManager:
    """
    Manages writing quarantined records to data/processed/quarantine/.
    """
    def __init__(self, quarantine_dir: Optional[Path] = None):
        self.quarantine_dir = quarantine_dir or settings.QUARANTINE_DIR
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def quarantine_record(
        self,
        raw_record: Any,
        source_name: str,
        row_number: Optional[int],
        error_reason: str,
        run_id: Optional[str] = None
    ) -> Path:
        """
        Persists a rejected/malformed record with context into a quarantine JSON file.
        Returns the path to the written quarantine file.
        """
        ts = datetime.now(timezone.utc)
        ts_slug = ts.strftime("%Y%m%d_%H%M%S_%f")
        filename = f"quarantine_{run_id or 'manual'}_{ts_slug}.json"
        target_path = self.quarantine_dir / filename

        quarantine_payload = {
            "quarantined_at": ts.isoformat(),
            "run_id": run_id,
            "source_name": source_name,
            "row_number": row_number,
            "error_reason": error_reason,
            "original_record": raw_record,
        }

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(quarantine_payload, f, indent=2, default=str)
            logger.warning(
                f"Quarantined record from {source_name} (row {row_number}): {error_reason} -> {target_path.name}"
            )
        except Exception as e:
            logger.error(f"Failed to write quarantine file {target_path}: {e}")

        return target_path


quarantine_manager = QuarantineManager()
