"""Abstract base detector interface."""
from abc import ABC, abstractmethod
import numpy as np

class BaseDetector(ABC):
    """Base class for all drift detectors."""
    
    @abstractmethod
    def fit(self, baseline: np.ndarray) -> None:
        """Fit detector to baseline data."""
        pass
    
    @abstractmethod
    def score(self, current: np.ndarray) -> float:
        """Score current data for drift."""
        pass
