"""
Unit tests and edge-case test matrix for PhishingIntelligenceAgent.
Section 92 Test Matrix:
- legitimate email
- generic phishing
- spear-phishing indicators
- BEC indicators
- empty email / body / subject
- malformed email / URL / punycode
- double extension attachment
- missing sender/recipient/timestamp
- HTML-only, Unicode, conflicting headers, SPF/DKIM/DMARC failure
"""

import pytest
from hactm.phishing.agent import PhishingIntelligenceAgent
from hactm.phishing.normalization import normalize_email_event


@pytest.fixture
def agent():
    return PhishingIntelligenceAgent()


def test_legitimate_email(agent):
    raw = {
        "message_id": "legit_001",
        "sender": "alice@company-corp.org",
        "recipient": "bob@company-corp.org",
        "subject": "Weekly Sprint Sync",
        "body": "Hi Bob, let's sync on sprint goals at 2 PM.",
        "headers": {"From": "alice@company-corp.org", "Reply-To": "alice@company-corp.org"},
        "authentication_results": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
    }
    dets = agent.process_event(raw)
    high_risk_dets = [d for d in dets if d.risk_score >= 0.5]
    assert len(high_risk_dets) == 0


def test_generic_phishing(agent):
    raw = {
        "message_id": "phish_001",
        "sender": "alert@examp1e-login.xyz",
        "recipient": "user@company-corp.org",
        "subject": "URGENT: Your Account Has Been Suspended! Verify Password Now",
        "body": "Dear user, unauthorized login detected. Click http://examp1e-login.xyz/login to reset password immediately.",
        "headers": {"From": "alert@examp1e-login.xyz"},
        "urls": ["http://examp1e-login.xyz/login"],
        "authentication_results": {"spf": "fail", "dkim": "fail"},
    }
    dets = agent.process_event(raw)
    assert len(dets) > 0
    categories = [d.category for d in dets]
    assert any(c in {"EMAIL_HEADER_ANOMALY", "GENERIC_PHISHING", "SUSPICIOUS_URL"} for c in categories)


def test_spear_phishing_indicators(agent):
    raw = {
        "message_id": "spear_001",
        "sender": "hr-review@eval-service.click",
        "recipient": "john_doe@company-corp.org",
        "subject": "Action Required: john_doe Performance Document",
        "body": "Dear john_doe, please review your confidential HR performance document attached for department approval.",
        "attachments": [{"filename": "employee_eval.pdf.exe", "size": 104000}],
    }
    dets = agent.process_event(raw)
    assert len(dets) > 0
    spear_dets = [d for d in dets if d.is_spear_phishing]
    assert len(spear_dets) > 0
    assert "spear-phishing indicators detected" in spear_dets[0].explanation.lower()


def test_bec_indicators(agent):
    raw = {
        "message_id": "bec_001",
        "sender": "ceo@company-corp.org",
        "recipient": "cfo@company-corp.org",
        "subject": "Urgent Wire Transfer Request - Confidential Acquisition",
        "body": "I am in an executive meeting and need an urgent wire transfer processed for vendor invoice payment immediately.",
        "reply_to": "exec-private@gmail.com",
    }
    dets = agent.process_event(raw)
    assert len(dets) > 0
    bec_dets = [d for d in dets if d.is_bec]
    assert len(bec_dets) > 0
    assert "bec indicators detected" in bec_dets[0].explanation.lower()


def test_phishing_edge_cases_matrix(agent):
    """Executes full edge-case matrix without crashing."""
    edge_cases = [
        {"message_id": "ec_01"},  # completely empty raw
        {"message_id": "ec_02", "subject": "", "body": ""},  # empty subject & body
        {"message_id": "ec_03", "body": "<html><body><a href='http://192.168.1.1/admin'>Click</a></body></html>"},  # HTML-only
        {"message_id": "ec_04", "body": "Unicode text 登录 🔒 Verify account: http://xn--e1afmkfd.xn--p1ai"},  # Unicode & Punycode
        {"message_id": "ec_05", "urls": ["http://malformed_url_without_proper_host", "http://10.0.0.1/test"]},  # Malformed URLs
        {"message_id": "ec_06", "attachments": [{"filename": "no_ext_file", "size": 0}, {"filename": "invoice.pdf.exe", "size": 500}]},  # Attachments
    ]

    for ec in edge_cases:
        dets = agent.process_event(ec)
        assert isinstance(dets, list)
