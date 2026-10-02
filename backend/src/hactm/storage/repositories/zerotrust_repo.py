"""
Zero-Trust Engine Storage Repository for Zero-Trust Policy Engine, Security Context, and Micro-segmentation.
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, update, delete
from datetime import datetime, timezone

from hactm.storage.models import (
    PolicyModel,
    PolicyVersionModel,
    PolicyDecisionModel,
    PolicyConflictModel,
    SecurityTagModel,
    SecurityTagHistoryModel,
    SecurityGroupModel,
    SecurityGroupMembershipModel,
    SecurityZoneModel,
    MicroSegmentModel,
    EnforcementActionModel,
    VerificationEventModel,
    AuthenticationAssuranceModel,
    PolicyOverrideModel,
    PolicyAuditLogModel,
)


class ZeroTrustRepository:
    """Repository handling DB CRUD operations for Zero-Trust Engine Zero-Trust Policy Layer."""

    def __init__(self, db: Session):
        self.db = db

    # --- Policies ---
    def save_policy(self, model: PolicyModel) -> PolicyModel:
        self.db.merge(model)
        self.db.commit()
        return model

    def get_policy(self, policy_id: str) -> Optional[PolicyModel]:
        return self.db.query(PolicyModel).filter(PolicyModel.policy_id == policy_id).first()

    def list_policies(self, enabled_only: bool = False) -> List[PolicyModel]:
        query = self.db.query(PolicyModel)
        if enabled_only:
            query = query.filter(PolicyModel.enabled == "true")
        return query.order_by(PolicyModel.priority.desc()).all()

    def save_policy_version(self, model: PolicyVersionModel) -> PolicyVersionModel:
        self.db.add(model)
        self.db.commit()
        return model

    def list_policy_versions(self, policy_id: str) -> List[PolicyVersionModel]:
        return (
            self.db.query(PolicyVersionModel)
            .filter(PolicyVersionModel.policy_id == policy_id)
            .order_by(PolicyVersionModel.created_at.desc())
            .all()
        )

    # --- Policy Decisions ---
    def save_policy_decision(self, model: PolicyDecisionModel) -> PolicyDecisionModel:
        self.db.add(model)
        self.db.commit()
        return model

    def get_policy_decision(self, decision_id: str) -> Optional[PolicyDecisionModel]:
        return self.db.query(PolicyDecisionModel).filter(PolicyDecisionModel.decision_id == decision_id).first()

    def list_policy_decisions(
        self, subject_id: Optional[str] = None, limit: int = 50
    ) -> Tuple[List[PolicyDecisionModel], int]:
        query = self.db.query(PolicyDecisionModel)
        if subject_id:
            query = query.filter(PolicyDecisionModel.subject_id == subject_id)
        total = query.count()
        items = query.order_by(PolicyDecisionModel.created_at.desc()).limit(limit).all()
        return items, total

    def save_policy_conflict(self, model: PolicyConflictModel) -> PolicyConflictModel:
        self.db.add(model)
        self.db.commit()
        return model

    # --- Security Tags ---
    def save_security_tag(self, model: SecurityTagModel) -> SecurityTagModel:
        self.db.merge(model)
        self.db.commit()
        return model

    def get_active_tags_for_entity(self, entity_id: str) -> List[SecurityTagModel]:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(SecurityTagModel)
            .filter(
                SecurityTagModel.entity_id == entity_id,
                SecurityTagModel.status == "ACTIVE",
            )
            .all()
        )

    def expire_outdated_tags(self) -> int:
        now = datetime.now(timezone.utc)
        expired_tags = (
            self.db.query(SecurityTagModel)
            .filter(
                SecurityTagModel.status == "ACTIVE",
                SecurityTagModel.expires_at <= now,
            )
            .all()
        )
        count = 0
        for tag in expired_tags:
            tag.status = "EXPIRED"
            hist = SecurityTagHistoryModel(
                history_id=f"hist_{tag.tag_id}_{int(now.timestamp())}",
                tag_id=tag.tag_id,
                entity_id=tag.entity_id,
                tag=tag.tag,
                action="EXPIRED",
                reason="TTL Expiration",
                timestamp=now,
            )
            self.db.add(hist)
            count += 1
        self.db.commit()
        return count

    # --- Security Groups & Zones ---
    def save_security_group(self, model: SecurityGroupModel) -> SecurityGroupModel:
        self.db.merge(model)
        self.db.commit()
        return model

    def list_security_groups(self) -> List[SecurityGroupModel]:
        return self.db.query(SecurityGroupModel).all()

    def save_security_zone(self, model: SecurityZoneModel) -> SecurityZoneModel:
        self.db.merge(model)
        self.db.commit()
        return model

    def list_security_zones(self) -> List[SecurityZoneModel]:
        return self.db.query(SecurityZoneModel).all()

    # --- Micro-segmentation ---
    def save_micro_segment(self, model: MicroSegmentModel) -> MicroSegmentModel:
        self.db.merge(model)
        self.db.commit()
        return model

    def list_micro_segments(self, enabled_only: bool = True) -> List[MicroSegmentModel]:
        query = self.db.query(MicroSegmentModel)
        if enabled_only:
            query = query.filter(MicroSegmentModel.enabled == "true")
        return query.order_by(MicroSegmentModel.priority.desc()).all()

    # --- Enforcement Actions ---
    def save_enforcement_action(self, model: EnforcementActionModel) -> EnforcementActionModel:
        self.db.merge(model)
        self.db.commit()
        return model

    def get_enforcement_action(self, action_id: str) -> Optional[EnforcementActionModel]:
        return self.db.query(EnforcementActionModel).filter(EnforcementActionModel.action_id == action_id).first()

    def list_enforcement_actions(self, limit: int = 50) -> List[EnforcementActionModel]:
        return self.db.query(EnforcementActionModel).order_by(EnforcementActionModel.requested_at.desc()).limit(limit).all()

    # --- Verification & Assurance ---
    def save_verification_event(self, model: VerificationEventModel) -> VerificationEventModel:
        self.db.add(model)
        self.db.commit()
        return model

    def get_assurance(self, subject_id: str) -> Optional[AuthenticationAssuranceModel]:
        return self.db.query(AuthenticationAssuranceModel).filter(AuthenticationAssuranceModel.subject_id == subject_id).first()

    def save_assurance(self, model: AuthenticationAssuranceModel) -> AuthenticationAssuranceModel:
        self.db.merge(model)
        self.db.commit()
        return model

    # --- Overrides & Audit ---
    def save_policy_override(self, model: PolicyOverrideModel) -> PolicyOverrideModel:
        self.db.add(model)
        self.db.commit()
        return model

    def save_audit_log(self, model: PolicyAuditLogModel) -> PolicyAuditLogModel:
        self.db.add(model)
        self.db.commit()
        return model

    def list_audit_logs(self, limit: int = 50) -> List[PolicyAuditLogModel]:
        return self.db.query(PolicyAuditLogModel).order_by(PolicyAuditLogModel.timestamp.desc()).limit(limit).all()
