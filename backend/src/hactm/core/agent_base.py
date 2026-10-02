"""
Base Security Agent Interface for HACTM.
Specialized Security Agents — Multi-Domain Specialized Security Agents.

Provides abstract base class BaseSecurityAgent defining the canonical interface
required across all heterogeneous security agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from hactm.core.models import SecurityEvidence


class SecurityDetectionResult:
    """
    Common Detection Result schema across all security agents.
    Represents an explainable detection finding produced by an agent detector.
    """
    def __init__(
        self,
        detection_id: str,
        event_id: str,
        agent_id: str,
        detector_type: str,
        detector_id: str,
        category: str,
        risk_score: float,
        confidence: float,
        uncertainty: float,
        severity: str,
        explanation: str,
        features_used: Dict[str, Any],
        detector_version: str = "1.0.0",
        reason_codes: Optional[List[str]] = None,
        model_version: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        processing_time_ms: float = 0.0,
        subcategories: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        matched_rules: Optional[List[str]] = None,
        model_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.detection_id = detection_id
        self.event_id = event_id
        self.agent_id = agent_id
        self.detector_type = detector_type  # e.g., NLP, SIGNATURE, STATISTICAL, HEURISTIC, RULE, ANOMALY
        self.detector_id = detector_id
        self.detector_version = detector_version
        self.category = category
        self.risk_score = max(0.0, min(1.0, float(risk_score)))
        self.confidence = max(0.0, min(1.0, float(confidence)))
        self.uncertainty = max(0.0, min(1.0, float(uncertainty)))
        self.severity = severity
        self.reason_codes = reason_codes or []
        self.explanation = explanation
        self.features_used = features_used or {}
        self.model_version = model_version
        self.timestamp = timestamp or datetime.utcnow()
        self.processing_time_ms = processing_time_ms
        self.subcategories = subcategories or []
        self.labels = labels or []
        self.matched_rules = matched_rules or []
        self.model_metadata = model_metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "event_id": self.event_id,
            "agent_id": self.agent_id,
            "detector_type": self.detector_type,
            "detector_id": self.detector_id,
            "detector_version": self.detector_version,
            "category": self.category,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "severity": self.severity,
            "reason_codes": self.reason_codes,
            "explanation": self.explanation,
            "features_used": self.features_used,
            "model_version": self.model_version,
            "timestamp": self.timestamp.isoformat() if hasattr(self.timestamp, "isoformat") else str(self.timestamp),
            "processing_time_ms": self.processing_time_ms,
            "subcategories": self.subcategories,
            "labels": self.labels,
            "matched_rules": self.matched_rules,
            "model_metadata": self.model_metadata,
        }


class BaseSecurityAgent(ABC):
    """
    Standard interface contract for HACTM security agents.
    All Specialized Security Agents security agents must implement this interface.
    """

    @abstractmethod
    def initialize(self) -> "BaseSecurityAgent":
        """Initialize models, configurations, and internal states."""
        pass

    @abstractmethod
    def validate(self, raw_event: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input domain event structure and required fields."""
        pass

    @abstractmethod
    def extract_features(self, event: Any) -> Dict[str, Any]:
        """Extract domain features from normalized event."""
        pass

    @abstractmethod
    def detect(self, event: Any) -> List[SecurityDetectionResult]:
        """Perform threat and anomaly detection on a single event."""
        pass

    @abstractmethod
    def explain(self, detection: SecurityDetectionResult) -> str:
        """Generate human-understandable explanation for a detection."""
        pass

    @abstractmethod
    def calculate_risk(self, features: Dict[str, Any], detections: List[SecurityDetectionResult]) -> Tuple[float, float, float]:
        """
        Calculate baseline (Cyber Risk Score, Confidence, Uncertainty).
        Risk Score: 0.0 (benign) to 1.0 (high cyber risk).
        Confidence: Detector certainty.
        Uncertainty: Baseline/variance uncertainty.
        """
        pass

    @abstractmethod
    def generate_evidence(self, detection: SecurityDetectionResult, dataset_name: str = "default") -> SecurityEvidence:
        """Convert a domain detection result into a canonical SecurityEvidence model."""
        pass

    @abstractmethod
    def process_event(self, raw_event: Dict[str, Any]) -> List[SecurityDetectionResult]:
        """Normalize, validate, extract features, detect, and return detection results."""
        pass

    @abstractmethod
    def process_batch(
        self, events: List[Dict[str, Any]], dataset_name: str = "default"
    ) -> Tuple[List[SecurityDetectionResult], List[SecurityEvidence]]:
        """Process a batch of domain events into detections and SecurityEvidence."""
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Return operational health, processing metrics, and active detector statuses."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Gracefully release resources and flush state buffers."""
        pass
