"""
Transaction Data Normalization Engine.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.

Safety: Detection only. NEVER executes payments, transfers, account freezes, or stores card/CVV secrets.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from hactm.transaction.models import TransactionEvent


def normalize_transaction_event(raw: Dict[str, Any]) -> TransactionEvent:
    """Normalizes raw financial transaction telemetry dictionary safely."""
    tx_id = str(raw.get("transaction_id") or raw.get("id") or f"tx_{hash(str(raw))}").strip()
    account_id = str(raw.get("account_id") or raw.get("account") or "unknown_account").strip()

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

    tx_type = str(raw.get("transaction_type") or raw.get("type") or "PAYMENT").strip().upper()
    amount = float(raw.get("amount") or 0.0)

    # Validate amount
    if amount < 0.0 and tx_type not in {"REFUND", "CHARGEBACK"}:
        # Non-negative correction if standard payment
        amount = abs(amount)

    currency = str(raw.get("currency") or "USD").strip().upper()
    merchant_id = str(raw.get("merchant_id") or raw.get("merchant") or "").strip() or None
    merchant_cat = str(raw.get("merchant_category") or raw.get("mcc") or "").strip() or None
    recipient_id = str(raw.get("recipient_id") or raw.get("recipient") or "").strip() or None
    source_acc = str(raw.get("source_account") or account_id).strip() or None
    dest_acc = str(raw.get("destination_account") or recipient_id or "").strip() or None
    channel = str(raw.get("channel") or "WEB").strip().upper()
    user_id = str(raw.get("user_id") or "").strip() or None
    device_id = str(raw.get("device_id") or "").strip() or None
    status = str(raw.get("status") or "COMPLETED").strip().upper()

    location = raw.get("location")
    if not isinstance(location, dict):
        location = None

    return TransactionEvent(
        transaction_id=tx_id,
        timestamp=dt,
        account_id=account_id,
        user_id=user_id,
        device_id=device_id,
        amount=amount,
        currency=currency,
        merchant_id=merchant_id,
        merchant_category=merchant_cat,
        recipient_id=recipient_id,
        source_account=source_acc,
        destination_account=dest_acc,
        transaction_type=tx_type,
        channel=channel,
        location=location,
        status=status,
    )
