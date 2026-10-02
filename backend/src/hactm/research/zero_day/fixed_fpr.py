"""
Fixed-FPR Operating Point Evaluator for HACTM.
Calculates True Positive Rate (TPR) at fixed False Positive Rate (FPR) thresholds (1%, 0.5%, 0.1%), ROC curves, and PR curves.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class FixedFPROperatingPoint(BaseModel):
    """Data point for TPR at a target fixed FPR operating point."""
    target_fpr_percent: float
    actual_fpr: float
    threshold_used: float
    tpr_recall: float
    precision: float
    f1_score: float


class FixedFPREvaluationResult(BaseModel):
    """Summary of fixed-FPR operating point evaluation."""
    operating_points: List[FixedFPROperatingPoint]
    roc_curve: Dict[str, List[float]]  # {"fpr": [...], "tpr": [...]}
    pr_curve: Dict[str, List[float]]   # {"recall": [...], "precision": [...]}
    auroc: float
    auprc: float


class FixedFPREvaluator:
    """Evaluates operational detection efficacy at strict low-FPR operating points."""

    @staticmethod
    def evaluate(
        y_true: List[int],
        anomaly_scores: List[float],
        target_fpr_levels: Optional[List[float]] = None
    ) -> FixedFPREvaluationResult:
        
        target_fpr_levels = target_fpr_levels or [0.01, 0.005, 0.001]
        y_t = np.array(y_true, dtype=np.int32)
        scores = np.array(anomaly_scores, dtype=np.float32)

        # Sort thresholds descending
        thresholds = np.sort(scores)[::-1]
        
        tpr_list, fpr_list, prec_list, rec_list = [], [], [], []

        positives = np.sum(y_t == 1)
        negatives = np.sum(y_t == 0)

        if positives == 0 or negatives == 0:
            return FixedFPREvaluationResult(
                operating_points=[],
                roc_curve={"fpr": [0.0, 1.0], "tpr": [0.0, 1.0]},
                pr_curve={"recall": [0.0, 1.0], "precision": [0.0, 1.0]},
                auroc=0.50,
                auprc=0.50
            )

        # Compute full ROC/PR points
        for thresh in thresholds[::max(1, len(thresholds)//100)]:
            preds = (scores >= thresh).astype(int)
            tp = np.sum((preds == 1) & (y_t == 1))
            fp = np.sum((preds == 1) & (y_t == 0))
            
            tpr = tp / positives
            fpr = fp / negatives
            precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0

            tpr_list.append(float(tpr))
            fpr_list.append(float(fpr))
            prec_list.append(float(precision))
            rec_list.append(float(tpr))

        # Calculate TPR @ fixed target FPRs
        op_results = []
        for target_fpr in target_fpr_levels:
            # Find highest threshold where FPR <= target_fpr
            valid_thresholds = []
            for thresh in np.linspace(1.0, 0.0, 200):
                preds = (scores >= thresh).astype(int)
                fp = np.sum((preds == 1) & (y_t == 0))
                fpr = fp / negatives
                if fpr <= target_fpr:
                    valid_thresholds.append((thresh, fpr))
            
            if valid_thresholds:
                best_thresh, actual_fpr = valid_thresholds[0]
                preds = (scores >= best_thresh).astype(int)
                tp = np.sum((preds == 1) & (y_t == 1))
                fp = np.sum((preds == 1) & (y_t == 0))
                tpr = tp / positives
                prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                f1 = 2 * prec * tpr / (prec + tpr) if (prec + tpr) > 0 else 0.0
            else:
                best_thresh, actual_fpr, tpr, prec, f1 = 1.0, 0.0, 0.0, 0.0, 0.0

            op_results.append(
                FixedFPROperatingPoint(
                    target_fpr_percent=round(target_fpr * 100.0, 2),
                    actual_fpr=round(float(actual_fpr), 5),
                    threshold_used=round(float(best_thresh), 4),
                    tpr_recall=round(float(tpr), 4),
                    precision=round(float(prec), 4),
                    f1_score=round(float(f1), 4)
                )
            )

        # Trapezoidal AUROC & AUPRC calculation
        trapz_fn = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
        # Ensure x is sorted ascending
        sorted_roc = sorted(zip(fpr_list, tpr_list), key=lambda item: item[0])
        x_fpr = [pt[0] for pt in sorted_roc]
        y_tpr = [pt[1] for pt in sorted_roc]
        auroc = float(trapz_fn(y_tpr, x_fpr))

        sorted_pr = sorted(zip(rec_list, prec_list), key=lambda item: item[0])
        x_rec = [pt[0] for pt in sorted_pr]
        y_prec = [pt[1] for pt in sorted_pr]
        auprc = float(trapz_fn(y_prec, x_rec))

        return FixedFPREvaluationResult(
            operating_points=op_results,
            roc_curve={"fpr": [round(x, 4) for x in fpr_list], "tpr": [round(y, 4) for y in tpr_list]},
            pr_curve={"recall": [round(x, 4) for x in rec_list], "precision": [round(y, 4) for y in prec_list]},
            auroc=round(max(0.0, min(1.0, auroc)), 4),
            auprc=round(max(0.0, min(1.0, auprc)), 4)
        )
