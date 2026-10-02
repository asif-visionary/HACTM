"""
Unit Tests for Evidence Fusion Engine Evaluation Suite.
"""

from hactm.fusion.evaluation import CrossDomainFusionEvaluator


def test_fusion_evaluation_suite():
    evaluator = CrossDomainFusionEvaluator()
    res = evaluator.run_evaluation_suite()

    assert "scenarios_results" in res
    assert "baselines_comparison" in res
    assert "ablations_results" in res
    assert "benchmark_results" in res
    assert "hypotheses_validation" in res

    hypotheses = res["hypotheses_validation"]
    assert hypotheses["H1_multi_domain_contextual_advantage"]["supported"] is True
    assert hypotheses["H4_redundancy_control_prevents_inflation"]["supported"] is True
    assert hypotheses["H5_conflict_aware_produces_stable_assessment"]["supported"] is True
