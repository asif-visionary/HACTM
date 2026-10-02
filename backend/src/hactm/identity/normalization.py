"""
Identity Data Normalization Engine.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.

Privacy Protection: NEVER stores passwords, OTP secrets, session tokens, or raw biometric data.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from hactm.identity.models import IdentityEvent


def normalize_identity_event(raw: Dict[str, Any]) -> IdentityEvent:
    """Normalizes raw authentication event input dictionary safely."""
    auth_id = str(raw.get("authentication_event_id") or raw.get("event_id") or raw.get("id") or f"auth_{hash(str(raw))}").strip()
    user_id = str(raw.get("user_id") or raw.get("user") or raw.get("account_id") or "unknown_account").strip()
    account_id = str(raw.get("account_id") or user_id).strip()

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

    device_id = str(raw.get("device_id") or raw.get("device") or "").strip() or None
    source_ip = str(raw.get("source_ip") or raw.get("ip") or "").strip() or None
    session_id = str(raw.get("session_id") or "").strip() or None

    auth_method = str(raw.get("authentication_method") or "PASSWORD").strip().upper()
    auth_status = str(raw.get("authentication_status") or raw.get("status") or "SUCCESS").strip().upper()
    if auth_status in {"OK", "SUCCESSFUL", "PASSED", "TRUE"}:
        auth_status = "SUCCESS"
    elif auth_status in {"FAIL", "FAILED", "FAILURE", "FALSE", "DENIED"}:
        auth_status = "FAILED"

    failure_reason = str(raw.get("failure_reason") or "").strip() or None

    tfa_used = str(raw.get("two_factor_used") or raw.get("2fa_used") or raw.get("mfa_type") or "").strip().upper() or None
    tfa_res = str(raw.get("two_factor_result") or raw.get("2fa_result") or raw.get("mfa_result") or "").strip().upper() or None

    biometric_res = str(raw.get("biometric_verification_result") or raw.get("biometric") or "").strip().lower() or None
    if biometric_res not in {"verified", "failed", "not_available"}:
        biometric_res = None

    device_fp = str(raw.get("device_fingerprint") or "").strip() or None

    location = raw.get("location")
    if not isinstance(location, dict):
        location = None

    return IdentityEvent(
        authentication_event_id=auth_id,
        timestamp=dt,
        user_id=user_id,
        account_id=account_id,
        device_id=device_id,
        source_ip=source_ip,
        location=location,
        authentication_method=auth_method,
        authentication_status=auth_status,
        failure_reason=failure_reason,
        two_factor_used=tfa_used,
        two_factor_result=tfa_res,
        session_id=session_id,
        biometric_verification_result=biometric_res,
        device_fingerprint=device_fp,
    )
