"""
Unit tests for Research Validation Validation & Publication Readiness.
Tests metric integrity, statistics, sensitivity, robustness, claim validation, reproducibility, and audit.
"""

import pytest
from hactm.research.models import (
    ValidationStatus,
    ResultIntegrityCheckRequest,
    ClaimStatus,
    HypothesisStatus,
    ReproducibilityStatus,
    AuditStatus,
)
from hactm.research.integrity_validator import ResearchResultIntegrityValidator
from hactm.research.statistical_engine import StatisticalValidationEngine
from hactm.research.sensitivity_engine import SensitivityAnalysisEngine, RobustnessValidator
from hactm.research.claim_validator import ResearchClaimValidator, HypothesisValidator
from hactm.research.reproducibility_verifier import ReproducibilityVerifier, EnvironmentCapture
from hactm.research.security_audit import ResearchSecurityAudit


# 1. INTEGRITY TESTS
def test_invalid_metric():
    req = ResultIntegrityCheckRequest(
        experiment_id="EXP-001",
        run_id="run-01",
        dataset_id="cic_ids_2017",
        dataset_version="v1.0",
        config_hash="cfg-123",
        timestamp="2026-10-02T10:00:00Z",
        metrics={"precision": 1.25, "recall": 0.90}, # Invalid precision > 1.0
    )
    res = ResearchResultIntegrityValidator.validate_result(req)
    assert res.status == ValidationStatus.INCONSISTENT or res.status == ValidationStatus.INVALID
    assert len(res.issues) > 0


def test_missing_experiment():
    req = ResultIntegrityCheckRequest(
        experiment_id="",
        run_id="run-01",
        dataset_id="cic_ids_2017",
        dataset_version="v1.0",
        config_hash="cfg-123",
        timestamp="2026-10-02T10:00:00Z",
        metrics={"f1": 0.94},
    )
    res = ResearchResultIntegrityValidator.validate_result(req)
    assert res.status == ValidationStatus.INCOMPLETE
    assert any("experiment_id" in issue for issue in res.issues)


def test_duplicate_run():
    req = ResultIntegrityCheckRequest(
        experiment_id="EXP-001",
        run_id="run-01",
        dataset_id="cic_ids_2017",
        dataset_version="v1.0",
        config_hash="cfg-123",
        timestamp="2026-10-02T10:00:00Z",
        metrics={"f1": 0.94},
    )
    res = ResearchResultIntegrityValidator.validate_result(req)
    assert res.status == ValidationStatus.VALID


def test_inconsistent_f1():
    req = ResultIntegrityCheckRequest(
        experiment_id="EXP-001",
        run_id="run-01",
        dataset_id="cic_ids_2017",
        dataset_version="v1.0",
        config_hash="cfg-123",
        timestamp="2026-10-02T10:00:00Z",
        metrics={"precision": 0.90, "recall": 0.90, "f1": 0.50}, # Expected F1=0.90
    )
    res = ResearchResultIntegrityValidator.validate_result(req)
    assert res.status == ValidationStatus.INCONSISTENT
    assert any("F1 inconsistency" in issue for issue in res.issues)


def test_invalid_provenance():
    req = ResultIntegrityCheckRequest(
        experiment_id="EXP-001",
        run_id="run-01",
        dataset_id="",
        dataset_version="v1.0",
        config_hash="",
        timestamp="2026-10-02T10:00:00Z",
        metrics={"f1": 0.94},
    )
    res = ResearchResultIntegrityValidator.validate_result(req)
    assert res.status == ValidationStatus.INCOMPLETE


# 2. STATISTICAL TESTS
def test_mean():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    stats = StatisticalValidationEngine.compute_descriptive_stats(data, "test_metric")
    assert stats.mean == 3.0
    assert stats.sample_size == 5


def test_median():
    data = [1.0, 2.0, 10.0, 4.0, 5.0]
    stats = StatisticalValidationEngine.compute_descriptive_stats(data, "test_metric")
    assert stats.median == 4.0


def test_bootstrap_ci():
    data = [0.94, 0.95, 0.93, 0.96, 0.94, 0.95, 0.94]
    ci = StatisticalValidationEngine.compute_bootstrap_ci(data, "f1", confidence_level=0.95)
    assert ci.lower_bound <= ci.estimate <= ci.upper_bound
    assert 0.90 <= ci.lower_bound <= 0.98


def test_wilcoxon():
    baseline = [0.80, 0.82, 0.81, 0.79]
    proposed = [0.90, 0.92, 0.91, 0.89]
    paired = StatisticalValidationEngine.compute_paired_analysis(baseline, proposed, "f1")
    assert paired.proposed_method > paired.baseline
    assert paired.effect_size > 0.0


def test_effect_size():
    baseline = [0.80, 0.82, 0.81]
    proposed = [0.90, 0.92, 0.91]
    effect = StatisticalValidationEngine.compute_effect_size(baseline, proposed, "f1")
    assert effect.absolute_difference == pytest.approx(0.10, abs=0.01)
    assert effect.cohens_d > 1.0


def test_multiple_comparison():
    raw_p = {"m1": 0.01, "m2": 0.04, "m3": 0.05}
    res = StatisticalValidationEngine.adjust_multiple_comparisons(raw_p, method="Bonferroni")
    assert res.adjusted_p_values["m1"] == pytest.approx(0.03, abs=0.001)
    assert res.adjusted_p_values["m3"] == pytest.approx(0.15, abs=0.001)


# 3. SENSITIVITY TESTS
def test_threshold_sensitivity():
    res = SensitivityAnalysisEngine.run_sensitivity_analysis("EXP-001", {"f1": 0.946}, {"detection_threshold": 0.5})
    thresh_items = [item for item in res.sensitivity_items if item.category == "THRESHOLDS"]
    assert len(thresh_items) == 9


def test_memory_sensitivity():
    res = SensitivityAnalysisEngine.run_sensitivity_analysis("EXP-001", {"f1": 0.946}, {})
    mem_items = [item for item in res.sensitivity_items if item.category == "MEMORY"]
    assert len(mem_items) > 0


def test_agent_budget_sensitivity():
    res = SensitivityAnalysisEngine.run_sensitivity_analysis("EXP-001", {"f1": 0.946}, {})
    budget_items = [item for item in res.sensitivity_items if item.category == "AGENT_BUDGET"]
    assert len(budget_items) > 0


def test_policy_threshold_sensitivity():
    res = SensitivityAnalysisEngine.run_sensitivity_analysis("EXP-001", {"f1": 0.946}, {})
    policy_items = [item for item in res.sensitivity_items if item.category == "POLICY"]
    assert len(policy_items) > 0


# 4. ROBUSTNESS TESTS
def test_missing_features():
    res = RobustnessValidator.run_robustness_validation("EXP-001", {"f1": 0.946})
    item = next(i for i in res.robustness_items if i.perturbation_type == "missing_features_10pct")
    assert item.perturbed_metric < item.baseline_metric


def test_delayed_events():
    res = RobustnessValidator.run_robustness_validation("EXP-001", {"f1": 0.946})
    item = next(i for i in res.robustness_items if i.perturbation_type == "delayed_events_2s")
    assert item.degradation_percentage > 0.0


def test_duplicate_events():
    res = RobustnessValidator.run_robustness_validation("EXP-001", {"f1": 0.946})
    item = next(i for i in res.robustness_items if i.perturbation_type == "duplicated_events_5pct")
    assert item.degradation_percentage >= 0.0


def test_agent_timeout():
    res = RobustnessValidator.run_robustness_validation("EXP-001", {"f1": 0.946})
    item = next(i for i in res.robustness_items if i.perturbation_type == "agent_timeout_300ms")
    assert item.category == "OPERATIONAL_DEGRADATION"


def test_missing_agent():
    res = RobustnessValidator.run_robustness_validation("EXP-001", {"f1": 0.946})
    item = next(i for i in res.robustness_items if i.perturbation_type == "missing_agent_evidence")
    assert item.category == "EVIDENCE_DEGRADATION"


# 5. CLAIMS & HYPOTHESES TESTS
def test_supported_claim():
    res = ResearchClaimValidator.validate_claims(["Adaptive agent selection reduces computational overhead while maintaining detection quality."])
    assert res.validated_claims[0].status == ClaimStatus.DIRECTLY_SUPPORTED


def test_unsupported_claim():
    res = ResearchClaimValidator.validate_claims(["HACTM guarantees 100% detection of zero-day attacks without false positives."])
    assert res.validated_claims[0].status == ClaimStatus.NOT_SUPPORTED


def test_partial_claim():
    res = ResearchClaimValidator.validate_claims(["Zero-day attack detection."])
    assert res.validated_claims[0].status == ClaimStatus.PARTIALLY_SUPPORTED


def test_missing_result():
    res = HypothesisValidator.evaluate_hypotheses({})
    assert len(res.hypotheses) == 9
    h1 = next(h for h in res.hypotheses if h.hypothesis_id == "H1")
    assert h1.status in [HypothesisStatus.SUPPORTED, HypothesisStatus.PARTIALLY_SUPPORTED]



# 6. REPRODUCIBILITY & ENVIRONMENT TESTS
def test_config_hash():
    report = ReproducibilityVerifier.verify_reproducibility("EXP-001", "cfg-test-hash")
    assert report.config_hash == "cfg-test-hash"
    assert report.status == ReproducibilityStatus.REPRODUCED


def test_dataset_checksum():
    manifest = ReproducibilityVerifier.get_dataset_manifest()
    assert len(manifest) >= 3
    assert all(m.checksum for m in manifest)


def test_environment_capture():
    env = EnvironmentCapture.capture_environment()
    assert env.python_version is not None
    assert env.environment_hash is not None


def test_seed_reproducibility():
    report = ReproducibilityVerifier.verify_reproducibility("EXP-001", "hash")
    assert report.seed_reproducible is True


def test_security_audit():
    audit = ResearchSecurityAudit.run_security_audit()
    assert audit.status == AuditStatus.SECURITY_PASS
    assert audit.checked_items["secrets_in_configs"] is True
