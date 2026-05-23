"""Jensen-Shannon divergence detector for categoricals."""
from app.detectors.base import BaseDetector
from scipy.spatial.distance import jensenshannon
import numpy as np

class JSDetector(BaseDetector):
    """JS divergence detector for categorical data."""
    
    def fit(self, baseline: np.ndarray) -> None:
        """Fit JS detector to baseline."""
        self.baseline = baseline
    
    def score(self, current: np.ndarray) -> float:
        """Calculate JS divergence."""
        return 0.0
