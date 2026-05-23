"""Tests for EWMA thresholds."""
import pytest
from app.novelties.ewma_thresholds import EWMAThresholds

def test_ewma_thresholds():
    """Test EWMA threshold management."""
    ewma = EWMAThresholds()
    ewma.update(5.0)
    assert ewma.threshold == 5.0
