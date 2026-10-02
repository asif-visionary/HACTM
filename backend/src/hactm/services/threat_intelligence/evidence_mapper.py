"""
Threat Intelligence Evidence Mapper for HACTM.
Maps normalized external threat intelligence results (e.g. AbuseIPDB) to canonical HACTM SecurityEvidence.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from hactm.core.models import SecurityEvidence
from hactm.core.constants import SeverityLevel, risk_score_to_severity
from hactm.services.threat_intelligence.provider import NormalizedThreatIntelResult


class ThreatIntelEvidenceMapper:
    """Converts normalized threat intelligence provider results into HACTM SecurityEvidence."""

    @staticmethod
    def to_security_evidence(
        res: NormalizedThreatIntelResult,
        entity_id: Optional[str] = None,
        event_id: Optional[str] = None
    ) -> SecurityEvidence:
        
        target_entity_id = entity_id or f"ip:{res.indicator}"
        target_event_id = event_id or f"evt-ti-{uuid.uuid4().hex[:10]}"

        # Risk score derived from abuse confidence score [0..100] -> [0.0..1.0]
        # Private IPs or unconfigured providers return 0.0 risk score
        risk_score = round(max(0.0, min(1.0, res.abuse_confidence_score / 100.0)), 4)
        
        # Confidence estimation: 0.90 for reported public IPs, 0.70 for zero-report IPs, 0.0 for unconfigured/unavailable
        if res.status in ["success", "cached"]:
            confidence = 0.90 if res.total_reports > 0 else 0.70
        else:
            confidence = 0.10

        uncertainty = round(1.0 - confidence, 4)
        reliability = res.source_reliability
        severity = risk_score_to_severity(risk_score)

        tags = ["threat_intel", res.provider]
        if res.abuse_confidence_score >= 50.0:
            tags.append("abusive_ip")
        if res.is_whitelisted:
            tags.append("whitelisted_ip")
        if not res.is_public_ip:
            tags.append("private_ip")

        evidence_payload: Dict[str, Any] = {
            "source_provider": res.provider,
            "source_type": "external_threat_intelligence",
            "indicator_type": res.indicator_type,
            "indicator": res.indicator,
            "abuse_confidence_score": res.abuse_confidence_score,
            "total_reports": res.total_reports,
            "country_code": res.country_code,
            "usage_type": res.usage_type,
            "isp": res.isp,
            "domain": res.domain,
            "last_reported_at": res.last_reported_at,
            "is_whitelisted": res.is_whitelisted,
            "provider_status": res.status,
            "error_type": res.error_type,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "reliability": reliability,
            "observed_at": res.observed_at,
            "normalization_version": "2.0.0"
        }

        return SecurityEvidence(
            event_id=target_event_id,
            agent_id=f"agent-{res.provider}-threat-intel",
            entity_id=target_entity_id,
            event_type="THREAT_INTELLIGENCE",
            timestamp=datetime.now(timezone.utc),
            risk_score=risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            evidence=evidence_payload,
            source=res.provider,
            source_type="external_threat_intelligence",
            severity=severity,
            agent_reliability=reliability,
            evidence_quality=0.85,
            security_tags=tags
        )
