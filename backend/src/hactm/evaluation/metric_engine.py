"""
MetricEngine: Comprehensive metric calculation engine for Evaluation HACTM.
Handles edge cases (single-class datasets, missing timestamps, zero positives) with strict NOT_AVAILABLE output.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
import numpy as np

from hactm.evaluation.models import ResultStatus, MetricResult


class MetricEngine:
    """Calculates quantitative detection, calibration, efficiency, and micro-segmentation metrics."""

    @staticmethod
    def calculate_precision(tp: int, fp: int) -> Tuple[Optional[float], ResultStatus]:
        if tp + fp == 0:
            return None, ResultStatus.NOT_AVAILABLE
        return round(float(tp) / float(tp + fp), 4), ResultStatus.COMPLETED

    @staticmethod
    def calculate_recall(tp: int, fn: int) -> Tuple[Optional[float], ResultStatus]:
        if tp + fn == 0:
            return None, ResultStatus.NOT_AVAILABLE
        return round(float(tp) / float(tp + fn), 4), ResultStatus.COMPLETED

    @staticmethod
    def calculate_f1(precision: Optional[float], recall: Optional[float]) -> Tuple[Optional[float], ResultStatus]:
        if precision is None or recall is None or (precision + recall) == 0:
            return None, ResultStatus.NOT_AVAILABLE
        f1 = (2.0 * precision * recall) / (precision + recall)
        return round(float(f1), 4), ResultStatus.COMPLETED

    @staticmethod
    def calculate_fpr(fp: int, tn: int) -> Tuple[Optional[float], ResultStatus]:
        if fp + tn == 0:
            return None, ResultStatus.NOT_AVAILABLE
        return round(float(fp) / float(fp + tn), 4), ResultStatus.COMPLETED

    @staticmethod
    def calculate_fnr(fn: int, tp: int) -> Tuple[Optional[float], ResultStatus]:
        if fn + tp == 0:
            return None, ResultStatus.NOT_AVAILABLE
        return round(float(fn) / float(fn + tp), 4), ResultStatus.COMPLETED

    @staticmethod
    def calculate_auroc(y_true: List[int], y_scores: List[float]) -> Tuple[Optional[float], ResultStatus]:
        """Calculates Area Under ROC Curve. Returns NOT_AVAILABLE for single-class datasets."""
        if not y_true or len(set(y_true)) < 2:
            return None, ResultStatus.NOT_AVAILABLE  # Single-class dataset edge case

        positives = [score for true, score in zip(y_true, y_scores) if true == 1]
        negatives = [score for true, score in zip(y_true, y_scores) if true == 0]

        if not positives or not negatives:
            return None, ResultStatus.NOT_AVAILABLE

        # Mann-Whitney U statistic calculation for AUROC
        u = 0
        for p in positives:
            for n in negatives:
                if p > n:
                    u += 1.0
                elif p == n:
                    u += 0.5

        auroc = u / (len(positives) * len(negatives))
        return round(float(auroc), 4), ResultStatus.COMPLETED

    @staticmethod
    def calculate_ece(y_true: List[int], y_prob: List[float], n_bins: int = 10) -> Tuple[Optional[float], ResultStatus]:
        """Calculates Expected Calibration Error (ECE)."""
        if not y_true or len(y_true) != len(y_prob):
            return None, ResultStatus.NOT_AVAILABLE

        bins = np.linspace(0.0, 1.0, n_bins + 1)
        ece = 0.0
        n_samples = len(y_true)

        for i in range(n_bins):
            bin_lower = bins[i]
            bin_upper = bins[i + 1]

            in_bin = [(t, p) for t, p in zip(y_true, y_prob) if bin_lower <= p < bin_upper or (i == n_bins - 1 and p == bin_upper)]
            if not in_bin:
                continue

            bin_acc = sum(t for t, _ in in_bin) / len(in_bin)
            bin_conf = sum(p for _, p in in_bin) / len(in_bin)
            ece += (len(in_bin) / n_samples) * abs(bin_acc - bin_conf)

        return round(float(ece), 4), ResultStatus.COMPLETED

    @staticmethod
    def calculate_brier(y_true: List[int], y_prob: List[float]) -> Tuple[Optional[float], ResultStatus]:
        """Calculates Brier Score (Mean Squared Error of probability predictions)."""
        if not y_true or len(y_true) != len(y_prob):
            return None, ResultStatus.NOT_AVAILABLE

        brier = sum((p - t) ** 2 for t, p in zip(y_true, y_prob)) / len(y_true)
        return round(float(brier), 4), ResultStatus.COMPLETED

    @staticmethod
    def calculate_latency_percentiles(latencies_ms: List[float]) -> Dict[str, float]:
        """Calculates P50, P95, and P99 latency percentiles."""
        if not latencies_ms:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_lat = sorted(latencies_ms)
        n = len(sorted_lat)
        p50 = sorted_lat[int(0.50 * n)]
        p95 = sorted_lat[min(n - 1, int(0.95 * n))]
        p99 = sorted_lat[min(n - 1, int(0.99 * n))]

        return {"p50": round(p50, 2), "p95": round(p95, 2), "p99": round(p99, 2)}

    @staticmethod
    def calculate_micro_segmentation_metrics(
        reachable_nodes: int, total_nodes: int, false_isolations: int, legitimate_total: int
    ) -> Dict[str, Any]:
        """Computes Blast Radius, Lateral Reachability, and False Isolation Rate."""
        blast_radius = round(float(reachable_nodes) / max(1.0, float(total_nodes)), 4)
        false_iso_rate = round(float(false_isolations) / max(1.0, float(legitimate_total)), 4)

        return {
            "blast_radius_score": blast_radius,
            "lateral_reachability_nodes": reachable_nodes,
            "false_isolation_rate": false_iso_rate,
        }
