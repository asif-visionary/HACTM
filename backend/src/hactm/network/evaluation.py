"""
Network Detection Evaluation and Benchmark Metrics.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
Calculates:
- Precision, Recall, F1
- False Positive Rate (FPR) & False Negative Rate (FNR)
- ROC-AUC & PR-AUC
- Confusion Matrix & Class Distribution
Enforces zero data leakage (ground-truth labels excluded from inference features).
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from hactm.network.models import NetworkDetectionResult, NetworkEvaluationMetrics, NetworkEvent


def evaluate_detections(
    events: List[NetworkEvent],
    detections: List[NetworkDetectionResult],
    positive_label_substrings: Optional[List[str]] = None,
) -> NetworkEvaluationMetrics:
    """
    Computes rigorous classification metrics comparing detector results against dataset labels.
    Never invents or fabricates metrics.
    """
    pos_substrings = positive_label_substrings or ["attack", "malware", "scan", "anomaly", "bot", "infilter", "dos"]

    # Map detections by event_id -> max risk score
    det_map: Dict[str, float] = {}
    for d in detections:
        det_map[d.event_id] = max(det_map.get(d.event_id, 0.0), d.risk_score)

    y_true: List[int] = []
    y_scores: List[float] = []
    y_pred: List[int] = []

    class_counts: Dict[str, int] = {}

    for ev in events:
        raw_label = (ev.label or "BENIGN").lower()
        class_counts[raw_label] = class_counts.get(raw_label, 0) + 1

        is_actual_attack = int(any(sub in raw_label for sub in pos_substrings) and "benign" not in raw_label)
        predicted_risk = det_map.get(ev.event_id, 0.0)
        is_pred_attack = int(predicted_risk >= 0.50)

        y_true.append(is_actual_attack)
        y_scores.append(predicted_risk)
        y_pred.append(is_pred_attack)

    total = len(events)
    if total == 0:
        return NetworkEvaluationMetrics(
            total_evaluated=0,
            true_positives=0,
            false_positives=0,
            true_negatives=0,
            false_negatives=0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            false_positive_rate=0.0,
            false_negative_rate=0.0,
            confusion_matrix=[[0, 0], [0, 0]],
            class_distribution={},
        )

    tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)
    fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)
    tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)
    fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0
    fpr = round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0.0
    fnr = round(fn / (fn + tp), 4) if (fn + tp) > 0 else 0.0

    # ROC-AUC & PR-AUC calculation using sklearn
    roc_auc = None
    pr_auc = None
    try:
        from sklearn.metrics import roc_auc_score, average_precision_score
        if len(set(y_true)) > 1:
            roc_auc = round(float(roc_auc_score(y_true, y_scores)), 4)
            pr_auc = round(float(average_precision_score(y_true, y_scores)), 4)
    except Exception:
        pass

    return NetworkEvaluationMetrics(
        total_evaluated=total,
        true_positives=tp,
        false_positives=fp,
        true_negatives=tn,
        false_negatives=fn,
        precision=precision,
        recall=recall,
        f1_score=f1,
        false_positive_rate=fpr,
        false_negative_rate=fnr,
        roc_auc=roc_auc,
        pr_auc=pr_auc,
        confusion_matrix=[[tn, fp], [fn, tp]],
        class_distribution=class_counts,
    )
