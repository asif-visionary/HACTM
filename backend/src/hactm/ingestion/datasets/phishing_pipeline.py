"""
Phishing Email Dataset Ingestion & Feature Extraction Pipeline.
Processes Phishing and Legitimate Emails dataset for Phishing Intelligence Agent.
Extracts email text, subject, URLs, NLP features, and label distribution.
"""

import csv
import json
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("hactm.datasets.phishing")


class PhishingEmailPipeline:
    """Ingests email text datasets into HACTM Phishing Evidence format."""

    def __init__(self, base_data_dir: Optional[Path] = None):
        self.base_dir = base_data_dir or Path(__file__).resolve().parents[5] / "data"
        self.raw_dir = self.base_dir / "raw" / "phishing" / "phishing_legitimate_emails"
        self.processed_dir = self.base_dir / "processed" / "phishing"
        self.splits_dir = self.base_dir / "splits" / "phishing"

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.splits_dir.mkdir(parents=True, exist_ok=True)

    def extract_urls(self, text: str) -> List[str]:
        """Extracts URLs from email body using regular expressions."""
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        return re.findall(url_pattern, text)

    def process_phishing_emails(self, max_records: Optional[int] = None) -> Dict[str, Any]:
        """Processes phishing email dataset into normalized email evidence records."""
        csv_files = list(self.raw_dir.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError("No Phishing Email CSV found.")

        target_file = csv_files[0]
        records = []
        labels_count = {"phishing": 0, "legitimate": 0}

        with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                raw_text = row.get("text", row.get("Email Text", ""))
                label_val = str(row.get("label", row.get("Email Type", "0"))).strip()
                
                # Determine binary label (1 = phishing, 0 = legitimate)
                is_phishing = 1 if label_val in ["1", "Phishing Email", "phishing"] else 0
                label_str = "phishing" if is_phishing == 1 else "legitimate"
                labels_count[label_str] += 1

                # Extract subject line if present in text
                subject = ""
                if raw_text.startswith("Subject:"):
                    parts = raw_text.split("\n\n", 1)
                    subject = parts[0].replace("Subject:", "").strip()
                    body = parts[1] if len(parts) > 1 else raw_text
                else:
                    body = raw_text

                urls = self.extract_urls(raw_text)

                record = {
                    "email_id": f"phish_email_{count}",
                    "subject": subject,
                    "body_snippet": body[:200],
                    "body_length": len(body),
                    "url_count": len(urls),
                    "urls": urls[:5],
                    "is_phishing": is_phishing,
                    "label_category": label_str,
                    "phishing_type": row.get("phishing_type", "general"),
                    "severity": row.get("severity", "low"),
                    "confidence": float(row.get("confidence", 0.95)) if row.get("confidence", "").replace('.', '', 1).isdigit() else 0.95,
                    "dataset_source": "phishing_legitimate_emails_2026"
                }
                records.append(record)
                count += 1
                if max_records and count >= max_records:
                    break

        out_file = self.processed_dir / "phishing_emails_processed.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

        # Generate splits
        n = len(records)
        train_idx = int(n * 0.8)
        val_idx = int(n * 0.9)

        splits = {
            "train": len(records[:train_idx]),
            "validation": len(records[train_idx:val_idx]),
            "test": len(records[val_idx:])
        }
        with open(self.splits_dir / "phishing_split.json", "w", encoding="utf-8") as f:
            json.dump(splits, f, indent=2)

        return {
            "dataset": "Phishing_Legitimate_Emails_2026",
            "total_processed": len(records),
            "label_distribution": labels_count,
            "output_file": str(out_file)
        }
