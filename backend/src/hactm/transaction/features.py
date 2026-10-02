"""
Transaction Feature Extractor & Account Baseline Manager.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np

from hactm.transaction.models import TransactionEvent


class AccountTransactionBaseline:
    """
    Stateful manager tracking historical transaction baseline per account.
    Tracks amount distribution (mean, median, std, max), velocity window, recipient set, and device set.
    """

    def __init__(self, max_history_per_account: int = 500):
        self.max_history = max_history_per_account
        self.account_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.max_history))
        self.known_recipients: Dict[str, set] = defaultdict(set)
        self.known_merchants: Dict[str, set] = defaultdict(set)
        self.known_devices: Dict[str, set] = defaultdict(set)

    def record_and_extract_features(self, event: TransactionEvent) -> Dict[str, Any]:
        acc_id = event.account_id
        dt = event.timestamp
        amt = event.amount
        history = list(self.account_history[acc_id])
        event_count = len(history)

        # Calculate Velocity (count of transactions in last 2 minutes / 120s)
        window_seconds = 120
        recent_count = 0
        for tx in reversed(history):
            if (dt - tx.timestamp).total_seconds() > window_seconds:
                break
            recent_count += 1

        # Calculate Amount Deviation (Robust z-score vs median & MAD)
        amounts = [tx.amount for tx in history if tx.amount > 0]
        amount_median = float(np.median(amounts)) if amounts else amt
        amount_std = float(np.std(amounts)) if len(amounts) > 1 else max(10.0, amt * 0.2)
        
        amount_ratio = round(amt / max(1.0, amount_median), 2) if amount_median > 0 else 1.0
        z_score = float((amt - amount_median) / max(1.0, amount_std)) if amount_std > 0 else 0.0

        # Recipient novelty
        is_new_recipient = False
        if event.recipient_id:
            if self.known_recipients[acc_id] and event.recipient_id not in self.known_recipients[acc_id]:
                is_new_recipient = True
            self.known_recipients[acc_id].add(event.recipient_id)

        # Merchant novelty
        is_new_merchant = False
        if event.merchant_id:
            if self.known_merchants[acc_id] and event.merchant_id not in self.known_merchants[acc_id]:
                is_new_merchant = True
            self.known_merchants[acc_id].add(event.merchant_id)

        # Device novelty
        is_new_device = False
        if event.device_id:
            if self.known_devices[acc_id] and event.device_id not in self.known_devices[acc_id]:
                is_new_device = True
            self.known_devices[acc_id].add(event.device_id)

        # Record current transaction
        self.account_history[acc_id].append(event)

        return {
            "account_id": acc_id,
            "transaction_id": event.transaction_id,
            "amount": amt,
            "currency": event.currency,
            "history_count": event_count,
            "recent_velocity_count": recent_count,
            "amount_median": amount_median,
            "amount_ratio": amount_ratio,
            "z_score": round(z_score, 2),
            "is_new_recipient": is_new_recipient,
            "is_new_merchant": is_new_merchant,
            "is_new_device": is_new_device,
            "transaction_type": event.transaction_type,
            "hour_of_day": dt.hour,
        }
