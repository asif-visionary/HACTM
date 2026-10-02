"""
Identity Dataset Loader & Synthetic Data Generator.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from typing import Any, Dict, List
import random


def generate_synthetic_identity_dataset(count: int = 100, anomaly_ratio: float = 0.25) -> List[Dict[str, Any]]:
    """
    Generates safe synthetic authentication dataset for testing and demonstration.
    Clearly labeled SYNTHETIC / DEMONSTRATION DATA.
    Contains normal logons, brute-force clusters, ATO scenarios, 2FA failures, impossible travel candidates.
    """
    events: List[Dict[str, Any]] = []
    accounts = [f"account_{i:03d}" for i in range(1, 8)]

    for i in range(count):
        acc = random.choice(accounts)
        is_suspicious = (i / count) < anomaly_ratio
        event_id = f"synth_auth_{i+1:05d}"

        if not is_suspicious:
            # Normal Successful Authentication
            events.append({
                "authentication_event_id": event_id,
                "timestamp": "2026-10-02T09:00:00Z",
                "user_id": acc,
                "account_id": acc,
                "device_id": "DEVICE-CORP-A",
                "source_ip": "198.51.100.10",
                "location": {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco", "country": "US"},
                "authentication_method": "PASSWORD",
                "authentication_status": "SUCCESS",
                "two_factor_used": "APP",
                "two_factor_result": "SUCCESS",
                "is_synthetic": True,
                "dataset_label": "normal"
            })
        else:
            anom_type = i % 4
            if anom_type == 0:
                # Brute-force / Credential Abuse
                events.append({
                    "authentication_event_id": event_id,
                    "timestamp": "2026-10-02T10:15:00Z",
                    "user_id": acc,
                    "account_id": acc,
                    "device_id": "BOTNET-ATTACKER-NODE",
                    "source_ip": "203.0.113.44",
                    "authentication_method": "PASSWORD",
                    "authentication_status": "FAILED",
                    "failure_reason": "INVALID_PASSWORD",
                    "is_synthetic": True,
                    "dataset_label": "credential_abuse"
                })
            elif anom_type == 1:
                # Account Takeover Candidate
                events.append({
                    "authentication_event_id": event_id,
                    "timestamp": "2026-10-02T11:00:00Z",
                    "user_id": acc,
                    "account_id": acc,
                    "device_id": "UNSEEN-FOREIGN-DEVICE",
                    "source_ip": "192.0.2.99",
                    "authentication_method": "PASSWORD",
                    "authentication_status": "SUCCESS",
                    "two_factor_used": "OTP",
                    "two_factor_result": "FAILED",
                    "is_synthetic": True,
                    "dataset_label": "account_takeover"
                })
            elif anom_type == 2:
                # Impossible Travel Candidate
                events.append({
                    "authentication_event_id": event_id,
                    "timestamp": "2026-10-02T09:15:00Z",  # Only 15 mins after SF login
                    "user_id": acc,
                    "account_id": acc,
                    "device_id": "DEVICE-OVERSEAS",
                    "source_ip": "198.51.100.222",
                    "location": {"lat": 51.5074, "lon": -0.1278, "city": "London", "country": "GB"},
                    "authentication_method": "PASSWORD",
                    "authentication_status": "SUCCESS",
                    "two_factor_used": "APP",
                    "two_factor_result": "SUCCESS",
                    "is_synthetic": True,
                    "dataset_label": "impossible_travel"
                })
            else:
                # 2FA Anomaly
                events.append({
                    "authentication_event_id": event_id,
                    "timestamp": "2026-10-02T13:00:00Z",
                    "user_id": acc,
                    "account_id": acc,
                    "device_id": "DEVICE-CORP-A",
                    "source_ip": "198.51.100.10",
                    "authentication_method": "PASSWORD",
                    "authentication_status": "SUCCESS",
                    "two_factor_used": "KEY",
                    "two_factor_result": "TIMEOUT",
                    "is_synthetic": True,
                    "dataset_label": "2fa_anomaly"
                })

    return events
