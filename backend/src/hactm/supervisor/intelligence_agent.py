"""
Central Agent Supervisor — Supervisor Intelligence Agent.
Produces high-level supervisory assessments, explains why agent trust degraded,
correlates multi-step agent anomalies, and generates structured executive briefs.
Operates on validated structured telemetry with deterministic safety fallbacks.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from hactm.supervisor.schemas import AnomalyAlertItem, AgentTrustResponse, FleetOverviewResponse


class SupervisorIntelligenceAgent:
    """Supervisory reasoning agent providing transparent explanations and governance advice."""

    def __init__(self):
        self.name = "Central Supervisor Intelligence Agent"
        self.role = "Supervisory Oversight & Agent Behaviour Analyst"

    def generate_fleet_intelligence_summary(
        self,
        fleet_overview: FleetOverviewResponse,
        active_anomalies: List[AnomalyAlertItem],
        isolated_agents: List[str],
    ) -> Dict[str, Any]:
        """Generates an executive supervisory brief of fleet health and active risks."""
        now = datetime.now(timezone.utc).isoformat()
        total = fleet_overview.total_registered_agents
        healthy = fleet_overview.healthy_agents
        critical_alerts = [a for a in active_anomalies if a.severity == "CRITICAL"]
        high_alerts = [a for a in active_anomalies if a.severity == "HIGH"]

        if critical_alerts or isolated_agents:
            posture = "ELEVATED_SUPERVISORY_ALERT"
            narrative = (
                f"Supervisory Mesh detected {len(critical_alerts)} critical security anomalies "
                f"and {len(isolated_agents)} quarantined agents ({', '.join(isolated_agents) if isolated_agents else 'None'}). "
                "Autonomous tool permissions have been restricted and high-impact actions require human verification."
            )
        elif high_alerts:
            posture = "INCREASED_OBSERVATION"
            narrative = (
                f"Fleet posture under active observation: {len(high_alerts)} high-severity deviations detected. "
                f"{healthy} of {total} agents are operating normally within baseline parameters."
            )
        else:
            posture = "NOMINAL_STABLE"
            narrative = (
                f"All {total} registered cybersecurity agents and orchestrators are operating normally. "
                "Tool invocations adhere strictly to active Work Order scopes with zero policy violations."
            )

        recommendations = []
        if isolated_agents:
            recommendations.append("Initiate multi-step recovery verification before reinstating isolated agents.")
        if critical_alerts:
            recommendations.append("Audit tool gateway logs for unauthorized execution attempts.")
        if not recommendations:
            recommendations.append("Continue standard 10-second heartbeat and telemetry monitoring.")

        return {
            "timestamp": now,
            "supervisory_posture": posture,
            "executive_narrative": narrative,
            "fleet_health_ratio": f"{healthy}/{total}",
            "critical_anomalies_count": len(critical_alerts),
            "high_anomalies_count": len(high_alerts),
            "isolated_agents_count": len(isolated_agents),
            "governance_recommendations": recommendations,
        }

    def explain_trust_transition(
        self,
        agent_id: str,
        previous_trust: float,
        current_trust: AgentTrustResponse,
        trigger_anomalies: List[AnomalyAlertItem],
    ) -> Dict[str, Any]:
        """Provides a natural-language forensic explanation for an agent trust status shift."""
        reasons = []
        for anom in trigger_anomalies:
            reasons.append(f"[{anom.severity}] {anom.anomaly_type}: {anom.description}")

        delta = round(current_trust.trust_score - previous_trust, 3)
        direction = "DEGRADED" if delta < 0 else "IMPROVED" if delta > 0 else "STABLE"

        explanation = (
            f"Agent '{agent_id}' trust assessment transitioned to '{current_trust.trust_status.value}' "
            f"(Score: {current_trust.trust_score:.2f}, Δ: {delta:+.2f}). "
            f"Trigger factors: {'; '.join(reasons) if reasons else 'Routine baseline calibration'}."
        )

        return {
            "agent_id": agent_id,
            "direction": direction,
            "previous_score": previous_trust,
            "current_score": current_trust.trust_score,
            "trust_status": current_trust.trust_status.value,
            "explanation": explanation,
            "contributing_anomalies": [a.dict() for a in trigger_anomalies],
            "governance_action": "ISOLATE" if current_trust.is_isolated else "MONITOR",
        }

