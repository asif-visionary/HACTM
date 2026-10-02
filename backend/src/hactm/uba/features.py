"""
UBA Feature Extractor.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from typing import Any, Dict
from hactm.uba.models import UbaEvent
from hactm.uba.profile_manager import ProfileManager


def extract_uba_features(event: UbaEvent, profile_mgr: ProfileManager) -> Dict[str, Any]:
    """Extracts features for an UBA event against user baseline and peer profiles."""
    user_id = event.user_id
    dt = event.timestamp
    profile = profile_mgr.get_profile(user_id)

    insufficient_baseline = True
    is_new_device = False
    is_new_ip = False
    is_new_app = False
    is_rare_resource = False
    is_off_hours = False
    bytes_deviation_ratio = 1.0
    is_privilege_escalation = False

    if profile and not profile.is_insufficient_baseline:
        insufficient_baseline = False

        # Device / IP novelty
        if event.device_id and profile.known_devices:
            is_new_device = event.device_id not in profile.known_devices

        if event.source_ip and profile.known_ips:
            is_new_ip = event.source_ip not in profile.known_ips

        # Application / Resource novelty
        if event.application and profile.known_applications:
            is_new_app = event.application not in profile.known_applications

        if event.resource and profile.typical_resources:
            is_rare_resource = event.resource not in profile.typical_resources

        # Temporal deviation (hour outside normal hours)
        if profile.normal_login_hours:
            is_off_hours = dt.hour not in profile.normal_login_hours
        else:
            is_off_hours = (dt.hour >= 22 or dt.hour <= 5)

        # Data volume deviation
        if profile.avg_bytes_transferred > 0 and event.bytes_transferred:
            bytes_deviation_ratio = round(event.bytes_transferred / max(1.0, profile.avg_bytes_transferred), 2)
    else:
        # Default heuristics for new user
        is_off_hours = (dt.hour >= 22 or dt.hour <= 5)
        if event.bytes_transferred and event.bytes_transferred > 100_000_000:
            bytes_deviation_ratio = 5.0

    # Privilege escalation indicator
    if event.privilege_level in {"ADMIN", "ROOT", "SYSTEM", "SUDO"}:
        if event.action in {"privilege_elevation", "sudo", "role_switch", "grant_access"}:
            is_privilege_escalation = True

    return {
        "user_id": user_id,
        "event_id": event.event_id,
        "insufficient_baseline": insufficient_baseline,
        "hour_of_day": dt.hour,
        "day_of_week": dt.weekday(),
        "is_off_hours": is_off_hours,
        "is_new_device": is_new_device,
        "is_new_ip": is_new_ip,
        "is_new_app": is_new_app,
        "is_rare_resource": is_rare_resource,
        "bytes_transferred": event.bytes_transferred or 0,
        "bytes_deviation_ratio": bytes_deviation_ratio,
        "is_privilege_escalation": is_privilege_escalation,
        "action": event.action,
        "privilege_level": event.privilege_level,
    }
