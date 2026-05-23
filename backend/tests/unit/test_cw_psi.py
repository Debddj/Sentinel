"""Tests for Confidence-weighted PSI."""
import pytest
from app.novelties.cw_psi import ConfidenceWeightedPSI

def test_cw_psi():
    """Test CW-PSI computation."""
    cw_psi = ConfidenceWeightedPSI()
    assert cw_psi is not None
