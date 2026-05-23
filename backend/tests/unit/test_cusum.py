"""Tests for CUSUM detector."""
import pytest
from app.detectors.cusum import CUSUMDetector

def test_cusum_detector():
    """Test CUSUM detector."""
    detector = CUSUMDetector()
    assert detector is not None
