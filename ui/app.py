"""Streamlit UI for CortexGIS."""
import streamlit as st
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from planner.geospatial_planner import GeospatialPlanner
from executor.executor import WorkflowExecutor, ToolRegistry


# Page config
st.set_page_config(
    page_title="CortexGIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "planner" not in st.session_state:
    st.session_state.planner = GeospatialPlanner()

if "executor" not in st.session_state:
    st.session_state.executor = WorkflowExecutor(ToolRegistry())

if "workflow" not in st.session_state:
    st.session_state.workflow = None

if "execution_result" not in st.session_state:
    st.session_state.execution_result = None

# Header
st.title("🌍 CortexGIS")
st.markdown("""
Chain-of-Thought reasoning for geospatial workflows.
Automatically generate and execute GIS tasks from natural language queries.
""")

# Sidebar: Tools info
with st.sidebar:
    st.header("🔧 Available Tools")
    registry = st.session_state.executor.registry
    tools_info = registry.list_tools()
    for tool_name, ops in tools_info.items():
        with st.expander(f"**{tool_name}**"):
            for op in ops:
                st.write(f"- `{op}`")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["Query", "Workflow", "Execute", "Results"])

# TAB 1: Query Input
with tab1:
    st.header("Step 1: Enter Your Query")
    st.markdown("Describe what geospatial analysis you want to perform.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_query = st.text_area(
            "Natural Language Query:",
            placeholder="E.g., 'Detect flooded areas using SAR imagery for August 2024'",
            height=100
        )
    with col2:
        st.write("")
        st.write("")
        generate_button = st.button("🔄 Generate Workflow", type="primary")
    
    if generate_button and user_query:
        with st.spinner("Reasoning... 💭"):
            cot, workflow = st.session_state.planner.plan_workflow(user_query)
            st.session_state.workflow = workflow
        
        # Display CoT reasoning
        st.subheader("Chain-of-Thought Reasoning")
        for i, step in enumerate(cot, 1):
            st.write(f"**{i}.** {step}")
        
        st.success("✓ Workflow generated! Check the 'Workflow' tab.")

# TAB 2: Workflow Inspection
with tab2:
    st.header("Step 2: Review Workflow")
    
    if st.session_state.workflow:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Workflow Summary")
            workflow = st.session_state.workflow
            st.write(f"**ID**: `{workflow.get('id')}`")
            st.write(f"**Description**: {workflow.get('description')}")
            st.write(f"**Total Steps**: {len(workflow.get('steps', []))}")
            st.write(f"**Outputs**: {workflow.get('outputs')}")
        
        with col2:
            st.subheader("Workflow Validation")
            valid, errors = st.session_state.planner.validate_workflow(workflow)
            if valid:
                st.success("✓ Workflow is valid")
            else:
                st.error("✗ Validation errors:")
                for err in errors:
                    st.write(f"- {err}")
        
        # Show full JSON
        st.subheader("Full Workflow JSON")
        st.json(workflow)
        
        # Option to edit
        st.subheader("Edit Workflow (Advanced)")
        edited_json = st.text_area(
            "Edit JSON directly:",
            value=json.dumps(workflow, indent=2),
            height=300
        )
        if st.button("Update Workflow from JSON"):
            try:
                st.session_state.workflow = json.loads(edited_json)
                st.success("✓ Workflow updated")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
    else:
        st.info("📝 No workflow yet. Generate one from a query in the 'Query' tab.")

# TAB 3: Execute
with tab3:
    st.header("Step 3: Execute Workflow")
    
    if st.session_state.workflow:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Ready to execute the workflow.")
        with col2:
            execute_button = st.button("▶️ Execute", type="primary")
        
        if execute_button:
            with st.spinner("Executing workflow... ⏳"):
                result = st.session_state.executor.execute_workflow(
                    st.session_state.workflow,
                    output_dir="./outputs"
                )
                st.session_state.execution_result = result
            st.success("✓ Execution complete! Check the 'Results' tab.")
    else:
        st.warning("⚠️ No workflow to execute. Generate one first.")

# TAB 4: Results
with tab4:
    st.header("Step 4: View Results")
    
    if st.session_state.execution_result:
        result = st.session_state.execution_result
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Steps", result.get("total_steps", 0))
        col2.metric("✓ Successful", result.get("successful_steps", 0))
        col3.metric("✗ Failed", result.get("failed_steps", 0))
        col4.metric("Success Rate", 
                   f"{100 * result.get('successful_steps', 0) / max(1, result.get('total_steps', 1)):.0f}%")
        
        # Execution log
        st.subheader("Execution Log")
        for entry in result.get("execution_log", []):
            with st.expander(f"**{entry['step_id']}**: {entry['tool']}.{entry['operation']}"):
                step_result = entry.get("result", {})
                status = step_result.get("status", "unknown")
                
                if status == "success":
                    st.success(f"Status: {status}")
                else:
                    st.error(f"Status: {status}")
                
                if step_result.get("error"):
                    st.write(f"**Error**: {step_result['error']}")
                
                if step_result.get("output_files"):
                    st.write(f"**Outputs**: {step_result['output_files']}")
                
                if step_result.get("metrics"):
                    st.write(f"**Metrics**: {step_result['metrics']}")
        
        # Full result JSON
        st.subheader("Full Result JSON")
        st.json(result)
    else:
        st.info("📊 No execution results yet. Execute a workflow first.")

# Footer
st.markdown("---")
st.markdown("""
**CortexGIS** | Chain-of-Thought reasoning for geospatial workflows  
Powered by LLM planning, RAG retrieval, and geospatial tool abstraction.
""")
