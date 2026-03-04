#!/usr/bin/env python3
"""
CortexGIS Verification Script
Systematically tests all completed components
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and report result."""
    print(f"\n{'='*70}")
    print(f"✓ Testing: {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, cwd="c:\\projects\\cortexgis")
    
    if result.returncode == 0:
        print(f"✓ PASS: {description}")
        return True
    else:
        print(f"✗ FAIL: {description}")
        return False

def main():
    print("\n" + "="*70)
    print("CortexGIS - Complete Verification Suite")
    print("="*70)
    
    results = {}
    
    # Task 1: Architecture
    results["Architecture Doc"] = run_command(
        "python -c \"import os; assert os.path.exists('ARCHITECTURE.md'); print('✓ ARCHITECTURE.md exists')\"",
        "Task 1: Architecture document exists"
    )
    
    # Task 2: JSON Schemas
    results["Workflow Schema"] = run_command(
        "python scripts/generate_example_workflow.py",
        "Task 2: Workflow schema validation"
    )
    
    results["GIS Functions Schema"] = run_command(
        "python -c \"import json; schema = json.load(open('schemas/gis_functions_schema.json')); print('✓ GIS functions schema valid')\"",
        "Task 2: GIS functions schema validation"
    )
    
    # Task 3: RAG Pipeline
    results["RAG Index"] = run_command(
        "python scripts/init_rag_index.py",
        "Task 3: RAG index initialization"
    )
    
    # Task 4: LLM Planner
    results["LLM Planner"] = run_command(
        "python scripts/demo_planner.py",
        "Task 4: LLM planner workflow generation"
    )
    
    # Task 5: Tool Abstraction & Executor
    results["Integrated Pipeline"] = run_command(
        "python scripts/demo_integrated.py",
        "Task 5: Planner + Executor integration"
    )
    
    # Task 6: Streamlit UI
    results["Streamlit UI Syntax"] = run_command(
        "python -m py_compile ui/app.py && echo ✓ Streamlit UI app compiles",
        "Task 6: Streamlit UI syntax check"
    )
    
    # Task 7: Data Ingestion
    results["Data Ingestion"] = run_command(
        "python scripts/demo_data_ingestion.py",
        "Task 7: Dataset ingestion demo"
    )
    
    # Task 8: Example Workflows
    results["Example Workflows"] = run_command(
        "python scripts/validate_workflows.py",
        "Task 8: Example workflow validation"
    )
    
    # Task 9: Benchmarking
    results["Benchmarking Suite"] = run_command(
        "python scripts/demo_benchmarking.py",
        "Task 9: Evaluation & benchmarking"
    )
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*70)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
