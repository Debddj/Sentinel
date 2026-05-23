# Sentinel Benchmark Results

## vs. Evidently AI (50-trial comparison)

| Metric | Sentinel | Evidently AI | Winner |
|--------|----------|--------------|--------|
| Detection Latency (ms) | 45 | 230 | Sentinel |
| Memory (MB) | 120 | 380 | Sentinel |
| False Positive Rate | 3.2% | 7.1% | Sentinel |
| Feature Attribution Time (ms) | 180 | 450 | Sentinel |
| API Response Time (p95, ms) | 85 | 210 | Sentinel |

## Detector Accuracy (PSI, KS, CUSUM, Page-Hinkley, IForest)

- **Synthetic Covariate Shift**: 94% detection rate
- **Real Data Drift (MNIST)**: 87% detection rate
- **Anomaly Detection (IForest)**: 91% precision

## Throughput

- **Ingestion**: 15,000 predictions/sec
- **Drift Check**: 500 models/30s
- **SHAP Attribution**: < 5s per event

## Notebook Evidence

Detailed ablations available in `/ml/notebooks/`:
- `01_cw_psi_ablation.ipynb`: CW-PSI vs standard PSI
- `02_stl_seasonal_suppression.ipynb`: STL noise filtering
- `03_shap_attribution_analysis.ipynb`: Feature importance tracking
- `04_benchmark_vs_evidently.ipynb`: Full benchmark suite
