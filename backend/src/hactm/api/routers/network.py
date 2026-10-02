"""
Network Security Agent API Router.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Exposes endpoints for events, detections, detection details, model training/evaluation, and agent metrics.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from hactm.api.schemas.common import PaginatedResponse, PaginationMeta, SingleResponse
from hactm.core.errors import HACTMValidationError
from hactm.network.models import AnalystLabel, NetworkDetectionResult, NetworkEvent
from hactm.services.network_service import NetworkService
from hactm.storage.database import get_db

router = APIRouter(prefix="/network", tags=["Network Security Agent"])


# Request / Response Schemas
class NetworkEventDto(BaseModel):
    event_id: str
    timestamp: Any
    src_ip: str
    dst_ip: str
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: str
    duration: Optional[float] = None
    flow_bytes: Optional[int] = None
    flow_packets: Optional[int] = None
    forward_bytes: Optional[int] = None
    backward_bytes: Optional[int] = None
    tcp_flags: Optional[str] = None
    connection_state: Optional[str] = None
    flow_rate: Optional[float] = None
    packet_rate: Optional[float] = None
    dataset: Optional[str] = None
    src_ip_classification: Optional[str] = None
    dst_ip_classification: Optional[str] = None
    label: Optional[str] = None

    class Config:
        from_attributes = True


class NetworkDetectionDto(BaseModel):
    detection_id: str
    event_id: str
    detector_type: str
    detector_id: str
    detector_version: str
    category: str
    risk_score: float
    confidence: float
    uncertainty: float
    severity: str
    reason_codes: List[str]
    explanation: str
    features_used: Dict[str, Any]
    model_version: Optional[str] = None
    signature_id: Optional[str] = None
    processing_time_ms: float
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    timestamp: Any

    class Config:
        from_attributes = True


class NetworkDetectRequest(BaseModel):
    events: Optional[List[NetworkEvent]] = None
    file_path: Optional[str] = None
    dataset_name: Optional[str] = None
    persist: bool = True


class TrainModelRequest(BaseModel):
    file_path: str
    dataset_name: Optional[str] = None
    algorithm: str = "isolation_forest"
    contamination: float = 0.05


class EvaluateModelRequest(BaseModel):
    file_path: str
    dataset_name: Optional[str] = None


class FeedbackRequest(BaseModel):
    detection_id: str
    label: AnalystLabel
    analyst_note: Optional[str] = None


@router.get("/events", response_model=PaginatedResponse[NetworkEventDto])
def list_network_events(
    src_ip: Optional[str] = Query(None, description="Filter by source IP"),
    dst_ip: Optional[str] = Query(None, description="Filter by destination IP"),
    protocol: Optional[str] = Query(None, description="Filter by protocol"),
    dst_port: Optional[int] = Query(None, description="Filter by destination port"),
    dataset: Optional[str] = Query(None, description="Filter by dataset"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    service = NetworkService(db)
    items, total = service.list_events(
        src_ip=src_ip,
        dst_ip=dst_ip,
        protocol=protocol,
        dst_port=dst_port,
        dataset=dataset,
        page=page,
        page_size=page_size,
    )
    data = [NetworkEventDto.model_validate(i) for i in items]
    return PaginatedResponse(data=data, pagination=PaginationMeta(page=page, page_size=page_size, total=total))


@router.get("/detections", response_model=PaginatedResponse[NetworkDetectionDto])
def list_network_detections(
    detector_type: Optional[str] = Query(None, description="SIGNATURE, HEURISTIC, ANOMALY"),
    category: Optional[str] = Query(None, description="Category filter"),
    severity: Optional[str] = Query(None, description="LOW, MEDIUM, HIGH, CRITICAL"),
    min_risk: Optional[float] = Query(None, ge=0.0, le=1.0),
    max_risk: Optional[float] = Query(None, ge=0.0, le=1.0),
    src_ip: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    service = NetworkService(db)
    items, total = service.list_detections(
        detector_type=detector_type,
        category=category,
        severity=severity,
        min_risk=min_risk,
        max_risk=max_risk,
        src_ip=src_ip,
        page=page,
        page_size=page_size,
    )
    data = [NetworkDetectionDto.model_validate(i) for i in items]
    return PaginatedResponse(data=data, pagination=PaginationMeta(page=page, page_size=page_size, total=total))


@router.get("/detections/{detection_id}", response_model=SingleResponse[NetworkDetectionDto])
def get_detection_details(
    detection_id: str,
    db: Session = Depends(get_db),
):
    service = NetworkService(db)
    det = service.get_detection(detection_id)
    return SingleResponse(data=NetworkDetectionDto.model_validate(det))


@router.post("/detect", response_model=SingleResponse[Dict[str, Any]], status_code=status.HTTP_201_CREATED)
def trigger_network_detection(
    payload: NetworkDetectRequest,
    db: Session = Depends(get_db),
):
    service = NetworkService(db)
    if payload.file_path:
        # Path traversal guard (Section 65)
        if ".." in payload.file_path:
            raise HACTMValidationError("Path traversal characters not allowed in file_path")
        summary = service.ingest_network_file(
            file_path=payload.file_path,
            dataset_name=payload.dataset_name,
            run_detection=True,
        )
        return SingleResponse(data=summary)
    elif payload.events:
        results = service.detect_events(
            events=payload.events,
            persist=payload.persist,
            dataset_name=payload.dataset_name or "ad_hoc",
        )
        return SingleResponse(
            data={
                "events_evaluated": len(payload.events),
                "detections_count": len(results),
                "detections": [NetworkDetectionDto.model_validate(r) for r in results],
            }
        )
    else:
        raise HACTMValidationError("Must provide either 'events' or 'file_path'")


@router.post("/train", response_model=SingleResponse[Dict[str, Any]])
def train_network_model(
    payload: TrainModelRequest,
    db: Session = Depends(get_db),
):
    if ".." in payload.file_path:
        raise HACTMValidationError("Path traversal characters not allowed")
    service = NetworkService(db)
    meta = service.train_anomaly_model(
        file_path=payload.file_path,
        dataset_name=payload.dataset_name,
        algorithm=payload.algorithm,
        contamination=payload.contamination,
    )
    return SingleResponse(data=meta.model_dump())


@router.post("/evaluate", response_model=SingleResponse[Dict[str, Any]])
def evaluate_network_agent(
    payload: EvaluateModelRequest,
    db: Session = Depends(get_db),
):
    if ".." in payload.file_path:
        raise HACTMValidationError("Path traversal characters not allowed")
    service = NetworkService(db)
    metrics = service.evaluate(
        file_path=payload.file_path,
        dataset_name=payload.dataset_name,
    )
    return SingleResponse(data=metrics.model_dump())


@router.get("/models", response_model=SingleResponse[List[Dict[str, Any]]])
def list_network_models(db: Session = Depends(get_db)):
    service = NetworkService(db)
    models = service.list_models()
    return SingleResponse(
        data=[
            {
                "model_id": m.model_id,
                "model_version": m.model_version,
                "algorithm": m.algorithm,
                "parameters": m.parameters,
                "status": m.status,
                "training_dataset": m.training_dataset,
                "training_timestamp": m.training_timestamp.isoformat() if m.training_timestamp else None,
                "evaluation_summary": m.evaluation_summary,
            }
            for m in models
        ]
    )


@router.post("/models/{model_id}/activate", response_model=SingleResponse[Dict[str, Any]])
def activate_network_model(
    model_id: str,
    db: Session = Depends(get_db),
):
    service = NetworkService(db)
    service.activate_model(model_id)
    return SingleResponse(data={"model_id": model_id, "status": "ACTIVE"})


@router.get("/metrics", response_model=SingleResponse[Dict[str, Any]])
def get_network_metrics(db: Session = Depends(get_db)):
    service = NetworkService(db)
    metrics = service.get_metrics()
    return SingleResponse(data=metrics)


@router.get("/health", response_model=SingleResponse[Dict[str, Any]])
def get_network_agent_health(db: Session = Depends(get_db)):
    service = NetworkService(db)
    health = service.agent.health()
    return SingleResponse(data=health)


@router.get("/config", response_model=SingleResponse[Dict[str, Any]])
def get_network_config(db: Session = Depends(get_db)):
    service = NetworkService(db)
    return SingleResponse(data=service.agent.config)


@router.post("/detections/{detection_id}/feedback", response_model=SingleResponse[Dict[str, Any]])
@router.post("/feedback", response_model=SingleResponse[Dict[str, Any]])
def submit_detection_feedback(
    payload: FeedbackRequest,
    detection_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = NetworkService(db)
    target_id = detection_id or payload.detection_id
    fb = service.submit_feedback(
        detection_id=target_id,
        label=payload.label,
        note=payload.analyst_note,
    )
    return SingleResponse(data={"id": fb.id, "detection_id": fb.detection_id, "label": fb.label})
