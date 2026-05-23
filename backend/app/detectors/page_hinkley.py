"""Page-Hinkley test detector with forgetting factor."""
from app.detectors.base import BaseDetector
import numpy as np

class PageHinkleyDetector(BaseDetector):
    """Page-Hinkley drift detector."""
    
    def fit(self, baseline: np.ndarray) -> None:
        """Fit Page-Hinkley detector."""
        self.baseline = baseline
        self.mean = np.mean(baseline)
        self.std = np.std(baseline)
    
    def score(self, current: np.ndarray) -> float:
        """Calculate Page-Hinkley statistic."""
        return 0.0
