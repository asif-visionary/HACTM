"""
Data Movement / Exfiltration Indicator Detector for UBA Agent.
"""

from typing import Any, Dict, Optional
from hactm.uba.models import UbaDetectionResult, UbaEvent
from hactm.core.constants import risk_score_to_severity


class DataExfiltrationDetector:
    """Detects potential data movement anomaly (large transfer volume, rare file/destination)."""

    def __init__(self, version: str = "1.0.0", threshold_bytes: int = 100_000_000):
        self.detector_id = "uba-exfiltration-detector"
        self.version = version
        self.threshold_bytes = threshold_bytes

    def detect(self, event: UbaEvent, features: Dict[str, Any]) -> Optional[UbaDetectionResult]:
        bytes_trans = features.get("bytes_transferred", 0)
        ratio = features.get("bytes_deviation_ratio", 1.0)

        if bytes_trans < self.threshold_bytes and ratio < 5.0:
            return None

        score = min(1.0, 0.40 + min(0.50, (ratio / 20.0)))
        confidence = 0.85 if not features.get("insufficient_baseline") else 0.60
        uncertainty = round(1.0 - confidence, 4)

        mb_str = f"{bytes_trans / (1024*1024):.1f} MB"

        return UbaDetectionResult(
            detection_id=f"det_uba_exfil_{event.event_id}",
            event_id=event.event_id,
            user_id=event.user_id,
            detector_type="HEURISTIC",
            detector_id=self.detector_id,
            category="POTENTIAL_DATA_MOVEMENT_ANOMALY",
            risk_score=score,
            confidence=confidence,
            uncertainty=uncertainty,
            severity=risk_score_to_severity(score).value,
            explanation=f"Potential data movement anomaly: User '{event.user_id}' transferred {mb_str} ({ratio}x baseline median)",
            features_used={
                "bytes_transferred": bytes_trans,
                "bytes_deviation_ratio": ratio,
            },
            detector_version=self.version,
            reason_codes=["UBA_DATA_MOVEMENT_ANOMALY"],
        )
