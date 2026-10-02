"""
Ingestion Service for HACTM.
Exposes pipeline runs and execution history.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from sqlalchemy.orm import Session

from hactm.core.constants import IngestionPolicy
from hactm.core.errors import NotFoundError
from hactm.core.models import IngestionResult
from hactm.ingestion.pipeline import IngestionPipeline
from hactm.storage.models import IngestionRunModel
from hactm.storage.repositories.ingestion_repo import IngestionRepository


class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = IngestionRepository(db)
        self.pipeline = IngestionPipeline(db)

    def ingest_file(
        self,
        file_path: Union[str, Path],
        policy: IngestionPolicy = IngestionPolicy.QUARANTINE_INVALID,
        batch_size: int = 1000,
        dataset_name: Optional[str] = None
    ) -> IngestionResult:
        return self.pipeline.ingest_file(
            file_path=file_path,
            policy=policy,
            batch_size=batch_size,
            dataset_name=dataset_name
        )

    def ingest_records(
        self,
        records: List[Dict[str, Any]],
        source_name: str = "api_ingestion",
        policy: IngestionPolicy = IngestionPolicy.QUARANTINE_INVALID,
        dataset_name: Optional[str] = None
    ) -> IngestionResult:
        return self.pipeline.ingest_records(
            records=records,
            source_name=source_name,
            policy=policy,
            dataset_name=dataset_name
        )

    def get_run(self, run_id: str) -> IngestionRunModel:
        run = self.repo.get_run(run_id)
        if not run:
            raise NotFoundError(f"Ingestion run '{run_id}' not found")
        return run
