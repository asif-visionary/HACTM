"""
HACTM Core Constants.
Foundation Architecture - Hierarchical Adaptive Cyber Trust Mesh.
"""

from enum import Enum

SCHEMA_VERSION = "1.0.0"
PREPROCESSING_VERSION = "1.0.0"

# Risk Semantics Definition:
# 0.0 = lowest cyber risk (benign / trusted)
# 1.0 = highest cyber risk (severe threat / critical anomalous risk)
# Do NOT call this "Trust Score" unless the direction is explicitly reversed.
# In HACTM, risk_score measures "Cyber Risk Score" (0.0 to 1.0).
MIN_RISK_SCORE = 0.0
MAX_RISK_SCORE = 1.0

MIN_CONFIDENCE_SCORE = 0.0
MAX_CONFIDENCE_SCORE = 1.0

MIN_UNCERTAINTY_SCORE = 0.0
MAX_UNCERTAINTY_SCORE = 1.0


class IngestionPolicy(str, Enum):
    """Policies for handling validation/format errors during dataset ingestion."""
    STRICT = "STRICT"
    SKIP_INVALID = "SKIP_INVALID"
    QUARANTINE_INVALID = "QUARANTINE_INVALID"


class EventType(str, Enum):
    """Core security event categories supported in Foundation."""
    NETWORK = "NETWORK"
    EMAIL = "EMAIL"
    AUTHENTICATION = "AUTHENTICATION"
    UBA = "UBA"
    TRANSACTION = "TRANSACTION"
    SYSTEM = "SYSTEM"
    IDENTITY = "IDENTITY"
    OTHER = "OTHER"


class SeverityLevel(str, Enum):
    """Standardized severity levels mapped from risk scores or source values."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EntityType(str, Enum):
    """Deterministic entity categories."""
    IP = "IP"
    EMAIL = "EMAIL"
    USER = "USER"
    HOST = "HOST"
    DEVICE = "DEVICE"
    ACCOUNT = "ACCOUNT"
    UNKNOWN = "UNKNOWN"


def risk_score_to_severity(risk_score: float) -> SeverityLevel:
    """
    Deterministically map a 0.0 - 1.0 cyber risk score to a standard severity level.
    """
    if risk_score >= 0.8:
        return SeverityLevel.CRITICAL
    if risk_score >= 0.6:
        return SeverityLevel.HIGH
    if risk_score >= 0.3:
        return SeverityLevel.MEDIUM
    return SeverityLevel.LOW
