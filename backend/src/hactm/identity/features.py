"""
Identity & Authentication Feature Extractor & History Manager.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from collections import defaultdict, deque
from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional, Tuple

from hactm.identity.models import IdentityEvent


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geographical points in kilometers."""
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class IdentityHistoryManager:
    """
    Stateful bounded history manager tracking login history per user/account.
    Tracks failure rates, novel devices/IPs, and consecutive authentication location coordinates.
    """

    def __init__(self, max_history_per_user: int = 100):
        self.max_history = max_history_per_user
        self.user_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.max_history))
        self.known_devices: Dict[str, set] = defaultdict(set)
        self.known_ips: Dict[str, set] = defaultdict(set)

    def record_and_extract_features(self, event: IdentityEvent) -> Dict[str, Any]:
        user_id = event.user_id
        dt = event.timestamp
        history = list(self.user_history[user_id])

        # Calculate failures in last 5 minutes (300s)
        window_seconds = 300
        recent_failures = 0
        recent_events = 0
        for ev in reversed(history):
            delta = (dt - ev.timestamp).total_seconds()
            if delta > window_seconds:
                break
            recent_events += 1
            if ev.authentication_status == "FAILED":
                recent_failures += 1

        # Check consecutive failures right before this event
        consecutive_failures = 0
        for ev in reversed(history):
            if ev.authentication_status == "FAILED":
                consecutive_failures += 1
            else:
                break

        # Check device/IP novelty
        is_new_device = False
        if event.device_id:
            if self.known_devices[user_id] and event.device_id not in self.known_devices[user_id]:
                is_new_device = True
            self.known_devices[user_id].add(event.device_id)

        is_new_ip = False
        if event.source_ip:
            if self.known_ips[user_id] and event.source_ip not in self.known_ips[user_id]:
                is_new_ip = True
            self.known_ips[user_id].add(event.source_ip)

        # Impossible Travel Heuristic Check vs Previous Event
        impossible_travel_detected = False
        calculated_speed_kmh = 0.0
        prev_location_desc = ""

        if event.location and isinstance(event.location, dict):
            lat1 = event.location.get("lat")
            lon1 = event.location.get("lon")
            if lat1 is not None and lon1 is not None and history:
                # Find previous event with valid location
                for prev in reversed(history):
                    if prev.location and isinstance(prev.location, dict):
                        lat2 = prev.location.get("lat")
                        lon2 = prev.location.get("lon")
                        if lat2 is not None and lon2 is not None:
                            dist_km = haversine_distance_km(lat1, lon1, lat2, lon2)
                            elapsed_hours = (dt - prev.timestamp).total_seconds() / 3600.0
                            if elapsed_hours > 0.001 and dist_km > 10.0:
                                calculated_speed_kmh = dist_km / elapsed_hours
                                if calculated_speed_kmh > 900.0:  # Physically implausible speed
                                    impossible_travel_detected = True
                                    prev_location_desc = f"{prev.location.get('city', 'loc2')} ({dist_km:.0f} km away in {elapsed_hours*60:.1f} mins)"
                            break

        # Append current event to user history
        self.user_history[user_id].append(event)

        return {
            "user_id": user_id,
            "event_id": event.authentication_event_id,
            "authentication_status": event.authentication_status,
            "recent_failures_count": recent_failures,
            "consecutive_failures": consecutive_failures,
            "is_new_device": is_new_device,
            "is_new_ip": is_new_ip,
            "two_factor_used": event.two_factor_used,
            "two_factor_result": event.two_factor_result,
            "mfa_failed": event.two_factor_result in {"FAILED", "TIMEOUT"},
            "impossible_travel_detected": impossible_travel_detected,
            "calculated_speed_kmh": round(calculated_speed_kmh, 1),
            "prev_location_desc": prev_location_desc,
            "biometric_verification_result": event.biometric_verification_result,
        }
