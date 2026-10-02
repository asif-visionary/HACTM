"""
FastAPI Router for Evaluation - Evaluation, Scalability & Baseline Research Endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api/v1/evaluation", tags=["Evaluation Framework & Scalability"])


@router.get("/datasets")
def list_datasets(domain: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Lists registered evaluation datasets for research experiments."""
    svc = EvaluationService(db)
    return {"datasets": svc.list_datasets(domain=domain)}


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str = Path(...), db: Session = Depends(get_db)):
    """Retrieves dataset registry metadata."""
    svc = EvaluationService(db)
    ds = svc.get_dataset(dataset_id)
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    return ds


@router.get("/experiments")
def list_experiments(db: Session = Depends(get_db)):
    """Lists Master Experiments 1 through 14 configuration definitions."""
    svc = EvaluationService(db)
    return {"experiments": svc.list_experiments()}


@router.post("/experiments/run")
def run_experiment(
    experiment_id: str = Query("EXP_14_END_TO_END"),
    workload_size: int = Query(10000, ge=100, le=5000000),
    db: Session = Depends(get_db),
):
    """Executes a master research experiment run."""
    svc = EvaluationService(db)
    return svc.run_experiment(experiment_id, workload_size)


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    """Lists recent experiment execution runs and status."""
    svc = EvaluationService(db)
    return {"runs": svc.list_runs()}


@router.get("/metrics")
def get_metrics_summary(db: Session = Depends(get_db)):
    """Retrieves empirical quantitative metrics summary across detection, calibration, and efficiency."""
    svc = EvaluationService(db)
    return svc.get_metrics_summary()


@router.get("/scalability")
def get_scalability_matrix(db: Session = Depends(get_db)):
    """Retrieves workload scalability benchmark matrix from 10K to 5M events."""
    svc = EvaluationService(db)
    return svc.get_scalability_matrix()


@router.get("/ablations")
def get_ablation_matrix(db: Session = Depends(get_db)):
    """Retrieves system component ablation matrix (A1 to A12)."""
    svc = EvaluationService(db)
    return svc.get_ablation_matrix()


@router.get("/baselines")
def get_baselines_comparison(db: Session = Depends(get_db)):
    """Retrieves comparative evaluation matrix against Baselines 1 through 9."""
    svc = EvaluationService(db)
    return svc.get_baselines_comparison()
