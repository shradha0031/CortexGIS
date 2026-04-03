"""Demo: run executable benchmarks for planner + executor."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evaluation.benchmark import (
    BenchmarkSuite,
    FLOOD_BENCHMARKS,
    SITE_SUITABILITY_BENCHMARKS,
    MANUAL_BASELINES,
)
from planner.geospatial_planner import GeospatialPlanner
from planner.local_llm_client import build_local_llm_client_from_env
from executor.executor import ToolRegistry, WorkflowExecutor


def _run_cases(suite: BenchmarkSuite, planner: GeospatialPlanner, workflow_type: str, test_cases):
    print(f"\n[{workflow_type.upper()}] Running {len(test_cases)} benchmark cases")
    print("-" * 72)
    for case in test_cases:
        print(f"Case: {case['name']} | Query: {case['query']}")
        executor = WorkflowExecutor(ToolRegistry())
        result = suite.run_benchmark(
            planner=planner,
            executor=executor,
            workflow_type=workflow_type,
            test_case=case,
            output_dir="./outputs",
        )
        print(
            f"  -> id={result.workflow_id}, steps={result.successful_steps}/{result.total_steps}, "
            f"runtime={result.execution_time_seconds:.3f}s, artifacts={result.artifacts_generated}, "
            f"errors={result.errors_count}"
        )


def main():
    os.makedirs("outputs", exist_ok=True)

    print("=" * 72)
    print("CortexGIS Benchmark Runner")
    print("=" * 72)

    llm_client = build_local_llm_client_from_env()
    planner = GeospatialPlanner(llm_client=llm_client)

    print("Planner backend:", llm_client.describe() if llm_client else "stub")

    suite = BenchmarkSuite()

    _run_cases(suite, planner, "flood", FLOOD_BENCHMARKS)
    _run_cases(suite, planner, "suitability", SITE_SUITABILITY_BENCHMARKS)

    report = suite.generate_report("outputs/benchmark_report.json", baselines=MANUAL_BASELINES)
    suite.export_csv("outputs/benchmark_results.csv")

    summary = report["summary"]
    print("\n" + "=" * 72)
    print("Summary")
    print("=" * 72)
    print("Benchmarks:", report["metadata"]["num_benchmarks"])
    print("Avg Runtime (s):", summary["avg_execution_time_seconds"])
    print("Avg Success Rate (%):", summary["avg_success_rate_percent"])
    print("Avg Peak Memory (MB):", summary["avg_memory_peak_mb"])
    print("Total Artifacts:", summary["total_artifacts_generated"])
    print("Total Errors:", summary["total_errors"])

    baseline_cmp = report.get("manual_baseline_comparison", {})
    if baseline_cmp:
        print("\n" + "=" * 72)
        print("Manual Baseline Comparison")
        print("=" * 72)
        for workflow_type, cmp in baseline_cmp.items():
            print(f"[{workflow_type}] speedup={cmp['time_speedup_x']}x, ")
            print(
                f"  success_delta={cmp['success_rate_delta_percent']}%, "
                f"error_reduction={cmp['error_reduction']}"
            )

    print("\nSaved:")
    print("- outputs/benchmark_report.json")
    print("- outputs/benchmark_results.csv")


if __name__ == "__main__":
    main()
