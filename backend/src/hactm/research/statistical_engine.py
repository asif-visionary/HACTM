"""
Statistical Validation Engine for Research Validation.
Provides descriptive statistics, confidence intervals, paired experiment analysis,
effect size calculation, and multiple comparison correction.
"""

import math
import random
from typing import List, Dict, Any, Optional

from hactm.research.models import (
    DescriptiveStats,
    ConfidenceIntervalResult,
    PairedAnalysisResult,
    EffectSizeResult,
    MultipleComparisonResult,
    StatisticalValidationResponse,
)


class StatisticalValidationEngine:
    """Rigorous statistical validation engine for experimental metrics."""

    @staticmethod
    def compute_descriptive_stats(data: List[float], metric_name: str) -> DescriptiveStats:
        """Computes summary statistics, quartiles, and percentiles."""
        if not data:
            return DescriptiveStats(
                metric=metric_name, sample_size=0, mean=0.0, median=0.0,
                std_dev=0.0, variance=0.0, min_val=0.0, max_val=0.0,
                iqr=0.0, p50=0.0, p90=0.0, p95=0.0, p99=0.0
            )

        n = len(data)
        sorted_data = sorted(data)
        mean_val = sum(sorted_data) / n

        variance_val = sum((x - mean_val) ** 2 for x in sorted_data) / (n - 1) if n > 1 else 0.0
        std_dev_val = math.sqrt(variance_val)

        def percentile(arr: List[float], p: float) -> float:
            if not arr:
                return 0.0
            k = (len(arr) - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return arr[int(k)]
            d0 = arr[int(f)] * (c - k)
            d1 = arr[int(c)] * (k - f)
            return d0 + d1

        p25 = percentile(sorted_data, 0.25)
        p50 = percentile(sorted_data, 0.50)
        p75 = percentile(sorted_data, 0.75)
        p90 = percentile(sorted_data, 0.90)
        p95 = percentile(sorted_data, 0.95)
        p99 = percentile(sorted_data, 0.99)
        iqr_val = p75 - p25

        return DescriptiveStats(
            metric=metric_name,
            sample_size=n,
            mean=round(mean_val, 4),
            median=round(p50, 4),
            std_dev=round(std_dev_val, 4),
            variance=round(variance_val, 4),
            min_val=round(sorted_data[0], 4),
            max_val=round(sorted_data[-1], 4),
            iqr=round(iqr_val, 4),
            p50=round(p50, 4),
            p90=round(p90, 4),
            p95=round(p95, 4),
            p99=round(p99, 4),
        )

    @staticmethod
    def compute_bootstrap_ci(
        data: List[float],
        metric_name: str,
        confidence_level: float = 0.95,
        num_bootstrap: int = 1000,
        random_seed: int = 42
    ) -> ConfidenceIntervalResult:
        """Computes bootstrap non-parametric 95% confidence intervals."""
        if not data:
            return ConfidenceIntervalResult(
                metric=metric_name, sample_size=0, estimate=0.0,
                confidence_level=confidence_level, lower_bound=0.0, upper_bound=0.0, method="bootstrap"
            )

        rng = random.Random(random_seed)
        n = len(data)
        estimate = sum(data) / n

        bootstrap_means: List[float] = []
        for _ in range(num_bootstrap):
            sample = [rng.choice(data) for _ in range(n)]
            bootstrap_means.append(sum(sample) / n)

        bootstrap_means.sort()
        alpha = 1.0 - confidence_level
        lower_idx = int(num_bootstrap * (alpha / 2.0))
        upper_idx = int(num_bootstrap * (1.0 - alpha / 2.0))

        lower_bound = bootstrap_means[max(0, min(lower_idx, num_bootstrap - 1))]
        upper_bound = bootstrap_means[max(0, min(upper_idx, num_bootstrap - 1))]

        return ConfidenceIntervalResult(
            metric=metric_name,
            sample_size=n,
            estimate=round(estimate, 4),
            confidence_level=confidence_level,
            lower_bound=round(lower_bound, 4),
            upper_bound=round(upper_bound, 4),
            method="bootstrap",
        )

    @staticmethod
    def compute_paired_analysis(
        baseline: List[float],
        proposed: List[float],
        metric_name: str
    ) -> PairedAnalysisResult:
        """Performs paired experiment analysis (Wilcoxon signed-rank / paired t-test approximation)."""
        n = min(len(baseline), len(proposed))
        if n == 0:
            return PairedAnalysisResult(
                test_name="Wilcoxon Signed-Rank Test",
                metric=metric_name, baseline=0.0, proposed_method=0.0,
                sample_size=0, statistic=0.0, p_value=1.0, effect_size=0.0,
                confidence_interval=[0.0, 0.0], assumptions=["Paired measurements across identical scenarios"]
            )

        diffs = [proposed[i] - baseline[i] for i in range(n)]
        avg_baseline = sum(baseline[:n]) / n
        avg_proposed = sum(proposed[:n]) / n

        # Wilcoxon signed-rank test approximation
        non_zero_diffs = [d for d in diffs if d != 0]
        if not non_zero_diffs:
            p_val = 1.0
            stat = 0.0
        else:
            abs_diffs = sorted(enumerate(non_zero_diffs), key=lambda x: abs(x[1]))
            w_plus = 0.0
            for rank, (idx, val) in enumerate(abs_diffs, start=1):
                if val > 0:
                    w_plus += rank
            stat = w_plus
            # Approximate z-score for Wilcoxon test
            m = len(non_zero_diffs)
            mean_w = m * (m + 1) / 4.0
            var_w = m * (m + 1) * (2 * m + 1) / 24.0
            z = (w_plus - mean_w) / math.sqrt(var_w) if var_w > 0 else 0.0
            # Two-tailed p-value approximation via normal CDF
            p_val = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0))))

        # Effect size (Cohen's d for paired samples)
        mean_diff = sum(diffs) / n if n > 0 else 0.0
        std_diff = math.sqrt(sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)) if n > 1 else 0.0
        effect_d = mean_diff / std_diff if std_diff > 0 else 0.0

        ci_lower = mean_diff - 1.96 * (std_diff / math.sqrt(n)) if n > 0 else 0.0
        ci_upper = mean_diff + 1.96 * (std_diff / math.sqrt(n)) if n > 0 else 0.0

        return PairedAnalysisResult(
            test_name="Wilcoxon Signed-Rank Test",
            metric=metric_name,
            baseline=round(avg_baseline, 4),
            proposed_method=round(avg_proposed, 4),
            sample_size=n,
            statistic=round(stat, 4),
            p_value=round(p_val, 6),
            effect_size=round(effect_d, 4),
            confidence_interval=[round(ci_lower, 4), round(ci_upper, 4)],
            assumptions=["Paired measurements evaluated on identical benchmark scenarios"],
        )

    @staticmethod
    def compute_effect_size(
        baseline_data: List[float],
        proposed_data: List[float],
        metric_name: str
    ) -> EffectSizeResult:
        """Computes Cohen's d, Cliff's delta, absolute difference, and relative change."""
        n1 = len(baseline_data)
        n2 = len(proposed_data)

        if n1 == 0 or n2 == 0:
            return EffectSizeResult(
                metric=metric_name, baseline=0.0, proposed=0.0,
                cohens_d=0.0, cliffs_delta=0.0, absolute_difference=0.0, relative_change=None
            )

        mean1 = sum(baseline_data) / n1
        mean2 = sum(proposed_data) / n2
        abs_diff = mean2 - mean1

        rel_change = None
        if abs(mean1) > 1e-9:
            rel_change = abs_diff / mean1

        # Cohen's d
        var1 = sum((x - mean1) ** 2 for x in baseline_data) / (n1 - 1) if n1 > 1 else 0.0
        var2 = sum((x - mean2) ** 2 for x in proposed_data) / (n2 - 1) if n2 > 1 else 0.0
        pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2)) if (n1 + n2) > 2 else 0.0
        cohens_d = abs_diff / pooled_std if pooled_std > 0 else 0.0

        # Cliff's delta
        more = 0
        less = 0
        for x in proposed_data:
            for y in baseline_data:
                if x > y:
                    more += 1
                elif x < y:
                    less += 1
        cliffs_delta = (more - less) / (n1 * n2) if (n1 * n2) > 0 else 0.0

        return EffectSizeResult(
            metric=metric_name,
            baseline=round(mean1, 4),
            proposed=round(mean2, 4),
            cohens_d=round(cohens_d, 4),
            cliffs_delta=round(cliffs_delta, 4),
            absolute_difference=round(abs_diff, 4),
            relative_change=round(rel_change, 4) if rel_change is not None else None,
        )

    @staticmethod
    def adjust_multiple_comparisons(
        p_values: Dict[str, float],
        family_name: str = "HACTM Evaluation Family",
        method: str = "Benjamini-Hochberg"
    ) -> MultipleComparisonResult:
        """Applies Bonferroni or Benjamini-Hochberg correction."""
        m = len(p_values)
        if m == 0:
            return MultipleComparisonResult(
                comparison_family=family_name, correction_method=method,
                raw_p_values={}, adjusted_p_values={}
            )

        adjusted: Dict[str, float] = {}

        if method.lower() == "bonferroni":
            for k, p in p_values.items():
                adjusted[k] = min(1.0, p * m)
        else:
            # Benjamini-Hochberg
            sorted_items = sorted(p_values.items(), key=lambda x: x[1])
            adj_p = [0.0] * m
            prev = 1.0
            for i in range(m - 1, -1, -1):
                k, p = sorted_items[i]
                rank = i + 1
                val = min(prev, p * m / rank)
                adj_p[i] = min(1.0, val)
                prev = adj_p[i]

            for i, (k, _) in enumerate(sorted_items):
                adjusted[k] = round(adj_p[i], 6)

        return MultipleComparisonResult(
            comparison_family=family_name,
            correction_method=method,
            raw_p_values={k: round(v, 6) for k, v in p_values.items()},
            adjusted_p_values=adjusted,
        )
