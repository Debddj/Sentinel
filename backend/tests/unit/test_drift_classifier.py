"""Tests for drift classifier."""
import pytest
from app.novelties.drift_classifier import DriftClassifier

def test_drift_classifier():
    """Test drift type classification."""
    classifier = DriftClassifier()
    drift_type = classifier.classify({})
    assert drift_type in ["data_drift", "concept_drift", "covariate_shift"]
