"""
Model Registry Service for HACTM.
Specialized Security Agents — Model Lifecycle, Versioning, & Provenance Management.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from hactm.storage.models import ModelRegistryModel
from hactm.core.logging import logger


class ModelRegistry:
    """
    Manages registration, activation, retirement, and metadata persistence
    of machine learning models across all security agents.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def register_model(
        self,
        model_id: str,
        agent_id: str,
        algorithm: str,
        version: str = "1.0.0",
        dataset: Optional[str] = None,
        feature_schema: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        random_seed: int = 42,
        status: str = "CANDIDATE",
        evaluation_metrics: Optional[Dict[str, Any]] = None,
        artifact_path: Optional[str] = None,
    ) -> ModelRegistryModel:
        """Registers a new model entry in the CANDIDATE state by default."""
        existing = self.db.query(ModelRegistryModel).filter(ModelRegistryModel.model_id == model_id).first()
        if existing:
            logger.info(f"Updating existing model entry: {model_id}")
            existing.version = version
            existing.algorithm = algorithm
            existing.dataset = dataset
            existing.feature_schema = feature_schema or {}
            existing.parameters = parameters or {}
            existing.random_seed = random_seed
            existing.status = status
            existing.evaluation_metrics = evaluation_metrics or {}
            existing.artifact_path = artifact_path
            existing.training_time = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        model_entry = ModelRegistryModel(
            model_id=model_id,
            agent_id=agent_id,
            version=version,
            algorithm=algorithm,
            dataset=dataset,
            feature_schema=feature_schema or {},
            parameters=parameters or {},
            random_seed=random_seed,
            status=status,
            evaluation_metrics=evaluation_metrics or {},
            artifact_path=artifact_path,
            training_time=datetime.now(timezone.utc),
        )
        self.db.add(model_entry)
        self.db.commit()
        self.db.refresh(model_entry)
        logger.info(f"Registered model {model_id} for agent {agent_id} in state {status}")
        return model_entry

    def activate_model(self, model_id: str) -> Optional[ModelRegistryModel]:
        """Sets target model to ACTIVE and retires previous ACTIVE models for the same agent."""
        target = self.db.query(ModelRegistryModel).filter(ModelRegistryModel.model_id == model_id).first()
        if not target:
            logger.warning(f"Cannot activate non-existent model: {model_id}")
            return None

        # Retire current ACTIVE models for this agent
        active_models = self.db.query(ModelRegistryModel).filter(
            ModelRegistryModel.agent_id == target.agent_id,
            ModelRegistryModel.status == "ACTIVE"
        ).all()
        for am in active_models:
            am.status = "RETIRED"

        target.status = "ACTIVE"
        self.db.commit()
        self.db.refresh(target)
        logger.info(f"Activated model {model_id} for agent {target.agent_id}")
        return target

    def get_active_model(self, agent_id: str) -> Optional[ModelRegistryModel]:
        """Returns the currently ACTIVE model for an agent, if any."""
        return self.db.query(ModelRegistryModel).filter(
            ModelRegistryModel.agent_id == agent_id,
            ModelRegistryModel.status == "ACTIVE"
        ).first()

    def get_model(self, model_id: str) -> Optional[ModelRegistryModel]:
        """Retrieves model by model_id."""
        return self.db.query(ModelRegistryModel).filter(ModelRegistryModel.model_id == model_id).first()

    def list_models(self, agent_id: Optional[str] = None) -> List[ModelRegistryModel]:
        """Lists models, optionally filtered by agent_id."""
        query = self.db.query(ModelRegistryModel)
        if agent_id:
            query = query.filter(ModelRegistryModel.agent_id == agent_id)
        return query.all()
