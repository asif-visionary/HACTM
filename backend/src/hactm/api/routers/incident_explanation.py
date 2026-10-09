"""
FastAPI Router for Incident Explanation and Structured Report Export.
"""

from typing import Dict, List, Any
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.fusion.incident_explainer import IncidentExplainerEngine
from hactm.api.routers.reports import export_evidence_pdf, ReportRequest

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


@router.get("/{incident_id}/explanation", response_model=Dict[str, Any])
def get_incident_explanation(incident_id: str, db: Session = Depends(get_db)):
    explainer = IncidentExplainerEngine(db)
    explanation = explainer.generate_explanation(incident_id)
    return {"status": "SUCCESS", "data": explanation}


@router.get("/{incident_id}/report/pdf")
def export_incident_pdf_report(incident_id: str, db: Session = Depends(get_db)):
    """Exports structured incident explanation report as a downloadable PDF."""
    explainer = IncidentExplainerEngine(db)
    explanation = explainer.generate_explanation(incident_id)

    # Reuse existing PDF generation pipeline from reports router
    req = ReportRequest(source=explanation["correlated_sources"][0] if explanation["correlated_sources"] else None, min_risk=0.0)
    return export_evidence_pdf(req, db)
