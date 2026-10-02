"""
Orchestration Agent Registry and Capability Model.
Maintains metadata, capabilities, health, cost profiles, and latency specs for security agents.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from hactm.orchestration.models import (
    AgentRecord,
    AgentAvailabilityStatus,
    AgentCost,
)


class AgentRegistry:
    """Central registry and capability manager for HACTM Security Agents."""

    def __init__(self):
        self._agents: Dict[str, AgentRecord] = {}
        self._costs: Dict[str, AgentCost] = {}
        self._initialize_default_registry()

    def _initialize_default_registry(self):
        """Initializes default Network Security Agent-6 specialized security agents and capabilities."""
        now = datetime.now(timezone.utc)

        # 1. Network Security Agent
        net_agent = AgentRecord(
            agent_id="network-security-agent",
            agent_name="Network Security Agent",
            domain="network",
            capabilities=["network_anomaly", "intrusion", "scanning", "lateral_movement", "exfiltration"],
            supported_event_types=["network_flow", "network_anomaly", "signature_match", "port_scan", "dns_tunnel"],
            supported_entity_types=["IP", "HOST", "DEVICE", "SUBNET"],
            supported_attack_categories=["RECONNAISSANCE", "INITIAL_ACCESS", "LATERAL_MOVEMENT", "EXFILTRATION"],
            reliability_score=0.91,
            reliability_lower_bound=0.86,
            reliability_upper_bound=0.94,
            average_latency_ms=120.0,
            p95_latency_ms=250.0,
            computational_cost=1.0,
            communication_cost=0.4,
            availability_status=AgentAvailabilityStatus.AVAILABLE,
            current_model_version="1.0.0",
            drift_status="STABLE",
            calibration_status="CALIBRATED",
            enabled=True,
            last_updated_at=now,
        )

        # 2. Phishing Intelligence Agent
        phish_agent = AgentRecord(
            agent_id="phishing-intelligence-agent",
            agent_name="Phishing Intelligence Agent",
            domain="phishing",
            capabilities=["phishing", "spear_phishing", "BEC", "malicious_email", "credential_harvesting"],
            supported_event_types=["phishing_email", "email_telemetry", "suspicious_url", "attachment_anomaly"],
            supported_entity_types=["EMAIL", "USER", "DOMAIN", "URL"],
            supported_attack_categories=["INITIAL_ACCESS", "CREDENTIAL_ACCESS", "SOCIAL_ENGINEERING"],
            reliability_score=0.86,
            reliability_lower_bound=0.81,
            reliability_upper_bound=0.91,
            average_latency_ms=180.0,
            p95_latency_ms=350.0,
            computational_cost=0.7,
            communication_cost=0.3,
            availability_status=AgentAvailabilityStatus.AVAILABLE,
            current_model_version="1.0.0",
            drift_status="STABLE",
            calibration_status="CALIBRATED",
            enabled=True,
            last_updated_at=now,
        )

        # 3. User Behavior Analytics (UBA) Agent
        uba_agent = AgentRecord(
            agent_id="uba-agent",
            agent_name="User Behavior Analytics Agent",
            domain="uba",
            capabilities=["insider_threat", "abnormal_user_behavior", "privilege_abuse", "data_hoarding"],
            supported_event_types=["user_action", "uba_anomaly", "resource_access", "file_exfiltration"],
            supported_entity_types=["USER", "ACCOUNT", "SESSION", "FILE"],
            supported_attack_categories=["PRIVILEGE_ESCALATION", "INSIDER_THREAT", "DATA_LEAKAGE"],
            reliability_score=0.88,
            reliability_lower_bound=0.82,
            reliability_upper_bound=0.92,
            average_latency_ms=220.0,
            p95_latency_ms=450.0,
            computational_cost=1.2,
            communication_cost=0.6,
            availability_status=AgentAvailabilityStatus.AVAILABLE,
            current_model_version="1.0.0",
            drift_status="STABLE",
            calibration_status="CALIBRATED",
            enabled=True,
            last_updated_at=now,
        )

        # 4. Identity & Authentication Agent
        identity_agent = AgentRecord(
            agent_id="identity-authentication-agent",
            agent_name="Identity & Authentication Agent",
            domain="identity",
            capabilities=["account_takeover", "authentication_anomaly", "2FA", "identity_risk", "credential_stuffing"],
            supported_event_types=["authentication_attempt", "login_failure", "mfa_challenge", "session_anomaly"],
            supported_entity_types=["USER", "ACCOUNT", "DEVICE", "SESSION"],
            supported_attack_categories=["CREDENTIAL_ACCESS", "INITIAL_ACCESS", "ACCOUNT_TAKEOVER"],
            reliability_score=0.94,
            reliability_lower_bound=0.90,
            reliability_upper_bound=0.97,
            average_latency_ms=90.0,
            p95_latency_ms=180.0,
            computational_cost=0.5,
            communication_cost=0.2,
            availability_status=AgentAvailabilityStatus.AVAILABLE,
            current_model_version="1.0.0",
            drift_status="STABLE",
            calibration_status="CALIBRATED",
            enabled=True,
            last_updated_at=now,
        )

        # 5. Transaction Security Agent
        txn_agent = AgentRecord(
            agent_id="transaction-security-agent",
            agent_name="Transaction Security Agent",
            domain="transaction",
            capabilities=["transaction_anomaly", "fraud", "unusual_recipient", "velocity_anomaly", "payment_risk"],
            supported_event_types=["payment_transaction", "fund_transfer", "account_withdrawal", "credit_event"],
            supported_entity_types=["ACCOUNT", "USER", "MERCHANT", "TRANSACTION"],
            supported_attack_categories=["FINANCIAL_FRAUD", "UNAUTHORIZED_TRANSFER", "MONEY_LAUNDERING"],
            reliability_score=0.89,
            reliability_lower_bound=0.83,
            reliability_upper_bound=0.93,
            average_latency_ms=140.0,
            p95_latency_ms=280.0,
            computational_cost=0.8,
            communication_cost=0.4,
            availability_status=AgentAvailabilityStatus.AVAILABLE,
            current_model_version="1.0.0",
            drift_status="STABLE",
            calibration_status="CALIBRATED",
            enabled=True,
            last_updated_at=now,
        )

        for agent in [net_agent, phish_agent, uba_agent, identity_agent, txn_agent]:
            self.register_agent(agent)

    def register_agent(self, agent: AgentRecord):
        """Registers or updates an agent record in memory."""
        self._agents[agent.agent_id] = agent
        cost_total = agent.computational_cost + agent.communication_cost
        self._costs[agent.agent_id] = AgentCost(
            agent_id=agent.agent_id,
            cpu_cost=agent.computational_cost,
            communication_cost=agent.communication_cost,
            latency_cost=agent.average_latency_ms / 100.0,
            total_normalized_cost=round(cost_total, 4),
        )

    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        return self._agents.get(agent_id)

    def get_all_agents(self, enabled_only: bool = True) -> List[AgentRecord]:
        if enabled_only:
            return [a for a in self._agents.values() if a.enabled and a.availability_status != AgentAvailabilityStatus.DISABLED]
        return list(self._agents.values())

    def list_agents(self, domain: Optional[str] = None, enabled_only: bool = True) -> List[AgentRecord]:
        agents = self.get_all_agents(enabled_only=enabled_only)
        if domain:
            agents = [a for a in agents if a.domain.lower() == domain.lower()]
        return agents

    def register_default_agents(self):
        self._initialize_default_registry()

    def get_agent_cost(self, agent_id: str) -> AgentCost:
        if agent_id in self._costs:
            return self._costs[agent_id]
        return AgentCost(agent_id=agent_id, total_normalized_cost=1.0)

    def update_agent_status(self, agent_id: str, status: AgentAvailabilityStatus, drift_status: Optional[str] = None):
        agent = self.get_agent(agent_id)
        if agent:
            agent.availability_status = status
            if drift_status:
                agent.drift_status = drift_status
            agent.last_updated_at = datetime.now(timezone.utc)
