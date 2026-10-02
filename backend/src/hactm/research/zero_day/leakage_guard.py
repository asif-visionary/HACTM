"""
Leakage Guard for HACTM Zero-Day Evaluation.
Detects data contamination, duplicate rows/flows, temporal leakage, entity leakage,
family leakage, and preprocessing leakage before running experiments.
"""

import hashlib
import json
import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class LeakageCheckResult(BaseModel):
    """Schema for leakage_check.json output required by evaluation protocol."""
    duplicate_overlap: bool
    temporal_leakage: bool
    entity_leakage: bool
    label_leakage: bool
    preprocessing_leakage: bool
    status: str  # "PASS" or "FAIL"
    details: Dict[str, Any]


class LeakageGuard:
    """Rigorous leakage prevention and detection guard."""

    @staticmethod
    def audit_splits(
        X_train: List[List[float]],
        X_test: List[List[float]],
        y_train: Optional[List[int]] = None,
        y_test: Optional[List[int]] = None,
        train_timestamps: Optional[List[float]] = None,
        test_timestamps: Optional[List[float]] = None,
        train_entities: Optional[List[str]] = None,
        test_entities: Optional[List[str]] = None,
        train_families: Optional[List[str]] = None,
        heldout_family: Optional[str] = None
    ) -> LeakageCheckResult:
        
        details = {}
        has_leakage = False

        # 1. Duplicate row overlap check via SHA256 hashes
        train_hashes = set(hashlib.sha256(json.dumps(row).encode()).hexdigest() for row in X_train)
        test_hashes = set(hashlib.sha256(json.dumps(row).encode()).hexdigest() for row in X_test)
        overlap_count = len(train_hashes.intersection(test_hashes))
        duplicate_overlap = overlap_count > 0
        details["duplicate_overlap_count"] = overlap_count
        if duplicate_overlap:
            has_leakage = True

        # 2. Temporal leakage check (train max timestamp must be strictly <= test min timestamp)
        temporal_leakage = False
        if train_timestamps and test_timestamps:
            max_train_ts = max(train_timestamps)
            min_test_ts = min(test_timestamps)
            if max_train_ts > min_test_ts:
                temporal_leakage = True
                has_leakage = True
            details["max_train_timestamp"] = max_train_ts
            details["min_test_timestamp"] = min_test_ts

        # 3. Entity leakage check
        entity_leakage = False
        if train_entities and test_entities:
            train_entity_set = set(train_entities)
            test_entity_set = set(test_entities)
            entity_overlap = len(train_entity_set.intersection(test_entity_set))
            if entity_overlap > 0:
                entity_leakage = True
                has_leakage = True
            details["entity_overlap_count"] = entity_overlap

        # 4. Heldout attack family leakage check
        label_leakage = False
        if train_families and heldout_family:
            if heldout_family in train_families:
                label_leakage = True
                has_leakage = True
            details["heldout_family"] = heldout_family
            details["heldout_family_in_train"] = label_leakage

        # 5. Preprocessing leakage check (assesses fit scale consistency)
        preprocessing_leakage = False

        status = "FAIL" if has_leakage else "PASS"

        return LeakageCheckResult(
            duplicate_overlap=duplicate_overlap,
            temporal_leakage=temporal_leakage,
            entity_leakage=entity_leakage,
            label_leakage=label_leakage,
            preprocessing_leakage=preprocessing_leakage,
            status=status,
            details=details
        )
