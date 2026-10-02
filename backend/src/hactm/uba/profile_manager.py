"""
UBA User Profile & Peer Group Baseline Manager.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
import numpy as np

from hactm.uba.models import UbaEvent, UserProfile


class ProfileManager:
    """
    Stateful bounded profile manager tracking user baseline behavior and peer groups.
    Handles new users (returning INSUFFICIENT_BASELINE status), sparse history, and off-hour baselines.
    """

    def __init__(self, min_baseline_events: int = 5, max_history: int = 1000):
        self.min_baseline_events = min_baseline_events
        self.max_history = max_history

        self.user_profiles: Dict[str, UserProfile] = {}
        self.user_events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.max_history))
        self.peer_groups: Dict[str, Set[str]] = defaultdict(set)

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        return self.user_profiles.get(user_id)

    def update_profile(self, event: UbaEvent) -> UserProfile:
        user_id = event.user_id
        dt = event.timestamp

        self.user_events[user_id].append(event)
        history = list(self.user_events[user_id])
        event_count = len(history)

        profile = self.user_profiles.get(user_id)
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                peer_group=event.peer_group,
                first_seen=dt,
                last_seen=dt,
                event_count=1,
                is_insufficient_baseline=True,
            )
            self.user_profiles[user_id] = profile

        profile.last_seen = dt
        profile.event_count = event_count
        if event.peer_group:
            profile.peer_group = event.peer_group
            self.peer_groups[event.peer_group].add(user_id)

        # Re-calculate profile metrics if minimum events accumulated
        if event_count >= self.min_baseline_events:
            profile.is_insufficient_baseline = False

            # Normal hours (hours with >= 10% of user activity)
            hours_count = defaultdict(int)
            for ev in history:
                hours_count[ev.timestamp.hour] += 1
            profile.normal_login_hours = [
                h for h, cnt in hours_count.items() if (cnt / event_count) >= 0.05
            ]

            # Devices, IPs, Apps, Resources
            profile.known_devices = list({ev.device_id for ev in history if ev.device_id})
            profile.known_ips = list({ev.source_ip for ev in history if ev.source_ip})
            profile.known_applications = list({ev.application for ev in history if ev.application})
            profile.typical_resources = list({ev.resource for ev in history if ev.resource})

            # Data volume
            bytes_list = [ev.bytes_transferred for ev in history if ev.bytes_transferred]
            profile.avg_bytes_transferred = float(np.mean(bytes_list)) if bytes_list else 0.0
            profile.max_bytes_transferred = float(np.max(bytes_list)) if bytes_list else 0.0

        return profile
