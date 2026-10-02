"""
Ingestion Router for HACTM.
Handles dataset ingestion requests and run audit retrieval.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from hactm.api.schemas.common import SingleResponse
from hactm.api.schemas.evidence import IngestionRequest, IngestionRunResponse
from hactm.core.constants import IngestionPolicy
from hactm.core.errors import HACTMValidationError
from hactm.core.models import IngestionResult
from hactm.services.ingestion_service import IngestionService
from hactm.storage.database import get_db

router = APIRouter(prefix="/ingestion", tags=["Dataset Ingestion"])


@router.post("", response_model=SingleResponse[IngestionResult], status_code=status.HTTP_201_CREATED)
def trigger_ingestion(
    payload: IngestionRequest,
    db: Session = Depends(get_db),
):
    service = IngestionService(db)

    try:
        policy_enum = IngestionPolicy(payload.policy.upper())
    except ValueError:
        raise HACTMValidationError(
            f"Invalid policy '{payload.policy}'. Allowed: STRICT, SKIP_INVALID, QUARANTINE_INVALID"
        )

    if payload.file_path:
        result = service.ingest_file(
            file_path=payload.file_path,
            policy=policy_enum,
            batch_size=payload.batch_size,
            dataset_name=payload.dataset_name,
        )
    elif payload.records is not None:
        result = service.ingest_records(
            records=payload.records,
            source_name=payload.source_name or "api_payload",
            policy=policy_enum,
            dataset_name=payload.dataset_name,
        )
    else:
        raise HACTMValidationError("Must provide either 'file_path' or 'records' in ingestion payload")

    return SingleResponse(data=result)


@router.get("/{run_id}", response_model=SingleResponse[IngestionRunResponse])
def get_ingestion_run(
    run_id: str,
    db: Session = Depends(get_db),
):
    service = IngestionService(db)
    run = service.get_run(run_id)
    return SingleResponse(data=IngestionRunResponse.model_validate(run))
