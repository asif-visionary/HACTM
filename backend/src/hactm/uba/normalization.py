"""
UBA Data Normalization Engine.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from hactm.uba.models import UbaEvent


def normalize_uba_event(raw: Dict[str, Any]) -> UbaEvent:
    """Normalizes raw user activity dictionary into UbaEvent safely."""
    event_id = str(raw.get("event_id") or raw.get("id") or f"uba_ev_{hash(str(raw))}").strip()
    user_id = str(raw.get("user_id") or raw.get("user") or raw.get("account") or "unknown_user").strip()

    raw_ts = raw.get("timestamp") or raw.get("date")
    dt = datetime.now(timezone.utc)
    if isinstance(raw_ts, datetime):
        dt = raw_ts if raw_ts.tzinfo else raw_ts.replace(tzinfo=timezone.utc)
    elif isinstance(raw_ts, str):
        from dateutil import parser
        try:
            parsed_dt = parser.parse(raw_ts)
            dt = parsed_dt if parsed_dt.tzinfo else parsed_dt.replace(tzinfo=timezone.utc)
        except Exception:
            pass

    action = str(raw.get("action") or raw.get("activity") or "access").strip().lower()
    resource = str(raw.get("resource") or raw.get("target") or "").strip() or None
    resource_type = str(raw.get("resource_type") or "").strip() or None
    file_name = str(raw.get("file_name") or raw.get("filename") or "").strip() or None
    file_size = int(raw.get("file_size") or 0)
    bytes_transferred = int(raw.get("bytes_transferred") or raw.get("bytes") or 0)
    application = str(raw.get("application") or raw.get("app") or "").strip() or None
    device_id = str(raw.get("device_id") or raw.get("device") or "").strip() or None
    source_ip = str(raw.get("source_ip") or raw.get("ip") or "").strip() or None
    session_id = str(raw.get("session_id") or "").strip() or None
    auth_status = str(raw.get("authentication_status") or "SUCCESS").strip().upper()
    priv_level = str(raw.get("privilege_level") or "USER").strip().upper()
    location = str(raw.get("location") or "").strip() or None
    peer_group = str(raw.get("peer_group") or raw.get("department") or "").strip() or None

    return UbaEvent(
        event_id=event_id,
        user_id=user_id,
        timestamp=dt,
        session_id=session_id,
        device_id=device_id,
        source_ip=source_ip,
        action=action,
        resource=resource,
        resource_type=resource_type,
        file_name=file_name,
        file_size=max(0, file_size),
        application=application,
        authentication_status=auth_status,
        privilege_level=priv_level,
        location=location,
        bytes_transferred=max(0, bytes_transferred),
        peer_group=peer_group,
    )
