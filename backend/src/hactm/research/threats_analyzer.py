"""
Threats to Validity Analyzer for Research Validation.
Provides structured identification of internal, external, construct, and statistical conclusion validity threats.
"""

from hactm.research.models import ThreatsToValidityResponse


class ThreatsToValidityAnalyzer:
    """Analyzes threats to research validity across all 4 classical scientific dimensions."""

    @staticmethod
    def analyze_threats() -> ThreatsToValidityResponse:
        return ThreatsToValidityResponse(
            internal_validity=[
                "Potential implementation errors in synthetic scenario generators or feature extractors.",
                "Risk of implicit hyperparameter tuning leakage if evaluation splits were inspected during design.",
                "Possible train/test temporal contamination if time-series boundaries were randomly shuffled instead of strictly split.",
                "Sensitivity of small-scale bootstrap iterations to outlier events in small test cohorts.",
            ],
            external_validity=[
                "Evaluation relies primarily on public benchmark datasets (CIC-IDS2017, UNSW-NB15) which may not fully reflect enterprise traffic.",
                "Simulated attack scenarios operate under controlled environments with static network topology.",
                "Agent latency measurements were benchmarked on standard developer workstation hardware rather than cloud-scale clusters.",
                "Evolving zero-day attack patterns in live production environments may exceed synthetic drift simulations.",
            ],
            construct_validity=[
                "The unified Cyber Risk Score represents an ordinal risk index rather than a strict frequentist probability.",
                "Security agent confidence ratings represent model certainty rather than perfectly calibrated posteriors.",
                "Simulated micro-segmentation containment time assumes zero-latency network controller API response.",
                "Attack evidence graph relationships represent temporal correlation and structural adjacency, not definitive causality.",
            ],
            statistical_conclusion_validity=[
                "Sample size limitations in specific rare attack categories (e.g. spear phishing) increase metric variance.",
                "Multiple hypothesis comparisons across dozens of metric pairs require family-wise error rate corrections.",
                "Non-independent event streams within identical sessions require non-parametric paired tests (Wilcoxon).",
                "Confidence intervals generated via bootstrap assume representative sampling from the underlying benchmark distribution.",
            ],
        )
