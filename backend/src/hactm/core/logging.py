"""
Logging infrastructure with sensitive data redaction.
Ensures passwords, tokens, and secret keys are never exposed in log outputs.
"""

import logging
import re
import sys
from typing import Any

# Patterns matching sensitive keys in dictionaries or strings
SENSITIVE_PATTERNS = [
    re.compile(r'(?i)(password|passwd|token|api[_-]?key|secret|authorization|bearer)\s*[:=]\s*["\']?([^"\'\s,;]+)["\']?'),
    re.compile(r'(?i)"(password|passwd|token|api[_-]?key|secret|authorization)":\s*"[^"]+"'),
]


def redact_sensitive_text(text: str) -> str:
    """Masks secret tokens, passwords, and API keys from a given log string."""
    redacted = text
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub(r'\1: [REDACTED]', redacted)
    return redacted


class RedactingFormatter(logging.Formatter):
    """Custom logging formatter that strips sensitive patterns before emission."""
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return redact_sensitive_text(original)


def setup_logger(name: str = "hactm", level: str = "INFO") -> logging.Logger:
    """Configures and returns a centralized HACTM logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = RedactingFormatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        logger.propagate = False
    return logger


logger = setup_logger()
