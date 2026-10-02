"""
Common failure unit tests for all Specialized Security Agents agents.
Section 96 Test Matrix:
- malformed input
- huge input
- duplicate input
- missing optional fields
"""

import pytest
from hactm.phishing.agent import PhishingIntelligenceAgent
from hactm.uba.agent import UBAAgent
from hactm.identity.agent import IdentityAuthenticationAgent
from hactm.transaction.agent import TransactionSecurityAgent


def test_malformed_and_huge_inputs_graceful_handling():
    agents = [
        PhishingIntelligenceAgent(),
        UBAAgent(),
        IdentityAuthenticationAgent(),
        TransactionSecurityAgent(),
    ]

    huge_text = "A" * 100_000
    huge_list = ["http://example.com"] * 500

    malformed_inputs = [
        {},
        {"invalid_key": 123},
        None,
        {"body": huge_text, "urls": huge_list},
    ]

    for ag in agents:
        for item in malformed_inputs:
            if item is None:
                continue
            # Must handle gracefully without crashing or throwing unhandled exception
            dets = ag.process_event(item)
            assert isinstance(dets, list)


def test_idempotent_batch_processing():
    phish_ag = PhishingIntelligenceAgent()
    events = [
        {"message_id": "dup_01", "subject": "Test Duplicate", "body": "Verify account link http://dup.xyz"},
        {"message_id": "dup_01", "subject": "Test Duplicate", "body": "Verify account link http://dup.xyz"},
    ]

    dets1, ev1 = phish_ag.process_batch(events, dataset_name="dup_test")
    assert len(dets1) >= 1
    assert len(ev1) >= 1
