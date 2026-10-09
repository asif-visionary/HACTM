"""
SQLAlchemy Database Models for HACTM.
Tables:
- events
- entities
- security_evidence
- ingestion_runs
- ingestion_errors
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    JSON,
    ForeignKey,
    Index,
    Text,
)
from hactm.storage.database import Base


class EntityModel(Base):
    __tablename__ = "entities"

    entity_id = Column(String(255), primary_key=True, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    canonical_name = Column(String(255), nullable=False)
    attributes = Column(JSON, default=dict)
    first_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    event_count = Column(Integer, default=1, nullable=False)

    __table_args__ = (
        Index("idx_entities_type", "entity_type"),
        Index("idx_entities_last_seen", "last_seen"),
    )


class EventModel(Base):
    __tablename__ = "events"

    event_id = Column(String(255), primary_key=True, index=True)
    entity_id = Column(String(255), ForeignKey("entities.entity_id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    source = Column(String(128), nullable=True)
    risk_score = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_events_entity_time", "entity_id", "timestamp"),
        Index("idx_events_type_time", "event_type", "timestamp"),
    )


class SecurityEvidenceModel(Base):
    __tablename__ = "security_evidence"

    event_id = Column(String(255), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    entity_id = Column(String(255), ForeignKey("entities.entity_id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False, index=True)

    # Telemetry and context
    evidence = Column(JSON, nullable=False)
    source = Column(String(128), nullable=True, index=True)
    source_type = Column(String(64), nullable=True)
    dataset = Column(String(128), nullable=True, index=True)
    event_category = Column(String(128), nullable=True)

    # Identifiers
    raw_event_id = Column(String(255), nullable=True)
    parent_event_id = Column(String(255), nullable=True)
    session_id = Column(String(255), nullable=True)
    correlation_id = Column(String(255), nullable=True)

    # Lineage & Audit
    dataset_name = Column(String(128), nullable=True)
    dataset_version = Column(String(64), nullable=True)
    schema_version = Column(String(32), default="1.0.0")
    preprocessing_version = Column(String(32), default="1.0.0")
    source_record_id = Column(String(128), nullable=True)
    ingestion_run_id = Column(String(128), nullable=True, index=True)

    # Security Context
    security_tags = Column(JSON, default=list)
    security_group = Column(String(128), nullable=True)
    security_zone = Column(String(128), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Future-Phase Extensions (Must remain Nullable in Foundation)
    calibrated_probability = Column(Float, nullable=True)
    agent_reliability = Column(Float, nullable=True)
    evidence_quality = Column(Float, nullable=True)
    recommended_action = Column(String(255), nullable=True)

    __table_args__ = (
        Index("idx_evidence_risk_time", "risk_score", "timestamp"),
        Index("idx_evidence_entity_type", "entity_id", "event_type"),
    )


class IngestionRunModel(Base):
    __tablename__ = "ingestion_runs"

    run_id = Column(String(128), primary_key=True, index=True)
    source_name = Column(String(255), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False, default="IN_PROGRESS")
    total_records = Column(Integer, default=0)
    inserted = Column(Integer, default=0)
    duplicates = Column(Integer, default=0)
    invalid = Column(Integer, default=0)
    quarantined = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    policy = Column(String(32), nullable=False)
    error_message = Column(Text, nullable=True)


class IngestionErrorModel(Base):
    __tablename__ = "ingestion_errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(128), nullable=True, index=True)
    source_name = Column(String(255), nullable=False)
    row_number = Column(Integer, nullable=True)
    error_reason = Column(Text, nullable=False)
    quarantine_file = Column(String(512), nullable=True)
    raw_record = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class NetworkEventModel(Base):
    __tablename__ = "network_events"

    event_id = Column(String(255), primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    src_ip = Column(String(64), nullable=False, index=True)
    dst_ip = Column(String(64), nullable=False, index=True)
    src_port = Column(Integer, nullable=True)
    dst_port = Column(Integer, nullable=True, index=True)
    protocol = Column(String(32), nullable=False, default="OTHER")
    duration = Column(Float, nullable=True)
    flow_bytes = Column(Integer, nullable=True)
    flow_packets = Column(Integer, nullable=True)
    forward_bytes = Column(Integer, nullable=True)
    backward_bytes = Column(Integer, nullable=True)
    forward_packets = Column(Integer, nullable=True)
    backward_packets = Column(Integer, nullable=True)
    tcp_flags = Column(String(64), nullable=True)
    connection_state = Column(String(64), nullable=True)
    flow_rate = Column(Float, nullable=True)
    packet_rate = Column(Float, nullable=True)
    dataset = Column(String(128), nullable=True)
    src_ip_classification = Column(String(32), nullable=True)
    dst_ip_classification = Column(String(32), nullable=True)
    label = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_net_events_src_time", "src_ip", "timestamp"),
        Index("idx_net_events_dst_port", "dst_port", "protocol"),
    )


class NetworkDetectionModel(Base):
    __tablename__ = "network_detections"

    detection_id = Column(String(255), primary_key=True, index=True)
    event_id = Column(String(255), nullable=False, index=True)
    detector_type = Column(String(32), nullable=False, index=True)
    detector_id = Column(String(128), nullable=False)
    detector_version = Column(String(32), nullable=False, default="1.0.0")
    category = Column(String(128), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False, index=True)
    reason_codes = Column(JSON, default=list)
    explanation = Column(Text, nullable=False)
    features_used = Column(JSON, default=dict)
    model_version = Column(String(64), nullable=True)
    signature_id = Column(String(64), nullable=True)
    processing_time_ms = Column(Float, default=0.0)
    src_ip = Column(String(64), nullable=True, index=True)
    dst_ip = Column(String(64), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_net_det_risk_time", "risk_score", "timestamp"),
        Index("idx_net_det_cat_type", "category", "detector_type"),
    )


class NetworkModelDbModel(Base):
    __tablename__ = "network_models"

    model_id = Column(String(128), primary_key=True, index=True)
    model_version = Column(String(32), nullable=False)
    algorithm = Column(String(64), nullable=False)
    parameters = Column(JSON, default=dict)
    feature_schema_version = Column(String(32), default="1.0.0")
    features = Column(JSON, default=list)
    training_dataset = Column(String(128), nullable=True)
    training_timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    training_samples = Column(Integer, default=0)
    artifact_path = Column(String(512), nullable=True)
    random_seed = Column(Integer, default=42)
    status = Column(String(32), default="CANDIDATE", index=True)  # ACTIVE, CANDIDATE, RETIRED
    evaluation_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DetectionFeedbackModel(Base):
    __tablename__ = "detection_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detection_id = Column(String(255), ForeignKey("network_detections.detection_id", ondelete="CASCADE"), nullable=False, index=True)
    label = Column(String(32), nullable=False)
    analyst_note = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ============================================================
# SPECIALIZED AGENTS — MULTI-DOMAIN SPECIALIZED SECURITY AGENT TABLES
# ============================================================

class ModelRegistryModel(Base):
    """General Model Registry for all domain agents."""
    __tablename__ = "model_registry"

    model_id = Column(String(128), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    version = Column(String(32), nullable=False, default="1.0.0")
    algorithm = Column(String(64), nullable=False)
    dataset = Column(String(128), nullable=True)
    feature_schema = Column(JSON, default=dict)
    parameters = Column(JSON, default=dict)
    random_seed = Column(Integer, default=42)
    training_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status = Column(String(32), default="CANDIDATE", index=True)  # CANDIDATE, ACTIVE, RETIRED, FAILED
    evaluation_metrics = Column(JSON, nullable=True)
    artifact_path = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AgentRunModel(Base):
    """Tracks agent execution runs and operational metrics."""
    __tablename__ = "agent_runs"

    run_id = Column(String(128), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False, default="IN_PROGRESS")
    events_processed = Column(Integer, default=0)
    detections_generated = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    average_latency_ms = Column(Float, default=0.0)
    model_version = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)


# ------------------------------------------------------------
# 1. Phishing Intelligence Tables
# ------------------------------------------------------------
class PhishingEventModel(Base):
    __tablename__ = "phishing_events"

    message_id = Column(String(255), primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    sender = Column(String(255), nullable=True, index=True)
    recipient = Column(String(255), nullable=True, index=True)
    subject = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    headers = Column(JSON, nullable=True)
    urls = Column(JSON, default=list)
    attachments = Column(JSON, default=list)
    sender_domain = Column(String(255), nullable=True, index=True)
    reply_to = Column(String(255), nullable=True)
    return_path = Column(String(255), nullable=True)
    authentication_results = Column(JSON, nullable=True)
    source_ip = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PhishingDetectionModel(Base):
    __tablename__ = "phishing_detections"

    detection_id = Column(String(255), primary_key=True, index=True)
    event_id = Column(String(255), ForeignKey("phishing_events.message_id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(String(128), default="phishing-intelligence-agent", nullable=False)
    detector_type = Column(String(32), nullable=False, index=True)
    detector_id = Column(String(128), nullable=False)
    detector_version = Column(String(32), default="1.0.0")
    category = Column(String(128), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    reason_codes = Column(JSON, default=list)
    explanation = Column(Text, nullable=False)
    features_used = Column(JSON, default=dict)
    model_version = Column(String(64), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    processing_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ------------------------------------------------------------
# 2. User Behavior Analytics (UBA) Tables
# ------------------------------------------------------------
class UbaEventModel(Base):
    __tablename__ = "uba_events"

    event_id = Column(String(255), primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    session_id = Column(String(255), nullable=True)
    device_id = Column(String(255), nullable=True)
    source_ip = Column(String(64), nullable=True)
    action = Column(String(128), nullable=False, index=True)
    resource = Column(String(255), nullable=True)
    resource_type = Column(String(128), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    application = Column(String(128), nullable=True)
    authentication_status = Column(String(64), nullable=True)
    privilege_level = Column(String(64), nullable=True)
    location = Column(String(128), nullable=True)
    bytes_transferred = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UbaDetectionModel(Base):
    __tablename__ = "uba_detections"

    detection_id = Column(String(255), primary_key=True, index=True)
    event_id = Column(String(255), ForeignKey("uba_events.event_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(128), default="uba-agent", nullable=False)
    detector_type = Column(String(32), nullable=False, index=True)
    detector_id = Column(String(128), nullable=False)
    detector_version = Column(String(32), default="1.0.0")
    category = Column(String(128), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    reason_codes = Column(JSON, default=list)
    explanation = Column(Text, nullable=False)
    features_used = Column(JSON, default=dict)
    model_version = Column(String(64), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    processing_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UbaProfileModel(Base):
    __tablename__ = "uba_profiles"

    user_id = Column(String(255), primary_key=True, index=True)
    peer_group = Column(String(128), nullable=True, index=True)
    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    event_count = Column(Integer, default=0)
    normal_login_hours = Column(JSON, default=list)  # e.g., list of frequent hours
    known_devices = Column(JSON, default=list)
    known_ips = Column(JSON, default=list)
    known_applications = Column(JSON, default=list)
    typical_resources = Column(JSON, default=list)
    avg_bytes_transferred = Column(Float, default=0.0)
    max_bytes_transferred = Column(Float, default=0.0)
    profile_metadata = Column(JSON, default=dict)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ------------------------------------------------------------
# 3. Identity & Authentication Tables
# ------------------------------------------------------------
class IdentityEventModel(Base):
    __tablename__ = "identity_events"

    authentication_event_id = Column(String(255), primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    account_id = Column(String(255), nullable=True, index=True)
    device_id = Column(String(255), nullable=True)
    source_ip = Column(String(64), nullable=True)
    location = Column(JSON, nullable=True)  # Lat, lon, country, etc.
    authentication_method = Column(String(128), nullable=False)
    authentication_status = Column(String(64), nullable=False, index=True)
    failure_reason = Column(String(255), nullable=True)
    two_factor_used = Column(String(64), nullable=True)
    two_factor_result = Column(String(64), nullable=True)
    session_id = Column(String(255), nullable=True)
    biometric_verification_result = Column(String(64), nullable=True)  # verified, failed, not_available (metadata only)
    device_fingerprint = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IdentityDetectionModel(Base):
    __tablename__ = "identity_detections"

    detection_id = Column(String(255), primary_key=True, index=True)
    event_id = Column(String(255), ForeignKey("identity_events.authentication_event_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(128), default="identity-authentication-agent", nullable=False)
    detector_type = Column(String(32), nullable=False, index=True)
    detector_id = Column(String(128), nullable=False)
    detector_version = Column(String(32), default="1.0.0")
    category = Column(String(128), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    reason_codes = Column(JSON, default=list)
    explanation = Column(Text, nullable=False)
    features_used = Column(JSON, default=dict)
    model_version = Column(String(64), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    processing_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ------------------------------------------------------------
# 4. Transaction Security Tables
# ------------------------------------------------------------
class TransactionEventModel(Base):
    __tablename__ = "transaction_events"

    transaction_id = Column(String(255), primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    account_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    device_id = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(16), nullable=False, default="USD")
    merchant_id = Column(String(255), nullable=True)
    merchant_category = Column(String(128), nullable=True)
    recipient_id = Column(String(255), nullable=True, index=True)
    source_account = Column(String(255), nullable=True)
    destination_account = Column(String(255), nullable=True)
    transaction_type = Column(String(64), nullable=False, default="PAYMENT")
    channel = Column(String(64), nullable=True)
    location = Column(JSON, nullable=True)
    status = Column(String(64), nullable=False, default="COMPLETED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TransactionDetectionModel(Base):
    __tablename__ = "transaction_detections"

    detection_id = Column(String(255), primary_key=True, index=True)
    event_id = Column(String(255), ForeignKey("transaction_events.transaction_id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(128), default="transaction-security-agent", nullable=False)
    detector_type = Column(String(32), nullable=False, index=True)
    detector_id = Column(String(128), nullable=False)
    detector_version = Column(String(32), default="1.0.0")
    category = Column(String(128), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    severity = Column(String(32), nullable=False)
    reason_codes = Column(JSON, default=list)
    explanation = Column(Text, nullable=False)
    features_used = Column(JSON, default=dict)
    model_version = Column(String(64), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    processing_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ============================================================
# EVIDENCE FUSION — CROSS-DOMAIN EVIDENCE FUSION TABLES
# ============================================================

class FusionResultModel(Base):
    """Stores unified cross-domain evidence fusion decisions."""
    __tablename__ = "fusion_results"

    fusion_id = Column(String(255), primary_key=True, index=True)
    fusion_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    primary_entity_id = Column(String(255), nullable=False, index=True)
    related_entities = Column(JSON, default=list)
    source_evidence_ids = Column(JSON, default=list)
    source_agents = Column(JSON, default=list)
    source_domains = Column(JSON, default=list)
    correlation_type = Column(String(64), nullable=False, index=True)
    temporal_window = Column(Float, default=1800.0)
    evidence_count = Column(Integer, default=0)
    unique_domain_count = Column(Integer, default=0)
    supporting_evidence_count = Column(Integer, default=0)
    conflicting_evidence_count = Column(Integer, default=0)
    redundant_evidence_count = Column(Integer, default=0)
    quality_score = Column(Float, nullable=False)
    fusion_score = Column(Float, nullable=False)
    unified_risk_score = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    risk_category = Column(String(32), nullable=False, index=True)  # LOW, MODERATE, HIGH, CRITICAL
    reason_codes = Column(JSON, default=list)
    explanation = Column(Text, nullable=False)
    fusion_algorithm = Column(String(128), default="weighted_contextual_baseline")
    fusion_version = Column(String(32), default="1.0.0")
    configuration_version = Column(String(32), default="1.0.0")
    previous_fusion_id = Column(String(255), nullable=True)  # Late evidence revision reference
    revision_number = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_fusion_risk_time", "unified_risk_score", "fusion_timestamp"),
        Index("idx_fusion_entity_cat", "primary_entity_id", "risk_category"),
    )


class FusionInputModel(Base):
    """Maps specific SecurityEvidence records participating in a fusion decision."""
    __tablename__ = "fusion_inputs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fusion_id = Column(String(255), ForeignKey("fusion_results.fusion_id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(128), nullable=False)
    domain = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False, default="SUPPORTING")  # SUPPORTING, CONFLICTING, REDUNDANT, EXCLUDED
    weight = Column(Float, default=1.0)
    contribution = Column(Float, default=0.0)


class EvidenceConflictModel(Base):
    """Stores conflicts identified during evidence correlation & fusion."""
    __tablename__ = "evidence_conflicts"

    conflict_id = Column(String(255), primary_key=True, index=True)
    fusion_id = Column(String(255), ForeignKey("fusion_results.fusion_id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_ids = Column(JSON, default=list)
    entities = Column(JSON, default=list)
    domains = Column(JSON, default=list)
    risk_difference = Column(Float, nullable=False)
    conflict_type = Column(String(64), nullable=False, index=True)  # RISK_DISAGREEMENT, CLASSIFICATION_DISAGREEMENT, etc.
    severity = Column(String(32), nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class FusionAuditModel(Base):
    """Audit record for reproducible evidence fusion decision lineage."""
    __tablename__ = "fusion_audit"

    audit_id = Column(String(255), primary_key=True, index=True)
    fusion_id = Column(String(255), ForeignKey("fusion_results.fusion_id", ondelete="CASCADE"), nullable=False, index=True)
    input_evidence_ids = Column(JSON, default=list)
    deduplicated_evidence_ids = Column(JSON, default=list)
    excluded_evidence_ids = Column(JSON, default=list)
    conflict_ids = Column(JSON, default=list)
    weights = Column(JSON, default=dict)
    quality_scores = Column(JSON, default=dict)
    correlation_results = Column(JSON, default=dict)
    risk_result = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RiskHistoryModel(Base):
    """Tracks entity unified cyber-risk evolution over time."""
    __tablename__ = "risk_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    risk_category = Column(String(32), nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    coverage = Column(Float, nullable=False)
    fusion_id = Column(String(255), ForeignKey("fusion_results.fusion_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EvidenceQualityModel(Base):
    """Stores evidence quality assessment ratings for individual SecurityEvidence."""
    __tablename__ = "evidence_quality"

    quality_id = Column(String(255), primary_key=True, index=True)
    evidence_id = Column(String(255), nullable=False, index=True)
    completeness_score = Column(Float, nullable=False)
    provenance_score = Column(Float, nullable=False)
    freshness_score = Column(Float, nullable=False)
    validity_score = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False, index=True)
    evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ============================================================
# ADAPTIVE MEMORY & GRAPH: ADAPTIVE MEMORY, TEMPORAL CORRELATION & ATTACK GRAPH
# ============================================================

class EvidenceMemoryModel(Base):
    """Storage model for Adaptive Evidence Memory entries (HOT, WARM, COLD)."""
    __tablename__ = "evidence_memory"

    memory_id = Column(String(255), primary_key=True, index=True)
    evidence_id = Column(String(255), nullable=False, index=True)
    entity_ids = Column(JSON, default=list)
    event_type = Column(String(64), nullable=False, index=True)
    domain = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    importance_score = Column(Float, nullable=False, index=True)
    memory_tier = Column(String(32), nullable=False, index=True)  # HOT, WARM, COLD
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    retrieval_count = Column(Integer, default=0)
    source_dataset = Column(String(128), nullable=True)
    agent_id = Column(String(128), nullable=True)
    detector_id = Column(String(128), nullable=True)
    model_version = Column(String(64), nullable=True)
    summary = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)

    __table_args__ = (
        Index("idx_memory_tier_importance", "memory_tier", "importance_score"),
        Index("idx_memory_domain_timestamp", "domain", "timestamp"),
    )


class MemoryAccessLogModel(Base):
    """Audit log tracking historical memory retrievals and queries."""
    __tablename__ = "memory_access_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    memory_id = Column(String(255), ForeignKey("evidence_memory.memory_id", ondelete="CASCADE"), nullable=False, index=True)
    query_id = Column(String(255), nullable=True)
    access_time = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    reason = Column(String(255), nullable=False)
    retrieval_rank = Column(Integer, default=1)
    requesting_component = Column(String(128), nullable=False)


class MemoryTransitionLogModel(Base):
    """Transition history for memory promotions and demotions across tiers."""
    __tablename__ = "memory_transitions"

    transition_id = Column(Integer, primary_key=True, autoincrement=True)
    memory_id = Column(String(255), ForeignKey("evidence_memory.memory_id", ondelete="CASCADE"), nullable=False, index=True)
    previous_tier = Column(String(32), nullable=False)
    new_tier = Column(String(32), nullable=False)
    reason = Column(String(255), nullable=False)
    importance_score = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class MemorySummaryModel(Base):
    """Summarized historical security evidence for memory compaction."""
    __tablename__ = "memory_summaries"

    summary_id = Column(String(255), primary_key=True, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    source_evidence_ids = Column(JSON, default=list)
    summary_version = Column(String(32), default="1.0.0")
    algorithm_version = Column(String(32), default="1.0.0")
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class GraphNodeModel(Base):
    """Nodes in the Attack Evidence Graph (User, Device, IP, Evidence, etc.)."""
    __tablename__ = "graph_nodes"

    node_id = Column(String(255), primary_key=True, index=True)
    node_type = Column(String(64), nullable=False, index=True)
    canonical_id = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    attributes = Column(JSON, default=dict)
    first_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class GraphEdgeModel(Base):
    """Edges linking nodes in the Attack Evidence Graph with relationship context."""
    __tablename__ = "graph_edges"

    edge_id = Column(String(255), primary_key=True, index=True)
    source_node_id = Column(String(255), ForeignKey("graph_nodes.node_id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id = Column(String(255), ForeignKey("graph_nodes.node_id", ondelete="CASCADE"), nullable=False, index=True)
    edge_type = Column(String(64), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=1.0)
    weight = Column(Float, nullable=False, default=1.0)
    first_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    evidence_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_edge_source_target", "source_node_id", "target_node_id"),
    )


class GraphEdgeEvidenceModel(Base):
    """Provenance mapping connecting Graph Edges to observed Security Evidence."""
    __tablename__ = "graph_edge_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    edge_id = Column(String(255), ForeignKey("graph_edges.edge_id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(String(255), nullable=False, index=True)
    confidence = Column(Float, default=1.0)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TemporalRelationshipModel(Base):
    """Pairwise temporal relationships between security evidence items."""
    __tablename__ = "temporal_relationships"

    relationship_id = Column(String(255), primary_key=True, index=True)
    source_evidence_id = Column(String(255), nullable=False, index=True)
    target_evidence_id = Column(String(255), nullable=False, index=True)
    relationship_type = Column(String(64), nullable=False, index=True)  # BEFORE, AFTER, WITHIN_WINDOW, BURST, etc.
    time_difference_seconds = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AttackChainCandidateModel(Base):
    """Detected attack-chain candidates across correlated temporal security events."""
    __tablename__ = "attack_chain_candidates"

    chain_id = Column(String(255), primary_key=True, index=True)
    pattern_id = Column(String(128), nullable=False, index=True)
    primary_entity_id = Column(String(255), nullable=False, index=True)
    stage_count = Column(Integer, nullable=False)
    matched_stage_count = Column(Integer, nullable=False)
    completeness = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(32), nullable=False, index=True)  # PARTIAL, CANDIDATE, INVALIDATED, EXPIRED
    explanation = Column(Text, nullable=False)
    pattern_version = Column(String(32), default="1.0.0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AttackChainStageModel(Base):
    """Specific stage in a candidate attack chain."""
    __tablename__ = "attack_chain_stages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chain_id = Column(String(255), ForeignKey("attack_chain_candidates.chain_id", ondelete="CASCADE"), nullable=False, index=True)
    stage_index = Column(Integer, nullable=False)
    evidence_id = Column(String(255), nullable=False, index=True)
    domain = Column(String(64), nullable=False)
    event_type = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    entity_id = Column(String(255), nullable=False)
    stage_confidence = Column(Float, nullable=False, default=1.0)


class TemporalFusionContextModel(Base):
    """Enriched historical, temporal, and attack graph context passed to Evidence Fusion Fusion."""
    __tablename__ = "temporal_fusion_contexts"

    context_id = Column(String(255), primary_key=True, index=True)
    current_evidence_id = Column(String(255), nullable=False, index=True)
    historical_evidence_ids = Column(JSON, default=list)
    graph_node_ids = Column(JSON, default=list)
    graph_edge_ids = Column(JSON, default=list)
    temporal_relationships = Column(JSON, default=list)
    attack_chain_candidates = Column(JSON, default=list)
    memory_coverage = Column(Float, nullable=False, default=1.0)
    context_completeness = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ============================================================
# RELIABILITY & TRUST: RELIABILITY, UNCERTAINTY, CALIBRATION, DRIFT & REPUTATION
# ============================================================

class AgentReliabilityModel(Base):
    """Stores contextual reliability records for agents, detectors, and domain pairs."""
    __tablename__ = "agent_reliability"

    reliability_id = Column(String(255), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    detector_id = Column(String(128), nullable=True, index=True)
    domain = Column(String(128), nullable=True, index=True)
    model_version = Column(String(64), nullable=False, default="1.0.0", index=True)
    evaluation_window_start = Column(DateTime(timezone=True), nullable=False, index=True)
    evaluation_window_end = Column(DateTime(timezone=True), nullable=False)
    sample_count = Column(Integer, default=0)
    precision = Column(Float, default=0.0)
    recall = Column(Float, default=0.0)
    f1_score = Column(Float, default=0.0)
    false_positive_rate = Column(Float, default=0.0)
    false_negative_rate = Column(Float, default=0.0)
    calibration_error = Column(Float, default=0.0)
    uncertainty_quality = Column(Float, default=0.0)
    stability_score = Column(Float, default=1.0)
    drift_score = Column(Float, default=0.0)
    reliability_score = Column(Float, nullable=False, default=0.5, index=True)
    confidence_interval_lower = Column(Float, default=0.0)
    confidence_interval_upper = Column(Float, default=1.0)
    evaluation_dataset = Column(String(128), nullable=True)
    evaluation_method = Column(String(128), default="empirical_validation")
    reliability_status = Column(String(64), default="WELL_SUPPORTED", index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    metadata_json = Column(JSON, default=dict)

    __table_args__ = (
        Index("idx_rel_agent_detector", "agent_id", "detector_id"),
        Index("idx_rel_agent_domain", "agent_id", "domain"),
        Index("idx_rel_created_ver", "model_version", "created_at"),
    )


class ReliabilityHistoryModel(Base):
    """Audit log tracking historical reliability updates and lineage."""
    __tablename__ = "reliability_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    reliability_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    detector_id = Column(String(128), nullable=True, index=True)
    domain = Column(String(128), nullable=True, index=True)
    model_version = Column(String(64), nullable=False, index=True)
    evaluation_window_start = Column(DateTime(timezone=True), nullable=False)
    evaluation_window_end = Column(DateTime(timezone=True), nullable=False)
    dataset = Column(String(128), nullable=True)
    previous_reliability_score = Column(Float, nullable=True)
    new_reliability_score = Column(Float, nullable=False)
    change_reason = Column(String(255), nullable=False)
    configuration_version = Column(String(32), default="1.0.0")
    triggering_evaluation_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    metadata_json = Column(JSON, default=dict)


class CalibrationRecordModel(Base):
    """Stores detector confidence calibration evaluation metrics and curves."""
    __tablename__ = "calibration_records"

    calibration_id = Column(String(255), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    detector_id = Column(String(128), nullable=True, index=True)
    model_version = Column(String(64), nullable=False, default="1.0.0", index=True)
    dataset = Column(String(128), nullable=True)
    evaluation_window_start = Column(DateTime(timezone=True), nullable=False)
    evaluation_window_end = Column(DateTime(timezone=True), nullable=False)
    sample_count = Column(Integer, default=0)
    ece = Column(Float, nullable=False, default=0.0)
    mce = Column(Float, nullable=False, default=0.0)
    brier_score = Column(Float, nullable=False, default=0.0)
    calibration_method = Column(String(64), default="temperature_scaling")
    pre_calibration_metric = Column(Float, nullable=True)
    post_calibration_metric = Column(Float, nullable=True)
    calibration_parameters = Column(JSON, default=dict)
    reliability_diagram_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class UncertaintyRecordModel(Base):
    """Stores calculated uncertainty details for individual evidence records."""
    __tablename__ = "uncertainty_records"

    uncertainty_id = Column(String(255), primary_key=True, index=True)
    evidence_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    detector_id = Column(String(128), nullable=True, index=True)
    uncertainty_score = Column(Float, nullable=False, index=True)
    uncertainty_type = Column(String(64), nullable=False, default="PROXY")
    source = Column(String(128), nullable=True)
    calculation_method = Column(String(128), default="entropy_disagreement_composite")
    contributing_factors = Column(JSON, default=dict)
    model_version = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class DriftRecordModel(Base):
    """Tracks feature, prediction, or performance distribution drift events."""
    __tablename__ = "drift_records"

    drift_id = Column(String(255), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    detector_id = Column(String(128), nullable=True, index=True)
    feature_or_signal = Column(String(128), nullable=False, index=True)
    reference_window_start = Column(DateTime(timezone=True), nullable=False)
    reference_window_end = Column(DateTime(timezone=True), nullable=False)
    current_window_start = Column(DateTime(timezone=True), nullable=False)
    current_window_end = Column(DateTime(timezone=True), nullable=False)
    drift_method = Column(String(64), nullable=False, default="PSI")
    drift_score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False, default=0.2)
    drift_detected = Column(String(8), nullable=False, default="false", index=True)
    severity = Column(String(32), default="LOW")
    model_version = Column(String(64), nullable=True)
    policy_action = Column(String(64), default="MONITOR")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ConflictRecordModel(Base):
    """Stores cross-agent evidence conflicts and diagnostic causes."""
    __tablename__ = "conflict_records"

    conflict_id = Column(String(255), primary_key=True, index=True)
    evidence_ids = Column(JSON, default=list)
    entity_id = Column(String(255), nullable=False, index=True)
    conflict_type = Column(String(64), nullable=False, index=True)
    risk_range = Column(JSON, default=dict)
    disagreement_score = Column(Float, nullable=False)
    likely_causes = Column(JSON, default=list)
    resolution_status = Column(String(64), default="OPEN", index=True)
    resolution_method = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AgentReputationModel(Base):
    """Tracks historical operational performance reputation per security agent."""
    __tablename__ = "agent_reputation"

    reputation_id = Column(String(255), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    reputation_score = Column(Float, nullable=False, default=0.8, index=True)
    historical_precision = Column(Float, default=0.8)
    historical_recall = Column(Float, default=0.8)
    stability_score = Column(Float, default=1.0)
    calibration_score = Column(Float, default=0.9)
    drift_score = Column(Float, default=0.0)
    coverage_score = Column(Float, default=1.0)
    last_evaluated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    evaluation_count = Column(Integer, default=0)
    confidence_interval_lower = Column(Float, default=0.7)
    confidence_interval_upper = Column(Float, default=0.9)
    reputation_version = Column(String(32), default="1.0.0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ReliabilityEvaluationModel(Base):
    """Stores full research evaluation runs, baseline comparisons, and ablations."""
    __tablename__ = "reliability_evaluations"

    evaluation_id = Column(String(255), primary_key=True, index=True)
    evaluation_type = Column(String(64), nullable=False, index=True)
    agent_id = Column(String(128), nullable=True, index=True)
    detector_id = Column(String(128), nullable=True, index=True)
    dataset = Column(String(128), nullable=True)
    dataset_version = Column(String(64), nullable=True)
    evaluation_window_start = Column(DateTime(timezone=True), nullable=True)
    evaluation_window_end = Column(DateTime(timezone=True), nullable=True)
    sample_count = Column(Integer, default=0)
    results_summary = Column(JSON, default=dict)
    configuration_version = Column(String(32), default="1.0.0")
    environment_info = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


# ============================================================
# ORCHESTRATION: ADAPTIVE AGENT SELECTION & EVIDENCE ORCHESTRATION
# ============================================================

class AgentRegistryModel(Base):
    """Registry maintaining metadata, status, health, and latency for security agents."""
    __tablename__ = "agent_registry"

    agent_id = Column(String(128), primary_key=True, index=True)
    agent_name = Column(String(255), nullable=False)
    domain = Column(String(128), nullable=False, index=True)
    capabilities = Column(JSON, default=list)
    supported_event_types = Column(JSON, default=list)
    supported_entity_types = Column(JSON, default=list)
    supported_attack_categories = Column(JSON, default=list)
    reliability_score = Column(Float, default=0.85)
    reliability_lower_bound = Column(Float, default=0.75)
    reliability_upper_bound = Column(Float, default=0.95)
    uncertainty_profile = Column(JSON, default=dict)
    average_latency_ms = Column(Float, default=150.0)
    p95_latency_ms = Column(Float, default=300.0)
    computational_cost = Column(Float, default=1.0)
    communication_cost = Column(Float, default=0.5)
    availability_status = Column(String(32), default="AVAILABLE", index=True)  # AVAILABLE, DEGRADED, UNAVAILABLE, DISABLED
    current_model_version = Column(String(64), default="1.0.0")
    drift_status = Column(String(32), default="STABLE")
    calibration_status = Column(String(32), default="CALIBRATED")
    enabled = Column(String(8), default="true", index=True)
    configuration_version = Column(String(32), default="1.0.0")
    last_updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_reg_domain_status", "domain", "availability_status"),
    )


class AgentCapabilityModel(Base):
    """Specific capabilities offered by individual security agents."""
    __tablename__ = "agent_capabilities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(128), ForeignKey("agent_registry.agent_id", ondelete="CASCADE"), nullable=False, index=True)
    capability_name = Column(String(128), nullable=False, index=True)
    target_entity_type = Column(String(64), nullable=True)
    supported_attack_stage = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)


class AgentSelectionContextModel(Base):
    """Context snapshot evaluated during dynamic agent selection decision."""
    __tablename__ = "agent_selection_context"

    context_id = Column(String(255), primary_key=True, index=True)
    event_id = Column(String(255), nullable=True, index=True)
    entity_ids = Column(JSON, default=list)
    event_type = Column(String(64), nullable=False, index=True)
    domains_observed = Column(JSON, default=list)
    current_risk = Column(Float, nullable=False, default=0.0)
    current_uncertainty = Column(Float, nullable=False, default=1.0)
    evidence_count = Column(Integer, default=0)
    evidence_quality = Column(Float, default=1.0)
    temporal_context = Column(JSON, default=dict)
    graph_context = Column(JSON, default=dict)
    attack_chain_candidates = Column(JSON, default=list)
    missing_domains = Column(JSON, default=list)
    missing_evidence_types = Column(JSON, default=list)
    previous_agent_calls = Column(JSON, default=list)
    latency_budget_ms = Column(Float, default=1000.0)
    resource_budget = Column(JSON, default=dict)
    policy_constraints = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AgentSelectionDecisionModel(Base):
    """Audit record for orchestrator agent selection decisions."""
    __tablename__ = "agent_selection_decisions"

    decision_id = Column(String(255), primary_key=True, index=True)
    context_id = Column(String(255), ForeignKey("agent_selection_context.context_id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_agents = Column(JSON, default=list)
    selected_agents = Column(JSON, default=list)
    selection_method = Column(String(64), nullable=False, default="full_adaptive_orchestration", index=True)
    selection_scores = Column(JSON, default=dict)
    constraints = Column(JSON, default=dict)
    expected_total_gain = Column(Float, default=0.0)
    expected_total_cost = Column(Float, default=0.0)
    expected_latency = Column(Float, default=0.0)
    stopping_reason = Column(String(128), default="STOPPING_CRITERIA_SATISFIED", index=True)
    configuration_version = Column(String(32), default="1.0.0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AgentSelectionCandidateModel(Base):
    """Detailed scores for all candidate agents evaluated during a selection decision."""
    __tablename__ = "agent_selection_candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_id = Column(String(255), ForeignKey("agent_selection_decisions.decision_id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    relevance_score = Column(Float, default=0.0)
    reliability_score = Column(Float, default=0.0)
    expected_gain = Column(Float, default=0.0)
    cost_score = Column(Float, default=0.0)
    latency_score = Column(Float, default=0.0)
    diversity_score = Column(Float, default=0.0)
    redundancy_penalty = Column(Float, default=0.0)
    final_score = Column(Float, nullable=False, index=True)
    selected = Column(String(8), default="false", index=True)


class AgentInvocationModel(Base):
    """Detailed audit record for executed agent invocations."""
    __tablename__ = "agent_invocations"

    invocation_id = Column(String(255), primary_key=True, index=True)
    context_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    detector_id = Column(String(128), nullable=True)
    model_version = Column(String(64), default="1.0.0")
    selection_round = Column(Integer, default=1, index=True)
    selection_score = Column(Float, default=0.0)
    expected_gain = Column(Float, default=0.0)
    actual_gain = Column(Float, default=0.0)
    reliability_at_selection = Column(Float, default=0.85)
    uncertainty_before = Column(Float, default=1.0)
    uncertainty_after = Column(Float, default=0.5)
    risk_before = Column(Float, default=0.0)
    risk_after = Column(Float, default=0.0)
    cost_estimate = Column(Float, default=1.0)
    actual_cost = Column(Float, default=1.0)
    latency_estimate = Column(Float, default=150.0)
    actual_latency = Column(Float, default=140.0)
    reason_codes = Column(JSON, default=list)
    invocation_status = Column(String(32), default="SUCCESS", index=True)  # SUCCESS, TIMEOUT, FAILED, SKIPPED
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class SelectionRoundModel(Base):
    """Sequential selection round history within a closed-loop orchestration session."""
    __tablename__ = "selection_rounds"

    round_id = Column(String(255), primary_key=True, index=True)
    context_id = Column(String(255), nullable=False, index=True)
    round_number = Column(Integer, nullable=False, index=True)
    selected_agent = Column(String(128), nullable=False, index=True)
    selection_score = Column(Float, nullable=False)
    expected_gain = Column(Float, default=0.0)
    actual_gain = Column(Float, default=0.0)
    cost = Column(Float, default=1.0)
    latency = Column(Float, default=150.0)
    resulting_uncertainty = Column(Float, default=0.5)
    resulting_risk = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class InformationGainEstimateModel(Base):
    """Historical uncertainty reduction statistics for expected gain estimation."""
    __tablename__ = "information_gain_estimates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(128), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    domain = Column(String(64), nullable=False, index=True)
    average_uncertainty_reduction = Column(Float, default=0.25)
    median_uncertainty_reduction = Column(Float, default=0.20)
    sample_count = Column(Integer, default=1)
    last_updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AgentCostProfileModel(Base):
    """Normalized computational, communication, and latency cost profiles."""
    __tablename__ = "agent_cost_profiles"

    profile_id = Column(String(128), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    cpu_cost = Column(Float, default=1.0)
    memory_cost = Column(Float, default=1.0)
    inference_cost = Column(Float, default=1.0)
    network_cost = Column(Float, default=1.0)
    communication_cost = Column(Float, default=1.0)
    latency_cost = Column(Float, default=1.0)
    storage_cost = Column(Float, default=1.0)
    total_normalized_cost = Column(Float, default=1.0)


class OrchestrationMetricsModel(Base):
    """Aggregated operational metrics for Orchestration orchestration performance."""
    __tablename__ = "orchestration_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    total_events = Column(Integer, default=0)
    total_agent_calls = Column(Integer, default=0)
    average_calls_per_event = Column(Float, default=0.0)
    average_latency_ms = Column(Float, default=0.0)
    total_cost_units = Column(Float, default=0.0)
    average_uncertainty_reduction = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SelectionHistoryModel(Base):
    """Audit dataset for research optimization and offline learning."""
    __tablename__ = "selection_history"

    history_id = Column(String(255), primary_key=True, index=True)
    context_id = Column(String(255), nullable=False, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    selection_score = Column(Float, nullable=False)
    expected_gain = Column(Float, default=0.0)
    actual_gain = Column(Float, default=0.0)
    gain_prediction_error = Column(Float, default=0.0)
    uncertainty_before = Column(Float, default=1.0)
    uncertainty_after = Column(Float, default=0.5)
    cost = Column(Float, default=1.0)
    latency = Column(Float, default=150.0)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


# =====================================================================
# ZERO-TRUST ENGINE: ZERO-TRUST POLICY DECISION & DYNAMIC SECURITY CONTEXT MODELS
# =====================================================================

class PolicyModel(Base):
    """Declarative Policy Definition."""
    __tablename__ = "policies"

    policy_id = Column(String(128), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(64), nullable=False, default="1.0.0")
    priority = Column(Integer, default=100, index=True)
    enabled = Column(String(16), default="true", index=True)
    scope = Column(String(128), default="GLOBAL")
    conditions = Column(JSON, nullable=False, default=dict)
    required_assurance = Column(String(64), default="AAL1")
    decision = Column(String(64), nullable=False, default="VERIFY")
    actions = Column(JSON, nullable=True, default=list)
    expiration = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    author = Column(String(128), default="SYSTEM")
    configuration_version = Column(String(64), default="1.0.0")


class PolicyVersionModel(Base):
    """Immutable version history for declarative policies."""
    __tablename__ = "policy_versions"

    version_id = Column(String(255), primary_key=True, index=True)
    policy_id = Column(String(128), nullable=False, index=True)
    version = Column(String(64), nullable=False, index=True)
    policy_snapshot = Column(JSON, nullable=False)
    change_reason = Column(Text, nullable=True)
    author = Column(String(128), default="SYSTEM")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class PolicyDecisionModel(Base):
    """Auditable Zero-Trust Policy Decision Record."""
    __tablename__ = "policy_decisions"

    decision_id = Column(String(255), primary_key=True, index=True)
    subject_id = Column(String(255), nullable=False, index=True)
    subject_type = Column(String(64), default="USER")
    resource_id = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(64), default="APPLICATION")
    requested_action = Column(String(64), nullable=False, default="READ")
    decision = Column(String(64), nullable=False, index=True)
    cyber_risk_score = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    uncertainty = Column(Float, default=0.0)
    evidence_ids = Column(JSON, nullable=True, default=list)
    applicable_policy_ids = Column(JSON, nullable=True, default=list)
    policy_versions = Column(JSON, nullable=True, default=dict)
    security_tags = Column(JSON, nullable=True, default=list)
    security_groups = Column(JSON, nullable=True, default=list)
    security_zone = Column(String(128), default="USER_ZONE", index=True)
    authentication_assurance = Column(String(64), default="AAL1")
    enforcement_mode = Column(String(64), default="DRY_RUN", index=True)
    enforcement_status = Column(String(64), default="SIMULATED", index=True)
    explanation = Column(Text, nullable=True)
    reasons = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class PolicyConflictModel(Base):
    """Log of policy conflict resolutions."""
    __tablename__ = "policy_conflicts"

    conflict_id = Column(String(255), primary_key=True, index=True)
    decision_id = Column(String(255), nullable=False, index=True)
    conflicting_policy_ids = Column(JSON, nullable=False)
    winning_policy_id = Column(String(128), nullable=False)
    winning_decision = Column(String(64), nullable=False)
    resolution_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class SecurityTagModel(Base):
    """Dynamic Security Tags with TTL expiration."""
    __tablename__ = "security_tags"

    tag_id = Column(String(255), primary_key=True, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    tag = Column(String(128), nullable=False, index=True)
    confidence = Column(Float, default=1.0)
    source_evidence_ids = Column(JSON, nullable=True, default=list)
    status = Column(String(64), default="ACTIVE", index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    policy_version = Column(String(64), default="1.0.0")


class SecurityTagHistoryModel(Base):
    """Historical audit log of security tag assignments and expirations."""
    __tablename__ = "security_tag_history"

    history_id = Column(String(255), primary_key=True, index=True)
    tag_id = Column(String(255), nullable=False, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    tag = Column(String(128), nullable=False)
    action = Column(String(64), nullable=False)  # ASSIGNED, EXPIRED, REVOKED, REFRESHED
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class SecurityGroupModel(Base):
    """Dynamic Security Group Definitions."""
    __tablename__ = "security_groups"

    group_id = Column(String(128), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    membership_rule = Column(JSON, nullable=True, default=dict)
    members = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    policy_version = Column(String(64), default="1.0.0")


class SecurityGroupMembershipModel(Base):
    """Entity memberships in dynamic security groups."""
    __tablename__ = "security_group_memberships"

    membership_id = Column(String(255), primary_key=True, index=True)
    group_id = Column(String(128), nullable=False, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    assigned_by = Column(String(128), default="POLICY_ENGINE")


class SecurityZoneModel(Base):
    """Logical Security Zones."""
    __tablename__ = "security_zones"

    zone_id = Column(String(128), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    risk_level = Column(String(64), default="MODERATE")
    allowed_actions = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MicroSegmentModel(Base):
    """Logical Micro-segmentation Rules."""
    __tablename__ = "micro_segments"

    segment_id = Column(String(128), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    zone = Column(String(128), nullable=False, index=True)
    subject_groups = Column(JSON, nullable=True, default=list)
    resource_groups = Column(JSON, nullable=True, default=list)
    allowed_actions = Column(JSON, nullable=True, default=list)
    denied_actions = Column(JSON, nullable=True, default=list)
    required_assurance = Column(String(64), default="AAL1")
    conditions = Column(JSON, nullable=True, default=dict)
    priority = Column(Integer, default=100)
    enabled = Column(String(16), default="true")
    policy_version = Column(String(64), default="1.0.0")


class EnforcementActionModel(Base):
    """Simulated or Controlled Enforcement Action Execution Record."""
    __tablename__ = "enforcement_actions"

    action_id = Column(String(255), primary_key=True, index=True)
    decision_id = Column(String(255), nullable=False, index=True)
    action_type = Column(String(64), nullable=False, index=True)
    target = Column(String(255), nullable=False)
    mode = Column(String(64), default="DRY_RUN", index=True)
    status = Column(String(64), default="SIMULATED", index=True)
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    applied_at = Column(DateTime(timezone=True), nullable=True)
    expiration = Column(DateTime(timezone=True), nullable=True)
    rollback_reference = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)


class VerificationEventModel(Base):
    """2FA and Biometric Step-Up Verification Events."""
    __tablename__ = "verification_events"

    event_id = Column(String(255), primary_key=True, index=True)
    subject_id = Column(String(255), nullable=False, index=True)
    verification_type = Column(String(64), nullable=False)  # 2FA, BIOMETRIC
    method = Column(String(64), default="TOTP")
    status = Column(String(64), nullable=False)  # SUCCESS, FAILED, TIMEOUT, CANCELLED
    assurance_level = Column(String(64), default="AAL2")
    evidence_reference = Column(String(255), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AuthenticationAssuranceModel(Base):
    """Subject Authentication Assurance Level Tracking."""
    __tablename__ = "authentication_assurance"

    subject_id = Column(String(255), primary_key=True, index=True)
    current_assurance_level = Column(String(64), default="AAL1")
    last_2fa_at = Column(DateTime(timezone=True), nullable=True)
    last_biometric_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PolicyOverrideModel(Base):
    """Human Analyst Overrides."""
    __tablename__ = "policy_overrides"

    override_id = Column(String(255), primary_key=True, index=True)
    decision_id = Column(String(255), nullable=False, index=True)
    analyst_id = Column(String(128), nullable=False)
    override_type = Column(String(64), nullable=False)  # ALLOW_OVERRIDE, DENY_OVERRIDE, REQUIRE_REVIEW
    previous_decision = Column(String(64), nullable=False)
    new_decision = Column(String(64), nullable=False)
    reason = Column(Text, nullable=False)
    evidence_ids = Column(JSON, nullable=True, default=list)
    policy_version = Column(String(64), default="1.0.0")
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class PolicyAuditLogModel(Base):
    """Comprehensive policy engine audit trial."""
    __tablename__ = "policy_audit_logs"

    audit_id = Column(String(255), primary_key=True, index=True)
    event_type = Column(String(128), nullable=False, index=True)
    decision_id = Column(String(255), nullable=True, index=True)
    policy_id = Column(String(128), nullable=True, index=True)
    subject_id = Column(String(255), nullable=True, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    details = Column(JSON, nullable=True, default=dict)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


# =====================================================================
# CLOSED-LOOP ADAPTATION: CLOSED-LOOP FEEDBACK & CONTINUOUS ADAPTATION MODELS
# =====================================================================

class SecurityDecisionOutcomeModel(Base):
    """Post-decision observed security outcomes."""
    __tablename__ = "security_decision_outcomes"

    outcome_id = Column(String(255), primary_key=True, index=True)
    decision_id = Column(String(255), nullable=False, index=True)
    subject_id = Column(String(255), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    original_decision = Column(String(64), nullable=False)
    observed_outcome = Column(String(64), nullable=False)  # ACCESS_LEGITIMATE, ATTACK_CONFIRMED, FALSE_ALARM, etc.
    validation_status = Column(String(64), nullable=False, default="PENDING", index=True)
    validation_source = Column(String(128), nullable=True)
    validation_confidence = Column(Float, default=1.0)
    analyst_id = Column(String(128), nullable=True)
    evidence_ids = Column(JSON, nullable=True, default=list)
    incident_id = Column(String(255), nullable=True)
    ground_truth_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(JSON, nullable=True, default=dict)

    __table_args__ = (
        Index("idx_outcomes_decision_status", "decision_id", "validation_status"),
    )


class FeedbackEventModel(Base):
    """Traceable feedback event emitted from internal/external sources."""
    __tablename__ = "feedback_events"

    feedback_id = Column(String(255), primary_key=True, index=True)
    source_type = Column(String(128), nullable=False, index=True)
    source_id = Column(String(255), nullable=False)
    event_type = Column(String(128), nullable=False)  # DETECTION_FEEDBACK, POLICY_FEEDBACK, etc.
    subject_id = Column(String(255), nullable=True, index=True)
    decision_id = Column(String(255), nullable=True, index=True)
    outcome_id = Column(String(255), nullable=True, index=True)
    agent_ids = Column(JSON, nullable=True, default=list)
    evidence_ids = Column(JSON, nullable=True, default=list)
    policy_ids = Column(JSON, nullable=True, default=list)
    validation_status = Column(String(64), nullable=False, default="PENDING", index=True)
    trust_level = Column(String(64), nullable=False, default="UNRESOLVED")
    quality_score = Column(Float, default=0.0)
    feedback_weight = Column(Float, default=1.0)
    details = Column(JSON, nullable=True, default=dict)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_feedback_source_status", "source_type", "validation_status"),
    )


class FeedbackValidationModel(Base):
    """Validation process metadata for feedback events."""
    __tablename__ = "feedback_validations"

    validation_id = Column(String(255), primary_key=True, index=True)
    feedback_id = Column(String(255), ForeignKey("feedback_events.feedback_id", ondelete="CASCADE"), nullable=False, index=True)
    validator_type = Column(String(64), nullable=False)  # ANALYST, GROUND_TRUTH, 2FA_VERIFICATION, EXPERIMENT
    validator_id = Column(String(255), nullable=False)
    validation_status = Column(String(64), nullable=False)
    trust_level = Column(String(64), nullable=False)
    quality_metrics = Column(JSON, nullable=True, default=dict)
    comments = Column(Text, nullable=True)
    validated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class FeedbackConflictModel(Base):
    """Conflicting feedback from multiple analysts or sources."""
    __tablename__ = "feedback_conflicts"

    conflict_id = Column(String(255), primary_key=True, index=True)
    decision_id = Column(String(255), nullable=False, index=True)
    feedback_ids = Column(JSON, nullable=False)  # List of conflicting feedback IDs
    source_views = Column(JSON, nullable=False)   # Summary of opinions
    status = Column(String(64), default="UNRESOLVED", index=True) # UNRESOLVED, RESOLVED
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class FeedbackRetractionModel(Base):
    """Historical record of retracted feedback."""
    __tablename__ = "feedback_retractions"

    retraction_id = Column(String(255), primary_key=True, index=True)
    original_feedback_id = Column(String(255), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    retracted_by = Column(String(128), nullable=False)
    affected_updates = Column(JSON, nullable=True, default=list)
    requires_rollback = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AdaptationProposalModel(Base):
    """Proposed configuration or weight updates calculated by adaptation engine."""
    __tablename__ = "adaptation_proposals"

    proposal_id = Column(String(255), primary_key=True, index=True)
    component = Column(String(128), nullable=False, index=True)  # AGENT_RELIABILITY, SELECTION_WEIGHT, POLICY_THRESHOLD, MODEL
    target_id = Column(String(255), nullable=False, index=True)
    parameter_name = Column(String(128), nullable=False)
    current_value = Column(Float, nullable=False)
    proposed_value = Column(Float, nullable=False)
    change_delta = Column(Float, nullable=False)
    adaptation_mode = Column(String(64), nullable=False, default="SHADOW")  # STATIC, ADVISORY, SHADOW, CONTROLLED, ACTIVE
    approval_status = Column(String(64), nullable=False, default="PROPOSED", index=True) # PROPOSED, AUTO_APPROVED, ANALYST_APPROVED, REJECTED, APPLIED
    trigger_reason = Column(Text, nullable=False)
    supporting_feedback_ids = Column(JSON, nullable=True, default=list)
    evaluation_results = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AdaptationRecordModel(Base):
    """Auditable log of applied or rejected adaptations."""
    __tablename__ = "adaptation_records"

    adaptation_id = Column(String(255), primary_key=True, index=True)
    proposal_id = Column(String(255), nullable=True, index=True)
    component = Column(String(128), nullable=False, index=True)
    parameter_name = Column(String(128), nullable=False)
    previous_value = Column(Float, nullable=False)
    proposed_value = Column(Float, nullable=False)
    applied_value = Column(Float, nullable=False)
    trigger = Column(Text, nullable=False)
    feedback_ids = Column(JSON, nullable=True, default=list)
    evaluation_id = Column(String(255), nullable=True)
    approval_status = Column(String(64), nullable=False)
    operator = Column(String(128), default="SYSTEM")
    configuration_version = Column(String(64), default="1.0.0")
    rollback_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    applied_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AdaptationReviewModel(Base):
    """Human-in-the-loop analyst review for policy & model adaptations."""
    __tablename__ = "adaptation_reviews"

    review_id = Column(String(255), primary_key=True, index=True)
    proposal_id = Column(String(255), ForeignKey("adaptation_proposals.proposal_id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer = Column(String(128), nullable=False)
    decision = Column(String(64), nullable=False)  # APPROVE, REJECT, REQUEST_MORE_EVIDENCE, DEFER
    reason = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class PolicyEffectivenessRecordModel(Base):
    """Aggregate policy effectiveness metrics."""
    __tablename__ = "policy_effectiveness"

    record_id = Column(String(255), primary_key=True, index=True)
    policy_id = Column(String(128), nullable=False, index=True)
    policy_version = Column(String(64), nullable=False, default="1.0.0")
    evaluation_window = Column(String(64), default="24h")
    decisions_count = Column(Integer, default=0)
    allowed_count = Column(Integer, default=0)
    monitored_count = Column(Integer, default=0)
    verification_count = Column(Integer, default=0)
    quarantined_count = Column(Integer, default=0)
    blocked_count = Column(Integer, default=0)
    false_block_count = Column(Integer, default=0)
    missed_attack_count = Column(Integer, default=0)
    policy_violation_count = Column(Integer, default=0)
    legitimate_access_rate = Column(Float, default=1.0)
    security_effectiveness = Column(Float, default=1.0)
    decision_latency_ms = Column(Float, default=0.0)
    review_required = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AgentPerformanceUpdateModel(Base):
    """Validated updates to Reliability & Trust agent performance & reputation."""
    __tablename__ = "agent_performance_updates"

    update_id = Column(String(255), primary_key=True, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    detector_id = Column(String(128), nullable=True)
    sample_count = Column(Integer, default=0)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    fpr = Column(Float, nullable=False)
    fnr = Column(Float, nullable=False)
    ece = Column(Float, nullable=False)
    brier_score = Column(Float, nullable=False)
    reputation_score = Column(Float, nullable=False)
    confidence_interval_low = Column(Float, default=0.0)
    confidence_interval_high = Column(Float, default=1.0)
    feedback_event_ids = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class SelectionFeedbackModel(Base):
    """Orchestration agent-selection expected vs actual information gain tracking."""
    __tablename__ = "selection_feedback"

    selection_id = Column(String(255), primary_key=True, index=True)
    decision_id = Column(String(255), nullable=False, index=True)
    selected_agent_ids = Column(JSON, nullable=False)
    expected_info_gain = Column(Float, nullable=False)
    actual_info_gain = Column(Float, nullable=True)
    gain_prediction_error = Column(Float, nullable=True)
    validation_status = Column(String(64), default="PENDING", index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ModelVersionModel(Base):
    """Model Registry tracking Champion & Challenger model versions."""
    __tablename__ = "model_versions"

    version_id = Column(String(255), primary_key=True, index=True)
    model_id = Column(String(128), nullable=False, index=True)
    agent_id = Column(String(128), nullable=False, index=True)
    detector_id = Column(String(128), nullable=True)
    version = Column(String(64), nullable=False)
    parent_version = Column(String(64), nullable=True)
    training_dataset = Column(String(255), nullable=True)
    dataset_version = Column(String(64), nullable=True)
    feature_schema_version = Column(String(64), default="1.0.0")
    training_config_version = Column(String(64), default="1.0.0")
    calibration_version = Column(String(64), default="1.0.0")
    metrics = Column(JSON, nullable=True, default=dict)
    robustness_metrics = Column(JSON, nullable=True, default=dict)
    status = Column(String(64), nullable=False, default="CANDIDATE", index=True)
    is_champion = Column(Integer, default=0, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    retired_at = Column(DateTime(timezone=True), nullable=True)


class ModelEvaluationModel(Base):
    """Champion vs Challenger shadow evaluation records."""
    __tablename__ = "model_evaluations"

    evaluation_id = Column(String(255), primary_key=True, index=True)
    champion_version_id = Column(String(255), nullable=False)
    challenger_version_id = Column(String(255), nullable=False)
    dataset_version = Column(String(64), nullable=True)
    sample_count = Column(Integer, default=0)
    champion_metrics = Column(JSON, nullable=False)
    challenger_metrics = Column(JSON, nullable=False)
    comparison_summary = Column(JSON, nullable=False)
    recommendation = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ModelPromotionModel(Base):
    """Model promotion audit log."""
    __tablename__ = "model_promotions"

    promotion_id = Column(String(255), primary_key=True, index=True)
    model_id = Column(String(128), nullable=False, index=True)
    promoted_version_id = Column(String(255), nullable=False)
    demoted_version_id = Column(String(255), nullable=True)
    promoted_by = Column(String(128), nullable=False)
    reason = Column(Text, nullable=False)
    evaluation_id = Column(String(255), nullable=True)
    promoted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ModelRollbackModel(Base):
    """Model rollback audit log."""
    __tablename__ = "model_rollbacks"

    rollback_id = Column(String(255), primary_key=True, index=True)
    model_id = Column(String(128), nullable=False, index=True)
    from_version_id = Column(String(255), nullable=False)
    to_version_id = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    operator = Column(String(128), nullable=False)
    rolled_back_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class DriftResponseModel(Base):
    """Decided response action to detected concept drift."""
    __tablename__ = "drift_responses"

    response_id = Column(String(255), primary_key=True, index=True)
    drift_event_id = Column(String(255), nullable=False, index=True)
    detector_id = Column(String(128), nullable=False)
    drift_score = Column(Float, nullable=False)
    chosen_action = Column(String(64), nullable=False, index=True)
    justification = Column(Text, nullable=False)
    status = Column(String(64), default="EXECUTED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class DecisionReplayModel(Base):
    """Historical decision replay runs."""
    __tablename__ = "decision_replays"

    replay_id = Column(String(255), primary_key=True, index=True)
    target_decision_id = Column(String(255), nullable=False, index=True)
    replayed_at_time = Column(DateTime(timezone=True), nullable=False)
    original_decision = Column(String(64), nullable=False)
    replayed_decision = Column(String(64), nullable=False)
    matches_original = Column(Integer, nullable=False)
    differences = Column(JSON, nullable=True, default=dict)
    reconstruction_metadata = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class CounterfactualRunModel(Base):
    """Counterfactual scenario simulation runs."""
    __tablename__ = "counterfactual_runs"

    run_id = Column(String(255), primary_key=True, index=True)
    scenario_name = Column(String(255), nullable=False, index=True)
    decision_ids = Column(JSON, nullable=False)
    parameters_modified = Column(JSON, nullable=False)
    original_outcomes_summary = Column(JSON, nullable=False)
    simulated_outcomes_summary = Column(JSON, nullable=False)
    impact_analysis = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AdaptationStabilityModel(Base):
    """System adaptation stability metrics tracking."""
    __tablename__ = "adaptation_stability"

    metric_id = Column(String(255), primary_key=True, index=True)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), nullable=False)
    policy_churn = Column(Float, nullable=False)
    selection_churn = Column(Float, nullable=False)
    threshold_variance = Column(Float, nullable=False)
    reliability_volatility = Column(Float, nullable=False)
    rollback_frequency = Column(Float, nullable=False)
    adaptation_frequency = Column(Float, nullable=False)
    is_stable = Column(Integer, default=1, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class LearningDatasetVersionModel(Base):
    """Dataset versioning for training & validation."""
    __tablename__ = "learning_dataset_versions"

    dataset_id = Column(String(255), primary_key=True, index=True)
    dataset_version = Column(String(64), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    collection_start = Column(DateTime(timezone=True), nullable=False)
    collection_end = Column(DateTime(timezone=True), nullable=False)
    sample_count = Column(Integer, nullable=False)
    label_version = Column(String(64), default="1.0.0")
    validation_method = Column(String(128), default="TIME_AWARE_SPLIT")
    feature_schema = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


# =====================================================================
# EVALUATION: EVALUATION, SCALABILITY & RESEARCH REPORTING MODELS
# =====================================================================

class EvaluationDatasetModel(Base):
    """Dataset registry entry for reproducible research evaluation."""
    __tablename__ = "evaluation_datasets"

    dataset_id = Column(String(255), primary_key=True, index=True)
    dataset_name = Column(String(255), nullable=False, index=True)
    version = Column(String(64), nullable=False)
    domain = Column(String(64), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    license = Column(String(128), default="OPEN_RESEARCH")
    collection_period = Column(String(128), nullable=True)
    sample_count = Column(Integer, nullable=False)
    split_strategy = Column(String(64), default="TIME_AWARE_SPLIT")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    metadata_json = Column(JSON, nullable=True, default=dict)


class ExperimentConfigModel(Base):
    """Configuration definition for reproducible research experiments."""
    __tablename__ = "experiment_configs"

    experiment_id = Column(String(255), primary_key=True, index=True)
    experiment_name = Column(String(255), nullable=False, index=True)
    dataset_id = Column(String(255), nullable=False, index=True)
    dataset_version = Column(String(64), nullable=False)
    workload_size = Column(Integer, nullable=False)
    seed = Column(Integer, default=42)
    system_version = Column(String(64), default="1.0.0")
    agent_versions = Column(JSON, nullable=True, default=dict)
    model_versions = Column(JSON, nullable=True, default=dict)
    policy_versions = Column(JSON, nullable=True, default=dict)
    configuration_version = Column(String(64), default="1.0.0")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ExperimentRunModel(Base):
    """Execution state and outcome of an experiment run."""
    __tablename__ = "experiment_runs"

    run_id = Column(String(255), primary_key=True, index=True)
    experiment_id = Column(String(255), ForeignKey("experiment_configs.experiment_id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(64), nullable=False, default="QUEUED", index=True) # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    environment = Column(JSON, nullable=True, default=dict)
    host_information = Column(JSON, nullable=True, default=dict)
    metrics_summary = Column(JSON, nullable=True, default=dict)
    artifacts_path = Column(String(512), nullable=True)
    error_log = Column(Text, nullable=True)


class MetricResultModel(Base):
    """Empirical quantitative metric results for evaluation runs."""
    __tablename__ = "metric_results"

    metric_id = Column(String(255), primary_key=True, index=True)
    run_id = Column(String(255), ForeignKey("experiment_runs.run_id", ondelete="CASCADE"), nullable=False, index=True)
    domain = Column(String(64), nullable=False, index=True)
    metric_name = Column(String(128), nullable=False, index=True)
    metric_value = Column(Float, nullable=True)
    metric_unit = Column(String(32), nullable=False)
    status = Column(String(64), nullable=False, default="COMPLETED") # COMPLETED, NOT_RUN, FAILED, PARTIAL, NOT_AVAILABLE
    formula_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class BaselineResultModel(Base):
    """Comparative results for Baseline architectures (Baselines 1-8 / A-F)."""
    __tablename__ = "baseline_results"

    baseline_id = Column(String(255), primary_key=True, index=True)
    run_id = Column(String(255), nullable=False, index=True)
    baseline_name = Column(String(128), nullable=False, index=True)
    f1_score = Column(Float, nullable=True)
    fpr = Column(Float, nullable=True)
    fnr = Column(Float, nullable=True)
    ece = Column(Float, nullable=True)
    brier_score = Column(Float, nullable=True)
    agent_invocations = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AblationResultModel(Base):
    """Component ablation study results (A1 to A12)."""
    __tablename__ = "ablation_results"

    ablation_id = Column(String(255), primary_key=True, index=True)
    run_id = Column(String(255), nullable=False, index=True)
    ablation_name = Column(String(128), nullable=False, index=True)
    removed_component = Column(String(128), nullable=False)
    f1_score = Column(Float, nullable=True)
    ece = Column(Float, nullable=True)
    policy_churn = Column(Float, nullable=True)
    stability_status = Column(String(64), nullable=False)
    delta_from_full_system = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ScalabilityResultModel(Base):
    """Workload scalability benchmark measurements (10K to 5M events)."""
    __tablename__ = "scalability_results"

    result_id = Column(String(255), primary_key=True, index=True)
    run_id = Column(String(255), nullable=False, index=True)
    workload_size = Column(Integer, nullable=False, index=True) # 10K, 50K, 100K, 500K, 1M, 5M
    events_per_sec = Column(Float, nullable=False)
    p50_latency_ms = Column(Float, nullable=False)
    p95_latency_ms = Column(Float, nullable=False)
    p99_latency_ms = Column(Float, nullable=False)
    cpu_percent = Column(Float, nullable=False)
    ram_mb = Column(Float, nullable=False)
    storage_mb = Column(Float, nullable=False)
    agent_calls = Column(Integer, nullable=False)
    scaling_efficiency = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class SegmentationResultModel(Base):
    """Dynamic micro-segmentation evaluation results."""
    __tablename__ = "segmentation_results"

    result_id = Column(String(255), primary_key=True, index=True)
    run_id = Column(String(255), nullable=False, index=True)
    segmentation_mode = Column(String(64), nullable=False) # NO_SEGMENTATION, STATIC_SEGMENTATION, DYNAMIC_SEGMENTATION
    blast_radius_score = Column(Float, nullable=False)
    lateral_reachability_nodes = Column(Integer, nullable=False)
    containment_time_ms = Column(Float, nullable=True)
    false_isolation_rate = Column(Float, nullable=False)
    policy_violation_rate = Column(Float, nullable=False)
    enforcement_latency_ms = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class EvaluationReportModel(Base):
    """Generated research reports and exports."""
    __tablename__ = "evaluation_reports"

    report_id = Column(String(255), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    experiment_id = Column(String(255), nullable=False, index=True)
    format = Column(String(32), nullable=False) # PDF, JSON, CSV
    status = Column(String(64), default="QUEUED", index=True) # QUEUED, GENERATING, COMPLETED, FAILED
    artifact_path = Column(String(512), nullable=True)
    summary_metrics = Column(JSON, nullable=True, default=dict)
    limitations = Column(JSON, nullable=True, default=list)
    reproducibility_checksum = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)


class ResearchValidationRunModel(Base):
    """Research Validation research result validation run."""
    __tablename__ = "research_validation_runs"

    validation_id = Column(String(255), primary_key=True, index=True)
    experiment_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=False, index=True)
    dataset_id = Column(String(128), nullable=False, index=True)
    dataset_version = Column(String(64), nullable=False)
    config_hash = Column(String(128), nullable=False)
    model_versions = Column(JSON, default=dict)
    code_version = Column(String(64), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    random_seed = Column(Integer, nullable=False)
    environment_id = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, index=True) # VALID, INVALID, INCOMPLETE, INCONSISTENT, NOT_AVAILABLE
    issues = Column(JSON, default=list)
    validated_metrics = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class StatisticalResultModel(Base):
    """Statistical validation & confidence interval results."""
    __tablename__ = "statistical_results"

    stat_id = Column(String(255), primary_key=True, index=True)
    experiment_id = Column(String(255), nullable=False, index=True)
    metric = Column(String(128), nullable=False, index=True)
    sample_size = Column(Integer, nullable=False)
    mean = Column(Float, nullable=False)
    median = Column(Float, nullable=False)
    std_dev = Column(Float, nullable=False)
    variance = Column(Float, nullable=False)
    min_val = Column(Float, nullable=False)
    max_val = Column(Float, nullable=False)
    iqr = Column(Float, nullable=False)
    p50 = Column(Float, nullable=False)
    p90 = Column(Float, nullable=False)
    p95 = Column(Float, nullable=False)
    p99 = Column(Float, nullable=False)
    confidence_level = Column(Float, default=0.95)
    ci_lower = Column(Float, nullable=True)
    ci_upper = Column(Float, nullable=True)
    ci_method = Column(String(64), nullable=True)
    paired_test_results = Column(JSON, default=dict)
    effect_sizes = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class SensitivityRunModel(Base):
    """Sensitivity analysis evaluation results."""
    __tablename__ = "sensitivity_runs"

    sensitivity_id = Column(String(255), primary_key=True, index=True)
    experiment_id = Column(String(255), nullable=False, index=True)
    parameter_name = Column(String(128), nullable=False, index=True)
    original_value = Column(Float, nullable=False)
    tested_value = Column(Float, nullable=False)
    metric = Column(String(128), nullable=False, index=True)
    baseline_result = Column(Float, nullable=False)
    perturbed_result = Column(Float, nullable=False)
    absolute_change = Column(Float, nullable=False)
    relative_change = Column(Float, nullable=False)
    category = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class RobustnessRunModel(Base):
    """Robustness & perturbation validation results."""
    __tablename__ = "robustness_runs"

    robustness_id = Column(String(255), primary_key=True, index=True)
    experiment_id = Column(String(255), nullable=False, index=True)
    perturbation_type = Column(String(128), nullable=False, index=True)
    metric = Column(String(128), nullable=False, index=True)
    baseline_metric = Column(Float, nullable=False)
    perturbed_metric = Column(Float, nullable=False)
    absolute_change = Column(Float, nullable=False)
    relative_change = Column(Float, nullable=False)
    degradation_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class HypothesisResultModel(Base):
    """Hypothesis assessment results (H1-H9)."""
    __tablename__ = "hypothesis_results"

    hypothesis_id = Column(String(32), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    supporting_experiments = Column(JSON, default=list)
    measured_metrics = Column(JSON, default=dict)
    effect_size = Column(Float, nullable=True)
    effect_size_summary = Column(String(255), nullable=True)
    p_value = Column(Float, nullable=True)
    status = Column(String(64), nullable=False, index=True)
    reasoning = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)



class ResearchClaimModel(Base):
    """Research claim validation and evidence linkage."""
    __tablename__ = "research_claims"

    claim_id = Column(String(255), primary_key=True, index=True)
    claim_text = Column(Text, nullable=False)
    category = Column(String(64), nullable=False)
    supporting_experiments = Column(JSON, default=list)
    status = Column(String(64), nullable=False, index=True)
    evidence_details = Column(JSON, default=dict)
    limitations = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ReproducibilityRunModel(Base):
    """Reproducibility verification run result."""
    __tablename__ = "reproducibility_runs"

    reproducibility_id = Column(String(255), primary_key=True, index=True)
    experiment_id = Column(String(255), nullable=False, index=True)
    status = Column(String(64), nullable=False, index=True)
    config_hash = Column(String(128), nullable=False)
    environment_hash = Column(String(128), nullable=False)
    dataset_checksums = Column(JSON, default=dict)
    diff_metrics = Column(JSON, default=dict)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ResearchAuditResultModel(Base):
    """Security and ethics audit result."""
    __tablename__ = "research_audit_results"

    audit_id = Column(String(255), primary_key=True, index=True)
    audit_type = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False, index=True)
    findings = Column(JSON, default=list)
    checked_items = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class PublicationArtifactModel(Base):
    """Publication artifacts (manuscript, bib, figures, tables)."""
    __tablename__ = "publication_artifacts"

    artifact_id = Column(String(255), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(64), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    checksum = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ZeroDayCandidateModel(Base):
    """Zero-Day attack candidates detected by HACTM."""
    __tablename__ = "zero_day_candidates"

    candidate_id = Column(String(255), primary_key=True, index=True)
    event_id = Column(String(255), nullable=False, index=True)
    candidate_score = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    novelty_indicator = Column(Float, nullable=False)
    temporal_deviation = Column(Float, nullable=False)
    contextual_deviation = Column(Float, nullable=False)
    agent_disagreement = Column(Float, nullable=False)
    zero_day_category = Column(String(128), nullable=False)
    escalation_action = Column(String(64), nullable=False)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ZeroDayEvaluationRunModel(Base):
    """Zero-Day Evaluation protocol run execution result."""
    __tablename__ = "zero_day_evaluation_runs"

    run_id = Column(String(255), primary_key=True, index=True)
    experiment_id = Column(String(255), nullable=False, index=True)
    protocol_type = Column(String(64), nullable=False, index=True)  # standard, temporal, family_holdout, cross_dataset
    model_name = Column(String(128), nullable=False)
    dataset_name = Column(String(128), nullable=False)
    metrics = Column(JSON, default=dict)
    leakage_passed = Column(Integer, default=1)
    status = Column(String(64), nullable=False, index=True)
    manifest = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class LeakageCheckModel(Base):
    """Leakage audit record."""
    __tablename__ = "leakage_checks"

    check_id = Column(String(255), primary_key=True, index=True)
    experiment_id = Column(String(255), nullable=False, index=True)
    status = Column(String(64), nullable=False, index=True)
    duplicate_overlap = Column(Integer, default=0)
    temporal_leakage = Column(Integer, default=0)
    entity_leakage = Column(Integer, default=0)
    label_leakage = Column(Integer, default=0)
    preprocessing_leakage = Column(Integer, default=0)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class ResourceMeasurementModel(Base):
    """Resource footprint, latency, and throughput measurement record."""
    __tablename__ = "resource_measurements"

    measurement_id = Column(String(255), primary_key=True, index=True)
    model_name = Column(String(128), nullable=False, index=True)
    cpu_percent = Column(Float, nullable=False)
    memory_mb = Column(Float, nullable=False)
    model_size_mb = Column(Float, nullable=False)
    inference_latency_ms = Column(Float, nullable=False)
    throughput_events_sec = Column(Float, nullable=False)
    p50_latency_ms = Column(Float, nullable=False)
    p95_latency_ms = Column(Float, nullable=False)
    p99_latency_ms = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class WorkOrderModel(Base):
    """Governed Investigation Work Order model."""
    __tablename__ = "work_orders"

    work_order_id = Column(String(255), primary_key=True, index=True)
    investigation_id = Column(String(255), nullable=False, index=True)
    parent_incident_id = Column(String(255), nullable=False, index=True)
    objective = Column(Text, nullable=False)
    scope = Column(JSON, default=dict)
    required_questions = Column(JSON, default=list)
    success_criteria = Column(JSON, default=list)
    permitted_tools = Column(JSON, default=list)
    data_sources = Column(JSON, default=list)
    forbidden_actions = Column(JSON, default=list)
    resource_limits = Column(JSON, default=dict)
    required_evidence = Column(JSON, default=list)
    deadline = Column(DateTime(timezone=True), nullable=True)
    assigned_agent_id = Column(String(128), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="ASSIGNED", index=True)  # CREATED, ASSIGNED, IN_PROGRESS, COMPLETED, FAILED, CANCELLED
    evidence_pack = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ApprovalRequestModel(Base):
    """Human Response & Policy Approval Request Gate table."""
    __tablename__ = "approval_requests"

    request_id = Column(String(255), primary_key=True, index=True)
    incident_id = Column(String(255), nullable=False, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    policy_id = Column(String(255), nullable=True)
    action_type = Column(String(64), nullable=False, index=True)  # ACCOUNT_SUSPENSION, NETWORK_ISOLATION, BLOCK_CRITICAL_RESOURCE, DISRUPTIVE_CHANGE, etc.
    proposed_action = Column(String(255), nullable=False)
    risk_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=False)
    is_high_impact = Column(Integer, default=1, nullable=False)
    justification = Column(Text, nullable=False)
    expected_impact = Column(Text, nullable=False)
    alternatives = Column(JSON, default=list)
    supporting_evidence = Column(JSON, default=list)
    status = Column(String(32), nullable=False, default="PENDING_APPROVAL", index=True)  # PENDING_APPROVAL, APPROVED, REJECTED, MORE_EVIDENCE_REQUESTED, EXPIRED, EXECUTED, FAILED
    approver_identity = Column(String(255), nullable=True)
    approver_role = Column(String(64), nullable=True)
    approval_notes = Column(Text, nullable=True)
    approval_timestamp = Column(DateTime(timezone=True), nullable=True)
    execution_status = Column(String(32), nullable=True)  # PENDING, SIMULATED, EXECUTED, FAILED, REVERTED
    execution_result = Column(JSON, nullable=True)
    verification_status = Column(String(32), nullable=True)  # UNVERIFIED, VERIFIED, FAILED
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AuditEventModel(Base):
    """Persistent, tamper-evident append-only audit trail with hash chain verification."""
    __tablename__ = "audit_trail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(255), unique=True, index=True)

    incident_id = Column(String(255), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, default=lambda: datetime.now(timezone.utc))
    actor_id = Column(String(128), nullable=False, index=True)
    actor_type = Column(String(64), nullable=False)  # AGENT, SYSTEM, HUMAN_ANALYST, HUMAN_ADMIN
    event_type = Column(String(128), nullable=False, index=True)
    evidence_references = Column(JSON, default=list)
    work_order_references = Column(JSON, default=list)
    previous_state = Column(JSON, nullable=True)
    resulting_state = Column(JSON, nullable=True)
    decision_rationale = Column(Text, nullable=True)
    proposed_or_executed_action = Column(String(255), nullable=True)
    approver_identity = Column(String(255), nullable=True)
    approval_timestamp = Column(DateTime(timezone=True), nullable=True)
    execution_status = Column(String(64), nullable=True)
    failure_reason = Column(Text, nullable=True)
    model_version = Column(String(64), default="1.0.0")
    policy_version = Column(String(64), default="1.0.0")
    schema_version = Column(String(32), default="1.0.0")
    prev_hash = Column(String(128), nullable=False)
    record_hash = Column(String(128), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))












