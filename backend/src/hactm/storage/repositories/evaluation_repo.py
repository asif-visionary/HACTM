"""
EvaluationRepository: Database access layer for Evaluation Framework, Scalability, and Reports data.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from hactm.storage.models import (
    EvaluationDatasetModel,
    ExperimentConfigModel,
    ExperimentRunModel,
    MetricResultModel,
    BaselineResultModel,
    AblationResultModel,
    ScalabilityResultModel,
    SegmentationResultModel,
    EvaluationReportModel,
)


class EvaluationRepository:
    """Repository handling CRUD operations for Evaluation database tables."""

    def __init__(self, db: Session):
        self.db = db

    # --- Datasets ---
    def create_dataset(self, dataset_data: Dict[str, Any]) -> EvaluationDatasetModel:
        obj = EvaluationDatasetModel(**dataset_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_dataset(self, dataset_id: str) -> Optional[EvaluationDatasetModel]:
        return self.db.query(EvaluationDatasetModel).filter_by(dataset_id=dataset_id).first()

    def list_datasets(self, domain: Optional[str] = None) -> List[EvaluationDatasetModel]:
        query = self.db.query(EvaluationDatasetModel)
        if domain:
            query = query.filter(EvaluationDatasetModel.domain == domain)
        return query.order_by(EvaluationDatasetModel.created_at.desc()).all()

    # --- Experiments & Runs ---
    def create_experiment_config(self, config_data: Dict[str, Any]) -> ExperimentConfigModel:
        obj = ExperimentConfigModel(**config_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list_experiment_configs(self) -> List[ExperimentConfigModel]:
        return self.db.query(ExperimentConfigModel).order_by(ExperimentConfigModel.created_at.desc()).all()

    def create_experiment_run(self, run_data: Dict[str, Any]) -> ExperimentRunModel:
        obj = ExperimentRunModel(**run_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_run_status(
        self, run_id: str, status: str, metrics: Optional[Dict[str, Any]] = None, error: Optional[str] = None
    ) -> Optional[ExperimentRunModel]:
        run = self.db.query(ExperimentRunModel).filter_by(run_id=run_id).first()
        if run:
            run.status = status
            if metrics:
                run.metrics_summary = metrics
            if error:
                run.error_log = error
            if status in ("COMPLETED", "FAILED", "CANCELLED"):
                run.end_time = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(run)
        return run

    def list_experiment_runs(self, limit: int = 50) -> List[ExperimentRunModel]:
        return self.db.query(ExperimentRunModel).order_by(ExperimentRunModel.start_time.desc()).limit(limit).all()

    # --- Results ---
    def save_metric_results(self, metric_records: List[Dict[str, Any]]):
        for m in metric_records:
            obj = MetricResultModel(**m)
            self.db.add(obj)
        self.db.commit()

    def save_baseline_results(self, baseline_records: List[Dict[str, Any]]):
        for b in baseline_records:
            obj = BaselineResultModel(**b)
            self.db.add(obj)
        self.db.commit()

    def save_ablation_results(self, ablation_records: List[Dict[str, Any]]):
        for a in ablation_records:
            obj = AblationResultModel(**a)
            self.db.add(obj)
        self.db.commit()

    def save_scalability_results(self, scalability_records: List[Dict[str, Any]]):
        for s in scalability_records:
            obj = ScalabilityResultModel(**s)
            self.db.add(obj)
        self.db.commit()

    def get_latest_scalability(self) -> List[ScalabilityResultModel]:
        return self.db.query(ScalabilityResultModel).order_by(ScalabilityResultModel.created_at.desc()).limit(10).all()

    # --- Reports ---
    def create_report(self, report_data: Dict[str, Any]) -> EvaluationReportModel:
        obj = EvaluationReportModel(**report_data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_report(self, report_id: str) -> Optional[EvaluationReportModel]:
        return self.db.query(EvaluationReportModel).filter_by(report_id=report_id).first()

    def list_reports(self, limit: int = 50) -> List[EvaluationReportModel]:
        return self.db.query(EvaluationReportModel).order_by(EvaluationReportModel.created_at.desc()).limit(limit).all()
