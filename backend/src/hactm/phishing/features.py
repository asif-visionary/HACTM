"""
Phishing Intelligence Feature Extractor.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.
"""

import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

from hactm.phishing.models import AttachmentMetadata, PhishingEmailEvent, UrlFeature
from hactm.phishing.normalization import extract_domain


# Keyword Patterns
URGENCY_WORDS = {
    "urgent", "immediately", "action required", "critical", "suspension",
    "account locked", "verify now", "24 hours", "unauthorized", "security alert",
    "prompt action", "threatened", "terminate", "restricted"
}

CREDENTIAL_WORDS = {
    "password", "login", "credentials", "verify account", "update account",
    "reset password", "security question", "authenticate", "passcode", "sign in"
}

FINANCIAL_WORDS = {
    "wire transfer", "invoice", "payment", "bank account", "swift", "direct deposit",
    "remittance", "routing number", "gift card", "payroll", "purchase order"
}

BEC_WORDS = {
    "ceo", "executive", "wire transfer", "confidential request", "urgent payment",
    "out of office", "acquisition", "attorney", "gift card", "vendor payment"
}

PERSONALIZATION_WORDS = {
    "dear", "hello", "hi", "mr.", "ms.", "dr.", "team", "department"
}


def analyze_url(url_str: str, sender_domain: Optional[str] = None) -> UrlFeature:
    """Extracts analytical features from a single URL safely without network requests."""
    length = len(url_str)
    try:
        parsed = urllib.parse.urlparse(url_str)
        hostname = parsed.netloc.split(":")[0] if parsed.netloc else ""
        path = parsed.path or ""
        scheme = parsed.scheme.lower() or ""
        query = parsed.query or ""

        hostname_len = len(hostname)
        path_len = len(path)

        # Count subdomains
        subdomain_parts = [p for p in hostname.split(".") if p]
        num_subdomains = max(0, len(subdomain_parts) - 2) if len(subdomain_parts) > 2 else 0

        # Query parameters count
        query_params = urllib.parse.parse_qs(query)
        num_query_params = len(query_params)

        # IP hostname indicator
        is_ip = bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname))

        # Punycode indicator
        is_punycode = "xn--" in hostname.lower()

        # HTTPS presence
        is_https = (scheme == "https")

        # Special character density in URL
        specials = re.findall(r'[@%=\-_?~#+&]', url_str)
        spec_density = len(specials) / max(1, length)

        # Domain mismatch vs sender
        url_domain = extract_domain(hostname) or hostname.lower()
        domain_mismatch = False
        if sender_domain and url_domain:
            domain_mismatch = (sender_domain.lower() not in url_domain.lower()) and (url_domain.lower() not in sender_domain.lower())

        return UrlFeature(
            url=url_str,
            length=length,
            hostname_length=hostname_len,
            path_length=path_len,
            num_subdomains=num_subdomains,
            num_query_params=num_query_params,
            is_ip_hostname=is_ip,
            is_https=is_https,
            is_punycode=is_punycode,
            special_char_density=round(spec_density, 4),
            domain_mismatch=domain_mismatch,
        )
    except Exception:
        return UrlFeature(url=url_str, length=length)


def extract_email_features(event: PhishingEmailEvent) -> Dict[str, Any]:
    """
    Extracts comprehensive feature dictionary from normalized email event.
    """
    sender_domain = event.sender_domain
    reply_to_domain = extract_domain(event.reply_to) if event.reply_to else None
    return_path_domain = extract_domain(event.return_path) if event.return_path else None

    # Header Mismatches
    reply_to_mismatch = False
    if sender_domain and reply_to_domain:
        reply_to_mismatch = (sender_domain != reply_to_domain)

    return_path_mismatch = False
    if sender_domain and return_path_domain:
        return_path_mismatch = (sender_domain != return_path_domain)

    # Auth Results (SPF, DKIM, DMARC)
    auth = event.authentication_results or {}
    spf_fail = auth.get("spf", "").lower() in {"fail", "softfail"}
    dkim_fail = auth.get("dkim", "").lower() in {"fail", "permerror"}
    dmarc_fail = auth.get("dmarc", "").lower() in {"fail", "reject", "quarantine"}
    auth_evidence_present = bool(auth)

    # URL Features Summary
    url_features = [analyze_url(u, sender_domain) for u in event.urls[:50]]
    num_urls = len(url_features)
    has_ip_url = any(uf.is_ip_hostname for uf in url_features)
    has_punycode_url = any(uf.is_punycode for uf in url_features)
    has_mismatch_url = any(uf.domain_mismatch for uf in url_features)
    max_url_len = max([uf.length for uf in url_features], default=0)
    max_subdomains = max([uf.num_subdomains for uf in url_features], default=0)

    # Attachment Features
    num_attachments = len(event.attachments)
    has_double_ext = any(att.is_double_extension for att in event.attachments)
    has_archive = any(att.is_archive for att in event.attachments)
    exec_exts = {"exe", "bat", "cmd", "ps1", "vbs", "js", "scr", "jar"}
    has_executable = any(att.extension in exec_exts for att in event.attachments)

    # Text Features
    text_content = f"{event.subject or ''} {event.body or ''}".lower()
    urgency_count = sum(1 for word in URGENCY_WORDS if word in text_content)
    credential_count = sum(1 for word in CREDENTIAL_WORDS if word in text_content)
    financial_count = sum(1 for word in FINANCIAL_WORDS if word in text_content)
    bec_count = sum(1 for word in BEC_WORDS if word in text_content)

    # Personalization indicators (e.g. recipient username or email in body/subject)
    recipient_name = ""
    if event.recipient:
        recipient_name = event.recipient.split("@")[0].lower()
    
    is_personalized = False
    if recipient_name and len(recipient_name) > 2:
        if recipient_name in text_content:
            is_personalized = True

    return {
        "message_id": event.message_id,
        "sender_domain": sender_domain,
        "reply_to_mismatch": reply_to_mismatch,
        "return_path_mismatch": return_path_mismatch,
        "spf_fail": spf_fail,
        "dkim_fail": dkim_fail,
        "dmarc_fail": dmarc_fail,
        "auth_evidence_present": auth_evidence_present,
        "num_urls": num_urls,
        "has_ip_url": has_ip_url,
        "has_punycode_url": has_punycode_url,
        "has_mismatch_url": has_mismatch_url,
        "max_url_len": max_url_len,
        "max_subdomains": max_subdomains,
        "num_attachments": num_attachments,
        "has_double_ext": has_double_ext,
        "has_archive": has_archive,
        "has_executable": has_executable,
        "urgency_count": urgency_count,
        "credential_count": credential_count,
        "financial_count": financial_count,
        "bec_count": bec_count,
        "is_personalized": is_personalized,
        "subject_length": len(event.subject or ""),
        "body_length": len(event.body or ""),
    }
