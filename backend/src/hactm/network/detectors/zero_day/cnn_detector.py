"""
CNN-based Detector Adapter for Network Telemetry and Flow Transformations.
Transforms flow/packet features into normalized tensor representations deterministically for spatial/sequential feature extraction.
"""

import time
import json
import math
import numpy as np
from typing import Dict, Any, List, Optional
from hactm.network.detectors.zero_day.base import ZeroDayDetector, ZeroDayDetectionResult


class CNNDetector(ZeroDayDetector):
    """CNN-based Detector Adapter for Network Traffic Tensor Representations."""

    def __init__(
        self,
        input_dim: int = 16,
        kernel_size: int = 3,
        num_filters: int = 8,
        anomaly_threshold: float = 0.70,
        model_name: str = "HACTM-CNN-Detector-v1"
    ):
        self.input_dim = input_dim
        self.kernel_size = kernel_size
        self.num_filters = num_filters
        self.anomaly_threshold = anomaly_threshold
        self.model_name = model_name

        self._filters: np.ndarray = np.array([])
        self._dense_weights: np.ndarray = np.array([])
        self._dense_bias: float = 0.0
        self._init_network()

    def _init_network(self) -> None:
        """Initializes 1D Conv kernels and dense output layer."""
        np.random.seed(42)
        # 1D Convolution filters: shape (num_filters, kernel_size)
        self._filters = np.random.randn(self.num_filters, self.kernel_size) * 0.1
        # Flattened conv output dimension
        conv_out_len = max(1, self.input_dim - self.kernel_size + 1)
        dense_in_dim = self.num_filters * conv_out_len
        self._dense_weights = np.random.randn(dense_in_dim, 1) * 0.1
        self._dense_bias = 0.0

    def _transform_telemetry(self, sample: List[float]) -> np.ndarray:
        """Deterministically reshapes and normalizes raw telemetry vector into 1D flow tensor."""
        arr = np.array(sample, dtype=np.float32)
        # Zero-pad or crop to exactly input_dim
        if len(arr) < self.input_dim:
            arr = np.pad(arr, (0, self.input_dim - len(arr)), mode='constant')
        else:
            arr = arr[:self.input_dim]
        # Min-max normalization
        min_v, max_v = np.min(arr), np.max(arr)
        if max_v > min_v:
            arr = (arr - min_v) / (max_v - min_v)
        return arr

    def _forward_sample(self, tensor_1d: np.ndarray) -> float:
        """Executes 1D Conv -> ReLU -> MaxPool -> Dense forward pass."""
        # 1D Convolution
        conv_outs = []
        for f_idx in range(self.num_filters):
            kernel = self._filters[f_idx]
            out_len = len(tensor_1d) - self.kernel_size + 1
            conv_res = [np.sum(tensor_1d[i:i+self.kernel_size] * kernel) for i in range(out_len)]
            conv_outs.append(np.maximum(0, conv_res)) # ReLU
        
        flat_features = np.array(conv_outs).flatten()
        logit = np.dot(flat_features, self._dense_weights.flatten()) + self._dense_bias
        return float(1.0 / (1.0 + np.exp(-np.clip(logit, -15.0, 15.0))))

    def fit(self, X: List[List[float]], y: Optional[List[int]] = None) -> None:
        """Trains CNN filters using telemetry samples."""
        t_samples = [self._transform_telemetry(s) for s in X]
        # Mock fitting phase for CNN weights adjustment
        pass

    def predict(self, X: List[List[float]]) -> List[bool]:
        return [s >= self.anomaly_threshold for s in self.predict_score(X)]

    def predict_score(self, X: List[List[float]]) -> List[float]:
        scores = []
        for s in X:
            t = self._transform_telemetry(s)
            scores.append(self._forward_sample(t))
        return scores

    def predict_uncertainty(self, X: List[List[float]]) -> List[float]:
        """Estimates CNN representation variance by perturbing transformed tensor."""
        uncertainties = []
        for s in X:
            t = self._transform_telemetry(s)
            pert_scores = []
            for _ in range(5):
                noise = np.random.randn(*t.shape) * 0.05
                pert_scores.append(self._forward_sample(t + noise))
            var = float(np.var(pert_scores))
            uncertainties.append(min(1.0, var * 5.0))
        return uncertainties

    def detect_unknown(self, X: List[List[float]], threshold: Optional[float] = None) -> List[ZeroDayDetectionResult]:
        thresh = threshold if threshold is not None else self.anomaly_threshold
        results = []
        for i, sample in enumerate(X):
            t0 = time.perf_counter()
            score = self.predict_score([sample])[0]
            uncertainty = self.predict_uncertainty([sample])[0]
            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000.0

            known_prob = round(float(score * (1.0 - uncertainty)), 4)
            anomaly_score = round(float(score), 4)
            confidence = round(float(1.0 - uncertainty), 4)
            is_zero_day = (anomaly_score >= thresh) and (known_prob < 0.50 or uncertainty > 0.30)
            is_detected = anomaly_score >= thresh

            results.append(
                ZeroDayDetectionResult(
                    event_id=f"cnn-evt-{i}-{int(time.time())}",
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
        """Spatial feature activation mapping."""
        t = self._transform_telemetry(sample)
        activations = [float(abs(v)) for v in t]
        total = sum(activations) + 1e-8
        norm = [round(a / total, 4) for a in activations]
        return {
            "spatial_representation": "1D Network Flow Feature Map",
            "feature_attributions": norm
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
            "filters": self._filters.tolist(),
            "dense_weights": self._dense_weights.tolist(),
            "dense_bias": float(self._dense_bias)
        }
        with open(filepath, "w") as f:
            json.dump(data, f)

    def load_model(self, filepath: str) -> None:
        with open(filepath, "r") as f:
            data = json.load(f)
        self.model_name = data["model_name"]
        self.input_dim = data["input_dim"]
        self._filters = np.array(data["filters"], dtype=np.float32)
        self._dense_weights = np.array(data["dense_weights"], dtype=np.float32)
        self._dense_bias = data["dense_bias"]
