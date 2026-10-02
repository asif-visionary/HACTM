"""
Machine Learning and Statistical Anomaly Detection Engine.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Implements:
- AnomalyDetector interface (fit, predict, score, explain)
- IsolationForestDetector (scikit-learn with Sigmoid Cyber Risk Normalization)
- RobustZScoreDetector (Median Absolute Deviation statistical fallback)
- Model metadata versioning, safe local serialization, and feature schema enforcement.
"""

from abc import ABC, abstractmethod
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import joblib
import numpy as np

from hactm.core.constants import SeverityLevel, risk_score_to_severity
from hactm.core.errors import HACTMValidationError
from hactm.core.logging import logger
from hactm.network.detectors.base import BaseDetector
from hactm.network.features.extractor import (
    CANONICAL_FEATURE_NAMES,
    FEATURE_SCHEMA_VERSION,
    NetworkFeatureExtractor,
)
from hactm.network.models import (
    DetectorType,
    NetworkDetectionResult,
    NetworkEvent,
    NetworkModelMetadata,
)


class BaseAnomalyModel(ABC):
    """Abstract model interface for anomaly scoring."""
    @abstractmethod
    def fit(self, X: np.ndarray) -> None:
        pass

    @abstractmethod
    def score_sample(self, x: np.ndarray) -> float:
        """Returns normalized cyber risk score: 0.0 (benign) to 1.0 (highly anomalous)."""
        pass

    @abstractmethod
    def explain_sample(self, x: np.ndarray, feature_names: List[str]) -> Tuple[List[str], Dict[str, float]]:
        """Returns (contributing_reasons, feature_contributions)."""
        pass


class IsolationForestModel(BaseAnomalyModel):
    """
    Isolation Forest implementation with sigmoid cyber risk normalization.
    """
    def __init__(self, contamination: float = 0.05, n_estimators: int = 100, random_seed: int = 42):
        from sklearn.ensemble import IsolationForest
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_seed = random_seed
        self.model = IsolationForest(
            contamination=contamination,
            n_estimators=n_estimators,
            random_state=random_seed,
            n_jobs=-1,
        )
        self.is_fitted = False
        self.feature_means: Optional[np.ndarray] = None
        self.feature_stds: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> None:
        if X.shape[0] < 10:
            raise HACTMValidationError(f"Insufficient training data: requires at least 10 samples, got {X.shape[0]}")
        self.model.fit(X)
        self.feature_means = np.mean(X, axis=0)
        self.feature_stds = np.std(X, axis=0) + 1e-6
        self.is_fitted = True

    def score_sample(self, x: np.ndarray) -> float:
        """
        Calculates normalized cyber risk score from Isolation Forest decision function.
        Raw decision_function: positive = inlier, negative = outlier.
        Normalization Formula:
            risk_score = 1.0 / (1.0 + exp(decision_function * 8.0))
        Maps raw decision function to [0.0, 1.0] where 1.0 is maximum anomaly risk.
        """
        if not self.is_fitted:
            return 0.0
        x_2d = x.reshape(1, -1)
        raw_score = float(self.model.decision_function(x_2d)[0])
        # Sigmoid mapping centered near 0.0 decision boundary
        risk_score = 1.0 / (1.0 + math.exp(raw_score * 8.0))
        return float(np.clip(risk_score, 0.0, 1.0))

    def explain_sample(self, x: np.ndarray, feature_names: List[str]) -> Tuple[List[str], Dict[str, float]]:
        reasons = []
        contributions: Dict[str, float] = {}
        if self.feature_means is not None and self.feature_stds is not None:
            # Measure deviation from training feature means in standard deviations
            z_scores = (x - self.feature_means) / self.feature_stds
            top_indices = np.argsort(np.abs(z_scores))[::-1][:3]
            for idx in top_indices:
                feat = feature_names[idx]
                dev = float(z_scores[idx])
                contributions[feat] = round(float(x[idx]), 3)
                if abs(dev) >= 2.0:
                    reasons.append(f"{feat} deviated by {dev:+.1f} std-dev from baseline")
        return reasons, contributions


class RobustZScoreModel(BaseAnomalyModel):
    """
    Robust statistical z-score model using Median and Median Absolute Deviation (MAD).
    Serves as deterministic statistical fallback for small datasets or zero ML dependencies.
    """
    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold
        self.medians: Optional[np.ndarray] = None
        self.mads: Optional[np.ndarray] = None
        self.is_fitted = False

    def fit(self, X: np.ndarray) -> None:
        if X.shape[0] < 5:
            raise HACTMValidationError("Insufficient training data for statistical baseline (<5 samples)")
        self.medians = np.median(X, axis=0)
        self.mads = np.median(np.abs(X - self.medians), axis=0) + 1e-5
        self.is_fitted = True

    def score_sample(self, x: np.ndarray) -> float:
        if not self.is_fitted or self.medians is None or self.mads is None:
            return 0.0
        z_scores = np.abs(x - self.medians) / (1.4826 * self.mads)
        max_z = float(np.max(z_scores))
        # Logistic sigmoid mapping of max z-score to [0, 1]
        risk = 1.0 / (1.0 + math.exp(-0.8 * (max_z - self.threshold)))
        return float(np.clip(risk, 0.0, 1.0))

    def explain_sample(self, x: np.ndarray, feature_names: List[str]) -> Tuple[List[str], Dict[str, float]]:
        reasons = []
        contributions: Dict[str, float] = {}
        if self.medians is not None and self.mads is not None:
            z_scores = np.abs(x - self.medians) / (1.4826 * self.mads)
            for idx, z in enumerate(z_scores):
                if z >= self.threshold:
                    feat = feature_names[idx]
                    reasons.append(f"{feat} has robust z-score {z:.1f} (Threshold: {self.threshold})")
                    contributions[feat] = float(x[idx])
        return reasons, contributions


class AnomalyDetector(BaseDetector):
    """
    Anomaly Detector coordinating feature extraction, inference scoring, and model serialization.
    """
    detector_type = DetectorType.ANOMALY
    detector_id = "network-anomaly-detector"
    detector_version = "1.0.0"

    def __init__(
        self,
        algorithm: str = "isolation_forest",
        contamination: float = 0.05,
        anomaly_threshold: float = 0.65,
        features: Optional[List[str]] = None,
        model_dir: Optional[Path] = None,
    ):
        self.algorithm = algorithm
        self.anomaly_threshold = anomaly_threshold
        self.features = features or [
            "duration", "flow_bytes", "flow_packets",
            "bytes_per_second", "packets_per_second", "forward_ratio"
        ]
        self.extractor = NetworkFeatureExtractor(selected_features=self.features)
        self.model_dir = model_dir or Path(__file__).resolve().parent.parent.parent.parent / "models" / "network"
        self.model_dir.mkdir(parents=True, exist_ok=True)

        if algorithm == "isolation_forest":
            self.model: BaseAnomalyModel = IsolationForestModel(contamination=contamination)
        else:
            self.model = RobustZScoreModel()

        self.metadata = NetworkModelMetadata(
            model_id="model_net_baseline_v1",
            model_version="1.0.0",
            algorithm=algorithm,
            parameters={"contamination": contamination},
            features=self.features,
            feature_schema_version=FEATURE_SCHEMA_VERSION,
            status="ACTIVE",
        )

    def fit(self, events: List[NetworkEvent], dataset_name: Optional[str] = None) -> NetworkModelMetadata:
        """Trains the anomaly detector on a list of NetworkEvents."""
        if len(events) < 10:
            raise HACTMValidationError("Insufficient training data for network anomaly detector (<10 events)")

        X = self.extractor.to_matrix(events)
        self.model.fit(X)
        self.metadata.training_dataset = dataset_name or "in_memory"
        self.metadata.training_timestamp = datetime.now(timezone.utc)
        self.metadata.training_samples = len(events)
        self.metadata.status = "ACTIVE"
        logger.info(f"Trained {self.algorithm} anomaly model on {len(events)} network events")
        return self.metadata

    def save_model(self, file_stem: str = "model_net_baseline_v1") -> Tuple[Path, Path]:
        """Safely persists model artifact and schema metadata."""
        artifact_path = self.model_dir / f"{file_stem}.joblib"
        meta_path = self.model_dir / f"{file_stem}.meta.json"
        self.metadata.artifact_path = str(artifact_path)

        joblib.dump(self.model, artifact_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(self.metadata.model_dump_json(indent=2))

        logger.info(f"Saved network anomaly model to {artifact_path}")
        return artifact_path, meta_path

    def load_model(self, file_stem: str = "model_net_baseline_v1") -> bool:
        """Loads and validates model artifact and its metadata schema."""
        artifact_path = self.model_dir / f"{file_stem}.joblib"
        meta_path = self.model_dir / f"{file_stem}.meta.json"

        if not artifact_path.exists() or not meta_path.exists():
            return False

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta_dict = json.load(f)
            loaded_meta = NetworkModelMetadata(**meta_dict)

            # Validate feature schema version compatibility
            if loaded_meta.feature_schema_version != FEATURE_SCHEMA_VERSION:
                logger.error(f"Model schema mismatch: {loaded_meta.feature_schema_version} != {FEATURE_SCHEMA_VERSION}")
                return False

            self.model = joblib.load(artifact_path)
            self.metadata = loaded_meta
            self.features = loaded_meta.features
            self.extractor = NetworkFeatureExtractor(selected_features=self.features)
            logger.info(f"Loaded network anomaly model {loaded_meta.model_id} (Version {loaded_meta.model_version})")
            return True
        except Exception as e:
            logger.error(f"Failed to securely load anomaly model: {e}")
            return False

    def score(self, event: NetworkEvent) -> float:
        """Returns normalized cyber risk score: 0.0 to 1.0 (Section 22, 27)."""
        x = self.extractor.to_vector(event)
        return self.model.score_sample(x)

    def predict(self, event: NetworkEvent) -> int:
        """Binary prediction: 1 if anomaly score >= anomaly_threshold else 0."""
        return 1 if self.score(event) >= self.anomaly_threshold else 0

    def explain(self, event: NetworkEvent) -> Tuple[List[str], Dict[str, float]]:
        """Provides human and feature explanations for detection (Section 30)."""
        x = self.extractor.to_vector(event)
        return self.model.explain_sample(x, self.features)

    def detect(self, event: NetworkEvent) -> Optional[NetworkDetectionResult]:
        t0 = time.perf_counter()

        try:
            x = self.extractor.to_vector(event)
        except Exception as e:
            logger.warning(f"Feature extraction failed on {event.event_id}: {e}")
            return None

        try:
            risk_score = self.model.score_sample(x)
        except Exception as e:
            logger.warning(f"Anomaly scoring failed on {event.event_id}: {e}")
            return None

        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 3)

        if risk_score >= self.anomaly_threshold:
            reasons, contributions = self.model.explain_sample(x, self.features)
            explanation = (
                f"Statistical Anomaly Detected (Risk Score: {risk_score:.3f}, Threshold: {self.anomaly_threshold}). "
                + ("; ".join(reasons) if reasons else "Multi-dimensional feature vector deviated from baseline.")
            )

            severity = risk_score_to_severity(risk_score)
            confidence = 0.82  # Documented baseline confidence for unsupervised anomaly models
            uncertainty = round(max(0.0, 1.0 - confidence), 4)

            return NetworkDetectionResult(
                detection_id=f"DET-ANOM-{self.metadata.model_version}-{event.event_id}",
                event_id=event.event_id,
                detector_type=DetectorType.ANOMALY,
                detector_id=self.detector_id,
                detector_version=self.detector_version,
                category="Statistical / Unsupervised Flow Anomaly",
                risk_score=round(risk_score, 4),
                confidence=confidence,
                uncertainty=uncertainty,
                severity=severity,
                reason_codes=["FLOW_ANOMALY_SCORE_EXCEEDED"],
                explanation=explanation,
                features_used=contributions,
                timestamp=datetime.now(timezone.utc),
                model_version=self.metadata.model_version,
                processing_time_ms=elapsed_ms,
                src_ip=event.src_ip,
                dst_ip=event.dst_ip,
            )

        return None


class RobustZScoreDetector(AnomalyDetector):
    """
    Robust Z-Score statistical anomaly detector wrapping Median Absolute Deviation (MAD).
    """
    def __init__(self, threshold_z: float = 3.0, **kwargs):
        super().__init__(algorithm="robust_zscore", **kwargs)
        self.model = RobustZScoreModel(threshold=threshold_z)

