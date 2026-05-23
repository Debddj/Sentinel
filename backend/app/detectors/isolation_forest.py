"""Isolation Forest anomaly detector."""
from app.detectors.base import BaseDetector
from sklearn.ensemble import IsolationForest
import numpy as np

class IForestDetector(BaseDetector):
    """Isolation Forest detector for anomalies."""
    
    def fit(self, baseline: np.ndarray) -> None:
        """Train Isolation Forest on baseline."""
        self.iforest = IsolationForest(random_state=42)
        self.iforest.fit(baseline)
    
    def score(self, current: np.ndarray) -> float:
        """Score current data for anomalies."""
        anomaly_score = self.iforest.score_samples(current)
        return np.mean(anomaly_score)
