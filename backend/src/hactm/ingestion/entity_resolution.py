"""
Deterministic Entity Resolution for HACTM.
Resolves and canonicalizes entity identifiers deterministically:
- Same normalized email -> same canonical entity
- Same canonical IP -> same canonical entity
- Same explicit source ID -> same canonical entity
No machine learning, heuristic guessing, or graph clustering is used in Foundation.
"""

from typing import Any, Dict, Optional, Tuple
from hactm.core.constants import EntityType
from hactm.ingestion.normalization import (
    normalize_domain,
    normalize_email,
    normalize_ip,
    normalize_null_value,
)


def resolve_entity(record: Dict[str, Any]) -> Tuple[str, EntityType, str, Dict[str, Any]]:
    """
    Deterministically resolves an entity from record fields.
    Returns:
        (canonical_entity_id, entity_type, canonical_name, attributes)
    """
    raw_entity_id = normalize_null_value(record.get("entity_id"))
    email_val = normalize_email(record.get("email") or record.get("entity_email") or record.get("user_email"))
    ip_val = record.get("ip") or record.get("entity_ip") or record.get("src_ip") or record.get("ip_address")
    canonical_ip, ip_version = normalize_ip(ip_val)
    user_val = normalize_null_value(record.get("user") or record.get("username") or record.get("user_id"))
    host_val = normalize_null_value(record.get("host") or record.get("hostname") or record.get("host_id"))
    device_val = normalize_null_value(record.get("device") or record.get("device_id"))

    attributes: Dict[str, Any] = {}

    # 1. If explicit entity_id was provided:
    if raw_entity_id:
        clean_id = str(raw_entity_id).strip()
        # Check if already prefixed
        if ":" in clean_id:
            prefix, rest = clean_id.split(":", 1)
            prefix_upper = prefix.upper()
            if prefix_upper == "IP":
                c_ip, v = normalize_ip(rest)
                if v:
                    attributes["ip_version"] = v
                    return f"IP:{c_ip}", EntityType.IP, c_ip, attributes
            elif prefix_upper == "EMAIL":
                c_em = normalize_email(rest)
                if c_em:
                    return f"EMAIL:{c_em}", EntityType.EMAIL, c_em, attributes
            elif prefix_upper == "USER":
                return f"USER:{rest.strip()}", EntityType.USER, rest.strip(), attributes
            elif prefix_upper == "HOST":
                return f"HOST:{rest.strip().lower()}", EntityType.HOST, rest.strip().lower(), attributes
            elif prefix_upper == "DEVICE":
                return f"DEVICE:{rest.strip()}", EntityType.DEVICE, rest.strip(), attributes

        # If entity_id itself is a valid IP
        c_ip, v = normalize_ip(clean_id)
        if v:
            attributes["ip_version"] = v
            return f"IP:{c_ip}", EntityType.IP, c_ip, attributes

        # If entity_id itself is a valid email
        if "@" in clean_id:
            c_em = normalize_email(clean_id)
            if c_em:
                return f"EMAIL:{c_em}", EntityType.EMAIL, c_em, attributes

        return clean_id, EntityType.UNKNOWN, clean_id, attributes

    # 2. Derive from IP if present
    if canonical_ip and ip_version:
        attributes["ip_version"] = ip_version
        return f"IP:{canonical_ip}", EntityType.IP, canonical_ip, attributes

    # 3. Derive from Email if present
    if email_val and "@" in email_val:
        return f"EMAIL:{email_val}", EntityType.EMAIL, email_val, attributes

    # 4. Derive from Username/User ID if present
    if user_val:
        c_user = str(user_val).strip()
        return f"USER:{c_user}", EntityType.USER, c_user, attributes

    # 5. Derive from Hostname if present
    if host_val:
        c_host = str(host_val).strip().lower()
        return f"HOST:{c_host}", EntityType.HOST, c_host, attributes

    # 6. Derive from Device ID if present
    if device_val:
        c_device = str(device_val).strip()
        return f"DEVICE:{c_device}", EntityType.DEVICE, c_device, attributes

    # Fallback to an anonymous unknown entity if nothing identifiable
    event_id = str(record.get("event_id", "UNKNOWN")).strip()
    return f"ENTITY:UNRESOLVED_{event_id}", EntityType.UNKNOWN, f"Unresolved Entity ({event_id})", attributes
