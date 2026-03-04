"""Evaluation and benchmarking utilities for CortexGIS workflows."""
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import time


@dataclass
class BenchmarkResult:
    """Results from executing a benchmark."""
    workflow_id: str
    test_case: str
    execution_time_seconds: float
    memory_peak_mb: float
    successful_steps: int
    total_steps: int
    accuracy_metrics: Dict[str, float] = None
    error_message: Optional[str] = None
    
    def success_rate(self) -> float:
        """Return percentage of successful steps."""
        if self.total_steps == 0:
            return 0.0
        return 100.0 * self.successful_steps / self.total_steps
    
    def to_dict(self) -> Dict:
        return {
            "workflow_id": self.workflow_id,
            "test_case": self.test_case,
            "execution_time_seconds": self.execution_time_seconds,
            "memory_peak_mb": self.memory_peak_mb,
            "successful_steps": self.successful_steps,
            "total_steps": self.total_steps,
            "success_rate_percent": self.success_rate(),
            "accuracy_metrics": self.accuracy_metrics or {},
            "error": self.error_message,
        }


class MetricsComputer:
    """Compute evaluation metrics for workflows."""
    
    @staticmethod
    def compute_floating_point_accuracy(predicted, ground_truth, metric="iou"):
        """
        Compute accuracy metrics for raster outputs (flood mask, suitability map).
        
        Args:
            predicted: predicted binary/classified raster (array-like)
            ground_truth: reference raster (array-like)
            metric: "iou" (Intersection over Union), "f1", "accuracy", "precision", "recall"
        
        Returns:
            float: metric value in [0, 1]
        """
        # Stub implementation
        if metric == "iou":
            # IoU = TP / (TP + FP + FN)
            return 0.82  # Placeholder
        elif metric == "f1":
            # F1 = 2 * (precision * recall) / (precision + recall)
            return 0.87  # Placeholder
        elif metric == "accuracy":
            return 0.91  # Placeholder
        elif metric == "precision":
            return 0.89  # Placeholder
        elif metric == "recall":
            return 0.85  # Placeholder
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    @staticmethod
    def compute_spatial_accuracy(predicted_vector, ground_truth_vector):
        """
        Compute accuracy metrics for vector outputs (site boundaries, flood extents).
        
        Args:
            predicted_vector: predicted GeoJSON features
            ground_truth_vector: reference GeoJSON features
        
        Returns:
            dict with metrics (area_error_percent, boundary_shift_m, etc.)
        """
        # Stub: would use shapely for actual computation
        return {
            "area_error_percent": 8.5,
            "boundary_shift_meters": 45.2,
            "positional_accuracy_meters": 50,
        }
    
    @staticmethod
    def compute_temporal_performance(execution_log: List[Dict]) -> Dict[str, float]:
        """
        Compute timing metrics from execution log.
        
        Returns:
            dict with timing stats
        """
        step_times = []
        for entry in execution_log:
            # Stub: extract timing from logs
            pass
        
        return {
            "total_time_seconds": 1245.5,
            "mean_step_time_seconds": 124.55,
            "slowest_step_seconds": 450.2,
            "slowest_step_id": "fetch_sentinel1",
        }


class BenchmarkSuite:
    """Run benchmarks and generate reports."""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.baseline = None  # Reference for comparison
    
    def register_benchmark(self, workflow_id: str, test_cases: List[Dict]):
        """
        Register benchmark test cases for a workflow.
        
        Args:
            workflow_id: workflow identifier
            test_cases: list of {"name": "...", "aoi": "...", "params": {...}}
        """
        # Would store for later execution
        pass
    
    def run_benchmark(self, workflow, test_case: Dict, executor) -> BenchmarkResult:
        """
        Execute a single benchmark test case.
        
        Returns:
            BenchmarkResult with timing and accuracy metrics
        """
        test_name = test_case.get("name", "unknown")
        
        # Stub: would actually run workflow and collect metrics
        result = BenchmarkResult(
            workflow_id=workflow.get("id"),
            test_case=test_name,
            execution_time_seconds=1245.5,
            memory_peak_mb=2048.0,
            successful_steps=14,
            total_steps=14,
            accuracy_metrics={
                "iou": 0.82,
                "f1_score": 0.87,
                "execution_efficiency": 0.94,
            }
        )
        
        self.results.append(result)
        return result
    
    def compare_to_baseline(self, baseline_result: BenchmarkResult) -> Dict:
        """
        Compare benchmark results to baseline (e.g., manual workflow).
        
        Returns:
            dict with comparison metrics
        """
        if len(self.results) == 0:
            return {}
        
        latest = self.results[-1]
        
        return {
            "time_speedup": baseline_result.execution_time_seconds / latest.execution_time_seconds,
            "accuracy_improvement_percent": (
                (latest.accuracy_metrics.get("iou", 0) - baseline_result.accuracy_metrics.get("iou", 0)) * 100
            ),
            "consistency": "high" if latest.success_rate() > 95 else "medium",
        }
    
    def generate_report(self, output_path: str = "benchmark_report.json"):
        """Generate a comprehensive benchmark report."""
        report = {
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "num_benchmarks": len(self.results),
            },
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "avg_execution_time_seconds": sum(r.execution_time_seconds for r in self.results) / max(1, len(self.results)),
                "avg_success_rate_percent": sum(r.success_rate() for r in self.results) / max(1, len(self.results)),
                "total_memory_mb": sum(r.memory_peak_mb for r in self.results),
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def export_csv(self, output_path: str = "benchmark_results.csv"):
        """Export results to CSV for analysis."""
        import csv
        
        with open(output_path, 'w', newline='') as f:
            fieldnames = ["workflow_id", "test_case", "execution_time_s", "success_rate_pct", "iou", "f1_score"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow({
                    "workflow_id": result.workflow_id,
                    "test_case": result.test_case,
                    "execution_time_s": result.execution_time_seconds,
                    "success_rate_pct": result.success_rate(),
                    "iou": result.accuracy_metrics.get("iou", "") if result.accuracy_metrics else "",
                    "f1_score": result.accuracy_metrics.get("f1_score", "") if result.accuracy_metrics else "",
                })


# Predefined benchmark test cases

FLOOD_BENCHMARKS = [
    {
        "name": "small_aoi",
        "aoi": "test_data/aoi_small.geojson",
        "date_range": ["2024-08-01", "2024-08-31"],
        "description": "Small AOI (100 sq km) for regression testing"
    },
    {
        "name": "medium_aoi",
        "aoi": "test_data/aoi_medium.geojson",
        "date_range": ["2024-08-01", "2024-08-31"],
        "description": "Medium AOI (500 sq km) typical use case"
    },
    {
        "name": "large_aoi",
        "aoi": "test_data/aoi_large.geojson",
        "date_range": ["2024-08-01", "2024-08-31"],
        "description": "Large AOI (2000 sq km) stress test"
    },
]

SITE_SUITABILITY_BENCHMARKS = [
    {
        "name": "flat_terrain",
        "aoi": "test_data/aoi_flat.geojson",
        "constraints": {"max_slope": 5, "min_distance_to_roads": 1, "max_distance_to_roads": 5},
        "description": "Area with minimal topographic variation (easier case)"
    },
    {
        "name": "mountainous",
        "aoi": "test_data/aoi_mountainous.geojson",
        "constraints": {"max_slope": 5, "min_distance_to_roads": 1, "max_distance_to_roads": 5},
        "description": "Steep, complex terrain (harder case)"
    },
]
