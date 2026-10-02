"""
Reliability Processing Service.
Orchestrates database repositories, engines, audit histories, and APIs.
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from hactm.storage.repositories.reliability_repo import ReliabilityRepository
from hactm.storage.models import (
    AgentReliabilityModel,
    ReliabilityHistoryModel,
    CalibrationRecordModel,
    UncertaintyRecordModel,
    EvidenceQualityModel,
    DriftRecordModel,
    ConflictRecordModel,
    AgentReputationModel,
    ReliabilityEvaluationModel,
)
from hactm.reliability.models import ReliabilityConfig
from hactm.reliability.reliability_engine import ReliabilityEngine
from hactm.reliability.uncertainty_engine import UncertaintyEngine
from hactm.reliability.calibration_engine import CalibrationEngine
from hactm.reliability.quality_engine import EvidenceQualityEngine
from hactm.reliability.drift_engine import DriftEngine
from hactm.reliability.conflict_engine import ConflictEngine
from hactm.reliability.reputation_engine import ReputationEngine
from hactm.reliability.research_eval import ResearchEvaluator


class ReliabilityService:
    """Service orchestrator for Reliability Processing, Calibration, Drift, and Reputation."""

    def __init__(self, db: Session, config: Optional[ReliabilityConfig] = None):
        self.db = db
        self.repo = ReliabilityRepository(db)
        self.config = config or ReliabilityConfig()
        self.rel_engine = ReliabilityEngine(self.config)
        self.unc_engine = UncertaintyEngine()
        self.cal_engine = CalibrationEngine()
        self.qual_engine = EvidenceQualityEngine()
        self.drift_engine = DriftEngine()
        self.conflict_engine = ConflictEngine()
        self.rep_engine = ReputationEngine()
        self.evaluator = ResearchEvaluator()

    def evaluate_agent(
        self,
        agent_id: str,
        true_positives: int,
        false_positives: int,
        true_negatives: int,
        false_negatives: int,
        detector_id: Optional[str] = None,
        domain: Optional[str] = None,
        model_version: str = "1.0.0",
        calibration_error: float = 0.05,
        drift_score: float = 0.0,
        dataset: str = "synthetic_eval_v1",
        change_reason: str = "Empirical ground truth evaluation run",
    ) -> Dict[str, Any]:
        """
        Runs empirical ground-truth reliability evaluation for an agent/detector.
        Saves record, history audit log, and updates agent reputation.
        """
        existing_rel = self.repo.get_latest_reliability(agent_id, detector_id, domain, model_version)
        prev_score = existing_rel.reliability_score if existing_rel else None

        pydantic_rec = self.rel_engine.evaluate_reliability(
            agent_id=agent_id,
            true_positives=true_positives,
            false_positives=false_positives,
            true_negatives=true_negatives,
            false_negatives=false_negatives,
            detector_id=detector_id,
            domain=domain,
            model_version=model_version,
            calibration_error=calibration_error,
            drift_score=drift_score,
            evaluation_dataset=dataset,
        )

        db_model = AgentReliabilityModel(
            reliability_id=pydantic_rec.reliability_id,
            agent_id=pydantic_rec.agent_id,
            detector_id=pydantic_rec.detector_id,
            domain=pydantic_rec.domain,
            model_version=pydantic_rec.model_version,
            evaluation_window_start=pydantic_rec.evaluation_window_start,
            evaluation_window_end=pydantic_rec.evaluation_window_end,
            sample_count=pydantic_rec.sample_count,
            precision=pydantic_rec.precision,
            recall=pydantic_rec.recall,
            f1_score=pydantic_rec.f1_score,
            false_positive_rate=pydantic_rec.false_positive_rate,
            false_negative_rate=pydantic_rec.false_negative_rate,
            calibration_error=pydantic_rec.calibration_error,
            uncertainty_quality=pydantic_rec.uncertainty_quality,
            stability_score=pydantic_rec.stability_score,
            drift_score=pydantic_rec.drift_score,
            reliability_score=pydantic_rec.reliability_score,
            confidence_interval_lower=pydantic_rec.confidence_interval_lower,
            confidence_interval_upper=pydantic_rec.confidence_interval_upper,
            evaluation_dataset=pydantic_rec.evaluation_dataset,
            evaluation_method=pydantic_rec.evaluation_method,
            reliability_status=str(pydantic_rec.reliability_status.value if hasattr(pydantic_rec.reliability_status, "value") else pydantic_rec.reliability_status),
            created_at=pydantic_rec.created_at,
            updated_at=pydantic_rec.updated_at,
            metadata_json=pydantic_rec.metadata,
        )
        saved = self.repo.save_reliability_record(db_model)

        # Audit History Record
        hist_model = ReliabilityHistoryModel(
            reliability_id=saved.reliability_id,
            agent_id=saved.agent_id,
            detector_id=saved.detector_id,
            domain=saved.domain,
            model_version=saved.model_version,
            evaluation_window_start=saved.evaluation_window_start,
            evaluation_window_end=saved.evaluation_window_end,
            dataset=dataset,
            previous_reliability_score=prev_score,
            new_reliability_score=saved.reliability_score,
            change_reason=change_reason,
            configuration_version=self.config.version,
            timestamp=datetime.now(timezone.utc),
            metadata_json={"sample_count": saved.sample_count},
        )
        self.repo.save_history_record(hist_model)

        # Agent Reputation Update
        existing_rep = self.repo.get_agent_reputation(agent_id)
        prev_pyd_rep = None
        if existing_rep:
            prev_pyd_rep = self.rep_engine.calculate_reputation(
                agent_id=agent_id,
                historical_precision=existing_rep.historical_precision,
                historical_recall=existing_rep.historical_recall,
                evaluation_count=existing_rep.evaluation_count,
            )

        new_rep_pyd = self.rep_engine.calculate_reputation(
            agent_id=agent_id,
            historical_precision=saved.precision,
            historical_recall=saved.recall,
            stability_score=saved.stability_score,
            calibration_score=max(0.0, 1.0 - saved.calibration_error),
            drift_score=saved.drift_score,
            evaluation_count=(existing_rep.evaluation_count + 1) if existing_rep else 1,
            previous_reputation=prev_pyd_rep,
        )

        db_rep = AgentReputationModel(
            reputation_id=f"rep-{uuid.uuid4().hex[:12]}",
            agent_id=new_rep_pyd.agent_id,
            reputation_score=new_rep_pyd.reputation_score,
            historical_precision=new_rep_pyd.historical_precision,
            historical_recall=new_rep_pyd.historical_recall,
            stability_score=new_rep_pyd.stability_score,
            calibration_score=new_rep_pyd.calibration_score,
            drift_score=new_rep_pyd.drift_score,
            coverage_score=new_rep_pyd.coverage_score,
            last_evaluated_at=new_rep_pyd.last_evaluated_at,
            evaluation_count=new_rep_pyd.evaluation_count,
            confidence_interval_lower=new_rep_pyd.confidence_interval_lower,
            confidence_interval_upper=new_rep_pyd.confidence_interval_upper,
            reputation_version=new_rep_pyd.reputation_version,
            created_at=new_rep_pyd.created_at,
            updated_at=new_rep_pyd.updated_at,
        )
        self.repo.save_agent_reputation(db_rep)

        return self._model_to_dict(saved)

    def evaluate_calibration(
        self,
        agent_id: str,
        predicted_confidences: List[float],
        observed_outcomes: List[int],
        detector_id: Optional[str] = None,
        model_version: str = "1.0.0",
        dataset: str = "synthetic_eval_v1",
        calibration_method: str = "temperature_scaling",
        temperature: float = 1.2,
    ) -> Dict[str, Any]:
        """Runs confidence calibration evaluation and stores CalibrationRecord."""
        rec_pyd = self.cal_engine.evaluate_calibration(
            agent_id=agent_id,
            predicted_confidences=predicted_confidences,
            observed_outcomes=observed_outcomes,
            detector_id=detector_id,
            model_version=model_version,
            dataset=dataset,
            calibration_method=calibration_method,
            temperature=temperature,
        )

        db_model = CalibrationRecordModel(
            calibration_id=rec_pyd.calibration_id,
            agent_id=rec_pyd.agent_id,
            detector_id=rec_pyd.detector_id,
            model_version=rec_pyd.model_version,
            dataset=rec_pyd.dataset,
            evaluation_window_start=rec_pyd.evaluation_window_start,
            evaluation_window_end=rec_pyd.evaluation_window_end,
            sample_count=rec_pyd.sample_count,
            ece=rec_pyd.ece,
            mce=rec_pyd.mce,
            brier_score=rec_pyd.brier_score,
            calibration_method=rec_pyd.calibration_method,
            pre_calibration_metric=rec_pyd.pre_calibration_metric,
            post_calibration_metric=rec_pyd.post_calibration_metric,
            calibration_parameters=rec_pyd.calibration_parameters,
            reliability_diagram_data=rec_pyd.reliability_diagram_data,
            created_at=rec_pyd.created_at,
        )
        saved = self.repo.save_calibration_record(db_model)
        return self._model_to_dict(saved)

    def evaluate_drift(
        self,
        agent_id: str,
        feature_or_signal: str,
        reference_values: List[float],
        current_values: List[float],
        detector_id: Optional[str] = None,
        model_version: str = "1.0.0",
        drift_method: str = "PSI",
    ) -> Dict[str, Any]:
        """Runs drift detection monitoring and stores DriftRecord."""
        rec_pyd = self.drift_engine.monitor_drift(
            agent_id=agent_id,
            feature_or_signal=feature_or_signal,
            reference_values=reference_values,
            current_values=current_values,
            detector_id=detector_id,
            model_version=model_version,
            drift_method=drift_method,
        )

        db_model = DriftRecordModel(
            drift_id=rec_pyd.drift_id,
            agent_id=rec_pyd.agent_id,
            detector_id=rec_pyd.detector_id,
            feature_or_signal=rec_pyd.feature_or_signal,
            reference_window_start=rec_pyd.reference_window_start,
            reference_window_end=rec_pyd.reference_window_end,
            current_window_start=rec_pyd.current_window_start,
            current_window_end=rec_pyd.current_window_end,
            drift_method=rec_pyd.drift_method,
            drift_score=rec_pyd.drift_score,
            threshold=rec_pyd.threshold,
            drift_detected="true" if rec_pyd.drift_detected else "false",
            severity=str(rec_pyd.severity.value if hasattr(rec_pyd.severity, "value") else rec_pyd.severity),
            model_version=rec_pyd.model_version,
            policy_action=str(rec_pyd.policy_action.value if hasattr(rec_pyd.policy_action, "value") else rec_pyd.policy_action),
            created_at=rec_pyd.created_at,
        )
        saved = self.repo.save_drift_record(db_model)
        return self._model_to_dict(saved)

    def get_agent_reliability(self, agent_id: str, detector_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        record = self.repo.get_latest_reliability(agent_id, detector_id)
        return self._model_to_dict(record) if record else None

    def list_reliability_records(
        self, agent_id: Optional[str] = None, detector_id: Optional[str] = None, domain: Optional[str] = None, status: Optional[str] = None, page: int = 1, page_size: int = 50
    ) -> Dict[str, Any]:
        items, total = self.repo.list_reliability_records(agent_id, detector_id, domain, None, status, page, page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def list_history(self, agent_id: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_history_for_agent(agent_id, page=page, page_size=page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def list_calibration(self, agent_id: Optional[str] = None, detector_id: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_calibration_records(agent_id, detector_id, page=page, page_size=page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def list_drift(self, agent_id: Optional[str] = None, detector_id: Optional[str] = None, drift_detected: Optional[bool] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_drift_records(agent_id, detector_id, drift_detected, page, page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def list_conflicts(self, entity_id: Optional[str] = None, conflict_type: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_conflict_records(entity_id, conflict_type, page=page, page_size=page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def list_uncertainty(self, agent_id: Optional[str] = None, evidence_id: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_uncertainty_records(agent_id, evidence_id, page, page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def list_quality(self, evidence_id: Optional[str] = None, min_quality: Optional[float] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        items, total = self.repo.list_quality_records(evidence_id, min_quality, page, page_size)
        return {"items": [self._model_to_dict(i) for i in items], "total": total, "page": page, "page_size": page_size}

    def list_reputations(self) -> List[Dict[str, Any]]:
        items = self.repo.list_agent_reputations()
        return [self._model_to_dict(i) for i in items]

    def get_health(self) -> Dict[str, Any]:
        records, total_rel = self.repo.list_reliability_records(page_size=1)
        drifts, total_drift = self.repo.list_drift_records(drift_detected=True, page_size=1)

        return {
            "status": "HEALTHY",
            "phase": "RELIABILITY_TRUST_RELIABILITY_UNCERTAINTY_LAYER",
            "reliability_records_count": total_rel,
            "active_drift_alerts_count": total_drift,
            "version": self.config.version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def run_research_evaluation(self) -> Dict[str, Any]:
        baselines = self.evaluator.evaluate_baselines()
        ablations = self.evaluator.evaluate_ablations()
        scenarios = self.evaluator.run_adversarial_scenarios()

        eval_id = f"eval-{uuid.uuid4().hex[:12]}"
        db_eval = ReliabilityEvaluationModel(
            evaluation_id=eval_id,
            evaluation_type="FULL_RESEARCH_SUITE",
            sample_count=500,
            results_summary={"baselines": baselines, "ablations": ablations, "scenarios_count": len(scenarios)},
            configuration_version=self.config.version,
            created_at=datetime.now(timezone.utc),
        )
        self.repo.save_evaluation_record(db_eval)

        return {
            "evaluation_id": eval_id,
            "baselines": baselines,
            "ablations": ablations,
            "scenarios": scenarios,
        }

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
