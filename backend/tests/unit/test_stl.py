"""Tests for STL decomposition."""
import pytest
from app.novelties.stl_decomposition import STLDecomposition

def test_stl_decomposition():
    """Test STL decomposition."""
    stl = STLDecomposition()
    assert stl is not None
