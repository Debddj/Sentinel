"""Population Stability Index (PSI) detector."""
from app.detectors.base import BaseDetector
import numpy as np

class PSIDetector(BaseDetector):
    """PSI drift detector."""
    
    def fit(self, baseline: np.ndarray) -> None:
        """Fit PSI detector to baseline."""
        self.baseline = baseline
    
    def score(self, current: np.ndarray) -> float:
        """Calculate PSI score."""
        return 0.0
