"""Evaluation and benchmarking utilities for CortexGIS workflows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import csv
import json
import statistics
import time
import tracemalloc


@dataclass
class BenchmarkResult:
    """Results from executing one benchmark test case."""

    workflow_id: str
    workflow_type: str
    test_case: str
    query: str
    context: Optional[str]
    execution_time_seconds: float
    memory_peak_mb: float
    successful_steps: int
    total_steps: int
    artifacts_generated: int
    reasoning_steps: int
    errors_count: int
    accuracy_metrics: Dict[str, float] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def success_rate(self) -> float:
        if self.total_steps <= 0:
            return 0.0
        return 100.0 * self.successful_steps / self.total_steps

    def to_dict(self) -> Dict:
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "test_case": self.test_case,
            "query": self.query,
            "context": self.context,
            "execution_time_seconds": self.execution_time_seconds,
            "memory_peak_mb": self.memory_peak_mb,
            "successful_steps": self.successful_steps,
            "total_steps": self.total_steps,
            "success_rate_percent": self.success_rate(),
            "artifacts_generated": self.artifacts_generated,
            "reasoning_steps": self.reasoning_steps,
            "errors_count": self.errors_count,
            "validation_errors": self.validation_errors,
            "accuracy_metrics": self.accuracy_metrics,
            "error": self.error_message,
        }


class BenchmarkSuite:
    """Run benchmark scenarios and generate reports."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []

    def _compute_baseline_comparison(self, baselines: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
        """Compare measured workflow results against provided manual baseline values."""
        by_type: Dict[str, List[BenchmarkResult]] = {}
        for result in self.results:
            by_type.setdefault(result.workflow_type, []).append(result)

        comparison: Dict[str, Dict[str, float]] = {}
        for workflow_type, entries in by_type.items():
            baseline = baselines.get(workflow_type)
            if not baseline:
                continue

            avg_runtime = statistics.mean([e.execution_time_seconds for e in entries]) if entries else 0.0
            avg_success = statistics.mean([e.success_rate() for e in entries]) if entries else 0.0
            avg_errors = statistics.mean([e.errors_count for e in entries]) if entries else 0.0

            baseline_runtime = float(baseline.get("runtime_seconds", 0.0) or 0.0)
            baseline_success = float(baseline.get("success_rate_percent", 0.0) or 0.0)
            baseline_errors = float(baseline.get("errors_count", 0.0) or 0.0)

            speedup = (baseline_runtime / avg_runtime) if avg_runtime > 0 else 0.0

            comparison[workflow_type] = {
                "baseline_runtime_seconds": round(baseline_runtime, 4),
                "automated_avg_runtime_seconds": round(avg_runtime, 4),
                "time_speedup_x": round(speedup, 4),
                "baseline_success_rate_percent": round(baseline_success, 4),
                "automated_success_rate_percent": round(avg_success, 4),
                "success_rate_delta_percent": round(avg_success - baseline_success, 4),
                "baseline_errors_count": round(baseline_errors, 4),
                "automated_avg_errors_count": round(avg_errors, 4),
                "error_reduction": round(baseline_errors - avg_errors, 4),
            }

        return comparison

    def run_benchmark(
        self,
        *,
        planner,
        executor,
        workflow_type: str,
        test_case: Dict,
        output_dir: str = "./outputs",
    ) -> BenchmarkResult:
        """Execute one benchmark test case using planner + executor."""
        test_name = test_case.get("name", "unknown")
        query = test_case.get("query", "")
        context = test_case.get("context")

        t0 = time.perf_counter()
        tracemalloc.start()

        error_message: Optional[str] = None
        validation_errors: List[str] = []

        try:
            cot, workflow = planner.plan_workflow(query, context=context)
            is_valid, validation_errors = planner.validate_workflow(workflow)
            if not is_valid:
                error_message = "workflow_validation_failed"

            run_summary = executor.execute_workflow(workflow, output_dir=output_dir)
            runtime_seconds = float(run_summary.get("runtime_seconds", 0.0) or 0.0)
            successful_steps = int(run_summary.get("successful_steps", 0) or 0)
            total_steps = int(run_summary.get("total_steps", 0) or 0)
            generated_output_files = run_summary.get("generated_output_files", [])
            errors_count = int(run_summary.get("failed_steps", 0) or 0)

            # Derived quality metrics for benchmark comparability when no ground truth exists.
            logical_validity = 1.0 if is_valid else 0.0
            execution_reliability = (successful_steps / total_steps) if total_steps > 0 else 0.0
            error_resilience = 1.0 if errors_count == 0 else max(0.0, 1.0 - (errors_count / max(1, total_steps)))

            result = BenchmarkResult(
                workflow_id=str(workflow.get("id", "unknown_workflow")),
                workflow_type=workflow_type,
                test_case=test_name,
                query=query,
                context=context,
                execution_time_seconds=runtime_seconds if runtime_seconds > 0 else (time.perf_counter() - t0),
                memory_peak_mb=0.0,
                successful_steps=successful_steps,
                total_steps=total_steps,
                artifacts_generated=len(generated_output_files),
                reasoning_steps=len(cot) if isinstance(cot, list) else 0,
                errors_count=errors_count,
                accuracy_metrics={
                    "logical_validity_score": round(logical_validity, 3),
                    "execution_reliability": round(execution_reliability, 3),
                    "error_resilience": round(error_resilience, 3),
                },
                validation_errors=validation_errors,
                error_message=error_message,
            )
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            result = BenchmarkResult(
                workflow_id="unknown",
                workflow_type=workflow_type,
                test_case=test_name,
                query=query,
                context=context,
                execution_time_seconds=elapsed,
                memory_peak_mb=0.0,
                successful_steps=0,
                total_steps=0,
                artifacts_generated=0,
                reasoning_steps=0,
                errors_count=1,
                accuracy_metrics={
                    "logical_validity_score": 0.0,
                    "execution_reliability": 0.0,
                    "error_resilience": 0.0,
                },
                validation_errors=validation_errors,
                error_message=str(exc),
            )
        finally:
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        result.memory_peak_mb = round(peak_bytes / (1024 * 1024), 3)
        self.results.append(result)
        return result

    def generate_report(
        self,
        output_path: str = "outputs/benchmark_report.json",
        baselines: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> Dict:
        """Write JSON benchmark report and return its object."""
        by_type: Dict[str, List[BenchmarkResult]] = {}
        for result in self.results:
            by_type.setdefault(result.workflow_type, []).append(result)

        def avg(values: List[float]) -> float:
            return round(float(statistics.mean(values)), 4) if values else 0.0

        summary_by_type = {}
        for workflow_type, entries in by_type.items():
            summary_by_type[workflow_type] = {
                "count": len(entries),
                "avg_runtime_seconds": avg([e.execution_time_seconds for e in entries]),
                "avg_success_rate_percent": avg([e.success_rate() for e in entries]),
                "avg_memory_peak_mb": avg([e.memory_peak_mb for e in entries]),
                "avg_logical_validity": avg([e.accuracy_metrics.get("logical_validity_score", 0.0) for e in entries]),
                "avg_error_resilience": avg([e.accuracy_metrics.get("error_resilience", 0.0) for e in entries]),
            }

        report = {
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "num_benchmarks": len(self.results),
            },
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "avg_execution_time_seconds": avg([r.execution_time_seconds for r in self.results]),
                "avg_success_rate_percent": avg([r.success_rate() for r in self.results]),
                "avg_memory_peak_mb": avg([r.memory_peak_mb for r in self.results]),
                "total_artifacts_generated": sum(r.artifacts_generated for r in self.results),
                "total_errors": sum(r.errors_count for r in self.results),
            },
            "summary_by_workflow_type": summary_by_type,
        }

        if baselines:
            report["manual_baseline_comparison"] = self._compute_baseline_comparison(baselines)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report

    def export_csv(self, output_path: str = "outputs/benchmark_results.csv") -> None:
        """Export benchmark table for external analysis."""
        fieldnames = [
            "workflow_id",
            "workflow_type",
            "test_case",
            "query",
            "context",
            "execution_time_seconds",
            "memory_peak_mb",
            "successful_steps",
            "total_steps",
            "success_rate_percent",
            "artifacts_generated",
            "reasoning_steps",
            "errors_count",
            "logical_validity_score",
            "execution_reliability",
            "error_resilience",
            "error",
        ]

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in self.results:
                writer.writerow(
                    {
                        "workflow_id": result.workflow_id,
                        "workflow_type": result.workflow_type,
                        "test_case": result.test_case,
                        "query": result.query,
                        "context": result.context,
                        "execution_time_seconds": result.execution_time_seconds,
                        "memory_peak_mb": result.memory_peak_mb,
                        "successful_steps": result.successful_steps,
                        "total_steps": result.total_steps,
                        "success_rate_percent": result.success_rate(),
                        "artifacts_generated": result.artifacts_generated,
                        "reasoning_steps": result.reasoning_steps,
                        "errors_count": result.errors_count,
                        "logical_validity_score": result.accuracy_metrics.get("logical_validity_score", 0.0),
                        "execution_reliability": result.accuracy_metrics.get("execution_reliability", 0.0),
                        "error_resilience": result.accuracy_metrics.get("error_resilience", 0.0),
                        "error": result.error_message,
                    }
                )


FLOOD_BENCHMARKS = [
    {
        "name": "flood_mandi",
        "query": "Detect flood risk in Mandi",
        "context": "city:Mandi, Himachal Pradesh",
    },
    {
        "name": "flood_pune",
        "query": "Detect flooded areas after heavy rainfall in Pune",
        "context": "city:Pune",
    },
    {
        "name": "flood_bbox",
        "query": "Flood mapping for this AOI",
        "context": "bbox:76.85,31.65,77.00,31.78",
    },
]

SITE_SUITABILITY_BENCHMARKS = [
    {
        "name": "solar_mandi",
        "query": "Find suitable locations for solar farms in Mandi",
        "context": "city:Mandi, Himachal Pradesh",
    },
    {
        "name": "solar_bengaluru",
        "query": "Site suitability analysis for solar parks around Bengaluru",
        "context": "city:Bengaluru",
    },
    {
        "name": "site_bbox",
        "query": "Find suitable sites considering slope and roads",
        "context": "bbox:77.45,12.85,77.75,13.15",
    },
]


MANUAL_BASELINES = {
    "flood": {
        "runtime_seconds": 1800.0,
        "success_rate_percent": 92.0,
        "errors_count": 1.0,
    },
    "suitability": {
        "runtime_seconds": 2400.0,
        "success_rate_percent": 88.0,
        "errors_count": 2.0,
    },
}
