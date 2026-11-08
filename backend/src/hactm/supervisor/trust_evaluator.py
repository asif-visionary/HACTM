"""
Central Agent Supervisor — Agent Trust and Reliability Evaluator.
Executes deterministic, transparent trust assessment producing explainable Agent Trust Assessments
categorized into 7 formal states: TRUSTED, NORMAL, UNDER_OBSERVATION, SUSPICIOUS, RESTRICTED, ISOLATED, REVOKED.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from hactm.supervisor.schemas import AgentTrustStatus, AgentTrustResponse
from hactm.api.routers.trust_passport import ISOLATED_AGENTS, REVOKED_CAPABILITIES


class AgentTrustEvaluator:
    """Computes transparent, auditable trust assessments based on verifiable telemetry."""

    def __init__(self):
        # Local violation history cache: {agent_id: [violation_reasons]}
        self._violations: Dict[str, List[str]] = {}

    def record_violation(self, agent_id: str, reason: str):
        """Records an authoritative policy or behavioral violation."""
        if agent_id not in self._violations:
            self._violations[agent_id] = []
        self._violations[agent_id].append(reason)

    def evaluate_trust(
        self,
        agent_id: str,
        base_reliability: float = 0.90,
        health_score: float = 1.0,
        anomaly_count: int = 0,
        critical_anomaly: bool = False,
    ) -> AgentTrustResponse:
        """
        Calculates agent trust assessment.
        Formula:
            compliance = max(0.0, 1.0 - (anomaly_count * 0.15) - (0.4 if critical_anomaly else 0.0))
            trust_score = (0.50 * base_reliability) + (0.30 * compliance) + (0.20 * health_score)
        """
        now = datetime.now(timezone.utc)
        violations = self._violations.get(agent_id, [])
        is_isolated = agent_id in ISOLATED_AGENTS
        revoked = REVOKED_CAPABILITIES.get(agent_id, [])

        compliance = max(0.0, 1.0 - (anomaly_count * 0.15) - (0.40 if critical_anomaly else 0.0))
        trust_score = (0.50 * base_reliability) + (0.30 * compliance) + (0.20 * health_score)
        trust_score = round(max(0.0, min(1.0, trust_score)), 3)

        # Epistemic uncertainty scales with anomaly frequency and low observation count
        uncertainty = round(min(0.50, 0.05 + (anomaly_count * 0.08)), 3)

        # Deterministic Status Assignment
        if is_isolated:
            status = AgentTrustStatus.ISOLATED
            reasoning = f"Agent '{agent_id}' is quarantined in ISOLATED state: {ISOLATED_AGENTS.get(agent_id, {}).get('reason', 'Administrative quarantine')}."
        elif revoked:
            status = AgentTrustStatus.RESTRICTED
            reasoning = f"Agent '{agent_id}' has restricted capabilities: {revoked}."
        elif critical_anomaly or trust_score < 0.45 or len(violations) >= 3:
            status = AgentTrustStatus.SUSPICIOUS
            reasoning = f"Agent '{agent_id}' flagged as SUSPICIOUS due to high-severity violations or degraded trust score ({trust_score})."
        elif anomaly_count > 0 or health_score < 0.70 or trust_score < 0.75:
            status = AgentTrustStatus.UNDER_OBSERVATION
            reasoning = f"Agent '{agent_id}' placed UNDER_OBSERVATION due to minor anomaly activity or health fluctuation."
        elif trust_score >= 0.90 and anomaly_count == 0 and health_score >= 0.95:
            status = AgentTrustStatus.TRUSTED
            reasoning = f"Agent '{agent_id}' exhibits superior reliability ({trust_score}) and full policy compliance."
        else:
            status = AgentTrustStatus.NORMAL
            reasoning = f"Agent '{agent_id}' operates within expected operational baseline parameters."

        return AgentTrustResponse(
            agent_id=agent_id,
            trust_status=status,
            trust_score=trust_score,
            reliability_score=round(base_reliability, 3),
            compliance_score=round(compliance, 3),
            uncertainty=uncertainty,
            recent_anomalies_count=anomaly_count,
            violation_history=violations,
            revoked_capabilities=revoked,
            is_isolated=is_isolated,
            reasoning_summary=reasoning,
            last_assessed_at=now.isoformat(),
        )

