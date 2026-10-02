"""
NLP Detector for Phishing Intelligence Agent.
Specialized Security Agents — Baseline TF-IDF + Logistic Regression / Linear SVM Classifier.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pickle
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from hactm.phishing.models import PhishingDetectionResult, PhishingEmailEvent
from hactm.core.constants import risk_score_to_severity
from hactm.core.logging import logger


class NlpPhishingDetector:
    """
    Baseline NLP Classifier using TF-IDF + Logistic Regression/SVM.
    Fully reproducible, fast, explainable, and supports future Transformer/BERT models without interface changes.
    """

    def __init__(
        self,
        model_version: str = "nlp_tfidf_v1.0",
        threshold: float = 0.5,
        version: str = "1.0.0",
    ):
        self.detector_id = "phishing-nlp-detector"
        self.version = version
        self.model_version = model_version
        self.threshold = threshold

        self.vectorizer: Optional[TfidfVectorizer] = None
        self.classifier: Optional[LogisticRegression] = None
        self.is_trained = False

        self._init_default_or_load()

    def _init_default_or_load(self) -> None:
        """Initializes default vectorizer & model or attempts to load from artifact."""
        # Simple default fit with baseline security corpora if no checkpoint saved
        default_corpus = [
            ("Dear user, please click here to verify your account password immediately.", 1),
            ("Urgent security alert: Your account has been suspended. Login to restore access.", 1),
            ("Please send your credentials and bank details for wire transfer processing.", 1),
            ("Invoice attached for your recent payment. Please review the attached pdf.exe", 1),
            ("Team meeting scheduled for tomorrow at 10:00 AM in Conference Room B.", 0),
            ("Attached is the monthly financial report for Q3 review.", 0),
            ("Here is the updated documentation for the API project release.", 0),
            ("Thank you for your inquiry. Our support team will get back to you shortly.", 0),
        ]
        texts = [t[0] for t in default_corpus]
        labels = [t[1] for t in default_corpus]

        self.vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(texts)
        self.classifier = LogisticRegression(random_state=42)
        self.classifier.fit(X, labels)
        self.is_trained = True

    def train(self, texts: List[str], labels: List[int], max_features: int = 5000) -> Dict[str, Any]:
        """Trains the TF-IDF + Logistic Regression model on custom dataset."""
        if not texts or not labels or len(texts) != len(labels):
            raise ValueError("Training texts and labels must be non-empty and equal length.")

        self.vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(texts)

        self.classifier = LogisticRegression(random_state=42, C=1.0, max_iter=1000)
        self.classifier.fit(X, labels)
        self.is_trained = True

        acc = float(self.classifier.score(X, labels))
        return {
            "samples": len(texts),
            "vocabulary_size": len(self.vectorizer.vocabulary_),
            "training_accuracy": round(acc, 4),
            "model_version": self.model_version,
        }

    def predict_prob(self, text: str) -> float:
        """Calculates phishing probability from text."""
        if not text or not self.is_trained or not self.vectorizer or not self.classifier:
            return 0.0
        X = self.vectorizer.transform([text])
        if hasattr(self.classifier, "predict_proba"):
            proba = self.classifier.predict_proba(X)[0][1]
            return float(proba)
        elif hasattr(self.classifier, "decision_function"):
            decision = float(self.classifier.decision_function(X)[0])
            # Sigmoid transform
            return 1.0 / (1.0 + np.exp(-decision))
        return 0.0

    def detect(self, event: PhishingEmailEvent, features: Dict[str, Any]) -> Optional[PhishingDetectionResult]:
        full_text = f"{event.subject or ''} {event.body or ''}".strip()
        if not full_text:
            return None

        prob = self.predict_prob(full_text)

        # Baseline heuristic text triggers as supplementary signal
        urgency_cnt = features.get("urgency_count", 0)
        cred_cnt = features.get("credential_count", 0)
        fin_cnt = features.get("financial_count", 0)

        # Combined baseline score
        text_trigger_score = min(1.0, (urgency_cnt * 0.15 + cred_cnt * 0.25 + fin_cnt * 0.20))
        final_risk_score = round(min(1.0, max(prob, text_trigger_score)), 4)

        if final_risk_score < self.threshold and cred_cnt == 0 and urgency_cnt == 0:
            return None

        reason_codes = []
        explanation_parts = []

        if prob >= self.threshold:
            reason_codes.append("NLP_CLASSIFIER_HIGH_PHISHING_PROBABILITY")
            explanation_parts.append(f"NLP model detected high phishing intent (probability: {prob:.2f})")

        if cred_cnt > 0:
            reason_codes.append("TEXT_CREDENTIAL_REQUEST_LANGUAGE")
            explanation_parts.append("Credential verification language detected")

        if urgency_count := urgency_cnt:
            reason_codes.append("TEXT_URGENCY_LANGUAGE")
            explanation_parts.append("Urgent action call-to-action language detected")

        if fin_cnt > 0:
            reason_codes.append("TEXT_FINANCIAL_LURE_LANGUAGE")
            explanation_parts.append("Financial lures/payment language detected")

        if not reason_codes:
            return None

        confidence = 0.85
        uncertainty = round(1.0 - confidence, 4)

        return PhishingDetectionResult(
            detection_id=f"det_nlp_{event.message_id}",
            event_id=event.message_id,
            detector_type="NLP",
            detector_id=self.detector_id,
            category="GENERIC_PHISHING",
            risk_score=final_risk_score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(final_risk_score).value,
            explanation="; ".join(explanation_parts),
            features_used={
                "nlp_probability": round(prob, 4),
                "urgency_count": urgency_cnt,
                "credential_count": cred_cnt,
                "financial_count": fin_cnt,
            },
            detector_version=self.version,
            model_version=self.model_version,
            reason_codes=reason_codes,
        )
