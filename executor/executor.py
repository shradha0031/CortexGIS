"""Tool registry and workflow executor."""
from typing import Dict, List, Any, Optional
from executor.tool_base import GeoTool, ToolResult, ToolStatus
from executor.tool_adapters import VectorTool, RasterTool, WhiteboxTool, SentinelTool
import json


class ToolRegistry:
    """Central registry of available tools."""
    
    def __init__(self):
        self.tools: Dict[str, GeoTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register built-in tool adapters."""
        self.register("vector", VectorTool())
        self.register("raster", RasterTool())
        self.register("whitebox", WhiteboxTool())
        self.register("sentinel", SentinelTool())
    
    def register(self, name: str, tool: GeoTool):
        """Register a tool."""
        self.tools[name] = tool
    
    def get(self, name: str) -> Optional[GeoTool]:
        """Retrieve a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> Dict[str, List[str]]:
        """Return a mapping of tool_name -> supported_operations."""
        return {name: tool.supported_operations() for name, tool in self.tools.items()}


class WorkflowExecutor:
    """Executes workflows step-by-step."""
    
    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        self.registry = tool_registry or ToolRegistry()
        self.execution_log: List[Dict] = []
        self.step_outputs: Dict[str, ToolResult] = {}
    
    def execute_workflow(self, workflow: Dict[str, Any], output_dir: str = ".") -> Dict[str, Any]:
        """
        Execute a complete workflow.
        
        Args:
            workflow: Workflow JSON/dict
            output_dir: Directory to write outputs
        
        Returns:
            Execution summary dict
        """
        workflow_id = workflow.get("id", "unknown_workflow")
        steps = workflow.get("steps", [])

        # Reset execution state for each run so old step logs/results do not leak
        # into the current workflow execution summary.
        self.execution_log = []
        self.step_outputs = {}
        
        print(f"\n[Executor] Starting workflow: {workflow_id}")
        successful_steps = 0
        failed_steps = 0
        
        for step in steps:
            step_id = step.get("id")
            tool_name = step.get("tool")
            operation = step.get("op")
            params = step.get("params", {})
            
            print(f"  [Step] Executing {step_id} ({tool_name}.{operation})")
            
            # Resolve params (substitute references to previous outputs)
            resolved_params = self._resolve_params(params, self.step_outputs)
            
            # Get tool from registry
            tool = self.registry.get(tool_name)
            if tool is None:
                result = ToolResult(
                    tool_name=tool_name,
                    operation=operation,
                    status=ToolStatus.FAILED,
                    output_files=[],
                    error_message=f"Tool '{tool_name}' not found in registry"
                )
            else:
                # Execute tool
                result = tool.execute(operation, resolved_params, output_dir=output_dir)
            
            # Store result
            self.step_outputs[step_id] = result
            self.execution_log.append({
                "step_id": step_id,
                "tool": tool_name,
                "operation": operation,
                "result": result.to_dict()
            })
            
            # Print result
            if result.is_success():
                print(f"    ✓ Success: {result.output_files}")
                successful_steps += 1
            else:
                print(f"    ✗ Failed: {result.error_message}")
                failed_steps += 1
                # Optionally: stop on error or continue?
                # For now, continue to next step
        
        # Compile summary
        summary = {
            "workflow_id": workflow_id,
            "total_steps": len(steps),
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "execution_log": self.execution_log,
            "final_outputs": workflow.get("outputs", []),
        }
        
        print(f"\n[Executor] Workflow complete: {successful_steps}/{len(steps)} steps succeeded")
        return summary
    
    def _resolve_params(self, params: Dict[str, Any], step_outputs: Dict[str, ToolResult]) -> Dict[str, Any]:
        """
        Resolve parameter references.
        E.g., if params has {"input": "$step1.output"}, substitute with actual output.
        """
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("$"):
                # Reference to previous step output
                ref_parts = value[1:].split(".")
                step_id = ref_parts[0]
                if step_id in step_outputs:
                    # For now, just use the first output file
                    resolved[key] = step_outputs[step_id].output_files[0] if step_outputs[step_id].output_files else None
                else:
                    resolved[key] = None
            else:
                resolved[key] = value
        return resolved
