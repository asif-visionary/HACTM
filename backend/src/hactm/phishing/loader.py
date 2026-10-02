"""
Phishing Dataset Loader & Synthetic Data Generator.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union
import random


def generate_synthetic_phishing_dataset(count: int = 100, anomaly_ratio: float = 0.3) -> List[Dict[str, Any]]:
    """
    Generates safe synthetic phishing email dataset for testing and demonstration.
    Clearly labeled SYNTHETIC / DEMONSTRATION DATA.
    Contains normal benign emails, generic phishing, spear-phishing indicators, BEC indicators, and edge cases.
    """
    events: List[Dict[str, Any]] = []

    domains = ["example.com", "company-corp.org", "test-domain.net", "enterprise-service.com"]
    suspicious_domains = ["examp1e-login.xyz", "update-bank-security.click", "payroll-verify.top", "account-alert-security.link"]

    for i in range(count):
        is_suspicious = (i / count) < anomaly_ratio
        msg_id = f"synth_msg_{i+1:05d}"
        
        if not is_suspicious:
            # Benign email
            domain = random.choice(domains)
            sender = f"user_{i}@domain.com"
            recipient = f"colleague_{i}@domain.com"
            events.append({
                "message_id": msg_id,
                "timestamp": "2026-10-02T10:00:00Z",
                "sender": sender,
                "recipient": recipient,
                "subject": f"Quarterly Project Status Update #{i}",
                "body": f"Hi team, attached is the status update for project iteration {i}. Let me know if you have questions.",
                "headers": {"From": sender, "Reply-To": sender, "Return-Path": sender},
                "urls": ["https://example.com/docs/report.pdf"],
                "attachments": [{"filename": "project_report.pdf", "size": 154200, "mime_type": "application/pdf"}],
                "sender_domain": "domain.com",
                "reply_to": sender,
                "return_path": sender,
                "authentication_results": {"spf": "pass", "dkim": "pass", "dmarc": "pass"},
                "source_ip": "192.168.1.50",
                "is_synthetic": True,
                "dataset_label": "benign"
            })
        else:
            # Suspicious email types: 0=Generic Phishing, 1=Spear Phishing, 2=BEC, 3=Edge Case
            phish_type = i % 4
            if phish_type == 0:
                # Generic Phishing
                s_domain = random.choice(suspicious_domains)
                sender = f"security-alert@{s_domain}"
                recip = f"user_{i}@company-corp.org"
                events.append({
                    "message_id": msg_id,
                    "timestamp": "2026-10-02T11:15:00Z",
                    "sender": sender,
                    "recipient": recip,
                    "subject": "URGENT: Your Account Has Been Suspended! Verify Password Now",
                    "body": "Dear user, unauthorized login detected on your account. Please click the link to reset your credentials within 24 hours.",
                    "headers": {"From": sender, "Reply-To": f"phish-reply@{s_domain}"},
                    "urls": [f"http://{s_domain}/login/verify?user={i}"],
                    "attachments": [],
                    "sender_domain": s_domain,
                    "reply_to": f"phish-reply@{s_domain}",
                    "authentication_results": {"spf": "fail", "dkim": "fail", "dmarc": "fail"},
                    "source_ip": "203.0.113.88",
                    "is_synthetic": True,
                    "dataset_label": "phishing"
                })
            elif phish_type == 1:
                # Spear Phishing Indicators
                s_domain = random.choice(suspicious_domains)
                recip = f"john_doe_{i}@company-corp.org"
                events.append({
                    "message_id": msg_id,
                    "timestamp": "2026-10-02T12:00:00Z",
                    "sender": f"hr-support@{s_domain}",
                    "recipient": recip,
                    "subject": f"Action Required: john_doe_{i} Performance Review Document",
                    "body": f"Dear john_doe_{i}, please review your confidential HR performance document attached for department approval.",
                    "headers": {"From": f"hr-support@{s_domain}"},
                    "urls": [f"https://{s_domain}/hr/doc"],
                    "attachments": [{"filename": "employee_eval.pdf.exe", "size": 482000, "mime_type": "application/x-msdownload"}],
                    "sender_domain": s_domain,
                    "authentication_results": {"spf": "fail"},
                    "source_ip": "198.51.100.42",
                    "is_synthetic": True,
                    "dataset_label": "spear_phishing"
                })
            elif phish_type == 2:
                # BEC Indicators
                events.append({
                    "message_id": msg_id,
                    "timestamp": "2026-10-02T14:30:00Z",
                    "sender": "ceo@company-corp.org",
                    "recipient": "finance_dept@company-corp.org",
                    "subject": "Urgent Wire Transfer Request - Confidential Acquisition",
                    "body": "I am currently in an executive meeting and need an urgent wire transfer processed for vendor invoice payment immediately.",
                    "headers": {"From": "ceo@company-corp.org", "Reply-To": "ceo-private-exec@gmail.com"},
                    "urls": [],
                    "attachments": [{"filename": "urgent_payment_details.docm", "size": 120400, "mime_type": "application/msword"}],
                    "sender_domain": "company-corp.org",
                    "reply_to": "ceo-private-exec@gmail.com",
                    "authentication_results": {"spf": "softfail"},
                    "source_ip": "192.0.2.14",
                    "is_synthetic": True,
                    "dataset_label": "bec"
                })
            else:
                # Edge Case: Malformed / Unicode / Punycode
                events.append({
                    "message_id": msg_id,
                    "timestamp": "2026-10-02T15:45:00Z",
                    "sender": "alert@xn--e1afmkfd.xn--p1ai",
                    "recipient": "admin@company-corp.org",
                    "subject": "Unicode Alert ⚠️ 登录 🔒 Verification Required",
                    "body": "Please click http://192.168.1.1/login or http://xn--e1afmkfd.xn--p1ai/auth to confirm.",
                    "headers": {},
                    "urls": ["http://192.168.1.1/login", "http://xn--e1afmkfd.xn--p1ai/auth"],
                    "attachments": [{"filename": "file_no_ext", "size": 0}],
                    "source_ip": "203.0.113.99",
                    "is_synthetic": True,
                    "dataset_label": "phishing"
                })

    return events
