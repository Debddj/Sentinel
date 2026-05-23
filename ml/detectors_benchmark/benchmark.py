"""Benchmark runner."""
import pandas as pd

def run_benchmark():
    """Run detector benchmarks and generate report."""
    results = []
    # Benchmark logic
    report = pd.DataFrame(results)
    return report

if __name__ == "__main__":
    benchmark_report = run_benchmark()
    benchmark_report.to_markdown("benchmark.md")
