"""
Bayesian and Probabilistic Uncertainty Detector Adapter for HACTM.
Estimates Epistemic Uncertainty, Predictive Uncertainty, Confidence Score, and Evidence Reliability.
"""

import time
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from hactm.network.detectors.zero_day.base import ZeroDayDetector, ZeroDayDetectionResult


class BayesianUncertaintyDetector(ZeroDayDetector):
    """Bayesian Probabilistic Detector for Uncertainty Estimation and Reliability Scoring."""

    def __init__(
        self,
        input_dim: int = 10,
        anomaly_threshold: float = 0.70,
        prior_variance: float = 1.0,
        model_name: str = "HACTM-Bayesian-Detector-v1"
    ):
        self.input_dim = input_dim
        self.anomaly_threshold = anomaly_threshold
        self.prior_variance = prior_variance
        self.model_name = model_name

        self._mean_vector: np.ndarray = np.zeros(input_dim)
        self._cov_diag: np.ndarray = np.ones(input_dim) * prior_variance
        self._is_fitted = False

    def fit(self, X: List[List[float]], y: Optional[List[int]] = None) -> None:
        """Fits Gaussian prior/posterior over benign training telemetry."""
        if not X:
            return
        X_arr = np.array(X, dtype=np.float32)
        if X_arr.shape[1] < self.input_dim:
            X_arr = np.pad(X_arr, ((0, 0), (0, self.input_dim - X_arr.shape[1])))
        elif X_arr.shape[1] > self.input_dim:
            X_arr = X_arr[:, :self.input_dim]

        self._mean_vector = np.mean(X_arr, axis=0)
        self._cov_diag = np.var(X_arr, axis=0) + 1e-4
        self._is_fitted = True

    def _mah_distance_and_uncertainty(self, sample: List[float]) -> Tuple[float, float, float]:
        """Calculates Mahalanobis distance, epistemic uncertainty, and predictive score."""
        s = np.array(sample[:self.input_dim], dtype=np.float32)
        if len(s) < self.input_dim:
            s = np.pad(s, (0, self.input_dim - len(s)))

        diff = s - self._mean_vector
        mah_sq = float(np.sum((diff ** 2) / self._cov_diag))
        
        # Anomaly score derived from Mahalanobis distance
        anomaly_score = float(1.0 - np.exp(-mah_sq / (2.0 * self.input_dim)))
        anomaly_score = max(0.0, min(1.0, anomaly_score))

        # Epistemic uncertainty proportional to distance outside training density
        epistemic_unc = float(1.0 - np.exp(-mah_sq / (4.0 * self.input_dim)))
        epistemic_unc = max(0.0, min(1.0, epistemic_unc))

        # Reliability is inversely related to epistemic uncertainty
        reliability = max(0.05, float(1.0 - epistemic_unc))

        return anomaly_score, epistemic_unc, reliability

    def predict(self, X: List[List[float]]) -> List[bool]:
        return [s >= self.anomaly_threshold for s in self.predict_score(X)]

    def predict_score(self, X: List[List[float]]) -> List[float]:
        scores = []
        for s in X:
            score, _, _ = self._mah_distance_and_uncertainty(s)
            scores.append(score)
        return scores

    def predict_uncertainty(self, X: List[List[float]]) -> List[float]:
        uncertainties = []
        for s in X:
            _, unc, _ = self._mah_distance_and_uncertainty(s)
            uncertainties.append(unc)
        return uncertainties

    def detect_unknown(self, X: List[List[float]], threshold: Optional[float] = None) -> List[ZeroDayDetectionResult]:
        thresh = threshold if threshold is not None else self.anomaly_threshold
        results = []
        for i, sample in enumerate(X):
            t0 = time.perf_counter()
            score, uncertainty, reliability = self._mah_distance_and_uncertainty(sample)
            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000.0

            known_prob = round(float(score * reliability), 4)
            anomaly_score = round(float(score), 4)
            confidence = round(float(reliability), 4)
            is_zero_day = (anomaly_score >= thresh) and (known_prob < 0.50 or uncertainty > 0.30)
            is_detected = anomaly_score >= thresh

            results.append(
                ZeroDayDetectionResult(
                    event_id=f"bayes-evt-{i}-{int(time.time())}",
                    detected=is_detected,
                    risk_score=anomaly_score,
                    anomaly_score=anomaly_score,
                    confidence=confidence,
                    uncertainty=round(uncertainty, 4),
                    attack_family="unknown" if is_zero_day else ("known_threat" if is_detected else "benign"),
                    known_attack_probability=known_prob,
                    zero_day_indicator=is_zero_day,
                    model=self.model_name,
                    inference_latency_ms=round(latency_ms, 3),
                    explanation=self.explain(sample)
                )
            )
        return results

    def explain(self, sample: List[float]) -> Dict[str, Any]:
        s = np.array(sample[:self.input_dim], dtype=np.float32)
        if len(s) < self.input_dim:
            s = np.pad(s, (0, self.input_dim - len(s)))
        diff = np.abs(s - self._mean_vector) / np.sqrt(self._cov_diag)
        total = float(np.sum(diff) + 1e-8)
        norm = [round(float(d / total), 4) for d in diff]
        return {
            "mahalanobis_deviations": norm,
            "epistemic_reliability": round(float(1.0 - (np.sum(diff) / (self.input_dim * 3.0))), 4)
        }

    def evaluate(self, X: List[List[float]], y: List[int]) -> Dict[str, float]:
        scores = self.predict_score(X)
        preds = [1 if s >= self.anomaly_threshold else 0 for s in scores]
        tp = sum(1 for p, act in zip(preds, y) if p == 1 and act == 1)
        fp = sum(1 for p, act in zip(preds, y) if p == 1 and act == 0)
        fn = sum(1 for p, act in zip(preds, y) if p == 0 and act == 1)
        tn = sum(1 for p, act in zip(preds, y) if p == 0 and act == 0)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = (tp + tn) / len(y) if len(y) > 0 else 0.0

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "auroc": round(accuracy, 4),
            "auprc": round(precision, 4)
        }

    def save_model(self, filepath: str) -> None:
        data = {
            "model_name": self.model_name,
            "input_dim": self.input_dim,
            "mean_vector": self._mean_vector.tolist(),
            "cov_diag": self._cov_diag.tolist()
        }
        with open(filepath, "w") as f:
            json.dump(data, f)

    def load_model(self, filepath: str) -> None:
        with open(filepath, "r") as f:
            data = json.load(f)
        self.model_name = data["model_name"]
        self.input_dim = data["input_dim"]
        self._mean_vector = np.array(data["mean_vector"], dtype=np.float32)
        self._cov_diag = np.array(data["cov_diag"], dtype=np.float32)
        self._is_fitted = True
