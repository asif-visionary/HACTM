"""
Data Normalization Pipeline for HACTM.
Applies deterministic transformations:
- Timestamps -> UTC ISO 8601
- IP addresses -> IPv4 / IPv6 canonical format
- Domain / URL / Email -> Lowercase, trimmed, NO speculative typo corrections
- Null-like values -> None
- Whitespace stripping
"""

import ipaddress
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse
from dateutil import parser as date_parser

NULL_LIKE_STRINGS = {
    "", "none", "null", "nil", "n/a", "na", "-", "--", "undefined"
}


def normalize_null_value(val: Any) -> Any:
    """Converts null-like strings and placeholders to Python None."""
    if val is None:
        return None
    if isinstance(val, str):
        cleaned = val.strip()
        if cleaned.lower() in NULL_LIKE_STRINGS:
            return None
        return cleaned
    return val


def normalize_timestamp(val: Any) -> datetime:
    """
    Parses timestamps and converts to UTC timezone.
    Raises ValueError on malformed timestamps.
    """
    if val is None:
        raise ValueError("Timestamp cannot be null")

    if isinstance(val, (int, float)):
        # Check if milliseconds or seconds
        if val > 1e11:  # Milliseconds epoch
            val = val / 1000.0
        return datetime.fromtimestamp(val, tz=timezone.utc)

    if isinstance(val, str):
        val = val.strip()
        if not val or val.lower() in NULL_LIKE_STRINGS:
            raise ValueError("Timestamp cannot be empty or null-like")
        # Try parsing with dateutil
        parsed = date_parser.parse(val)
        if parsed.tzinfo is None:
            # Assume UTC if naive, or convert
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)
        return parsed

    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)

    raise ValueError(f"Unsupported timestamp format: {type(val)} - {val}")


def normalize_ip(ip_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Canonicalizes an IPv4 or IPv6 string.
    Returns: (canonical_ip, version_type: 'IPv4'|'IPv6') or (original_cleaned, None) if invalid.
    """
    cleaned = normalize_null_value(ip_str)
    if not cleaned:
        return None, None
    try:
        ip_obj = ipaddress.ip_address(cleaned)
        version = f"IPv{ip_obj.version}"
        return ip_obj.exploded, version
    except ValueError:
        # Invalid IP: return cleaned original, version None
        return str(cleaned), None


def normalize_email(email_str: Optional[str]) -> Optional[str]:
    """
    Normalizes email addresses to lowercase trimmed format.
    Does NOT attempt to correct domain typos (e.g. gmial.com stays gmial.com).
    """
    cleaned = normalize_null_value(email_str)
    if not cleaned:
        return None
    cleaned = str(cleaned).strip().lower()
    return cleaned


def normalize_domain(domain_str: Optional[str]) -> Optional[str]:
    """
    Normalizes domain names by stripping whitespace and lowercasing.
    Never alters domain spelling.
    """
    cleaned = normalize_null_value(domain_str)
    if not cleaned:
        return None
    cleaned = str(cleaned).strip().lower()
    # Strip port if present
    if ":" in cleaned:
        cleaned = cleaned.split(":")[0]
    return cleaned


def normalize_url(url_str: Optional[str]) -> Optional[str]:
    """
    Normalizes URLs by lowercasing scheme/hostname and stripping whitespace.
    """
    cleaned = normalize_null_value(url_str)
    if not cleaned:
        return None
    cleaned = str(cleaned).strip()
    try:
        parsed = urlparse(cleaned)
        if parsed.scheme and parsed.netloc:
            # Reconstruct with lowercase scheme & netloc
            normalized_netloc = parsed.netloc.lower()
            normalized_scheme = parsed.scheme.lower()
            return f"{normalized_scheme}://{normalized_netloc}{parsed.path}" + (f"?{parsed.query}" if parsed.query else "")
    except Exception:
        pass
    return cleaned


def normalize_record(raw_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes all standard fields in a dictionary record.
    """
    normalized: Dict[str, Any] = {}
    for k, v in raw_record.items():
        k_clean = k.strip()
        normalized[k_clean] = normalize_null_value(v)

    # Standardize common fields if present
    if "timestamp" in normalized and normalized["timestamp"] is not None:
        try:
            normalized["timestamp"] = normalize_timestamp(normalized["timestamp"])
        except Exception as e:
            raise ValueError(f"Failed to normalize timestamp: {e}")

    # Standardize string identifiers
    for id_field in ["event_id", "agent_id", "entity_id", "source", "event_type"]:
        if id_field in normalized and normalized[id_field] is not None:
            normalized[id_field] = str(normalized[id_field]).strip()

    return normalized
