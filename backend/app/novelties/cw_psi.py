"""
NOVEL #2: Confidence-Weighted Population Stability Index (CW-PSI)

Extends the standard PSI detector with model-confidence weighting so that
drift in high-confidence prediction regions is penalised more heavily than
drift in low-confidence "uncertain" regions.

Standard PSI:
    PSI = Σ (A_i − E_i) × ln(A_i / E_i)

Confidence-Weighted PSI:
    CW-PSI = Σ  w_i × (A_i − E_i) × ln(A_i / E_i)

where:
    E_i = expected (baseline) fraction of samples in bin i
    A_i = actual (current) fraction of samples in bin i
    w_i = mean prediction confidence in bin i  **from the current window**

Interpretation:
    - CW-PSI ≈ PSI when confidence is uniformly distributed across bins
    - CW-PSI > PSI when drift concentrates in high-confidence bins
      (more dangerous — the model is "confidently wrong")
    - CW-PSI < PSI when drift concentrates in low-confidence bins
      (less dangerous — the model already "knows it doesn't know")

Binning strategy:
    Identical to ``app.detectors.psi.PSIDetector`` — percentile-based edges
    derived from the baseline, deduplicated via ``np.unique`` to handle
    low-cardinality features gracefully.

Fallback behaviour:
    If ``score()`` is called without confidence data, the method silently
    falls back to standard (unweighted) PSI so callers never need to
    branch on data availability.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import structlog

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Epsilon floor to prevent log(0) and division-by-zero.  Deliberately larger
# than the 1e-10 used in psi.py — CW-PSI multiplies by per-bin weights which
# can amplify tiny numerical noise, so a slightly more conservative floor
# keeps results stable without affecting macro-level scores.
_EPSILON: float = 1e-6

# Default number of histogram bins (matches PSIDetector default).
_DEFAULT_N_BINS: int = 10

# Minimum number of samples required in both baseline and current windows.
_DEFAULT_MIN_SAMPLES: int = 50


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------
@dataclass
class CWPSIResult:
    """Immutable container returned by ``ConfidenceWeightedPSI.score()``.

    Attributes
    ----------
    psi : float
        Standard (unweighted) PSI score.
    cw_psi : float
        Confidence-weighted PSI score.  Equal to ``psi`` when no confidence
        data was supplied (fallback mode).
    per_bin_psi : np.ndarray
        Per-bin contribution to the standard PSI.
    per_bin_cw_psi : np.ndarray
        Per-bin contribution to the CW-PSI.
    current_weights : np.ndarray
        Mean confidence per bin from the *current* window.  All ones when
        operating in fallback mode.
    n_bins : int
        Actual number of bins used (may be < requested if edges were deduped).
    is_fallback : bool
        ``True`` if the score was computed in standard-PSI fallback mode
        (i.e. no confidence data was available).
    """
    psi: float = 0.0
    cw_psi: float = 0.0
    per_bin_psi: np.ndarray = field(default_factory=lambda: np.array([]))
    per_bin_cw_psi: np.ndarray = field(default_factory=lambda: np.array([]))
    current_weights: np.ndarray = field(default_factory=lambda: np.array([]))
    n_bins: int = 0
    is_fallback: bool = False

    # Convenience helpers for serialisation (e.g. storing in DriftEvent.shap_attribution JSON)
    def to_dict(self) -> dict:
        """Serialise to a plain dict safe for JSON / DB storage."""
        return {
            "psi": round(self.psi, 8),
            "cw_psi": round(self.cw_psi, 8),
            "per_bin_psi": self.per_bin_psi.tolist(),
            "per_bin_cw_psi": self.per_bin_cw_psi.tolist(),
            "current_weights": self.current_weights.tolist(),
            "n_bins": self.n_bins,
            "is_fallback": self.is_fallback,
        }


# ---------------------------------------------------------------------------
# Core detector
# ---------------------------------------------------------------------------
class ConfidenceWeightedPSI:
    """Confidence-Weighted PSI drift detector.

    Lifecycle
    ---------
    1. Instantiate with desired ``n_bins`` and ``min_samples``.
    2. Call ``fit()`` with baseline feature values and baseline confidence
       scores to learn bin edges and reference distributions.
    3. Call ``score()`` on each incoming window to obtain both PSI and CW-PSI.

    The class is intentionally **not** a subclass of ``BaseDetector`` because
    its ``fit`` and ``score`` signatures require additional arrays (confidence
    scores) that do not match the base interface.  It is designed as a
    standalone novelty module that can be composed alongside the existing
    detector suite in the drift-check task.
    """

    def __init__(
        self,
        n_bins: int = _DEFAULT_N_BINS,
        min_samples: int = _DEFAULT_MIN_SAMPLES,
        epsilon: float = _EPSILON,
    ) -> None:
        """
        Args:
            n_bins: Number of percentile-based histogram bins.
            min_samples: Minimum sample count required in each window.
            epsilon: Floor value to clamp near-zero fractions.
        """
        # --- Configuration (immutable after __init__) ---
        self._requested_n_bins: int = n_bins
        self.min_samples: int = min_samples
        self.epsilon: float = epsilon

        # --- Learned state (populated by fit()) ---
        self.n_bins: int = n_bins
        self.bin_edges: Optional[np.ndarray] = None
        self.baseline_dist: Optional[np.ndarray] = None
        self.baseline_confidence_weights: Optional[np.ndarray] = None
        self.feature_name: Optional[str] = None

        # --- Diagnostics ---
        self._is_fitted: bool = False

    # ------------------------------------------------------------------
    # FIT
    # ------------------------------------------------------------------
    def fit(
        self,
        baseline_values: np.ndarray,
        baseline_confidences: Optional[np.ndarray] = None,
        feature_name: str = "feature",
    ) -> None:
        """Fit histogram bins, baseline distribution, and per-bin confidence
        weights from the reference (training / golden) data.

        Args:
            baseline_values:
                1-D array of feature values from the baseline window.
            baseline_confidences:
                1-D array of prediction confidence scores aligned with
                ``baseline_values``.  Each element ∈ [0, 1].
                If ``None``, per-bin weights default to 1.0 (standard PSI).
            feature_name:
                Human-readable name for logging / error messages.

        Raises:
            ValueError: If the baseline is shorter than ``min_samples``.
        """
        # ── Input validation ──────────────────────────────────────────
        baseline_values = np.asarray(baseline_values, dtype=np.float64).ravel()

        if baseline_values.shape[0] < self.min_samples:
            raise ValueError(
                f"[CW-PSI] baseline for '{feature_name}' requires "
                f">={self.min_samples} samples, got {baseline_values.shape[0]}"
            )

        self.feature_name = feature_name

        # ── Step 1: Build percentile-based histogram bin edges ────────
        # Exactly mirrors PSIDetector.fit() in app/detectors/psi.py:
        #   • Compute (n_bins + 1) evenly-spaced percentiles from 0 to 100
        #   • De-duplicate edges with np.unique to handle low-cardinality
        #     features (e.g. a feature with only 3 distinct values)
        #   • Update n_bins to reflect the actual number of usable bins
        self.bin_edges = np.percentile(
            baseline_values,
            np.linspace(0, 100, self._requested_n_bins + 1),
        )
        self.bin_edges = np.unique(self.bin_edges)
        self.n_bins = len(self.bin_edges) - 1

        if self.n_bins < 1:
            raise ValueError(
                f"[CW-PSI] baseline for '{feature_name}' produced <1 usable "
                f"bin after edge deduplication (all values identical?)"
            )

        # ── Step 2: Compute baseline distribution fractions ───────────
        baseline_counts, _ = np.histogram(baseline_values, bins=self.bin_edges)
        self.baseline_dist = baseline_counts / baseline_values.shape[0]

        # ── Step 3: Compute per-bin mean confidence weights ───────────
        if baseline_confidences is not None:
            baseline_confidences = np.asarray(
                baseline_confidences, dtype=np.float64
            ).ravel()

            if baseline_confidences.shape[0] != baseline_values.shape[0]:
                raise ValueError(
                    f"[CW-PSI] baseline_confidences length "
                    f"({baseline_confidences.shape[0]}) must match "
                    f"baseline_values length ({baseline_values.shape[0]})"
                )

            # Digitize each sample into the correct bin index.
            # np.digitize returns 1-based indices; subtract 1 and clip to
            # [0, n_bins-1] so out-of-range points map to the first/last bin.
            bin_indices = np.digitize(baseline_values, self.bin_edges) - 1
            bin_indices = np.clip(bin_indices, 0, self.n_bins - 1)

            # Mean confidence per bin.  Bins with zero baseline samples get a
            # weight of 1.0 (neutral — they won't contribute to PSI anyway
            # because the baseline fraction will be ≈ epsilon).
            self.baseline_confidence_weights = np.ones(self.n_bins, dtype=np.float64)
            for b in range(self.n_bins):
                mask = bin_indices == b
                if mask.any():
                    self.baseline_confidence_weights[b] = float(
                        np.mean(baseline_confidences[mask])
                    )
        else:
            # No confidence data — weights default to 1.0 (standard PSI mode)
            self.baseline_confidence_weights = np.ones(self.n_bins, dtype=np.float64)

        self._is_fitted = True

        logger.info(
            "cw_psi_fitted",
            feature=feature_name,
            n_bins=self.n_bins,
            baseline_samples=baseline_values.shape[0],
            has_confidence=baseline_confidences is not None,
        )

    # ------------------------------------------------------------------
    # SCORE
    # ------------------------------------------------------------------
    def score(
        self,
        current_values: np.ndarray,
        current_confidences: Optional[np.ndarray] = None,
    ) -> CWPSIResult:
        """Compute standard PSI and confidence-weighted CW-PSI for the
        current observation window.

        Args:
            current_values:
                1-D array of feature values from the current (live) window.
            current_confidences:
                1-D array of prediction confidence scores aligned with
                ``current_values``.  Each element ∈ [0, 1].

                **Fallback**: If ``None``, CW-PSI degrades gracefully to
                standard PSI (all per-bin weights = 1.0) and the result's
                ``is_fallback`` flag is set to ``True``.

        Returns:
            CWPSIResult containing both PSI and CW-PSI alongside per-bin
            diagnostics.

        Raises:
            RuntimeError: If ``fit()`` has not been called.
            ValueError: If the current window is shorter than ``min_samples``
                or the confidence array length mismatches.
        """
        # ── Guard: detector must be fitted ────────────────────────────
        if not self._is_fitted:
            raise RuntimeError(
                "[CW-PSI] Detector not fitted.  Call fit() before score()."
            )

        # Narrow types for the type-checker: after fit(), these are always set.
        assert self.bin_edges is not None
        assert self.baseline_dist is not None

        # ── Input coercion & validation ───────────────────────────────
        current_values = np.asarray(current_values, dtype=np.float64).ravel()

        if current_values.shape[0] < self.min_samples:
            # Insufficient data — return zeroed result to avoid noisy scores
            # from tiny windows.  The orchestrator can check n_bins == 0 or
            # the raw PSI == 0 to know a real computation wasn't possible.
            logger.warning(
                "cw_psi_insufficient_samples",
                feature=self.feature_name,
                got=current_values.shape[0],
                need=self.min_samples,
            )
            return CWPSIResult(
                psi=0.0,
                cw_psi=0.0,
                per_bin_psi=np.zeros(self.n_bins),
                per_bin_cw_psi=np.zeros(self.n_bins),
                current_weights=np.ones(self.n_bins),
                n_bins=self.n_bins,
                is_fallback=True,
            )

        # ── Determine fallback mode ───────────────────────────────────
        is_fallback = current_confidences is None

        if not is_fallback:
            current_confidences = np.asarray(
                current_confidences, dtype=np.float64
            ).ravel()

            if current_confidences.shape[0] != current_values.shape[0]:
                raise ValueError(
                    f"[CW-PSI] current_confidences length "
                    f"({current_confidences.shape[0]}) must match "
                    f"current_values length ({current_values.shape[0]})"
                )

        # ── Step 1: Current distribution fractions ────────────────────
        current_counts, _ = np.histogram(current_values, bins=self.bin_edges)
        current_dist = current_counts / current_values.shape[0]

        # ── Step 2: Epsilon-safe distributions ────────────────────────
        # Clamp both distributions so that no bin fraction is below epsilon.
        # This prevents log(0) and division-by-zero in the PSI formula.
        baseline_safe = np.maximum(self.baseline_dist, self.epsilon)
        current_safe = np.maximum(current_dist, self.epsilon)

        # ── Step 3: Standard PSI (unweighted) ─────────────────────────
        per_bin_psi = (current_safe - baseline_safe) * np.log(
            current_safe / baseline_safe
        )
        psi_total = float(np.sum(per_bin_psi))

        # ── Step 4: Per-bin confidence weights from *current* window ──
        if not is_fallback:
            assert current_confidences is not None  # narrowed by is_fallback check
            # Digitize current samples into bins (same logic as fit()).
            bin_indices = np.digitize(current_values, self.bin_edges) - 1
            bin_indices = np.clip(bin_indices, 0, self.n_bins - 1)

            current_weights = np.ones(self.n_bins, dtype=np.float64)
            for b in range(self.n_bins):
                mask = bin_indices == b
                if mask.any():
                    current_weights[b] = float(
                        np.mean(current_confidences[mask])
                    )
                # Bins with no current samples keep weight = 1.0
                # Their current_safe fraction is already at epsilon so
                # the per-bin PSI contribution is negligible.
        else:
            # Fallback: uniform weights → CW-PSI collapses to standard PSI
            current_weights = np.ones(self.n_bins, dtype=np.float64)

        # ── Step 5: CW-PSI = Σ w_i × (A_i − E_i) × ln(A_i / E_i) ───
        per_bin_cw_psi = current_weights * per_bin_psi
        cw_psi_total = float(np.sum(per_bin_cw_psi))

        logger.info(
            "cw_psi_scored",
            feature=self.feature_name,
            psi=round(psi_total, 6),
            cw_psi=round(cw_psi_total, 6),
            n_current=current_values.shape[0],
            fallback=is_fallback,
        )

        return CWPSIResult(
            psi=psi_total,
            cw_psi=cw_psi_total,
            per_bin_psi=per_bin_psi,
            per_bin_cw_psi=per_bin_cw_psi,
            current_weights=current_weights,
            n_bins=self.n_bins,
            is_fallback=is_fallback,
        )

    # ------------------------------------------------------------------
    # CONVENIENCE / INTROSPECTION
    # ------------------------------------------------------------------
    @property
    def is_fitted(self) -> bool:
        """Whether ``fit()`` has been called successfully."""
        return self._is_fitted

    def __repr__(self) -> str:
        status = "fitted" if self._is_fitted else "unfitted"
        return (
            f"ConfidenceWeightedPSI(n_bins={self.n_bins}, "
            f"min_samples={self.min_samples}, status={status})"
        )
