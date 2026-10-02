"""
Base Zero-Day Detector Interface and Common Schema for HACTM.
Defines abstract ZeroDayDetector class and ZeroDayDetectionResult schema.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ZeroDayDetectionResult(BaseModel):
    """Standard result schema for Zero-Day and Anomaly Detection."""
    event_id: str
    detected: bool
    risk_score: float = Field(..., ge=0.0, le=1.0)
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    uncertainty: float = Field(..., ge=0.0, le=1.0)
    attack_family: str = "unknown"
    known_attack_probability: float = Field(..., ge=0.0, le=1.0)
    zero_day_indicator: bool
    model: str
    explanation: Optional[Dict[str, Any]] = None
    inference_latency_ms: float = 0.0


class ZeroDayDetector(ABC):
    """Abstract base class for all Zero-Day Detection Model Adapters."""

    @abstractmethod
    def fit(self, X: List[List[float]], y: Optional[List[int]] = None) -> None:
        """Fits model on training data."""
        pass

    @abstractmethod
    def predict(self, X: List[List[float]]) -> List[bool]:
        """Predicts binary detection status."""
        pass

    @abstractmethod
    def predict_score(self, X: List[List[float]]) -> List[float]:
        """Predicts anomaly score in range [0, 1]."""
        pass

    @abstractmethod
    def predict_uncertainty(self, X: List[List[float]]) -> List[float]:
        """Predicts model uncertainty in range [0, 1]."""
        pass

    @abstractmethod
    def detect_unknown(self, X: List[List[float]], threshold: float = 0.70) -> List[ZeroDayDetectionResult]:
        """Runs full zero-day evaluation returning structured result schema."""
        pass

    @abstractmethod
    def explain(self, sample: List[float]) -> Dict[str, Any]:
        """Provides feature importance or explanation for prediction."""
        pass

    @abstractmethod
    def evaluate(self, X: List[List[float]], y: List[int]) -> Dict[str, float]:
        """Evaluates detection metrics (precision, recall, f1, auroc, auprc)."""
        pass

    @abstractmethod
    def save_model(self, filepath: str) -> None:
        """Persists model artifact."""
        pass

    @abstractmethod
    def load_model(self, filepath: str) -> None:
        """Loads model artifact."""
        pass
