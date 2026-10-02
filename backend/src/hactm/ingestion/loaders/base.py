"""
Base Dataset Loader Interface for HACTM.
Provides memory-efficient batched streaming of records with source attribution.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union


class BaseDatasetLoader(ABC):
    """
    Abstract loader interface yielding batches of (row_number, record_dict).
    Supports memory-efficient streaming for files of any size.
    """
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {self.file_path}")

    @property
    def source_name(self) -> str:
        return self.file_path.name

    @abstractmethod
    def stream_batches(
        self, batch_size: int = 1000
    ) -> Generator[List[Tuple[int, Dict[str, Any]]], None, None]:
        """
        Yields batches of tuples: (row_number, raw_record_dict).
        Row numbers are 1-indexed for clear human & audit correlation.
        """
        pass
