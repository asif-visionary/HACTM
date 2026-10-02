"""
Health and Status Router for HACTM.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from hactm.core.config import settings
from hactm.storage.database import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "HACTM — Hierarchical Adaptive Cyber Trust Mesh",
        "phase": "Foundation: Foundation + Common Data Model",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "schema_version": "1.0.0",
    }
