"""
Application Configuration for HACTM.
Uses pydantic-settings to allow environment overrides while maintaining strong defaults.
"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
from hactm.core.constants import IngestionPolicy


class Settings(BaseSettings):
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent.parent / "data")
    QUARANTINE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed" / "quarantine"
    )

    # Database
    # Default is SQLite file inside DATA_DIR; structured to allow PostgreSQL via DATABASE_URL
    DATABASE_URL: str = "sqlite:///./data/hactm.db"

    # Ingestion Defaults
    DEFAULT_BATCH_SIZE: int = 1000
    DEFAULT_INGESTION_POLICY: IngestionPolicy = IngestionPolicy.QUARANTINE_INVALID

    # Environment & API
    ENVIRONMENT: str = "Development / Research"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    # AbuseIPDB & Threat Intelligence Configuration
    ABUSEIPDB_API_KEY: str = Field(default="", validation_alias="ABUSEIPDB_API_KEY")
    ABUSEIPDB_BASE_URL: str = Field(default="https://api.abuseipdb.com/api/v2", validation_alias="ABUSEIPDB_BASE_URL")
    ABUSEIPDB_API_TIMEOUT: int = Field(default=10, validation_alias="ABUSEIPDB_API_TIMEOUT")
    ABUSEIPDB_MAX_AGE_DAYS: int = Field(default=30, validation_alias="ABUSEIPDB_MAX_AGE_DAYS")
    ABUSEIPDB_RELIABILITY: float = Field(default=0.85, validation_alias="ABUSEIPDB_RELIABILITY")
    ABUSEIPDB_ENABLED: bool = Field(default=True, validation_alias="ABUSEIPDB_ENABLED")

    class Config:
        env_prefix = "HACTM_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
