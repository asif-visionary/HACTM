"""
Domain exceptions for the HACTM platform.
"""

from typing import Any, Dict, Optional


class HACTMError(Exception):
    """Base exception for all HACTM platform errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class HACTMValidationError(HACTMError):
    """Raised when record fails schema or semantic validation."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class QuarantineRecordError(HACTMError):
    """Raised when an ingested record must be isolated in quarantine."""
    def __init__(self, message: str, raw_record: Any, row_num: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        d = details or {}
        d["raw_record"] = raw_record
        d["row_num"] = row_num
        super().__init__(message=message, code="QUARANTINE_ERROR", details=d)
        self.raw_record = raw_record
        self.row_num = row_num


class EntityResolutionError(HACTMError):
    """Raised when entity identification fails deterministically."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="ENTITY_RESOLUTION_ERROR", details=details)


class NotFoundError(HACTMError):
    """Raised when requested resource does not exist."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="NOT_FOUND", details=details)


class DuplicateError(HACTMError):
    """Raised when duplicate entity or event is encountered in strict mode."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code="DUPLICATE_ERROR", details=details)
