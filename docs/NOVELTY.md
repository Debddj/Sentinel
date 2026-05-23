# Sentinel Innovations

## Novel #1: Adaptive EWMA Control Limits

Instead of static thresholds, we learn time-weighted adaptive limits from recent drift scores.

**Formula**: `threshold_t = α × score_t + (1-α) × threshold_{t-1}`

**Benefit**: Automatically adjusts to model's baseline behavior; reduces false positives.

---

## Novel #2: Confidence-Weighted PSI

Extends PSI by weighting bins by prediction confidence, catching "weak" distribution shifts.

**Formula**: `CW-PSI = Σ (p_i - q_i) × log(p_i/q_i) × confidence_i`

**Benefit**: Detects subtle covariate shifts early; complements standard PSI.

---

## Novel #3: Drift Type Classifier

Rule-based engine that classifies drift type from detector patterns:
- **Data Drift**: Large PSI + small prediction shift
- **Concept Drift**: Large prediction shift + increasing errors
- **Covariate Shift**: Feature distribution change, no target shift

**Benefit**: Actionable alerts (different mitigation per type).

---

## Novel #4: STL Decomposition + Alert Suppression

Decomposes drift score into trend/seasonal/residual, suppresses seasonal noise.

**Benefit**: Fewer false alerts; focuses on genuine degradation trends.

---

## Novel #5: Calibration Curve Analysis

Generates ROC-style false positive vs. detection rate curves, recommends optimal thresholds.

**Benefit**: Data-driven threshold selection; tunable precision/recall trade-off.

---

## Δ_SHAP: Feature Attribution

Tracks change in SHAP feature importance between baseline and current.

**Benefit**: Explains *which features* caused drift.
