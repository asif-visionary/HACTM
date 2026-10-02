"""
EvaluationDatasetRegistry: Dataset manifest & time-aware dataset splitting registry for Evaluation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from hactm.evaluation.models import EvaluationDataset, SplitStrategy


class EvaluationDatasetRegistry:
    """Registry managing standard evaluation datasets for HACTM research."""

    def __init__(self):
        self.datasets: Dict[str, EvaluationDataset] = {}
        self._register_default_datasets()

    def _register_default_datasets(self):
        defaults = [
            EvaluationDataset(
                dataset_id="ds_cicids2017",
                dataset_name="CIC-IDS2017 Network Intrusion",
                version="2017.1",
                domain="NETWORK",
                source="Canadian Institute for Cybersecurity",
                sample_count=2830743,
                split_strategy=SplitStrategy.TIME_AWARE_SPLIT,
            ),
            EvaluationDataset(
                dataset_id="ds_phish_bench",
                dataset_name="Multi-Domain Phishing & BEC Corpus",
                version="2024.1",
                domain="PHISHING",
                source="Open Cybersecurity Research Archive",
                sample_count=52400,
                split_strategy=SplitStrategy.TIME_AWARE_SPLIT,
            ),
            EvaluationDataset(
                dataset_id="ds_cert_r4.2",
                dataset_name="CERT Insider Threat Dataset r4.2",
                version="r4.2",
                domain="UBA",
                source="Carnegie Mellon University CERT",
                sample_count=3200000,
                split_strategy=SplitStrategy.CROSS_SESSION_SPLIT,
            ),
            EvaluationDataset(
                dataset_id="ds_auth_logs",
                dataset_name="Enterprise Identity & Authentication Events",
                version="1.0.0",
                domain="IDENTITY",
                source="HACTM Synthetic Benchmark",
                sample_count=1500000,
                split_strategy=SplitStrategy.TIME_AWARE_SPLIT,
            ),
            EvaluationDataset(
                dataset_id="ds_tx_fraud",
                dataset_name="Financial Transaction Security Benchmark",
                version="2024.2",
                domain="TRANSACTION",
                source="HACTM Synthetic Financial Security Set",
                sample_count=980000,
                split_strategy=SplitStrategy.TIME_AWARE_SPLIT,
            ),
            EvaluationDataset(
                dataset_id="ds_cross_domain_master",
                dataset_name="HACTM End-to-End Multi-Domain Master Set",
                version="1.0.0",
                domain="CROSS_DOMAIN",
                source="HACTM Fused Attack Corpus",
                sample_count=5000000,
                split_strategy=SplitStrategy.TIME_AWARE_SPLIT,
            ),
        ]
        for ds in defaults:
            self.datasets[ds.dataset_id] = ds

    def register_dataset(self, dataset: EvaluationDataset) -> EvaluationDataset:
        self.datasets[dataset.dataset_id] = dataset
        return dataset

    def get_dataset(self, dataset_id: str) -> Optional[EvaluationDataset]:
        return self.datasets.get(dataset_id)

    def list_datasets(self, domain: Optional[str] = None) -> List[EvaluationDataset]:
        if domain:
            return [ds for ds in self.datasets.values() if ds.domain == domain]
        return list(self.datasets.values())

    def create_time_aware_split(
        self, samples: List[Dict[str, Any]], train_ratio: float = 0.70, val_ratio: float = 0.15
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Creates a time-aware split based on sample timestamps to prevent future info leakage."""
        sorted_samples = sorted(samples, key=lambda x: x.get("timestamp", ""))
        n = len(sorted_samples)

        train_end = int(train_ratio * n)
        val_end = int((train_ratio + val_ratio) * n)

        return {
            "train": sorted_samples[:train_end],
            "validation": sorted_samples[train_end:val_end],
            "test": sorted_samples[val_end:],
            "split_info": {
                "strategy": "TIME_AWARE_SPLIT",
                "train_count": train_end,
                "val_count": val_end - train_end,
                "test_count": n - val_end,
                "data_leakage_protected": True,
            },
        }
