"""
Network Data Normalization and Validation Engine.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Handles:
- IP validation (IPv4 / IPv6) & deterministic classification (PRIVATE, PUBLIC, LOOPBACK, etc.)
- Port validation (0–65535) & zero-port handling
- Protocol normalization (numeric & string: TCP, UDP, ICMP, ICMPv6, SCTP, OTHER)
- Flow metric bounds checking (NaN, Infinity, negative values)
"""

import ipaddress
import math
import re
from typing import Any, Dict, Optional, Tuple, Union

from hactm.core.errors import HACTMValidationError
from hactm.ingestion.normalization import normalize_null_value, normalize_timestamp
from hactm.network.models import IPClassification, NetworkEvent

# Protocol number mapping
PROTOCOL_MAP: Dict[Union[int, str], str] = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
    58: "ICMPv6",
    132: "SCTP",
    "1": "ICMP",
    "6": "TCP",
    "17": "UDP",
    "58": "ICMPv6",
    "132": "SCTP",
    "tcp": "TCP",
    "udp": "UDP",
    "icmp": "ICMP",
    "icmpv6": "ICMPv6",
    "sctp": "SCTP",
}


def normalize_network_protocol(raw_proto: Any) -> str:
    """
    Standardizes protocol to canonical uppercase name.
    Preserves unknown strings as OTHER with sanitized representation.
    """
    val = normalize_null_value(raw_proto)
    if val is None:
        return "OTHER"

    if isinstance(val, (int, float)):
        int_val = int(val)
        return PROTOCOL_MAP.get(int_val, f"PROTO_{int_val}")

    s = str(val).strip().lower()
    if s in PROTOCOL_MAP:
        return PROTOCOL_MAP[s]

    if s.isdigit():
        return PROTOCOL_MAP.get(int(s), f"PROTO_{s}")

    return s.upper() if len(s) <= 12 else "OTHER"


def validate_and_normalize_port(raw_port: Any) -> Optional[int]:
    """
    Validates network port is an integer in range [0, 65535].
    Raises ValueError on invalid values (negative, decimal, out of bounds, non-numeric).
    """
    val = normalize_null_value(raw_port)
    if val is None:
        return None

    if isinstance(val, bool):
        raise ValueError(f"Invalid port boolean: {val}")

    if isinstance(val, float):
        if not val.is_integer():
            raise ValueError(f"Invalid decimal port: {val}")
        val = int(val)

    if isinstance(val, str):
        s = val.strip()
        if not s:
            return None
        if not s.isdigit() and not (s.startswith("-") and s[1:].isdigit()):
            raise ValueError(f"Invalid non-numeric port: '{val}'")
        val = int(s)

    if not isinstance(val, int):
        raise ValueError(f"Invalid port type: {type(val)}")

    if val < 0 or val > 65535:
        raise ValueError(f"Port out of range [0, 65535]: {val}")

    return val


def classify_ip_address(ip_obj: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]) -> IPClassification:
    """
    Deterministically classifies IP without external network lookups or GeoIP.
    """
    if ip_obj.is_loopback:
        return IPClassification.LOOPBACK
    if ip_obj.is_link_local:
        return IPClassification.LINK_LOCAL
    if ip_obj.is_multicast:
        return IPClassification.MULTICAST
    if ip_obj.is_unspecified:
        return IPClassification.UNSPECIFIED
    if ip_obj.is_reserved:
        return IPClassification.RESERVED
    if ip_obj.is_private:
        return IPClassification.PRIVATE
    return IPClassification.PUBLIC


def validate_and_classify_ip(raw_ip: Any) -> Tuple[str, IPClassification]:
    """
    Validates IP string is valid IPv4 or IPv6 and classifies its scope.
    Raises ValueError if malformed.
    """
    val = normalize_null_value(raw_ip)
    if val is None or not str(val).strip():
        raise ValueError("IP address cannot be null or empty")

    clean_ip = str(val).strip()
    try:
        ip_obj = ipaddress.ip_address(clean_ip)
        classification = classify_ip_address(ip_obj)
        return str(ip_obj), classification
    except ValueError as e:
        raise ValueError(f"Invalid IP address '{clean_ip}': {e}")


def sanitize_float_metric(val: Any, field_name: str) -> Optional[float]:
    """
    Safely sanitizes float metrics, catching NaN, Infinity, negative values.
    """
    clean = normalize_null_value(val)
    if clean is None:
        return None
    try:
        f = float(clean)
    except (ValueError, TypeError):
        raise ValueError(f"Field '{field_name}' must be numeric, got: {val}")

    if math.isnan(f) or math.isinf(f):
        raise ValueError(f"Field '{field_name}' cannot be NaN or Infinity")

    if f < 0.0:
        raise ValueError(f"Field '{field_name}' cannot be negative: {f}")

    return f


def sanitize_int_metric(val: Any, field_name: str) -> Optional[int]:
    """
    Safely sanitizes integer metrics, catching negative counts.
    """
    clean = normalize_null_value(val)
    if clean is None:
        return None
    try:
        i = int(float(clean))
    except (ValueError, TypeError):
        raise ValueError(f"Field '{field_name}' must be integer, got: {val}")

    if i < 0:
        raise ValueError(f"Field '{field_name}' cannot be negative: {i}")

    return i


# Functional Convenience Wrappers for testing and direct pipeline calls
def classify_ip(raw_ip: Any) -> str:
    """Classifies an IP string and returns deterministic string category or 'INVALID'."""
    try:
        _, classification = validate_and_classify_ip(raw_ip)
        return classification.value
    except Exception:
        return "INVALID"


def normalize_ip(raw_ip: Any, strict: bool = True) -> Optional[str]:
    """Validates and normalizes IP string, returning exploded format or None/raising error."""
    try:
        norm_ip, _ = validate_and_classify_ip(raw_ip)
        return norm_ip
    except Exception as e:
        if strict:
            raise ValueError(str(e))
        return None


def normalize_port(raw_port: Any, strict: bool = True) -> Optional[int]:
    """Validates port in range [0, 65535]."""
    try:
        return validate_and_normalize_port(raw_port)
    except Exception as e:
        if strict:
            raise ValueError(str(e))
        return None


def normalize_protocol(raw_proto: Any) -> str:
    """Normalizes network protocol to canonical uppercase string."""
    return normalize_network_protocol(raw_proto)


def clean_numeric(
    val: Any,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    default: float = 0.0,
) -> float:
    """Cleans numeric values handling NaN, Infinity, negative values, and bounds."""
    try:
        if val is None:
            return default
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        if min_val is not None and f < min_val:
            return min_val
        if max_val is not None and f > max_val:
            return max_val
        return f
    except (ValueError, TypeError):
        return default


def normalize_tcp_flags(flags: Any) -> Optional[str]:
    """Normalizes TCP flag representation."""
    if flags is None:
        return None
    if isinstance(flags, int):
        parts = []
        if flags & 0x02:
            parts.append("SYN")
        if flags & 0x10:
            parts.append("ACK")
        if flags & 0x01:
            parts.append("FIN")
        if flags & 0x04:
            parts.append("RST")
        if flags & 0x08:
            parts.append("PSH")
        if flags & 0x20:
            parts.append("URG")
        return ",".join(parts) if parts else str(flags)
    s = str(flags).strip().upper()
    return s if s else None
