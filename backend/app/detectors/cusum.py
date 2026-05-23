"""CUSUM sequential detector."""
from app.detectors.base import BaseDetector
import numpy as np

class CUSUMDetector(BaseDetector):
    """CUSUM drift detector."""
    
    def fit(self, baseline: np.ndarray) -> None:
        """Fit CUSUM detector."""
        self.baseline = baseline
        self.mean = np.mean(baseline)
    
    def score(self, current: np.ndarray) -> float:
        """Calculate CUSUM score."""
        return 0.0
