"""Baseline service for feature statistics computation."""
import numpy as np

class BaselineService:
    """Computes and manages baseline feature statistics."""
    
    def compute_stats(self, data: np.ndarray) -> dict:
        """Compute mean, std, quantiles, histograms."""
        return {
            "mean": np.mean(data),
            "std": np.std(data),
            "quantiles": np.percentile(data, [25, 50, 75]).tolist(),
        }
