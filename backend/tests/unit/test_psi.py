"""Tests for PSI detector."""
import pytest
from app.detectors.psi import PSIDetector

def test_psi_detector():
    """Test PSI detector."""
    detector = PSIDetector()
    assert detector is not None
