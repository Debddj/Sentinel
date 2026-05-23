"""Tests for KS detector."""
import pytest
from app.detectors.ks_test import KSDetector

def test_ks_detector():
    """Test KS detector."""
    detector = KSDetector()
    assert detector is not None
