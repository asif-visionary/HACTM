import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from hactm.api.schemas.common import SingleResponse
from hactm.api.schemas.evidence import EvidenceResponse, ReportRequest, ReportResponse
from hactm.services.evidence_service import EvidenceService
from hactm.services.evaluation_service import EvaluationService
from hactm.services.evidence_pdf_generator import generate_evidence_pdf
from hactm.storage.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reports", tags=["Evaluation Research Reports & Exports"])


def _build_evidence_report_data(payload: ReportRequest, db: Session) -> ReportResponse:
    if payload.min_risk is not None and (payload.min_risk < 0.0 or payload.min_risk > 1.0):
        raise HTTPException(
            status_code=400,
            detail="Minimum Cyber Risk must be a number between 0 and 1."
        )

    service = EvidenceService(db)
    items, total = service.list_evidence(
        entity_id=payload.entity_id,
        event_type=payload.event_type,
        source=payload.source,
        min_risk=payload.min_risk,
        start_time=payload.start_time,
        end_time=payload.end_time,
        page=1,
        page_size=250,
    )

    records = [EvidenceResponse.model_validate(i) for i in items]
    report_id = f"RPT-EVD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    avg_risk = round(sum(r.risk_score for r in records) / len(records), 4) if records else 0.0
    high_risk_in_report = sum(1 for r in records if r.risk_score >= 0.6)

    sev_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    risk_dist = {"LOW (<0.3)": 0, "MEDIUM (0.3-0.6)": 0, "HIGH (0.6-0.85)": 0, "CRITICAL (>=0.85)": 0}

    for r in records:
        sev_key = (r.severity or "LOW").upper()
        if sev_key in sev_dist:
            sev_dist[sev_key] += 1
        else:
            sev_dist["LOW"] += 1

        if r.risk_score < 0.3:
            risk_dist["LOW (<0.3)"] += 1
        elif r.risk_score < 0.6:
            risk_dist["MEDIUM (0.3-0.6)"] += 1
        elif r.risk_score < 0.85:
            risk_dist["HIGH (0.6-0.85)"] += 1
        else:
            risk_dist["CRITICAL (>=0.85)"] += 1

    entities_rep = len(set(r.entity_id for r in records))
    sources_rep = len(set(r.source or r.agent_id for r in records))
    types_rep = len(set(r.event_type for r in records))

    report_response = ReportResponse(
        report_id=report_id,
        title="Structured Security Evidence Report",
        generated_at=datetime.now(timezone.utc),
        filters=payload.model_dump(exclude_none=True),
        summary={
            "total_records": len(records),
            "total_records_in_scope": total,
            "included_records": len(records),
            "average_cyber_risk_score": avg_risk,
            "high_risk_events_count": high_risk_in_report,
            "entities_represented": entities_rep,
            "sources_represented": sources_rep,
            "event_types_represented": types_rep,
            "severity_distribution": sev_dist,
            "risk_distribution": risk_dist,
            "pdf_export_status": "AVAILABLE",
        },
        evidence_count=len(records),
        records=records,
    )

    logger.info(
        f"Generated Evidence Report: report_id={report_id}, records={len(records)}, "
        f"filters={payload.model_dump(exclude_none=True)}"
    )
    return report_response


@router.post("/evidence", response_model=SingleResponse[ReportResponse])
def generate_evidence_report(
    payload: ReportRequest,
    db: Session = Depends(get_db),
):
    """Synthesizes structured security evidence report based on applied filter parameters."""
    report = _build_evidence_report_data(payload, db)
    return SingleResponse(data=report)


@router.post("/evidence/pdf")
def export_evidence_pdf(
    payload: ReportRequest,
    db: Session = Depends(get_db),
):
    """Generates and downloads a formatted PDF Evidence Report document."""
    report = _build_evidence_report_data(payload, db)
    pdf_bytes = generate_evidence_pdf(report.model_dump())
    filename = f"{report.report_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# --- Evaluation Research Reports ---
@router.get("")
def list_reports(db: Session = Depends(get_db)):
    """Lists generated research reports and reproducibility bundles."""
    svc = EvaluationService(db)
    return {"reports": svc.list_reports()}


@router.post("/generate")
def generate_research_report(
    experiment_id: str = Query("EXP_14_END_TO_END"),
    title: str = Query("HACTM Final Research Evaluation & Scalability Report"),
    format: str = Query("PDF", regex="^(PDF|JSON|CSV)$"),
    db: Session = Depends(get_db),
):
    """Triggers asynchronous generation of a research report in PDF, JSON, or CSV format."""
    svc = EvaluationService(db)
    return svc.generate_report_job(experiment_id, title, format)


@router.get("/{report_id}")
def get_report(report_id: str = Path(...), db: Session = Depends(get_db)):
    """Retrieves metadata of a generated research report."""
    svc = EvaluationService(db)
    report = svc.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return report


@router.get("/{report_id}/status")
def get_report_status(report_id: str = Path(...), db: Session = Depends(get_db)):
    """Retrieves asynchronous generation status of a research report."""
    svc = EvaluationService(db)
    report = svc.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return {"report_id": report_id, "status": report.get("status", "COMPLETED")}


@router.get("/{report_id}/export")
def export_report_file(report_id: str = Path(...), db: Session = Depends(get_db)):
    """Exports and downloads the report file artifact (PDF/JSON/CSV)."""
    svc = EvaluationService(db)
    report = svc.get_report(report_id)
    if not report or not report.get("artifact_path"):
        raise HTTPException(status_code=404, detail=f"Report file artifact for {report_id} not found")

    path = report["artifact_path"]
    filename = f"{report_id}.pdf" if report.get("format") == "PDF" else f"{report_id}.json"
    return FileResponse(path, filename=filename, media_type="application/octet-stream")
