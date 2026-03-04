"""Demo of the LLM Planner generating workflows."""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from planner.geospatial_planner import GeospatialPlanner


def main():
    print("=" * 60)
    print("CortexGIS LLM Planner Demo")
    print("=" * 60)
    
    # Initialize planner (no LLM connected yet; uses stubs)
    planner = GeospatialPlanner(llm_client=None, rag_retriever=None)
    
    # Example queries
    queries = [
        "Detect flooded areas in the region using SAR imagery for August 2024.",
        "Find suitable locations for a solar farm in the area, avoiding wetlands and steep slopes.",
        "Analyze land cover changes between 2020 and 2024.",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"User: {query}\n")
        
        # Plan workflow
        cot, workflow = planner.plan_workflow(query)
        
        # Display CoT reasoning
        print("Chain-of-Thought Reasoning:")
        for step in cot:
            print(f"  {step}")
        
        # Display workflow
        print("\nGenerated Workflow:")
        print(json.dumps(workflow, indent=2))
        
        # Validate
        valid, errors = planner.validate_workflow(workflow)
        if valid:
            print("\n✓ Workflow validation PASSED")
        else:
            print("\n✗ Workflow validation FAILED:")
            for err in errors:
                print(f"  - {err}")
    
    # Display history
    print("\n" + "=" * 60)
    print(f"Planning history: {len(planner.reasoning_history)} queries processed")
    print("=" * 60)


if __name__ == "__main__":
    main()
