"""
Orchestration Candidate Agent Generator.
Executes deterministic candidate generation pipeline based on entity, event_type, domain,
temporal context, attack-chain candidates, missing evidence, agent capabilities, and policy constraints.
"""

from typing import Dict, List, Any, Set, Optional
from hactm.orchestration.models import AgentSelectionContext, AgentRecord, AgentAvailabilityStatus
from hactm.orchestration.registry import AgentRegistry


class CandidateAgentGenerator:
    """Deterministic candidate generator for Orchestration Engine."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def generate_candidates(self, context: AgentSelectionContext) -> List[AgentRecord]:
        """
        Executes 10-step deterministic candidate generation pipeline.
        Returns a sorted list of candidate AgentRecords.
        """
        # Step 1-3: Identify entity, event_type, domain
        event_type = (context.event_type or "").lower()
        observed_domains = set(context.domains_observed or [])

        # Step 4-5: Adaptive Memory & Graph temporal and attack-chain context
        attack_chains = context.attack_chain_candidates or []
        chain_stages = set()
        for chain in attack_chains:
            for st in chain.get("stages", []):
                domain = st.get("domain")
                if domain:
                    chain_stages.add(domain.lower())

        # Step 6-7: Identify missing evidence & agents capable of supplying missing evidence
        missing_domains = set(context.missing_domains or [])
        missing_evidence_types = set(context.missing_evidence_types or [])

        # Step 8-9: Retrieve registered enabled available agents
        all_agents = self.registry.get_all_agents(enabled_only=True)

        candidate_set: List[AgentRecord] = []
        already_called = set(context.previous_agent_calls or [])

        for agent in all_agents:
            # Check availability
            if agent.availability_status in [AgentAvailabilityStatus.UNAVAILABLE, AgentAvailabilityStatus.DISABLED]:
                continue

            agent_domain = agent.domain.lower()

            # Rule 1: Agent matches current event_type or supported event types
            event_match = any(e.lower() in event_type or event_type in e.lower() for e in agent.supported_event_types)

            # Rule 2: Agent matches entity type
            entity_match = any(ent in context.entity_ids for ent in agent.supported_entity_types) or len(agent.supported_entity_types) == 0

            # Rule 3: Agent domain is in missing domains or attack chain stage
            domain_match = agent_domain in missing_domains or agent_domain in chain_stages or agent_domain in observed_domains

            # Rule 4: Agent capability matches missing evidence type
            capability_match = any(cap.lower() in missing_evidence_types for cap in agent.capabilities)

            # Candidate inclusion criteria:
            # Must match at least one contextual relevance criteria
            is_candidate = event_match or domain_match or capability_match or (agent.domain in ["network", "identity"] and context.current_risk > 0.60)

            if is_candidate:
                candidate_set.append(agent)

        # Fallback guarantee: If candidate set is empty, return primary domain agent
        if not candidate_set and all_agents:
            candidate_set = [all_agents[0]]

        # Deterministic ordering by agent_id for reproducible evaluations
        candidate_set.sort(key=lambda a: a.agent_id)
        return candidate_set
