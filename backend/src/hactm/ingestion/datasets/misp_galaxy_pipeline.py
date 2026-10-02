"""
MISP Galaxy Threat Intelligence Ingestion & Enrichment Indexing Pipeline.
Parses MISP Galaxy structured clusters (threat actors, malware, ransomware, attack patterns, tools, botnets)
and builds a indexed lookup store for HACTM Threat Intelligence Enrichment.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("hactm.datasets.misp_galaxy")


class MISPGalaxyPipeline:
    """Ingests MISP Galaxy JSON threat intelligence clusters into HACTM Threat Intel store."""

    def __init__(self, base_data_dir: Optional[Path] = None):
        self.base_dir = base_data_dir or Path(__file__).resolve().parents[5] / "data"
        self.raw_dir = self.base_dir / "raw" / "threat_intelligence" / "misp_galaxy" / "repo" / "clusters"
        self.processed_dir = self.base_dir / "processed" / "threat_intelligence"

        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def process_clusters(self) -> Dict[str, Any]:
        """Reads MISP Galaxy cluster files and indexes threat entities."""
        if not self.raw_dir.exists():
            # Fallback if git clone directory differs slightly
            self.raw_dir = self.base_dir / "raw" / "threat_intelligence" / "misp_galaxy"

        cluster_files = list(self.raw_dir.rglob("*.json"))
        indexed_entities: Dict[str, List[Dict[str, Any]]] = {
            "threat_actor": [],
            "malware": [],
            "ransomware": [],
            "attack_pattern": [],
            "tool": [],
            "botnet": []
        }

        total_clusters = 0
        total_elements = 0

        for c_file in cluster_files:
            if "schema" in c_file.name:
                continue
            try:
                with open(c_file, "r", encoding="utf-8", errors="ignore") as f:
                    cluster_data = json.load(f)
                
                if not isinstance(cluster_data, dict):
                    continue

                category = cluster_data.get("type", c_file.stem).lower()
                values = cluster_data.get("values", [])

                total_clusters += 1
                total_elements += len(values)

                # Categorize elements into threat intelligence index
                mapped_cat = "threat_actor"
                if "malware" in category or "ransomware" in category:
                    mapped_cat = "malware"
                elif "attack" in category or "mitre" in category:
                    mapped_cat = "attack_pattern"
                elif "tool" in category:
                    mapped_cat = "tool"
                elif "botnet" in category:
                    mapped_cat = "botnet"

                for elem in values[:20]:  # Index top elements per cluster
                    indexed_entities[mapped_cat].append({
                        "value": elem.get("value"),
                        "description": elem.get("description", "")[:150],
                        "uuid": elem.get("uuid"),
                        "cluster_name": cluster_data.get("name"),
                        "category": category,
                        "source": "MISP Galaxy",
                        "meta": elem.get("meta", {})
                    })
            except Exception as e:
                logger.warning(f"Error reading MISP cluster {c_file}: {e}")

        out_file = self.processed_dir / "misp_galaxy_index.json"
        summary_data = {
            "total_clusters_processed": total_clusters,
            "total_elements": total_elements,
            "category_counts": {k: len(v) for k, v in indexed_entities.items()},
            "indexed_entities": indexed_entities
        }
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        return {
            "dataset": "MISP_Galaxy",
            "total_clusters": total_clusters,
            "total_elements": total_elements,
            "output_file": str(out_file)
        }
