"""
UBA Dataset Loader & Synthetic Data Generator.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from typing import Any, Dict, List
import random


def generate_synthetic_uba_dataset(count: int = 100, anomaly_ratio: float = 0.2) -> List[Dict[str, Any]]:
    """
    Generates safe synthetic UBA activity dataset for testing and demonstration.
    Clearly labeled SYNTHETIC / DEMONSTRATION DATA.
    Contains normal user activities, off-hours logins, data movement anomalies,
    resource anomalies, privilege escalations, and new user baseline tests.
    """
    events: List[Dict[str, Any]] = []
    users = [f"usr_employee_{i}" for i in range(1, 10)]
    devices = ["LAPTOP-WORK-01", "DESKTOP-FIN-02", "MACBOOK-DEV-03"]
    resources = ["/shared/finance/q3.xlsx", "/code/repo/src/main.py", "/hr/payroll_2026.pdf", "/db/customer_backup.sql"]

    for i in range(count):
        user = random.choice(users)
        is_suspicious = (i / count) < anomaly_ratio
        event_id = f"synth_uba_{i+1:05d}"

        if not is_suspicious:
            # Benign normal working hours activity
            hour = random.randint(9, 17)
            events.append({
                "event_id": event_id,
                "user_id": user,
                "timestamp": f"2026-10-02T{hour:02d}:15:00Z",
                "session_id": f"sess_{user}_{i}",
                "device_id": devices[0],
                "source_ip": "10.0.4.15",
                "action": "file_read",
                "resource": resources[0],
                "resource_type": "file",
                "file_name": "q3.xlsx",
                "file_size": 250000,
                "bytes_transferred": 250000,
                "application": "Excel",
                "authentication_status": "SUCCESS",
                "privilege_level": "USER",
                "peer_group": "Finance",
                "is_synthetic": True,
                "dataset_label": "benign"
            })
        else:
            anom_type = i % 3
            if anom_type == 0:
                # Off-hours activity
                events.append({
                    "event_id": event_id,
                    "user_id": user,
                    "timestamp": "2026-10-02T03:30:00Z",
                    "session_id": f"sess_{user}_{i}",
                    "device_id": "UNKNOWN-RDP-NODE",
                    "source_ip": "198.51.100.77",
                    "action": "login",
                    "resource": "RDP-Gateway",
                    "application": "RDP",
                    "authentication_status": "SUCCESS",
                    "privilege_level": "USER",
                    "peer_group": "Finance",
                    "is_synthetic": True,
                    "dataset_label": "off_hours"
                })
            elif anom_type == 1:
                # Potential Data Movement Anomaly
                events.append({
                    "event_id": event_id,
                    "user_id": user,
                    "timestamp": "2026-10-02T14:00:00Z",
                    "session_id": f"sess_{user}_{i}",
                    "device_id": devices[0],
                    "source_ip": "10.0.4.15",
                    "action": "file_download",
                    "resource": "/db/customer_backup.sql",
                    "resource_type": "database_export",
                    "file_name": "customer_backup.sql",
                    "file_size": 850_000_000,
                    "bytes_transferred": 850_000_000,
                    "application": "CloudStorageClient",
                    "authentication_status": "SUCCESS",
                    "privilege_level": "USER",
                    "peer_group": "Finance",
                    "is_synthetic": True,
                    "dataset_label": "data_movement"
                })
            else:
                # Privilege Escalation / Rare Resource
                events.append({
                    "event_id": event_id,
                    "user_id": user,
                    "timestamp": "2026-10-02T16:45:00Z",
                    "session_id": f"sess_{user}_{i}",
                    "device_id": devices[1],
                    "source_ip": "10.0.4.99",
                    "action": "privilege_elevation",
                    "resource": "/etc/sudoers",
                    "resource_type": "system_config",
                    "application": "Bash",
                    "authentication_status": "SUCCESS",
                    "privilege_level": "ADMIN",
                    "peer_group": "Finance",
                    "is_synthetic": True,
                    "dataset_label": "privilege_anomaly"
                })

    return events
