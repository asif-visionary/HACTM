"""
Ingestion Pipeline Orchestrator for HACTM.
Coordinates:
Loaders -> Validation -> Normalization -> Deterministic Entity Resolution ->
Idempotent Storage -> Quarantine Isolation -> Ingestion Audit Trail.
"""

import uuid
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple, Union
from sqlalchemy.orm import Session

from hactm.core.constants import IngestionPolicy, EntityType
from hactm.core.errors import HACTMValidationError, QuarantineRecordError
from hactm.core.logging import logger
from hactm.core.models import IngestionResult, SecurityEvidence
from hactm.ingestion.entity_resolution import resolve_entity
from hactm.ingestion.loaders.base import BaseDatasetLoader
from hactm.ingestion.loaders.csv_loader import CSVLoader
from hactm.ingestion.loaders.json_loader import JSONLoader
from hactm.ingestion.loaders.jsonl_loader import JSONLLoader
from hactm.ingestion.quarantine import quarantine_manager
from hactm.ingestion.validation import validate_and_build_evidence
from hactm.storage.repositories.entity_repo import EntityRepository
from hactm.storage.repositories.evidence_repo import EvidenceRepository
from hactm.storage.repositories.ingestion_repo import IngestionRepository


def get_loader_for_file(file_path: Union[str, Path]) -> BaseDatasetLoader:
    """Factory creating appropriate loader based on file extension."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return CSVLoader(path)
    elif suffix == ".json":
        return JSONLoader(path)
    elif suffix in [".jsonl", ".ndjson", ".log"]:
        return JSONLLoader(path)
    raise ValueError(f"Unsupported file format '{suffix}'. Supported formats: .csv, .json, .jsonl")


class IngestionPipeline:
    """
    Executes end-to-end ingestion with idempotency, batching, and error policy enforcement.
    """
    def __init__(self, db: Session):
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.entity_repo = EntityRepository(db)
        self.ingestion_repo = IngestionRepository(db)

    def ingest_file(
        self,
        file_path: Union[str, Path],
        policy: IngestionPolicy = IngestionPolicy.QUARANTINE_INVALID,
        batch_size: int = 1000,
        dataset_name: Optional[str] = None,
        agent_id: str = "HACTM_INGESTION"
    ) -> IngestionResult:
        """
        Ingests records from a file in memory-efficient batches.
        """
        path = Path(file_path)
        loader = get_loader_for_file(path)
        ds_name = dataset_name or path.stem

        return self.ingest_stream(
            records_stream=loader.stream_batches(batch_size=batch_size),
            source_name=path.name,
            policy=policy,
            dataset_name=ds_name,
            agent_id=agent_id
        )

    def ingest_records(
        self,
        records: List[Dict[str, Any]],
        source_name: str = "manual_input",
        policy: IngestionPolicy = IngestionPolicy.QUARANTINE_INVALID,
        dataset_name: Optional[str] = None,
        agent_id: str = "HACTM_API"
    ) -> IngestionResult:
        """
        Ingests a list of in-memory dictionary records.
        """
        def single_batch() -> Generator[List[Tuple[int, Dict[str, Any]]], None, None]:
            yield [(idx, r) for idx, r in enumerate(records, start=1)]

        return self.ingest_stream(
            records_stream=single_batch(),
            source_name=source_name,
            policy=policy,
            dataset_name=dataset_name or source_name,
            agent_id=agent_id
        )

    def ingest_stream(
        self,
        records_stream: Iterable[List[Tuple[int, Dict[str, Any]]]],
        source_name: str,
        policy: IngestionPolicy,
        dataset_name: str,
        agent_id: str
    ) -> IngestionResult:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        self.ingestion_repo.create_run(run_id=run_id, source_name=source_name, policy=policy.value)

        total = 0
        inserted = 0
        duplicates = 0
        invalid = 0
        quarantined = 0
        failed = 0

        # Maintain in-run seen event_ids for intra-batch idempotency
        seen_event_ids = set()

        try:
            for batch in records_stream:
                batch_evidence_to_insert = []
                batch_entities_to_upsert = []

                for row_num, raw_record in batch:
                    total += 1

                    # Check for loader-level decoding error
                    if "__malformed_json_error__" in raw_record:
                        err_msg = f"JSON decode error: {raw_record.get('__malformed_json_error__')}"
                        invalid += 1
                        if policy == IngestionPolicy.STRICT:
                            raise HACTMValidationError(err_msg)
                        elif policy == IngestionPolicy.QUARANTINE_INVALID:
                            q_file = quarantine_manager.quarantine_record(
                                raw_record=raw_record.get("__raw_line__"),
                                source_name=source_name,
                                row_number=row_num,
                                error_reason=err_msg,
                                run_id=run_id
                            )
                            self.ingestion_repo.record_error(
                                run_id=run_id,
                                source_name=source_name,
                                row_number=row_num,
                                error_reason=err_msg,
                                quarantine_file=str(q_file),
                                raw_record=raw_record
                            )
                            quarantined += 1
                        continue

                    # Validation & Canonicalization
                    try:
                        evidence_obj = validate_and_build_evidence(raw_record, default_agent_id=agent_id)
                        # Set Lineage fields
                        evidence_obj.source = evidence_obj.source or source_name
                        evidence_obj.dataset = evidence_obj.dataset or dataset_name
                        evidence_obj.dataset_name = evidence_obj.dataset_name or dataset_name
                        evidence_obj.source_record_id = str(row_num)
                        evidence_obj.ingestion_run_id = run_id

                        # Deterministic Entity Resolution
                        ent_id, ent_type, canon_name, attrs = resolve_entity(raw_record)
                        evidence_obj.entity_id = ent_id

                        # Idempotency Check
                        if evidence_obj.event_id in seen_event_ids or self.evidence_repo.exists(evidence_obj.event_id):
                            duplicates += 1
                            continue

                        seen_event_ids.add(evidence_obj.event_id)

                        # Queue entity upsert & evidence insert
                        self.entity_repo.upsert_entity(
                            entity_id=ent_id,
                            entity_type=ent_type,
                            canonical_name=canon_name,
                            attributes=attrs,
                            seen_at=evidence_obj.timestamp
                        )
                        self.evidence_repo.insert_evidence_and_event(evidence_obj)
                        inserted += 1

                    except (HACTMValidationError, Exception) as val_err:
                        err_reason = str(val_err)
                        invalid += 1
                        if policy == IngestionPolicy.STRICT:
                            self.db.rollback()
                            self.ingestion_repo.update_run_stats(
                                run_id=run_id,
                                total=total,
                                inserted=inserted,
                                duplicates=duplicates,
                                invalid=invalid,
                                quarantined=quarantined,
                                failed=total - inserted,
                                status="FAILED",
                                error_message=err_reason
                            )
                            raise val_err

                        elif policy == IngestionPolicy.QUARANTINE_INVALID:
                            q_file = quarantine_manager.quarantine_record(
                                raw_record=raw_record,
                                source_name=source_name,
                                row_number=row_num,
                                error_reason=err_reason,
                                run_id=run_id
                            )
                            self.ingestion_repo.record_error(
                                run_id=run_id,
                                source_name=source_name,
                                row_number=row_num,
                                error_reason=err_reason,
                                quarantine_file=str(q_file),
                                raw_record=raw_record
                            )
                            quarantined += 1

                        elif policy == IngestionPolicy.SKIP_INVALID:
                            self.ingestion_repo.record_error(
                                run_id=run_id,
                                source_name=source_name,
                                row_number=row_num,
                                error_reason=err_reason,
                                raw_record=raw_record
                            )

                # Commit batch transaction to DB
                self.db.commit()

            # Mark run completed
            self.ingestion_repo.update_run_stats(
                run_id=run_id,
                total=total,
                inserted=inserted,
                duplicates=duplicates,
                invalid=invalid,
                quarantined=quarantined,
                failed=0,
                status="COMPLETED"
            )

        except Exception as e:
            self.db.rollback()
            self.ingestion_repo.update_run_stats(
                run_id=run_id,
                total=total,
                inserted=inserted,
                duplicates=duplicates,
                invalid=invalid,
                quarantined=quarantined,
                failed=total - (inserted + duplicates),
                status="FAILED",
                error_message=str(e)
            )
            raise

        logger.info(
            f"Ingestion completed for '{source_name}' [Run {run_id}]: "
            f"Total={total}, Inserted={inserted}, Duplicates={duplicates}, "
            f"Invalid={invalid}, Quarantined={quarantined}"
        )

        return IngestionResult(
            run_id=run_id,
            inserted=inserted,
            duplicates=duplicates,
            invalid=invalid,
            quarantined=quarantined,
            failed=failed,
            total=total
        )
