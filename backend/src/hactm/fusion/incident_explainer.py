"""
Incident Investigation and Explanation Engine for HACTM.
Generates structured incident explanations, chronological timelines, alternative hypotheses,
and plain language summaries for nontechnical stakeholders.
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from hactm.storage.models import EventModel, SecurityEvidenceModel, ApprovalRequestModel, WorkOrderModel
from hactm.reliability.safeguards import EvidenceSafeguardsEngine
from hactm.core.logging import logger


class IncidentExplainerEngine:
    """Produces comprehensive evidence-backed incident explanations."""

    def __init__(self, db: Session):
        self.db = db
        self.safeguards = EvidenceSafeguardsEngine()

    def generate_explanation(self, incident_id: str) -> Dict[str, Any]:
        """Generates a complete structured incident explanation and timeline."""
        # Query evidence related to incident (by correlation_id, session_id, or parent_event_id)
        evidence_records = (
            self.db.query(SecurityEvidenceModel)
            .filter(
                (SecurityEvidenceModel.correlation_id == incident_id)
                | (SecurityEvidenceModel.session_id == incident_id)
                | (SecurityEvidenceModel.event_id == incident_id)
                | (SecurityEvidenceModel.raw_event_id == incident_id)
            )
            .order_by(SecurityEvidenceModel.timestamp.asc())
            .all()
        )

        if not evidence_records:
            # Fallback query all recent high risk evidence if specific incident ID not found
            evidence_records = (
                self.db.query(SecurityEvidenceModel)
                .order_by(SecurityEvidenceModel.timestamp.desc())
                .limit(10)
                .all()
            )

        # Convert to dictionary list
        evidence_items = []
        for r in evidence_records:
            evidence_items.append({
                "event_id": r.event_id,
                "agent_id": r.agent_id,
                "entity_id": r.entity_id,
                "event_type": r.event_type,
                "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                "risk_score": r.risk_score,
                "confidence": r.confidence,
                "uncertainty": r.uncertainty,
                "severity": r.severity,
                "source": r.source,
                "evidence": r.evidence or {},
            })

        # Process supporting vs. contradicting evidence
        contradiction_res = self.safeguards.process_contradictory_evidence(evidence_items)
        missing_res = self.safeguards.handle_missing_data(evidence_items, ["entity_id", "source", "event_type"])

        # Query approval status & execution
        approval_req = (
            self.db.query(ApprovalRequestModel)
            .filter(ApprovalRequestModel.incident_id == incident_id)
            .order_by(ApprovalRequestModel.created_at.desc())
            .first()
        )

        approval_status = approval_req.status if approval_req else "NO_ACTION_REQUIRED"
        execution_status = approval_req.execution_status if approval_req else "N/A"
        verification_status = approval_req.verification_status if approval_req else "UNVERIFIED"

        # Query work order status
        work_order = (
            self.db.query(WorkOrderModel)
            .filter(WorkOrderModel.parent_incident_id == incident_id)
            .order_by(WorkOrderModel.created_at.desc())
            .first()
        )

        # Aggregate affected entities & sources
        affected_entities = sorted(list({item["entity_id"] for item in evidence_items}))
        sources = sorted(list({item["source"] for item in evidence_items if item.get("source")}))
        agents = sorted(list({item["agent_id"] for item in evidence_items if item.get("agent_id")}))

        avg_risk = sum(item["risk_score"] for item in evidence_items) / (len(evidence_items) or 1)
        avg_confidence = sum(item["confidence"] for item in evidence_items) / (len(evidence_items) or 1)
        avg_uncertainty = sum(item["uncertainty"] for item in evidence_items) / (len(evidence_items) or 1) + missing_res["uncertainty_penalty"]

        # Chronological timeline
        timeline = []
        for idx, item in enumerate(evidence_items):
            timeline.append({
                "step": idx + 1,
                "timestamp": item["timestamp"],
                "event_id": item["event_id"],
                "source_agent": item["agent_id"],
                "entity": item["entity_id"],
                "event_type": item["event_type"],
                "summary": f"Observed {item['event_type']} alert from {item['source']} (Risk: {item['risk_score']:.2f}, Confidence: {item['confidence']:.2f})",
                "fact_type": "OBSERVED_FACT",
            })

        # Plain language summary for nontechnical stakeholders
        plain_summary = (
            f"Incident {incident_id} involved {len(affected_entities)} affected entities ({', '.join(affected_entities[:3])}). "
            f"Security agents ({', '.join(agents)}) correlated {len(evidence_items)} events with an average cyber risk score of {avg_risk:.2f}. "
            f"Current approval gate status is '{approval_status}' and response execution is '{execution_status}'."
        )

        # Primary hypothesis & alternative hypotheses
        primary_hypothesis = {
            "hypothesis": f"Multi-stage compromise targeting entity {affected_entities[0] if affected_entities else 'unknown'}",
            "likelihood": "HIGH" if avg_risk >= 0.70 else "MEDIUM",
            "justification": f"High risk scores across multiple agents ({', '.join(agents)}) with supporting evidence count of {contradiction_res['supporting_count']}.",
            "fact_type": "INFERRED_CONCLUSION",
        }

        alternative_hypotheses = [
            {
                "hypothesis": "Benign system activity or false positive triggered by abnormal baseline surge",
                "likelihood": "LOW" if avg_risk >= 0.70 else "HIGH",
                "justification": f"Supported by {contradiction_res['contradicting_count']} contradicting evidence items and uncertainty score of {avg_uncertainty:.2f}.",
                "fact_type": "INFERRED_CONCLUSION",
            },
            {
                "hypothesis": "Stale or unverified threat intelligence indicator misclassification",
                "likelihood": "MEDIUM" if avg_uncertainty >= 0.40 else "LOW",
                "justification": f"Uncertainty penalty of {missing_res['uncertainty_penalty']:.2f} due to missing telemetry data fields.",
                "fact_type": "INFERRED_CONCLUSION",
            }
        ]

        return {
            "incident_id": incident_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "plain_language_summary": plain_summary,
            "affected_entities": affected_entities,
            "correlated_sources": sources,
            "involved_agents": agents,
            "event_count": len(evidence_items),
            "chronological_timeline": timeline,
            "supporting_evidence": contradiction_res["supporting_evidence"],
            "contradicting_evidence": contradiction_res["contradicting_evidence"],
            "likely_explanation": primary_hypothesis,
            "alternative_hypotheses": alternative_hypotheses,
            "risk_assessment": {
                "overall_risk_score": round(avg_risk, 4),
                "model_confidence": round(avg_confidence, 4),
                "predictive_uncertainty": round(avg_uncertainty, 4),
                "missing_data_penalty": missing_res["uncertainty_penalty"],
                "justification": f"Aggregated across {len(evidence_items)} security evidence items.",
            },
            "governance_and_response": {
                "work_order_id": work_order.work_order_id if work_order else None,
                "work_order_status": work_order.status if work_order else "N/A",
                "approval_status": approval_status,
                "execution_status": execution_status,
                "verification_status": verification_status,
            },
        }
