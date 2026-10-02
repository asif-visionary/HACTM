"""
Zero-Day Detector Package for HACTM.
Exposes ZeroDayDetector interface, DNNDetector, CNNDetector, BayesianUncertaintyDetector,
ZeroDayCandidateScoreCalculator, AgentDisagreementTracker, and ZeroDayEscalationPolicy.
"""

from hactm.network.detectors.zero_day.base import ZeroDayDetector, ZeroDayDetectionResult
from hactm.network.detectors.zero_day.dnn_detector import DNNDetector
from hactm.network.detectors.zero_day.cnn_detector import CNNDetector
from hactm.network.detectors.zero_day.bayesian_detector import BayesianUncertaintyDetector
from hactm.network.detectors.zero_day.candidate_score import (
    ZeroDayCandidateScoreCalculator,
    ZeroDayCandidateResult,
    AgentDisagreementTracker,
    AgentDisagreementResult,
    ZeroDayEscalationPolicy
)

__all__ = [
    "ZeroDayDetector",
    "ZeroDayDetectionResult",
    "DNNDetector",
    "CNNDetector",
    "BayesianUncertaintyDetector",
    "ZeroDayCandidateScoreCalculator",
    "ZeroDayCandidateResult",
    "AgentDisagreementTracker",
    "AgentDisagreementResult",
    "ZeroDayEscalationPolicy"
]
