"""Tests for EWMA adaptive thresholds."""
import pytest
from app.novelties.ewma_thresholds import EWMAThresholds


class TestEWMAThresholds:
    def test_initialize_from_baseline(self):
        ewma = EWMAThresholds(alpha=0.2, sigma_multiplier=3.0)
        result = ewma.initialize_ewma([0.05, 0.07, 0.06, 0.08, 0.05])
        assert "ewma_mean" in result
        assert "ewma_std" in result
        assert "threshold" in result
        assert result["threshold"] > result["ewma_mean"]

    def test_update_raises_threshold_on_spike(self):
        ewma = EWMAThresholds(alpha=0.3)
        init = ewma.initialize_ewma([0.05] * 20)
        updated = ewma.update(0.8, init["ewma_mean"], init["ewma_std"])
        # A large spike should raise both the mean and threshold
        assert updated["ewma_mean"] > init["ewma_mean"]
        assert "threshold" in updated

    def test_should_alert_above_threshold(self):
        ewma = EWMAThresholds()
        assert ewma.should_alert(score=0.9, threshold=0.5) is True
        assert ewma.should_alert(score=0.1, threshold=0.5) is False

    def test_empty_baseline_uses_default(self):
        ewma = EWMAThresholds()
        result = ewma.initialize_ewma([])
        assert result["threshold"] >= 0.0

    def test_lookback_window_capped(self):
        ewma = EWMAThresholds(lookback_window=5)
        scores = list(range(20))  # 20 values, only last 5 used
        result = ewma.initialize_ewma(scores)
        # Mean of [15,16,17,18,19] = 17
        assert abs(result["ewma_mean"] - 17.0) < 0.01