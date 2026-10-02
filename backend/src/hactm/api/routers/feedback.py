"""
FastAPI Router for Closed-Loop Adaptation - Closed-Loop Cyber Trust Feedback & Continuous Adaptation.
Implements all 27 Closed-Loop Adaptation API endpoints.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.feedback_service import FeedbackService
from hactm.feedback.models import (
    SecurityDecisionOutcome,
    FeedbackEvent,
    ValidationStatus,
    DecisionReplayRequest,
    CounterfactualRequest,
)

router = APIRouter(prefix="/api/v1", tags=["Closed-Loop Adaptation Closed-Loop Feedback"])


# --- Feedback Endpoints ---
@router.post("/feedback")
def submit_feedback(feedback: FeedbackEvent, db: Session = Depends(get_db)):
    """Submits a traceable security feedback event."""
    svc = FeedbackService(db)
    return svc.ingest_feedback(feedback)


@router.get("/feedback")
def list_feedback(limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    """Lists recent feedback events."""
    svc = FeedbackService(db)
    return {"feedback": svc.list_feedback(limit=limit)}


@router.get("/feedback/{feedback_id}")
def get_feedback(feedback_id: str = Path(...), db: Session = Depends(get_db)):
    """Retrieves a specific feedback event by ID."""
    svc = FeedbackService(db)
    fb = svc.get_feedback(feedback_id)
    if not fb:
        raise HTTPException(status_code=404, detail=f"Feedback {feedback_id} not found")
    return fb


@router.post("/feedback/validate")
def validate_feedback(
    outcome_id: str = Query(...),
    validation_status: ValidationStatus = Query(...),
    analyst_id: str = Query("analyst_1"),
    db: Session = Depends(get_db),
):
    """Validates an observed outcome or feedback event."""
    svc = FeedbackService(db)
    res = svc.validate_outcome(outcome_id, validation_status, analyst_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Outcome {outcome_id} not found")
    return {"status": "SUCCESS", "outcome": res}


@router.post("/feedback/retract")
def retract_feedback(
    feedback_id: str = Query(...),
    reason: str = Query("Analyst error"),
    operator: str = Query("analyst_1"),
    db: Session = Depends(get_db),
):
    """Retracts an erroneous feedback event."""
    svc = FeedbackService(db)
    return svc.retract_feedback(feedback_id, reason, operator)


# --- Outcomes Endpoints ---
@router.get("/outcomes")
def list_outcomes(
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lists observed security decision outcomes."""
    svc = FeedbackService(db)
    return {"outcomes": svc.list_outcomes(limit=limit, status=status)}


@router.post("/outcomes")
def record_outcome(outcome: SecurityDecisionOutcome, db: Session = Depends(get_db)):
    """Records a post-decision observed outcome."""
    svc = FeedbackService(db)
    saved = svc.record_outcome(outcome)
    return {"status": "RECORDED", "outcome": saved}


# --- Adaptation Endpoints ---
@router.get("/adaptation")
def get_adaptation_status(db: Session = Depends(get_db)):
    """Returns adaptation engine configuration and mode status."""
    svc = FeedbackService(db)
    return {
        "learning_mode": svc.adaptation_engine.learning_mode.value,
        "current_agent_weights": svc.adaptation_engine.current_agent_weights,
        "current_policy_thresholds": svc.adaptation_engine.current_policy_thresholds,
    }


@router.get("/adaptation/proposals")
def list_adaptation_proposals(
    status: Optional[str] = Query(None), db: Session = Depends(get_db)
):
    """Lists calculated adaptation proposals."""
    svc = FeedbackService(db)
    return {"proposals": svc.list_proposals(status=status)}


@router.post("/adaptation/proposals/{proposal_id}/approve")
def approve_proposal(
    proposal_id: str = Path(...),
    reviewer: str = Query("analyst_admin"),
    reason: str = Query("Approved after shadow evaluation"),
    db: Session = Depends(get_db),
):
    """Analyst approves an adaptation proposal for runtime application."""
    svc = FeedbackService(db)
    return svc.approve_proposal(proposal_id, reviewer, reason)


@router.post("/adaptation/proposals/{proposal_id}/reject")
def reject_proposal(
    proposal_id: str = Path(...),
    reviewer: str = Query("analyst_admin"),
    reason: str = Query("Rejected due to safety risk"),
    db: Session = Depends(get_db),
):
    """Rejects a proposed adaptation."""
    svc = FeedbackService(db)
    return svc.reject_proposal(proposal_id, reviewer, reason)


@router.post("/adaptation/shadow-evaluate")
def shadow_evaluate_proposal(proposal_id: str = Query(...), db: Session = Depends(get_db)):
    """Runs shadow evaluation of a proposed adaptation against historical traffic."""
    svc = FeedbackService(db)
    return svc.shadow_evaluate_proposal(proposal_id)


@router.get("/adaptation/history")
def get_adaptation_history(db: Session = Depends(get_db)):
    """Retrieves full audit trail of applied adaptations."""
    svc = FeedbackService(db)
    return {"history": svc.get_adaptation_history()}


@router.get("/adaptation/stability")
def get_adaptation_stability(db: Session = Depends(get_db)):
    """Retrieves system adaptation stability metrics and policy churn."""
    svc = FeedbackService(db)
    return svc.get_stability_metrics()


# --- Model Registry Endpoints ---
@router.get("/models/champion")
def get_champion_models(db: Session = Depends(get_db)):
    """Lists active Champion model versions across agents."""
    svc = FeedbackService(db)
    return svc.get_champion_models()


@router.get("/models/challengers")
def get_challenger_models(db: Session = Depends(get_db)):
    """Lists candidate Challenger model versions."""
    svc = FeedbackService(db)
    return svc.get_challenger_models()


@router.post("/models/evaluate")
def evaluate_models(
    champion_id: str = Query(...),
    challenger_id: str = Query(...),
    db: Session = Depends(get_db),
):
    """Runs multi-criteria evaluation comparing Champion vs Challenger models."""
    svc = FeedbackService(db)
    return svc.evaluate_model_version(champion_id, challenger_id)


@router.post("/models/promote")
def promote_model(
    model_id: str = Query(...),
    version_id: str = Query(...),
    operator: str = Query("mlops_admin"),
    reason: str = Query("Superior F1 and ECE in shadow evaluation"),
    db: Session = Depends(get_db),
):
    """Promotes an approved Challenger model to active Champion."""
    svc = FeedbackService(db)
    return svc.promote_model_version(model_id, version_id, operator, reason)


@router.post("/models/rollback")
def rollback_model(
    model_id: str = Query(...),
    to_version_id: str = Query(...),
    operator: str = Query("mlops_admin"),
    reason: str = Query("Performance degradation detected"),
    db: Session = Depends(get_db),
):
    """Rolls back Champion model to a previous active version."""
    svc = FeedbackService(db)
    return svc.rollback_model_version(model_id, to_version_id, operator, reason)


# --- Policy & Research Analytics ---
@router.get("/policy-effectiveness")
def get_policy_effectiveness(db: Session = Depends(get_db)):
    """Retrieves security policy effectiveness, legitimate access rate, and false block metrics."""
    svc = FeedbackService(db)
    return svc.get_policy_effectiveness()


@router.get("/decision-replay")
def list_decision_replays(db: Session = Depends(get_db)):
    """Lists recent decision replay runs."""
    return {"replays": []}


@router.post("/decision-replay/run")
def run_decision_replay(request: DecisionReplayRequest, db: Session = Depends(get_db)):
    """Reconstructs historical decision given specific time or parameter overrides."""
    svc = FeedbackService(db)
    return svc.run_decision_replay(request)


@router.get("/counterfactual")
def list_counterfactuals(db: Session = Depends(get_db)):
    """Lists counterfactual scenario runs."""
    return {"counterfactual_runs": []}


@router.post("/counterfactual/run")
def run_counterfactual(request: CounterfactualRequest, db: Session = Depends(get_db)):
    """Runs counterfactual scenario simulation across historical traffic."""
    svc = FeedbackService(db)
    return svc.run_counterfactual_simulation(request)


@router.get("/drift/response")
def get_drift_responses(db: Session = Depends(get_db)):
    """Retrieves drift monitoring response decisions."""
    svc = FeedbackService(db)
    return svc.get_drift_responses()


@router.get("/closed_loop_adaptation/health")
def get_closed_loop_adaptation_health(db: Session = Depends(get_db)):
    """Retrieves Closed-Loop Adaptation system health status."""
    svc = FeedbackService(db)
    return svc.get_closed_loop_adaptation_health()


@router.post("/eval/baselines")
def run_eval_baselines(db: Session = Depends(get_db)):
    """Runs Closed-Loop Adaptation Baselines A-F and Ablation A1-A12 research evaluations."""
    svc = FeedbackService(db)
    baselines = svc.evaluator.run_baselines_comparison([])
    ablations = svc.evaluator.run_ablations_study([])
    scenario = svc.evaluator.run_evolving_threat_scenario()
    return {
        "baselines": baselines,
        "ablations": ablations,
        "evolving_threat_scenario": scenario,
    }
