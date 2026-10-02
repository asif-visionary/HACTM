"""
Transaction Dataset Loader & Synthetic Data Generator.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from typing import Any, Dict, List
import random


def generate_synthetic_transaction_dataset(count: int = 100, anomaly_ratio: float = 0.20) -> List[Dict[str, Any]]:
    """
    Generates safe synthetic financial transaction dataset for testing and demonstration.
    Clearly labeled SYNTHETIC / DEMONSTRATION DATA.
    Contains normal purchases/transfers, velocity bursts, large amount anomalies, new recipient transfers.
    """
    events: List[Dict[str, Any]] = []
    accounts = [f"acc_bank_{i:04d}" for i in range(1, 10)]
    recipients = [f"recip_vendor_{i:03d}" for i in range(1, 15)]

    for i in range(count):
        acc = random.choice(accounts)
        is_suspicious = (i / count) < anomaly_ratio
        tx_id = f"synth_tx_{i+1:05d}"

        if not is_suspicious:
            # Normal Transaction
            events.append({
                "transaction_id": tx_id,
                "timestamp": "2026-10-02T10:00:00Z",
                "account_id": acc,
                "user_id": f"usr_{acc}",
                "device_id": "MOBILE-APP-IOS",
                "amount": round(random.uniform(15.0, 150.0), 2),
                "currency": "USD",
                "merchant_id": "MERCHANT-GROCERY-01",
                "merchant_category": "5411",
                "recipient_id": recipients[0],
                "transaction_type": "PAYMENT",
                "channel": "MOBILE",
                "is_synthetic": True,
                "dataset_label": "normal"
            })
        else:
            anom_type = i % 3
            if anom_type == 0:
                # Velocity Burst
                events.append({
                    "transaction_id": tx_id,
                    "timestamp": "2026-10-02T11:05:00Z",
                    "account_id": acc,
                    "user_id": f"usr_{acc}",
                    "device_id": "UNKNOWN-EMULATOR",
                    "amount": round(random.uniform(50.0, 200.0), 2),
                    "currency": "USD",
                    "merchant_id": "ONLINE-STORE",
                    "recipient_id": random.choice(recipients),
                    "transaction_type": "PAYMENT",
                    "channel": "WEB",
                    "is_synthetic": True,
                    "dataset_label": "velocity"
                })
            elif anom_type == 1:
                # Huge Amount Anomaly
                events.append({
                    "transaction_id": tx_id,
                    "timestamp": "2026-10-02T14:20:00Z",
                    "account_id": acc,
                    "user_id": f"usr_{acc}",
                    "device_id": "DESKTOP-WEB",
                    "amount": 75_000.00,
                    "currency": "USD",
                    "merchant_id": "OFFSHORE-ESCROW",
                    "recipient_id": "UNKNOWN-OFFSHORE-ACC",
                    "transaction_type": "TRANSFER",
                    "channel": "WIRE",
                    "is_synthetic": True,
                    "dataset_label": "amount_anomaly"
                })
            else:
                # New Recipient + High Amount
                events.append({
                    "transaction_id": tx_id,
                    "timestamp": "2026-10-02T16:00:00Z",
                    "account_id": acc,
                    "user_id": f"usr_{acc}",
                    "device_id": "NEW-DEVICE-ID-99",
                    "amount": 12_500.00,
                    "currency": "USD",
                    "merchant_id": "CRYPTO-EXCHANGE",
                    "recipient_id": f"recip_new_{i}",
                    "transaction_type": "TRANSFER",
                    "channel": "WEB",
                    "is_synthetic": True,
                    "dataset_label": "new_recipient"
                })

    return events
