"""
FastAPI Router for Zero-Trust Engine Zero-Trust Policy Decision, Micro-Segmentation, Step-Up Verification, and Auditing.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from hactm.storage.database import get_db
from hactm.services.zerotrust_service import ZeroTrustService

router = APIRouter(prefix="/api/v1", tags=["Zero-Trust Policy Engine"])


def get_service(db: Session = Depends(get_db)) -> ZeroTrustService:
    return ZeroTrustService(db=db)


class DecideRequest(BaseModel):
    subject_id: str
    resource_id: str
    action: str = "READ"
    current_risk: float = 0.0
    uncertainty: float = 0.0
    security_zone: str = "USER_ZONE"
    two_factor_state: str = "NOT_REQUIRED"


class VerificationEventRequest(BaseModel):
    subject_id: str
    verification_type: str = "2FA"  # 2FA, BIOMETRIC
    status: str = "SUCCESS"  # SUCCESS, FAILED
    method: str = "TOTP"


class PolicySimulateRequest(BaseModel):
    subject_id: str = "usr_sim_100"
    resource_id: str = "app_critical_prod"
    action: str = "TRANSFER"
    current_risk: float = 0.75
    uncertainty: float = 0.15
    two_factor_state: str = "NOT_REQUIRED"
    security_zone: str = "USER_ZONE"


@router.get("/policy-health")
def get_policy_health(service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/policy-health - Operational status and configuration of Zero-Trust engine."""
    return service.get_health()


@router.get("/policies")
def list_policies(service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/policies - List declarative policy definitions."""
    return service.list_policies()


@router.post("/policies")
def create_policy(payload: Dict[str, Any], service: ZeroTrustService = Depends(get_service)):
    """POST /api/v1/policies - Create or update a declarative policy."""
    return service.create_policy(payload)


@router.get("/policies/{policy_id}")
def get_policy(policy_id: str, service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/policies/{policy_id} - Retrieve specific declarative policy details."""
    p = service.repo.get_policy(policy_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Policy {policy_id} not found")
    return service._model_to_dict(p)


@router.put("/policies/{policy_id}")
def update_policy(policy_id: str, payload: Dict[str, Any], service: ZeroTrustService = Depends(get_service)):
    """PUT /api/v1/policies/{policy_id} - Update policy conditions or decision."""
    payload["policy_id"] = policy_id
    return service.create_policy(payload)


@router.get("/policies/{policy_id}/versions")
def get_policy_versions(policy_id: str, service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/policies/{policy_id}/versions - Retrieve immutable version history of a policy."""
    versions = service.repo.list_policy_versions(policy_id)
    return [service._model_to_dict(v) for v in versions]


@router.post("/policies/simulate")
def simulate_policy(req: PolicySimulateRequest, service: ZeroTrustService = Depends(get_service)):
    """POST /api/v1/policies/simulate - Interactive research simulator for policy decisions."""
    return service.simulator.simulate_decision(
        subject_id=req.subject_id,
        resource_id=req.resource_id,
        action=req.action,
        current_risk=req.current_risk,
        uncertainty=req.uncertainty,
        two_factor_state=req.two_factor_state,
        security_zone=req.security_zone,
    )


@router.post("/zero-trust/decide")
def evaluate_zero_trust_decision(req: DecideRequest, service: ZeroTrustService = Depends(get_service)):
    """POST /api/v1/zero-trust/decide - Core Zero-Trust Policy Decision Endpoint."""
    return service.evaluate_decision(
        subject_id=req.subject_id,
        resource_id=req.resource_id,
        action=req.action,
        current_risk=req.current_risk,
        uncertainty=req.uncertainty,
        security_zone=req.security_zone,
        two_factor_state=req.two_factor_state,
    )


@router.get("/zero-trust/decisions")
def list_decisions(limit: int = Query(50, ge=1, le=500), service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/zero-trust/decisions - List history of zero-trust policy decisions."""
    return service.list_decisions(limit=limit)


@router.get("/zero-trust/decisions/{decision_id}")
def get_decision(decision_id: str, service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/zero-trust/decisions/{decision_id} - Retrieve specific decision details."""
    d = service.get_decision(decision_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return d


@router.get("/security-context/{entity_id}")
def get_security_context(entity_id: str, service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/security-context/{entity_id} - Dynamic Security Context for entity."""
    return service.get_security_context(entity_id)


@router.get("/security-tags")
def get_security_tags(service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/security-tags - Active security tags across entities."""
    tags = service.tag_manager.derive_security_tags("entity_global", current_risk=0.50)
    return [t.model_dump() for t in tags]


@router.get("/security-groups")
def get_security_groups(service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/security-groups - Dynamic security groups."""
    return [g.model_dump() for g in service.tag_manager._default_groups.values()]


@router.get("/security-zones")
def get_security_zones(service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/security-zones - Logical security zones."""
    zones = service.repo.list_security_zones()
    return [service._model_to_dict(z) for z in zones]


@router.get("/micro-segmentation/segments")
def list_micro_segments(service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/micro-segmentation/segments - Micro-segmentation access rules."""
    return service.list_micro_segments()


@router.post("/micro-segmentation/simulate")
def simulate_micro_segmentation(
    subject_zone: str = "USER_ZONE",
    target_zone: str = "DATABASE_ZONE",
    action: str = "READ",
    service: ZeroTrustService = Depends(get_service),
):
    """POST /api/v1/micro-segmentation/simulate - Test east-west cross-zone lateral control."""
    dec, reason = service.micro_engine.evaluate_micro_segment(
        subject_zone=subject_zone,
        target_zone=target_zone,
        subject_groups=["group_privileged_users"],
        requested_action=action,
        assurance="AAL1",
    )
    return {"decision": dec.value, "reason": reason, "subject_zone": subject_zone, "target_zone": target_zone}


@router.get("/enforcement/actions")
def list_enforcement_actions(limit: int = Query(50, ge=1, le=500), service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/enforcement/actions - List simulated or controlled enforcement actions."""
    actions = service.repo.list_enforcement_actions(limit=limit)
    return [service._model_to_dict(a) for a in actions]


@router.post("/enforcement/simulate")
def simulate_enforcement(action_type: str = "REQUIRE_2FA", target: str = "app_prod", service: ZeroTrustService = Depends(get_service)):
    """POST /api/v1/enforcement/simulate - Trigger simulated enforcement action."""
    return {
        "action_id": f"act_sim_{int(service.engine.engine_version)}",
        "action_type": action_type,
        "target": target,
        "mode": service.engine.enforcement_mode.value,
        "status": "SIMULATED",
    }


@router.get("/enforcement/{action_id}")
def get_enforcement_action(action_id: str, service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/enforcement/{action_id} - Retrieve enforcement action details."""
    act = service.repo.get_enforcement_action(action_id)
    if not act:
        raise HTTPException(status_code=404, detail=f"Action {action_id} not found")
    return service._model_to_dict(act)


@router.post("/verification/2fa/event")
def record_2fa_event(req: VerificationEventRequest, service: ZeroTrustService = Depends(get_service)):
    """POST /api/v1/verification/2fa/event - Record 2FA step-up event."""
    return service.record_verification_event(
        subject_id=req.subject_id,
        verification_type="2FA",
        status=req.status,
        method=req.method,
    )


@router.post("/verification/biometric/event")
def record_biometric_event(req: VerificationEventRequest, service: ZeroTrustService = Depends(get_service)):
    """POST /api/v1/verification/biometric/event - Record biometric verification metadata event."""
    return service.record_verification_event(
        subject_id=req.subject_id,
        verification_type="BIOMETRIC",
        status=req.status,
        method="BIOMETRIC_TOUCH_ID",
    )


@router.get("/policy-audit")
def list_policy_audit_logs(limit: int = Query(50, ge=1, le=500), service: ZeroTrustService = Depends(get_service)):
    """GET /api/v1/policy-audit - List policy decision audit trial logs."""
    logs = service.repo.list_audit_logs(limit=limit)
    return [service._model_to_dict(l) for l in logs]
