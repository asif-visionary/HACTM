"""
FastAPI Router for Governed Investigations, Human Approvals, and Audit Trail.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.orchestration.governed_controller import GovernedInvestigationController
from hactm.zerotrust.approval_gate import HumanApprovalGate
from hactm.storage.audit import AuditTrailService
from hactm.api.schemas.governed_investigation import WorkOrderCreate, WorkOrderResponse, ValidatePackRequest
from hactm.api.schemas.approval import ApprovalRequestCreate, HumanApprovalDecision, ApprovalRequestResponse
from hactm.storage.models import WorkOrderModel, ApprovalRequestModel, AuditEventModel
from hactm.core.errors import NotFoundError, HACTMValidationError

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])


# ============================================================
# 1. Governed Work Orders
# ============================================================
@router.post("/work-orders", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_work_order(payload: WorkOrderCreate, db: Session = Depends(get_db)):
    controller = GovernedInvestigationController(db)
    model = controller.create_work_order(payload)
    return {"status": "SUCCESS", "message": "Work Order created", "data": WorkOrderResponse.model_validate(model)}


@router.get("/work-orders", response_model=Dict[str, Any])
def list_work_orders(assigned_agent_id: Optional[str] = None, status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(WorkOrderModel)
    if assigned_agent_id:
        query = query.filter(WorkOrderModel.assigned_agent_id == assigned_agent_id)
    if status_filter:
        query = query.filter(WorkOrderModel.status == status_filter)
    orders = query.order_by(WorkOrderModel.created_at.desc()).all()
    return {"count": len(orders), "data": [WorkOrderResponse.model_validate(o) for o in orders]}


@router.get("/work-orders/{work_order_id}", response_model=Dict[str, Any])
def get_work_order(work_order_id: str, db: Session = Depends(get_db)):
    controller = GovernedInvestigationController(db)
    model = controller.get_work_order(work_order_id)
    return {"data": WorkOrderResponse.model_validate(model)}


@router.post("/evidence-packs/validate", response_model=Dict[str, Any])
def validate_evidence_pack(payload: ValidatePackRequest, db: Session = Depends(get_db)):
    controller = GovernedInvestigationController(db)
    res = controller.submit_and_validate_evidence_pack(
        work_order_id=payload.work_order_id,
        agent_id=payload.agent_id,
        pack=payload.evidence_pack,
    )
    return {"status": "SUCCESS", "data": res}


# ============================================================
# 2. Human Approval Gate
# ============================================================
@router.post("/approvals/propose", response_model=Dict[str, Any])
def propose_policy_action(payload: ApprovalRequestCreate, db: Session = Depends(get_db)):
    gate = HumanApprovalGate(db)
    res = gate.propose_and_gate_action(payload)
    return {"status": "SUCCESS", "data": res}


@router.get("/approvals", response_model=Dict[str, Any])
def list_approval_requests(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ApprovalRequestModel)
    if status_filter:
        query = query.filter(ApprovalRequestModel.status == status_filter)
    reqs = query.order_by(ApprovalRequestModel.created_at.desc()).all()
    return {"count": len(reqs), "data": [ApprovalRequestResponse.model_validate(r) for r in reqs]}


@router.post("/approvals/approve", response_model=Dict[str, Any])
def approve_action(decision: HumanApprovalDecision, db: Session = Depends(get_db)):
    gate = HumanApprovalGate(db)
    req = gate.approve_action(decision)
    return {"status": "SUCCESS", "message": "Action approved", "data": ApprovalRequestResponse.model_validate(req)}


@router.post("/approvals/reject", response_model=Dict[str, Any])
def reject_action(decision: HumanApprovalDecision, db: Session = Depends(get_db)):
    gate = HumanApprovalGate(db)
    req = gate.reject_action(decision)
    return {"status": "SUCCESS", "message": "Action rejected", "data": ApprovalRequestResponse.model_validate(req)}


@router.post("/approvals/request-evidence", response_model=Dict[str, Any])
def request_more_evidence(decision: HumanApprovalDecision, db: Session = Depends(get_db)):
    gate = HumanApprovalGate(db)
    req = gate.request_more_evidence(decision)
    return {"status": "SUCCESS", "message": "More evidence requested", "data": ApprovalRequestResponse.model_validate(req)}


# ============================================================
# 3. Auditable Decision Trail & Hash Verification
# ============================================================
@router.get("/audit-trail", response_model=Dict[str, Any])
def get_audit_trail(incident_id: Optional[str] = None, actor_id: Optional[str] = None, limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    query = db.query(AuditEventModel)
    if incident_id:
        query = query.filter(AuditEventModel.incident_id == incident_id)
    if actor_id:
        query = query.filter(AuditEventModel.actor_id == actor_id)
    events = query.order_by(AuditEventModel.created_at.desc()).limit(limit).all()
    
    formatted = []
    for e in events:
        formatted.append({
            "event_id": e.event_id,
            "incident_id": e.incident_id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else "",
            "actor_id": e.actor_id,
            "actor_type": e.actor_type,
            "event_type": e.event_type,
            "evidence_references": e.evidence_references,
            "work_order_references": e.work_order_references,
            "decision_rationale": e.decision_rationale,
            "proposed_or_executed_action": e.proposed_or_executed_action,
            "approver_identity": e.approver_identity,
            "execution_status": e.execution_status,
            "prev_hash": e.prev_hash,
            "record_hash": e.record_hash,
        })
    return {"count": len(formatted), "data": formatted}


@router.get("/audit-trail/verify", response_model=Dict[str, Any])
def verify_audit_trail_integrity(db: Session = Depends(get_db)):
    audit = AuditTrailService(db)
    res = audit.verify_integrity()
    return {"status": "SUCCESS", "data": res}
