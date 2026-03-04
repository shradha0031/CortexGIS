"""Validate example workflows against schema."""
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from planner.geospatial_planner import GeospatialPlanner


def validate_workflow_file(filepath: str) -> tuple:
    """
    Validate a workflow JSON file.
    
    Returns: (is_valid, errors, workflow_dict)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
    except Exception as e:
        return False, [f"Failed to parse JSON: {e}"], None
    
    # Use planner to validate
    planner = GeospatialPlanner()
    valid, errors = planner.validate_workflow(workflow)
    
    return valid, errors, workflow


def main():
    """Validate all example workflows."""
    workflows_dir = os.path.join(os.path.dirname(__file__), "..", "workflows")
    workflow_files = sorted(Path(workflows_dir).glob("*.json"))
    
    print("=" * 70)
    print("Workflow Validation Report")
    print("=" * 70)
    
    total = len(workflow_files)
    valid_count = 0
    
    for workflow_file in workflow_files:
        print(f"\n📄 {workflow_file.name}")
        is_valid, errors, workflow = validate_workflow_file(str(workflow_file))
        
        if is_valid:
            print(f"  ✓ VALID")
            if workflow:
                print(f"    ID: {workflow.get('id')}")
                print(f"    Name: {workflow.get('name')}")
                print(f"    Steps: {len(workflow.get('steps', []))}")
                print(f"    Confidence: {workflow.get('confidence', 'N/A')}")
            valid_count += 1
        else:
            print(f"  ✗ INVALID")
            for err in errors:
                print(f"    - {err}")
    
    print("\n" + "=" * 70)
    print(f"Summary: {valid_count}/{total} workflows valid")
    print("=" * 70)
    
    return 0 if valid_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
