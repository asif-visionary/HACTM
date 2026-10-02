"""
Zero-Day Evaluation Package for HACTM.
Exposes LeakageGuard, DatasetCompatibilityChecker, TemporalZeroDayEvaluator,
AttackFamilyHoldoutEvaluator, CalibrationEngine, FixedFPREvaluator, and ResourceProfiler.
"""

from hactm.research.zero_day.leakage_guard import LeakageGuard, LeakageCheckResult
from hactm.research.zero_day.compatibility import DatasetCompatibilityChecker, CompatibilityResult
from hactm.research.zero_day.temporal_eval import TemporalZeroDayEvaluator, TemporalEvaluationResult, TemporalSplitManifest
from hactm.research.zero_day.family_holdout import AttackFamilyHoldoutEvaluator, FamilyHoldoutResult
from hactm.research.zero_day.calibration import CalibrationEngine, CalibrationResult, ReliabilityBin
from hactm.research.zero_day.fixed_fpr import FixedFPREvaluator, FixedFPREvaluationResult, FixedFPROperatingPoint
from hactm.research.zero_day.resource_profiler import ResourceProfiler, ResourceUtilizationResult, TimeToAlertBreakdown

__all__ = [
    "LeakageGuard",
    "LeakageCheckResult",
    "DatasetCompatibilityChecker",
    "CompatibilityResult",
    "TemporalZeroDayEvaluator",
    "TemporalEvaluationResult",
    "TemporalSplitManifest",
    "AttackFamilyHoldoutEvaluator",
    "FamilyHoldoutResult",
    "CalibrationEngine",
    "CalibrationResult",
    "ReliabilityBin",
    "FixedFPREvaluator",
    "FixedFPREvaluationResult",
    "FixedFPROperatingPoint",
    "ResourceProfiler",
    "ResourceUtilizationResult",
    "TimeToAlertBreakdown"
]
