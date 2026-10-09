"""
FastAPI Router for Resilience Evaluation Harness.
Executes baseline vs. HACTM benchmark comparisons across 8 labeled scenarios.
"""

from typing import Dict, List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.eval.resilience_harness import ResilienceEvaluationHarness, SCENARIOS

router = APIRouter(prefix="/api/v1/resilience-evaluation", tags=["resilience-evaluation"])


@router.get("/scenarios", response_model=Dict[str, Any])
def list_resilience_scenarios():
    return {"count": len(SCENARIOS), "data": SCENARIOS}


@router.post("/run", response_model=Dict[str, Any])
def run_resilience_benchmark(db: Session = Depends(get_db)):
    harness = ResilienceEvaluationHarness(db)
    results = harness.run_full_evaluation()
    return {"status": "SUCCESS", "data": results}
