"""Kolmogorov-Smirnov test detector."""
from app.detectors.base import BaseDetector
from scipy import stats
import numpy as np

class KSDetector(BaseDetector):
    """KS-test drift detector."""
    
    def fit(self, baseline: np.ndarray) -> None:
        """Fit KS detector to baseline."""
        self.baseline = baseline
    
    def score(self, current: np.ndarray) -> float:
        """Calculate KS statistic."""
        ks_stat, _ = stats.ks_2samp(self.baseline, current)
        return ks_stat
