"""Adaptive EWMA control limits (Novel #1)."""

class EWMAThresholds:
    """Adaptive EWMA threshold manager."""
    
    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha
        self.threshold = None
    
    def update(self, score: float) -> None:
        """Update EWMA threshold."""
        if self.threshold is None:
            self.threshold = score
        else:
            self.threshold = self.alpha * score + (1 - self.alpha) * self.threshold
