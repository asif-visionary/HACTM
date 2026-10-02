"""
Zero-Trust Engine Security Tag and Dynamic Group Manager.
Derives security tags with TTL expiration and assigns dynamic security group membership based on evidence.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

from hactm.zerotrust.models import SecurityTag, SecurityGroup, SecurityZoneName


class SecurityTagManager:
    """Manages dynamic security tags, TTL expiration, and dynamic security group membership."""

    def __init__(self):
        self._default_groups: Dict[str, SecurityGroup] = {}
        self._initialize_default_groups()

    def _initialize_default_groups(self):
        now = datetime.now(timezone.utc)
        g1 = SecurityGroup(
            group_id="group_high_risk_users",
            name="High-Risk Users",
            description="Users with Cyber Risk Score >= 0.60 or COMPROMISED tag",
            membership_rule={"min_risk": 0.60, "required_tags": ["HIGH_RISK", "COMPROMISED"]},
            created_at=now,
        )
        g2 = SecurityGroup(
            group_id="group_privileged_users",
            name="Privileged Users",
            description="Administrative users requiring AAL2+",
            membership_rule={"required_tags": ["PRIVILEGED", "ADMIN"]},
            created_at=now,
        )
        g3 = SecurityGroup(
            group_id="group_critical_workloads",
            name="Critical Workloads",
            description="Production database and payment services",
            membership_rule={"required_tags": ["PRODUCTION", "CRITICAL"]},
            created_at=now,
        )
        g4 = SecurityGroup(
            group_id="group_suspicious_devices",
            name="Suspicious Devices",
            description="Devices exhibiting behavioral or network anomalies",
            membership_rule={"required_tags": ["SUSPICIOUS", "ELEVATED_RISK"]},
            created_at=now,
        )
        for g in [g1, g2, g3, g4]:
            self._default_groups[g.group_id] = g

    def derive_security_tags(
        self,
        entity_id: str,
        current_risk: float,
        evidence_list: Optional[List[Dict[str, Any]]] = None,
        identity_state: Optional[Dict[str, Any]] = None,
        ttl_minutes: int = 60,
    ) -> List[SecurityTag]:
        """
        Derives security tags dynamically based on Cyber Risk Score and incoming security evidence.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=ttl_minutes)
        tags: List[SecurityTag] = []

        # Risk-based dynamic tagging
        if current_risk >= 0.80:
            tags.append(
                SecurityTag(
                    tag_id=f"tag_risk_critical_{entity_id}",
                    entity_id=entity_id,
                    tag="COMPROMISED",
                    confidence=0.95,
                    created_at=now,
                    expires_at=expires_at,
                )
            )
            tags.append(
                SecurityTag(
                    tag_id=f"tag_risk_high_{entity_id}",
                    entity_id=entity_id,
                    tag="HIGH_RISK",
                    confidence=0.90,
                    created_at=now,
                    expires_at=expires_at,
                )
            )
        elif current_risk >= 0.60:
            tags.append(
                SecurityTag(
                    tag_id=f"tag_risk_elevated_{entity_id}",
                    entity_id=entity_id,
                    tag="ELEVATED_RISK",
                    confidence=0.85,
                    created_at=now,
                    expires_at=expires_at,
                )
            )
        elif current_risk <= 0.20:
            tags.append(
                SecurityTag(
                    tag_id=f"tag_risk_low_{entity_id}",
                    entity_id=entity_id,
                    tag="NORMAL",
                    confidence=0.90,
                    created_at=now,
                    expires_at=expires_at,
                )
            )

        # Context & Evidence-based tagging
        id_state = identity_state or {}
        if id_state.get("is_admin", False) or "ADMIN" in id_state.get("roles", []):
            tags.append(
                SecurityTag(
                    tag_id=f"tag_priv_{entity_id}",
                    entity_id=entity_id,
                    tag="PRIVILEGED",
                    confidence=1.0,
                    created_at=now,
                    expires_at=None,
                )
            )

        if id_state.get("is_third_party", False):
            tags.append(
                SecurityTag(
                    tag_id=f"tag_3p_{entity_id}",
                    entity_id=entity_id,
                    tag="THIRD_PARTY",
                    confidence=1.0,
                    created_at=now,
                    expires_at=None,
                )
            )

        for ev in evidence_list or []:
            ev_type = str(ev.get("event_type", "")).lower()
            if "phishing" in ev_type:
                tags.append(
                    SecurityTag(
                        tag_id=f"tag_phish_{entity_id}",
                        entity_id=entity_id,
                        tag="SUSPICIOUS",
                        confidence=0.80,
                        created_at=now,
                        expires_at=expires_at,
                    )
                )
            if "anomaly" in ev_type or "exfiltration" in ev_type:
                tags.append(
                    SecurityTag(
                        tag_id=f"tag_anom_{entity_id}",
                        entity_id=entity_id,
                        tag="ELEVATED_RISK",
                        confidence=0.85,
                        created_at=now,
                        expires_at=expires_at,
                    )
                )

        if not tags:
            tags.append(
                SecurityTag(
                    tag_id=f"tag_default_{entity_id}",
                    entity_id=entity_id,
                    tag="UNVERIFIED",
                    confidence=0.50,
                    created_at=now,
                    expires_at=expires_at,
                )
            )

        return tags

    def evaluate_security_groups(self, tags: List[SecurityTag], current_risk: float) -> List[str]:
        """
        Maps active security tags and Cyber Risk Score to dynamic security groups.
        """
        tag_set = {t.tag for t in tags if t.status == "ACTIVE"}
        assigned_groups = []

        if current_risk >= 0.60 or "HIGH_RISK" in tag_set or "COMPROMISED" in tag_set:
            assigned_groups.append("group_high_risk_users")

        if "PRIVILEGED" in tag_set or "ADMIN" in tag_set:
            assigned_groups.append("group_privileged_users")

        if "PRODUCTION" in tag_set or "CRITICAL" in tag_set:
            assigned_groups.append("group_critical_workloads")

        if "SUSPICIOUS" in tag_set or "ELEVATED_RISK" in tag_set:
            assigned_groups.append("group_suspicious_devices")

        return assigned_groups
