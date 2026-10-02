"""
Zero-Trust Engine ZeroTrust Service.
Orchestrates Zero-Trust policy decisions, dynamic security context, dynamic tags & groups,
micro-segmentation, 2FA/Biometric step-up events, analyst overrides, and research evaluation.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from hactm.storage.database import SessionLocal, init_db
from hactm.storage.repositories.zerotrust_repo import ZeroTrustRepository
from hactm.storage.models import (
    PolicyModel,
    PolicyDecisionModel,
    SecurityTagModel,
    SecurityGroupModel,
    SecurityZoneModel,
    MicroSegmentModel,
    EnforcementActionModel,
    VerificationEventModel,
    AuthenticationAssuranceModel,
    PolicyOverrideModel,
    PolicyAuditLogModel,
)
from hactm.zerotrust.models import (
    ZeroTrustDecisionContext,
    PolicyDecisionRecord,
    Policy,
    PolicyDecision,
    EnforcementMode,
    SubjectType,
    ResourceType,
    ActionType,
    SecurityZoneName,
    AuthenticationAssuranceLevel,
    DynamicSecurityContext,
)
from hactm.zerotrust.policy_engine import ZeroTrustPolicyEngine
from hactm.zerotrust.tags_and_groups import SecurityTagManager
from hactm.zerotrust.micro_segmentation import MicroSegmentationEngine
from hactm.zerotrust.simulator import ZeroTrustPolicySimulator
from hactm.zerotrust.evaluator import ZeroTrustEvaluator

class ZeroTrustService:
    """Service Orchestrator for HACTM Zero-Trust Engine Zero-Trust Layer."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db if db is not None else SessionLocal()
        self.repo = ZeroTrustRepository(self.db)
        self.engine = ZeroTrustPolicyEngine(enforcement_mode=EnforcementMode.DRY_RUN)
        self.tag_manager = SecurityTagManager()
        self.micro_engine = MicroSegmentationEngine()
        self.simulator = ZeroTrustPolicySimulator(self.engine)
        self.evaluator = ZeroTrustEvaluator()

        self._seed_default_database_records()

    def _seed_default_database_records(self):
        # Ensure tables created
        init_db()
        # Seed policies if empty
        existing_p = self.repo.list_policies()
        if not existing_p:
            for p in self.engine._policies.values():
                pm = PolicyModel(
                    policy_id=p.policy_id,
                    name=p.name,
                    description=p.description,
                    version=p.version,
                    priority=int(p.priority) if str(p.priority).isdigit() else 100,
                    enabled="true" if p.enabled else "false",
                    scope=p.scope,
                    conditions=p.conditions,
                    required_assurance=p.required_assurance.value if hasattr(p.required_assurance, "value") else str(p.required_assurance),
                    decision=p.decision.value if hasattr(p.decision, "value") else str(p.decision),
                    actions=p.actions,
                    author=p.author,
                )
                self.repo.save_policy(pm)

        # Seed zones if empty
        zones = self.repo.list_security_zones()
        if not zones:
            for z_name in SecurityZoneName:
                zm = SecurityZoneModel(
                    zone_id=f"zone_{z_name.value.lower()}",
                    name=z_name.value,
                    description=f"Logical security zone {z_name.value}",
                    risk_level="HIGH" if "ADMIN" in z_name.value or "DB" in z_name.value else "MODERATE",
                )
                self.repo.save_security_zone(zm)

    def get_health(self) -> Dict[str, Any]:
        policies = self.repo.list_policies()
        decisions, total_dec = self.repo.list_policy_decisions(limit=1)
        actions = self.repo.list_enforcement_actions(limit=1)

        return {
            "status": "HEALTHY",
            "phase": "ZERO_TRUST_ENGINE_ZERO_TRUST_POLICY_ENGINE",
            "enforcement_mode": self.engine.enforcement_mode.value,
            "total_policies": len(policies),
            "total_decisions": total_dec,
            "total_enforcement_actions": len(actions),
            "engine_version": self.engine.engine_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def evaluate_decision(
        self,
        subject_id: str,
        resource_id: str,
        action: str = "READ",
        current_risk: float = 0.0,
        uncertainty: float = 0.0,
        security_zone: str = "USER_ZONE",
        two_factor_state: str = "NOT_REQUIRED",
    ) -> Dict[str, Any]:
        """
        Executes real Zero-Trust Policy Decision for incoming authorization request.
        Persists decision record and simulated enforcement action in DB.
        """
        now = datetime.now(timezone.utc)
        ctx = ZeroTrustDecisionContext(
            context_id=f"ctx-{uuid.uuid4().hex[:12]}",
            subject_id=subject_id,
            subject_type=SubjectType.USER,
            resource_id=resource_id,
            resource_type=ResourceType.APPLICATION,
            requested_action=ActionType(action) if action in ActionType.__members__ else ActionType.READ,
            current_risk=current_risk,
            uncertainty=uncertainty,
            security_zone=SecurityZoneName(security_zone) if security_zone in SecurityZoneName.__members__ else SecurityZoneName.USER_ZONE,
            two_factor_state=two_factor_state,
            timestamp=now,
        )

        record = self.engine.evaluate_decision(ctx)

        # Save Decision Model
        dec_model = PolicyDecisionModel(
            decision_id=record.decision_id,
            subject_id=record.subject_id,
            subject_type=ctx.subject_type.value,
            resource_id=record.resource_id,
            resource_type=ctx.resource_type.value,
            requested_action=record.requested_action.value,
            decision=record.decision.value,
            cyber_risk_score=record.cyber_risk_score,
            confidence=record.confidence,
            uncertainty=record.uncertainty,
            evidence_ids=record.evidence_ids,
            applicable_policy_ids=record.applicable_policy_ids,
            policy_versions=record.policy_versions,
            security_tags=record.security_tags,
            security_groups=record.security_groups,
            security_zone=record.security_zone.value if hasattr(record.security_zone, "value") else str(record.security_zone),
            authentication_assurance=record.authentication_assurance.value if hasattr(record.authentication_assurance, "value") else str(record.authentication_assurance),
            enforcement_mode=record.enforcement_mode.value if hasattr(record.enforcement_mode, "value") else str(record.enforcement_mode),
            enforcement_status=record.enforcement_status,
            explanation=record.explanation,
            reasons=record.reasons,
            created_at=now,
        )
        self.repo.save_policy_decision(dec_model)

        # Save Enforcement Action Model
        act_model = EnforcementActionModel(
            action_id=f"act-{uuid.uuid4().hex[:12]}",
            decision_id=record.decision_id,
            action_type=record.decision.value,
            target=record.resource_id,
            mode=record.enforcement_mode.value,
            status=record.enforcement_status,
            requested_at=now,
            reason=record.explanation,
        )
        self.repo.save_enforcement_action(act_model)

        return record.model_dump()

    def get_security_context(self, entity_id: str) -> Dict[str, Any]:
        active_tags = self.repo.get_active_tags_for_entity(entity_id)
        tag_objects = [
            {
                "tag_id": t.tag_id,
                "entity_id": t.entity_id,
                "tag": t.tag,
                "confidence": t.confidence,
                "status": t.status,
                "expires_at": t.expires_at.isoformat() if t.expires_at else None,
            }
            for t in active_tags
        ]

        pyd_tags = self.tag_manager.derive_security_tags(entity_id=entity_id, current_risk=0.45)
        groups = self.tag_manager.evaluate_security_groups(pyd_tags, current_risk=0.45)
        assurance = self.repo.get_assurance(entity_id)

        dyn_ctx = DynamicSecurityContext(
            entity_id=entity_id,
            security_tags=pyd_tags,
            security_groups=groups,
            security_zone=SecurityZoneName.USER_ZONE,
            cyber_risk=0.45,
            uncertainty=0.15,
            evidence_coverage=0.90,
            authentication_assurance=AuthenticationAssuranceLevel(assurance.current_assurance_level) if assurance else AuthenticationAssuranceLevel.AAL1,
        )

        return dyn_ctx.model_dump()

    def record_verification_event(
        self,
        subject_id: str,
        verification_type: str,  # 2FA or BIOMETRIC
        status: str,  # SUCCESS, FAILED
        method: str = "TOTP",
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        evt_model = VerificationEventModel(
            event_id=f"vevt-{uuid.uuid4().hex[:12]}",
            subject_id=subject_id,
            verification_type=verification_type,
            method=method,
            status=status,
            assurance_level="AAL2" if status == "SUCCESS" else "AAL1",
            timestamp=now,
        )
        self.repo.save_verification_event(evt_model)

        if status == "SUCCESS":
            ass_model = AuthenticationAssuranceModel(
                subject_id=subject_id,
                current_assurance_level="AAL2",
                last_2fa_at=now,
                updated_at=now,
            )
            self.repo.save_assurance(ass_model)

        return {
            "event_id": evt_model.event_id,
            "subject_id": subject_id,
            "verification_type": verification_type,
            "status": status,
            "assurance_level": evt_model.assurance_level,
            "timestamp": now.isoformat(),
        }

    def list_policies(self) -> List[Dict[str, Any]]:
        policies = self.repo.list_policies()
        return [self._model_to_dict(p) for p in policies]

    def create_policy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pol_id = payload.get("policy_id") or f"pol_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        model = PolicyModel(
            policy_id=pol_id,
            name=payload.get("name", "Custom Policy"),
            description=payload.get("description", ""),
            priority=int(payload.get("priority", 100)),
            enabled="true" if payload.get("enabled", True) else "false",
            scope=payload.get("scope", "GLOBAL"),
            conditions=payload.get("conditions", {}),
            required_assurance=payload.get("required_assurance", "AAL1"),
            decision=payload.get("decision", "VERIFY"),
            actions=payload.get("actions", []),
            created_at=now,
            updated_at=now,
        )
        saved = self.repo.save_policy(model)
        return self._model_to_dict(saved)

    def list_decisions(self, limit: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_policy_decisions(limit=limit)
        return {"items": [self._model_to_dict(i) for i in items], "total": total}

    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        dec = self.repo.get_policy_decision(decision_id)
        return self._model_to_dict(dec) if dec else None

    def list_micro_segments(self) -> List[Dict[str, Any]]:
        segments = self.repo.list_micro_segments(enabled_only=False)
        if not segments:
            # Fallback to default in-memory engine
            return [s.model_dump() for s in self.micro_engine._segments.values()]
        return [self._model_to_dict(s) for s in segments]

    def run_research_evaluation(self, num_events: int = 10) -> Dict[str, Any]:
        return self.evaluator.run_all_evaluations(num_events=num_events)

    def _model_to_dict(self, model_inst: Any) -> Dict[str, Any]:
        if not model_inst:
            return {}
        res = {}
        for col in model_inst.__table__.columns.keys():
            val = getattr(model_inst, col)
            if isinstance(val, datetime):
                res[col] = val.isoformat()
            else:
                res[col] = val
        return res
