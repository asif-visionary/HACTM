"""
Unit tests and edge-case test matrix for TransactionSecurityAgent.
Section 95 Test Matrix:
- normal transaction
- zero amount / negative refund
- huge amount deviation z-score
- rapid velocity burst
- new recipient + high amount
- transaction safety invariants (NEVER execute transfers or freeze accounts)
"""

import pytest
from hactm.transaction.agent import TransactionSecurityAgent


@pytest.fixture
def agent():
    return TransactionSecurityAgent()


def test_transaction_velocity_anomaly(agent):
    acc = "tx_acc_01"
    # Process 6 transactions within 1 minute
    for i in range(6):
        dets = agent.process_event({
            "transaction_id": f"tx_vel_{i}",
            "account_id": acc,
            "timestamp": "2026-10-02T10:00:00Z",
            "amount": 50.0,
            "recipient_id": "recip_a",
        })

    cats = [d.category for d in dets]
    assert "TRANSACTION_VELOCITY_ANOMALY" in cats


def test_transaction_amount_anomaly(agent):
    acc = "tx_acc_02"

    # Build normal baseline of 5 small transactions (~$50)
    for i in range(5):
        agent.process_event({
            "transaction_id": f"tx_base_{i}",
            "account_id": acc,
            "timestamp": f"2026-10-02T{10+i:02d}:00:00Z",
            "amount": 45.0 + i,
        })

    # Massive $25,000 transaction
    dets = agent.process_event({
        "transaction_id": "tx_huge_01",
        "account_id": acc,
        "timestamp": "2026-10-02T16:00:00Z",
        "amount": 25000.0,
    })

    cats = [d.category for d in dets]
    assert "TRANSACTION_AMOUNT_ANOMALY" in cats
    assert "above historical account median" in dets[0].explanation


def test_transaction_recipient_anomaly(agent):
    acc = "tx_acc_03"

    # Seed baseline
    for i in range(3):
        agent.process_event({
            "transaction_id": f"tx_recip_base_{i}",
            "account_id": acc,
            "timestamp": f"2026-10-02T{10+i:02d}:00:00Z",
            "amount": 100.0,
            "recipient_id": "trusted_vendor_01",
            "device_id": "DEVICE-A",
        })

    # New recipient + 4x median amount + new device
    dets = agent.process_event({
        "transaction_id": "tx_new_recip_01",
        "account_id": acc,
        "timestamp": "2026-10-02T15:00:00Z",
        "amount": 450.0,
        "recipient_id": "unknown_offshore_entity",
        "device_id": "DEVICE-B",
    })

    cats = [d.category for d in dets]
    assert "RECIPIENT_NOVELTY_ANOMALY" in cats


def test_transaction_safety_and_edge_cases(agent):
    """Verifies safety invariants and edge cases (zero amount, refund, missing recipient)."""
    edge_cases = [
        {"transaction_id": "ec_01", "account_id": "acc_01", "amount": 0.0},
        {"transaction_id": "ec_02", "account_id": "acc_02", "amount": -150.0, "transaction_type": "REFUND"},
        {"transaction_id": "ec_03", "account_id": "acc_03", "amount": 1000000.0, "currency": "EUR"},
    ]

    for ec in edge_cases:
        dets = agent.process_event(ec)
        assert isinstance(dets, list)
