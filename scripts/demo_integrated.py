"""Demo: planner generates workflow, executor runs it."""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from planner.geospatial_planner import GeospatialPlanner
from executor.executor import WorkflowExecutor, ToolRegistry


def main():
    print("=" * 70)
    print("CortexGIS Integrated Demo: Planner → Executor")
    print("=" * 70)
    
    # Step 1: Use planner to generate workflow
    print("\n[Step 1: Planner] Generating workflow from user query...")
    planner = GeospatialPlanner(llm_client=None)
    
    query = "Detect flooded areas in the region using SAR imagery for August 2024."
    cot, workflow = planner.plan_workflow(query)
    
    print(f"\nUser Query: {query}\n")
    print("Chain-of-Thought Reasoning:")
    for step in cot:
        print(f"  {step}\n")
    
    print("Generated Workflow:")
    print(json.dumps(workflow, indent=2))
    
    # Step 2: Validate and setup executor
    print("\n\n[Step 2: Validation] Checking workflow...")
    valid, errors = planner.validate_workflow(workflow)
    if valid:
        print("✓ Workflow validation PASSED\n")
    else:
        print("✗ Workflow validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return
    
    # Step 3: Execute the workflow
    print("[Step 3: Executor] Executing workflow step-by-step...\n")
    registry = ToolRegistry()
    executor = WorkflowExecutor(tool_registry=registry)
    
    execution_summary = executor.execute_workflow(workflow, output_dir="./outputs")
    
    # Step 4: Report results
    print("\n\n" + "=" * 70)
    print("EXECUTION SUMMARY")
    print("=" * 70)
    print(json.dumps(execution_summary, indent=2, default=str))
    
    # List available tools
    print("\n\n" + "=" * 70)
    print("AVAILABLE TOOLS IN REGISTRY")
    print("=" * 70)
    tools_info = registry.list_tools()
    for tool_name, ops in tools_info.items():
        print(f"\n{tool_name}:")
        for op in ops:
            print(f"  - {op}")


if __name__ == "__main__":
    main()
