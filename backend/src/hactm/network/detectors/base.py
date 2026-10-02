"""
Base Detector Interface for HACTM Network Security Agent.
Network Security Agent — Hierarchical Adaptive Cyber Trust Mesh.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from hactm.network.models import DetectorType, NetworkDetectionResult, NetworkEvent


class BaseDetector(ABC):
    """
    Abstract contract for all network security detectors.
    """
    detector_type: DetectorType
    detector_id: str
    detector_version: str

    @abstractmethod
    def detect(self, event: NetworkEvent) -> Optional[NetworkDetectionResult]:
        """
        Evaluates a single NetworkEvent.
        Returns a NetworkDetectionResult if suspicious or anomalous, else None.
        """
        pass

    def detect_batch(self, events: List[NetworkEvent]) -> List[NetworkDetectionResult]:
        """
        Evaluates a batch of NetworkEvents.
        """
        results: List[NetworkDetectionResult] = []
        for e in events:
            res = self.detect(e)
            if res:
                results.append(res)
        return results
