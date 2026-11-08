"""
Central Agent Supervisor — Anomaly Detection Engine.
Correlates multidimensional signals across health, behaviour, tool gateway, evidence integrity,
and orchestrator actions into unified, prioritized supervisory anomalies.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from hactm.supervisor.schemas import AnomalyAlertItem, AnomalySeverity, AnomalyType
from hactm.storage.models import AgentAnomalyModel
from hactm.core.logging import logger


class AnomalyDetectionEngine:
    """Detects, prioritizes, and persists agent anomalies and security violations."""

    def __init__(self):
        # In-memory active anomaly alerts: {anomaly_id: AnomalyAlertItem}
        self._active_anomalies: Dict[str, AnomalyAlertItem] = {}

    def register_anomaly(
        self,
        agent_id: str,
        anomaly_type: str,
        severity: str,
        description: str,
        incident_id: Optional[str] = None,
        task_id: Optional[str] = None,
        source: str = "SUPERVISOR_ENGINE",
        evidence_references: Optional[List[str]] = None,
        recommended_action: str = "OBSERVE",
        db: Optional[Session] = None,
    ) -> AnomalyAlertItem:
        """Registers and records an anomaly event."""
        anomaly_id = f"ANOM-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        alert = AnomalyAlertItem(
            anomaly_id=anomaly_id,
            agent_id=agent_id,
            incident_id=incident_id,
            task_id=task_id,
            timestamp=now_iso,
            anomaly_type=anomaly_type,
            severity=severity,
            source=source,
            description=description,
            evidence_references=evidence_references or [],
            recommended_action=recommended_action,
            status="ACTIVE",
        )

        self._active_anomalies[anomaly_id] = alert
        logger.warning(f"CAS Anomaly Engine: [{severity}] {anomaly_type} on '{agent_id}': {description}")

        # Persist to database if session provided
        if db:
            try:
                db_model = AgentAnomalyModel(
                    anomaly_id=anomaly_id,
                    agent_id=agent_id,
                    incident_id=incident_id,
                    task_id=task_id,
                    timestamp=datetime.now(timezone.utc),
                    anomaly_type=anomaly_type,
                    severity=severity,
                    source=source,
                    description=description,
                    evidence_references=evidence_references or [],
                    recommended_action=recommended_action,
                    status="ACTIVE",
                )
                db.add(db_model)
                db.commit()
            except Exception as e:
                logger.error(f"Failed to persist anomaly to DB: {e}")

        return alert

    def get_anomalies(self, agent_id: Optional[str] = None, active_only: bool = True) -> List[AnomalyAlertItem]:
        """Returns anomalies filtered by agent or status."""
        anomalies = list(self._active_anomalies.values())
        if agent_id:
            anomalies = [a for a in anomalies if a.agent_id == agent_id]
        if active_only:
            anomalies = [a for a in anomalies if a.status == "ACTIVE"]
        # Return sorted by descending timestamp
        return sorted(anomalies, key=lambda a: a.timestamp, reverse=True)

    def resolve_anomaly(self, anomaly_id: str, status: str = "MITIGATED", db: Optional[Session] = None):
        """Marks an anomaly as resolved, dismissed, or mitigated."""
        if anomaly_id in self._active_anomalies:
            self._active_anomalies[anomaly_id].status = status
            if db:
                rec = db.query(AgentAnomalyModel).filter(AgentAnomalyModel.anomaly_id == anomaly_id).first()
                if rec:
                    rec.status = status
                    db.commit()

