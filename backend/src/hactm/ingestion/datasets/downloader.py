"""
Dataset Downloader, Verifier, and Manifest Generator for HACTM.
Handles downloading, verifying SHA-256 hashes, extracting archives, and generating
json manifests for ToN-IoT, BoT-IoT, Phishing Emails, NIST FRTE/FATE, MISP Galaxy, and Agent Failure datasets.
"""

import os
import sys
import json
import time
import zipfile
import hashlib
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("hactm.datasets.downloader")


class DatasetDownloader:
    """Orchestrates resource acquisition, verification, and manifest generation."""

    def __init__(self, base_data_dir: Optional[Path] = None):
        if base_data_dir:
            self.base_dir = Path(base_data_dir)
        else:
            # Point to root HACTM/data directory
            self.base_dir = Path(__file__).resolve().parents[5] / "data"
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.manifests_dir = self.base_dir / "manifests"
        self.splits_dir = self.base_dir / "splits"

        self._init_directories()

    def _init_directories(self) -> None:
        """Creates required directory hierarchy."""
        dirs = [
            self.raw_dir / "network" / "ton_iot",
            self.raw_dir / "network" / "bot_iot",
            self.raw_dir / "phishing" / "phishing_legitimate_emails",
            self.raw_dir / "identity" / "nist_frte_fate",
            self.raw_dir / "threat_intelligence" / "misp_galaxy",
            self.raw_dir / "agent_reliability" / "llm_agent_failure",
            self.processed_dir / "network",
            self.processed_dir / "phishing",
            self.processed_dir / "identity",
            self.processed_dir / "threat_intelligence",
            self.processed_dir / "agent_reliability",
            self.manifests_dir,
            self.splits_dir / "network",
            self.splits_dir / "phishing",
            self.splits_dir / "identity",
            self.splits_dir / "agent_reliability"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def calculate_sha256(filepath: Path) -> str:
        """Calculates SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_manifest(
        self,
        dataset_name: str,
        source_url: str,
        source_type: str,
        target_dir: Path,
        citation: str = "",
        license_notes: str = "",
        version: str = "1.0.0",
        commit_or_release: str = "main",
        status: str = "downloaded"
    ) -> Dict[str, Any]:
        """Generates and persists dataset_manifest.json."""
        files_info = []
        for file in target_dir.rglob("*"):
            if file.is_file() and not file.name.endswith("_manifest.json"):
                rel_path = str(file.relative_to(target_dir))
                size_bytes = file.stat().st_size
                sha256 = self.calculate_sha256(file)
                files_info.append({
                    "relative_path": rel_path,
                    "size_bytes": size_bytes,
                    "sha256": sha256
                })

        manifest_data = {
            "dataset_name": dataset_name,
            "source_url": source_url,
            "source_type": source_type,
            "download_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "version": version,
            "commit_or_release": commit_or_release,
            "file_count": len(files_info),
            "files": files_info,
            "license_or_usage_notes": license_notes,
            "citation": citation,
            "preprocessing_version": "1.0.0",
            "status": status
        }

        manifest_path = self.manifests_dir / f"{dataset_name.lower().replace('-', '_')}_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        logger.info(f"Manifest written to {manifest_path}")
        return manifest_data

    def download_file(self, url: str, dest_path: Path) -> bool:
        """Downloads a remote URL to destination path safely."""
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HACTM Research Engine"}
            )
            with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, "wb") as out_file:
                out_file.write(response.read())
            return True
        except Exception as e:
            logger.warning(f"Failed to download {url}: {e}")
            return False
