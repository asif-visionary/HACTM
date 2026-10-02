"""
Temporal Zero-Day Evaluator for HACTM.
Enforces non-random temporal train/val/test splits to measure temporal generalization without data leakage.
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from hactm.network.detectors.zero_day.base import ZeroDayDetector
from hactm.research.zero_day.leakage_guard import LeakageGuard


class TemporalSplitManifest(BaseModel):
    """Manifest recording exact temporal boundaries derived from dataset."""
    train_start: float
    train_end: float
    validation_start: float
    validation_end: float
    test_start: float
    test_end: float
    train_samples: int
    validation_samples: int
    test_samples: int
    temporal_leakage_detected: bool


class TemporalEvaluationResult(BaseModel):
    """Structured temporal generalization evaluation summary."""
    manifest: TemporalSplitManifest
    train_metrics: Dict[str, float]
    validation_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    temporal_degradation_pct: float  # Drop in F1 score from Train/Val to Future Test


class TemporalZeroDayEvaluator:
    """Runs temporal generalization experiments using timestamped security telemetry."""

    @staticmethod
    def split_by_time(
        X: List[List[float]],
        y: List[int],
        timestamps: List[float],
        train_ratio: float = 0.60,
        val_ratio: float = 0.20
    ) -> Tuple[
        List[List[float]], List[int], List[float],
        List[List[float]], List[int], List[float],
        List[List[float]], List[int], List[float],
        TemporalSplitManifest
    ]:
        # Sort items strictly by timestamp
        sorted_indices = sorted(range(len(timestamps)), key=lambda k: timestamps[k])
        
        X_sorted = [X[i] for i in sorted_indices]
        y_sorted = [y[i] for i in sorted_indices]
        ts_sorted = [timestamps[i] for i in sorted_indices]

        n = len(ts_sorted)
        train_end_idx = int(n * train_ratio)
        val_end_idx = int(n * (train_ratio + val_ratio))

        X_train, y_train, ts_train = X_sorted[:train_end_idx], y_sorted[:train_end_idx], ts_sorted[:train_end_idx]
        X_val, y_val, ts_val = X_sorted[train_end_idx:val_end_idx], y_sorted[train_end_idx:val_end_idx], ts_sorted[train_end_idx:val_end_idx]
        X_test, y_test, ts_test = X_sorted[val_end_idx:], y_sorted[val_end_idx:], ts_sorted[val_end_idx:]

        # Leakage audit
        leakage = LeakageGuard.audit_splits(
            X_train=X_train,
            X_test=X_test,
            train_timestamps=ts_train,
            test_timestamps=ts_test
        )

        manifest = TemporalSplitManifest(
            train_start=ts_train[0] if ts_train else 0.0,
            train_end=ts_train[-1] if ts_train else 0.0,
            validation_start=ts_val[0] if ts_val else 0.0,
            validation_end=ts_val[-1] if ts_val else 0.0,
            test_start=ts_test[0] if ts_test else 0.0,
            test_end=ts_test[-1] if ts_test else 0.0,
            train_samples=len(X_train),
            validation_samples=len(X_val),
            test_samples=len(X_test),
            temporal_leakage_detected=leakage.temporal_leakage
        )

        return X_train, y_train, ts_train, X_val, y_val, ts_val, X_test, y_test, ts_test, manifest

    @classmethod
    def evaluate_detector(
        self,
        detector: ZeroDayDetector,
        X_train: List[List[float]],
        y_train: List[int],
        X_val: List[List[float]],
        y_val: List[int],
        X_test: List[List[float]],
        y_test: List[int],
        manifest: TemporalSplitManifest
    ) -> TemporalEvaluationResult:
        
        # Fit on earlier time window
        detector.fit(X_train, y_train)

        train_metrics = detector.evaluate(X_train, y_train)
        val_metrics = detector.evaluate(X_val, y_val)
        test_metrics = detector.evaluate(X_test, y_test)

        val_f1 = val_metrics.get("f1", 0.0)
        test_f1 = test_metrics.get("f1", 0.0)
        degradation = round(((val_f1 - test_f1) / max(0.001, val_f1)) * 100.0, 2)

        return TemporalEvaluationResult(
            manifest=manifest,
            train_metrics=train_metrics,
            validation_metrics=val_metrics,
            test_metrics=test_metrics,
            temporal_degradation_pct=degradation
        )
