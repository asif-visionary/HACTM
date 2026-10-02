"""
Ingestion Repository for HACTM.
Tracks batch ingestion execution lifecycle and quarantine error audits.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from hactm.storage.models import IngestionRunModel, IngestionErrorModel


class IngestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_run(self, run_id: str, source_name: str, policy: str) -> IngestionRunModel:
        run = IngestionRunModel(
            run_id=run_id,
            source_name=source_name,
            started_at=datetime.now(timezone.utc),
            status="IN_PROGRESS",
            policy=policy,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def update_run_stats(
        self,
        run_id: str,
        total: int,
        inserted: int,
        duplicates: int,
        invalid: int,
        quarantined: int,
        failed: int,
        status: str = "COMPLETED",
        error_message: Optional[str] = None
    ) -> Optional[IngestionRunModel]:
        run = self.db.query(IngestionRunModel).filter(IngestionRunModel.run_id == run_id).first()
        if run:
            run.total_records = total
            run.inserted = inserted
            run.duplicates = duplicates
            run.invalid = invalid
            run.quarantined = quarantined
            run.failed = failed
            run.status = status
            run.error_message = error_message
            run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(run)
        return run

    def record_error(
        self,
        run_id: str,
        source_name: str,
        row_number: Optional[int],
        error_reason: str,
        quarantine_file: Optional[str] = None,
        raw_record: Optional[Dict[str, Any]] = None
    ) -> IngestionErrorModel:
        err = IngestionErrorModel(
            run_id=run_id,
            source_name=source_name,
            row_number=row_number,
            error_reason=error_reason,
            quarantine_file=quarantine_file,
            raw_record=raw_record,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(err)
        return err

    def get_run(self, run_id: str) -> Optional[IngestionRunModel]:
        return self.db.query(IngestionRunModel).filter(IngestionRunModel.run_id == run_id).first()

    def get_latest_run(self) -> Optional[IngestionRunModel]:
        return self.db.query(IngestionRunModel).order_by(IngestionRunModel.started_at.desc()).first()

    def calculate_health_percentage(self) -> float:
        """
        Calculates overall ingestion health:
        Percentage of total successfully processed records vs total ingested.
        Returns 100.0 if no runs have occurred.
        """
        runs = self.db.query(IngestionRunModel).all()
        if not runs:
            return 100.0
        total_rec = sum(r.total_records for r in runs)
        if total_rec == 0:
            return 100.0
        inserted_rec = sum(r.inserted for r in runs)
        return round((inserted_rec / total_rec) * 100.0, 1)
