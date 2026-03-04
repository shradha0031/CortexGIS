"""Base classes and interfaces for geospatial tools."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ToolStatus(Enum):
    """Status of a tool execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ToolResult:
    """Standardized result from any tool execution."""
    
    tool_name: str
    operation: str
    status: ToolStatus
    output_files: List[str]  # Paths to generated artifacts
    metrics: Dict[str, Any] = None  # Optional metrics (area, count, etc.)
    logs: List[str] = None  # Execution logs
    error_message: str = None
    
    def is_success(self) -> bool:
        return self.status == ToolStatus.SUCCESS
    
    def to_dict(self) -> Dict:
        return {
            "tool": self.tool_name,
            "operation": self.operation,
            "status": self.status.value,
            "output_files": self.output_files,
            "metrics": self.metrics or {},
            "logs": self.logs or [],
            "error": self.error_message,
        }


class GeoTool:
    """Abstract base class for geospatial tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, operation: str, params: Dict[str, Any], **kwargs) -> ToolResult:
        """
        Execute a named operation with given parameters.
        Must be implemented by subclasses.
        """
        raise NotImplementedError(f"{self.name}.execute() not implemented")
    
    def supported_operations(self) -> List[str]:
        """Return list of supported operations."""
        raise NotImplementedError


class DummyTool(GeoTool):
    """Placeholder tool for testing (always succeeds)."""
    
    def __init__(self, name: str = "dummy"):
        super().__init__(name, "Dummy tool for testing")
    
    def execute(self, operation: str, params: Dict[str, Any], **kwargs) -> ToolResult:
        return ToolResult(
            tool_name=self.name,
            operation=operation,
            status=ToolStatus.SUCCESS,
            output_files=[f"{self.name}_{operation}_output.tif"],
            metrics={"dummy_metric": len(params)},
            logs=[f"Executed {operation} with params: {params}"]
        )
    
    def supported_operations(self) -> List[str]:
        return ["test", "dummy_process"]
