"""
Phishing Email Data Normalization Engine.
Specialized Security Agents — Hierarchical Adaptive Cyber Trust Mesh.

Normalizes raw email input, headers, sender/recipient addresses, URLs, attachments,
text encoding, and HTML bodies safely offline without network requests.
"""

from datetime import datetime, timezone
import html
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

from hactm.phishing.models import AttachmentMetadata, PhishingEmailEvent
from hactm.core.logging import logger


URL_REGEX = re.compile(
    r'https?://[^\s<>"]+|www\.[^\s<>"]+', re.IGNORECASE
)

EMAIL_REGEX = re.compile(
    r'[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
)


def extract_domain(email_str: Optional[str]) -> Optional[str]:
    """Extracts domain from email address safely in lowercase."""
    if not email_str or not isinstance(email_str, str):
        return None
    match = EMAIL_REGEX.search(email_str.strip())
    if match:
        return match.group(1).lower()
    if "@" in email_str:
        parts = email_str.strip().split("@")
        if len(parts) >= 2 and parts[-1]:
            return parts[-1].lower()
    return None


def sanitize_text(text: Optional[str]) -> str:
    """Sanitizes text by unescaping HTML entities and removing HTML tags safely."""
    if not text or not isinstance(text, str):
        return ""
    # Unescape HTML entities (e.g. &amp;, &#39;)
    clean = html.unescape(text)
    # Strip basic HTML tags safely
    clean = re.sub(r'<[^>]+>', ' ', clean)
    # Normalize excessive whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def extract_urls_from_text(text: Optional[str]) -> List[str]:
    """Extracts URLs from raw or HTML text cleanly."""
    if not text or not isinstance(text, str):
        return []
    matches = URL_REGEX.findall(text)
    urls = []
    for m in matches:
        # Strip trailing punctuation commonly attached in text
        u = m.rstrip('.,;:\'">)<]')
        if u and u not in urls:
            urls.append(u)
    return urls


def normalize_attachment(att: Any) -> AttachmentMetadata:
    """Normalizes raw attachment dictionary or object into AttachmentMetadata."""
    if isinstance(att, AttachmentMetadata):
        return att

    if not isinstance(att, dict):
        return AttachmentMetadata(filename="unknown_file", extension="", size=0)

    filename = str(att.get("filename") or att.get("name") or "unknown_file").strip()
    size = int(att.get("size") or 0)
    mime_type = str(att.get("mime_type") or att.get("content_type") or "").strip().lower()
    file_hash = str(att.get("hash") or att.get("md5") or att.get("sha256") or "").strip()

    # Determine extension
    ext = ""
    if "." in filename:
        ext = filename.split(".")[-1].lower()

    # Detect double extension (e.g. invoice.pdf.exe)
    parts = [p for p in filename.split(".") if p]
    is_double_ext = False
    if len(parts) >= 3:
        known_doc_exts = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "jpg", "png"}
        known_exec_exts = {"exe", "bat", "cmd", "ps1", "vbs", "js", "scr", "jar", "zip"}
        if parts[-2].lower() in known_doc_exts and parts[-1].lower() in known_exec_exts:
            is_double_ext = True

    # Detect archive
    is_archive = ext in {"zip", "tar", "gz", "rar", "7z", "iso"}

    return AttachmentMetadata(
        filename=filename,
        extension=ext,
        mime_type=mime_type,
        size=max(0, size),
        hash=file_hash if file_hash else None,
        is_archive=is_archive,
        is_double_extension=is_double_ext,
    )


def normalize_email_event(raw: Dict[str, Any]) -> PhishingEmailEvent:
    """
    Normalizes raw email input dictionary into a canonical PhishingEmailEvent.
    Gracefully handles missing or malformed fields without crashing.
    """
    msg_id = str(raw.get("message_id") or raw.get("id") or raw.get("event_id") or f"msg_{hash(str(raw))}").strip()

    # Parse timestamp
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

    sender = str(raw.get("sender") or raw.get("from") or "").strip()
    recipient = str(raw.get("recipient") or raw.get("to") or "").strip()
    subject = str(raw.get("subject") or "").strip()
    raw_body = str(raw.get("body") or raw.get("content") or "").strip()
    sanitized_body = sanitize_text(raw_body)

    # Domains
    sender_domain = raw.get("sender_domain") or extract_domain(sender)
    reply_to = str(raw.get("reply_to") or "").strip() or None
    return_path = str(raw.get("return_path") or "").strip() or None

    # Headers
    headers = raw.get("headers") or {}
    if not isinstance(headers, dict):
        headers = {}

    # Extract URLs from body, subject, and explicit urls field
    urls_list = list(raw.get("urls") or [])
    body_urls = extract_urls_from_text(raw_body)
    subj_urls = extract_urls_from_text(subject)

    combined_urls = []
    for u in urls_list + body_urls + subj_urls:
        if u and isinstance(u, str) and u not in combined_urls:
            combined_urls.append(u)

    # Attachments
    raw_attachments = raw.get("attachments") or []
    norm_attachments = [normalize_attachment(a) for a in raw_attachments if a]

    # Authentication Results (SPF, DKIM, DMARC)
    auth_results = raw.get("authentication_results") or {}
    if not isinstance(auth_results, dict):
        auth_results = {}

    source_ip = str(raw.get("source_ip") or "").strip() or None

    return PhishingEmailEvent(
        message_id=msg_id,
        timestamp=dt,
        sender=sender if sender else None,
        recipient=recipient if recipient else None,
        subject=subject,
        body=sanitized_body,
        headers=headers,
        urls=combined_urls,
        attachments=norm_attachments,
        sender_domain=sender_domain,
        reply_to=reply_to,
        return_path=return_path,
        authentication_results=auth_results,
        source_ip=source_ip,
    )
