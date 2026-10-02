"""
Canonical Models for HACTM Network Security Agent.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from hactm.core.constants import SeverityLevel, risk_score_to_severity


class IPClassification(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    LOOPBACK = "LOOPBACK"
    LINK_LOCAL = "LINK_LOCAL"
    MULTICAST = "MULTICAST"
    UNSPECIFIED = "UNSPECIFIED"
    RESERVED = "RESERVED"


class DetectorType(str, Enum):
    SIGNATURE = "SIGNATURE"
    HEURISTIC = "HEURISTIC"
    ANOMALY = "ANOMALY"
    ML_IDS = "ML_IDS"


class AnalystLabel(str, Enum):
    TRUE_POSITIVE = "TRUE_POSITIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    TRUE_NEGATIVE = "TRUE_NEGATIVE"
    FALSE_NEGATIVE = "FALSE_NEGATIVE"
    UNKNOWN = "UNKNOWN"


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class NetworkEvent(BaseModel):
    """
    Canonical NetworkEvent Model.
    Standardized contract for all flow and packet-level security telemetry.
    """
    event_id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="UTC timestamp of observed flow")
    src_ip: str = Field(..., description="Source IPv4 or IPv6 address")
    dst_ip: str = Field(..., description="Destination IPv4 or IPv6 address")
    src_port: Optional[int] = Field(None, ge=0, le=65535, description="Source port (0-65535)")
    dst_port: Optional[int] = Field(None, ge=0, le=65535, description="Destination port (0-65535)")
    protocol: str = Field(default="OTHER", description="Transport protocol: TCP, UDP, ICMP, ICMPv6, SCTP, OTHER")

    # Flow Metrics
    duration: Optional[float] = Field(None, ge=0.0, description="Flow duration in seconds")
    flow_bytes: Optional[int] = Field(None, ge=0, description="Total flow volume in bytes")
    flow_packets: Optional[int] = Field(None, ge=0, description="Total packet count")
    forward_bytes: Optional[int] = Field(None, ge=0, description="Forward direction bytes")
    backward_bytes: Optional[int] = Field(None, ge=0, description="Backward direction bytes")
    forward_packets: Optional[int] = Field(None, ge=0, description="Forward direction packets")
    backward_packets: Optional[int] = Field(None, ge=0, description="Backward direction packets")

    # Telemetry Attributes
    tcp_flags: Optional[str] = Field(None, description="TCP control flags observed (e.g. SYN, ACK, FIN)")
    connection_state: Optional[str] = Field(None, description="Connection state (e.g. ESTABLISHED, S0, REJ)")
    flow_rate: Optional[float] = Field(None, ge=0.0, description="Bytes per second")
    packet_rate: Optional[float] = Field(None, ge=0.0, description="Packets per second")

    # Lineage & Audit
    dataset: Optional[str] = Field(None, description="Name of source network dataset")
    dataset_version: Optional[str] = Field(None, description="Version of source dataset")
    source_record_id: Optional[str] = Field(None, description="Row/index in source file")

    # Resolved Classifications
    src_ip_classification: Optional[IPClassification] = None
    dst_ip_classification: Optional[IPClassification] = None

    # Ground Truth Label (for evaluation datasets only; excluded from inference features)
    label: Optional[str] = Field(None, description="Dataset ground truth label if present")

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_utc_timestamp(cls, v: Any) -> Any:
        if isinstance(v, str):
            from dateutil import parser
            return ensure_utc(parser.parse(v))
        if isinstance(v, datetime):
            return ensure_utc(v)
        return v


class NetworkDetectionResult(BaseModel):
    """
    Standardized Network Detection Result.
    Produced by Signature, Heuristic, or Anomaly detectors.
    """
    detection_id: str = Field(..., description="Unique deterministic detection identifier")
    event_id: str = Field(..., description="Correlated NetworkEvent identifier")
    detector_type: DetectorType = Field(..., description="SIGNATURE, HEURISTIC, or ANOMALY")
    detector_id: str = Field(..., description="Identifier of detecting rule/module/model")
    detector_version: str = Field(default="1.0.0", description="Version of the detector component")
    category: str = Field(..., description="Cyber threat / anomaly category")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Normalized Cyber Risk Score: 0.0 to 1.0")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in detector mechanism: 0.0 to 1.0")
    uncertainty: float = Field(..., ge=0.0, le=1.0, description="Network Security Agent baseline uncertainty: 0.0 to 1.0")
    severity: SeverityLevel = Field(..., description="Severity tier: LOW, MEDIUM, HIGH, CRITICAL")
    reason_codes: List[str] = Field(default_factory=list, description="Machine-readable diagnostic reason codes")
    explanation: str = Field(..., description="Human-readable explanation of why event was flagged")
    features_used: Dict[str, Any] = Field(default_factory=dict, description="Values of features triggering detection")
    timestamp: datetime = Field(..., description="Detection generation timestamp (UTC)")
    model_version: Optional[str] = Field(None, description="ML model version if anomaly detector")
    signature_id: Optional[str] = Field(None, description="Signature ID if signature match")
    processing_time_ms: float = Field(default=0.0, ge=0.0, description="Processing latency in milliseconds")

    # Contextual Entities
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_utc(cls, v: Any) -> Any:
        if isinstance(v, str):
            from dateutil import parser
            return ensure_utc(parser.parse(v))
        if isinstance(v, datetime):
            return ensure_utc(v)
        return v


class NetworkModelMetadata(BaseModel):
    """
    Tracks ML and statistical anomaly model versions and reproducibility parameters.
    """
    model_id: str
    model_version: str
    algorithm: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    feature_schema_version: str = "1.0.0"
    features: List[str] = Field(default_factory=list)
    training_dataset: Optional[str] = None
    training_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    training_samples: int = 0
    artifact_path: Optional[str] = None
    random_seed: int = 42
    status: str = "CANDIDATE"  # ACTIVE, CANDIDATE, RETIRED, FAILED
    evaluation_summary: Optional[Dict[str, Any]] = None


class DetectionFeedback(BaseModel):
    """
    Analyst feedback and ground truth label assignment.
    """
    detection_id: str
    label: AnalystLabel
    analyst_note: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NetworkEvaluationMetrics(BaseModel):
    """
    Quantitative evaluation metrics for network detection validation.
    """
    total_evaluated: int
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    false_negative_rate: float
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None
    confusion_matrix: List[List[int]] = Field(default_factory=list)
    class_distribution: Dict[str, int] = Field(default_factory=dict)
