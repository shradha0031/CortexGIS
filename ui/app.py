"""Streamlit UI for CortexGIS."""
import streamlit as st
import streamlit.components.v1 as components
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from planner.geospatial_planner import GeospatialPlanner
from planner.local_llm_client import build_local_llm_client_from_env
from executor.executor import WorkflowExecutor, ToolRegistry


def _parse_bbox_text(bbox_text: str):
    """Parse bbox text in the form minlon,minlat,maxlon,maxlat."""
    if not bbox_text or not bbox_text.strip():
        return None
    parts = [p.strip() for p in bbox_text.split(",")]
    if len(parts) != 4:
        return None
    try:
        minlon, minlat, maxlon, maxlat = [float(p) for p in parts]
    except ValueError:
        return None
    if minlon >= maxlon or minlat >= maxlat:
        return None
    return [minlon, minlat, maxlon, maxlat]


def _view_from_bbox(bbox):
    """Return (lat, lon, zoom) from bbox."""
    minlon, minlat, maxlon, maxlat = bbox
    center_lat = (minlat + maxlat) / 2.0
    center_lon = (minlon + maxlon) / 2.0
    span = max(maxlon - minlon, maxlat - minlat)
    if span <= 0.02:
        zoom = 13
    elif span <= 0.05:
        zoom = 12
    elif span <= 0.1:
        zoom = 11
    elif span <= 0.2:
        zoom = 10
    elif span <= 0.5:
        zoom = 9
    elif span <= 1.0:
        zoom = 8
    else:
        zoom = 6
    return center_lat, center_lon, zoom


def _view_from_workflow(workflow: dict):
    """Infer map view from workflow AOI bbox or step params center coordinates."""
    if not workflow:
        return 18.5204, 73.8567, 9

    inputs = workflow.get("inputs", {})
    bbox = inputs.get("aoi_bbox")
    if isinstance(bbox, list) and len(bbox) == 4:
        return _view_from_bbox(bbox)

    for step in workflow.get("steps", []):
        params = step.get("params", {})
        if "center_lat" in params and "center_lon" in params:
            try:
                return float(params["center_lat"]), float(params["center_lon"]), 10
            except (TypeError, ValueError):
                continue

    return 18.5204, 73.8567, 9


def _extract_geojson_outputs(result: dict) -> list[str]:
    """Collect existing GeoJSON output files from execution logs."""
    output_paths = []
    for entry in result.get("execution_log", []):
        for output_file in entry.get("result", {}).get("output_files", []):
            if isinstance(output_file, str) and output_file.lower().endswith((".geojson", ".json")):
                candidate = Path(output_file)
                if candidate.exists():
                    output_paths.append(str(candidate))
    # Preserve order while removing duplicates.
    return list(dict.fromkeys(output_paths))


def _render_leaflet_map(
        center_lat: float,
        center_lon: float,
        zoom: int,
        geojson_data=None,
        basemap: str = "Road",
):
        """Render a real tile basemap with an optional GeoJSON overlay."""
        tile_layers = {
                "Road": {
                        "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                        "name": "OpenStreetMap",
                        "attribution": "&copy; OpenStreetMap contributors",
                },
                "Satellite": {
                        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                        "name": "Esri World Imagery",
                        "attribution": "Tiles &copy; Esri",
                },
        }
        tile = tile_layers.get(basemap, tile_layers["Road"])
        geojson_json = json.dumps(geojson_data) if geojson_data is not None else "null"
        map_html = f"""
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                html, body {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                }}
                #map {{
                    width: 100%;
                    height: 100%;
                    min-height: 520px;
                    border-radius: 16px;
                    overflow: hidden;
                }}
                .basemap-badge {{
                    position: absolute;
                    z-index: 1000;
                    top: 12px;
                    left: 12px;
                    background: rgba(16, 24, 40, 0.86);
                    color: #fff;
                    padding: 8px 10px;
                    border-radius: 999px;
                    font: 600 12px/1.2 Arial, sans-serif;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div class="basemap-badge">Basemap: {tile['name']}</div>
            <script>
                const map = L.map('map', {{ zoomControl: true, scrollWheelZoom: false }}).setView([{center_lat}, {center_lon}], {zoom});
                L.tileLayer('{tile['url']}', {{
                    attribution: '{tile['attribution']}',
                    maxZoom: 19,
                }}).addTo(map);

                const geojsonData = {geojson_json};
                if (geojsonData) {{
                    const layer = L.geoJSON(geojsonData, {{
                        style: function () {{
                            return {{ color: '#0ea5e9', weight: 3, fillColor: '#38bdf8', fillOpacity: 0.25 }};
                        }},
                        pointToLayer: function (feature, latlng) {{
                            return L.circleMarker(latlng, {{ radius: 6, color: '#0f172a', weight: 2, fillColor: '#38bdf8', fillOpacity: 0.95 }});
                        }},
                        onEachFeature: function (feature, layer) {{
                            if (feature.properties) {{
                                const props = Object.entries(feature.properties)
                                    .map(([key, value]) => `${{key}}: ${{value}}`)
                                    .join('<br>');
                                if (props) layer.bindPopup(props);
                            }}
                        }}
                    }}).addTo(map);

                    const bounds = layer.getBounds();
                    if (bounds.isValid()) {{
                        map.fitBounds(bounds.pad(0.15));
                    }}
                }}
            </script>
        </body>
        </html>
        """
        components.html(map_html, height=560, scrolling=False)


def _render_geojson_map(file_path: str, center_override=None, zoom_override=None, basemap: str = "Road"):
        """Render a GeoJSON file on an interactive map."""
        with open(file_path, "r", encoding="utf-8") as f:
                geojson_data = json.load(f)

        features = geojson_data.get("features", []) if isinstance(geojson_data, dict) else []
        if not features:
                st.warning(f"No features to display in map file: {file_path}")
                return

        # Compute a simple map center from the first coordinate in first feature.
        center_lat = 18.52
        center_lon = 73.84
        try:
                geometry = features[0].get("geometry", {})
                geom_type = geometry.get("type")
                coords = geometry.get("coordinates", [])
                if geom_type == "Point":
                        center_lon, center_lat = coords
                elif geom_type == "Polygon":
                        center_lon, center_lat = coords[0][0]
                elif geom_type == "MultiPolygon":
                        center_lon, center_lat = coords[0][0][0]
        except Exception:
                pass

        if center_override is not None:
                center_lat, center_lon = center_override

        _render_leaflet_map(
                center_lat=center_lat,
                center_lon=center_lon,
                zoom=zoom_override if zoom_override is not None else 10,
                geojson_data=geojson_data,
                basemap=basemap,
        )


def _render_default_map(center_lat: float = 18.5204, center_lon: float = 73.8567, zoom: int = 9, basemap: str = "Road"):
        """Always provide a map canvas even when no vector artifact exists yet."""
        st.caption("Default map view (no GeoJSON layer generated for this run).")
        _render_leaflet_map(center_lat, center_lon, zoom, geojson_data=None, basemap=basemap)


# Page config
st.set_page_config(
    page_title="CortexGIS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
llm_client = build_local_llm_client_from_env()
desired_llm_backend = llm_client.describe() if llm_client else None

if "planner" not in st.session_state or st.session_state.get("llm_backend") != desired_llm_backend:
    st.session_state.planner = GeospatialPlanner(llm_client=llm_client)
    st.session_state.llm_backend = desired_llm_backend

if "executor" not in st.session_state:
    st.session_state.executor = WorkflowExecutor(ToolRegistry())

if "workflow" not in st.session_state:
    st.session_state.workflow = None

if "execution_result" not in st.session_state:
    st.session_state.execution_result = None

if "aoi_context" not in st.session_state:
    st.session_state.aoi_context = None

# Header
st.title("🌍 CortexGIS")
st.markdown("""
Chain-of-Thought reasoning for geospatial workflows.
Automatically generate and execute GIS tasks from natural language queries.
""")
if st.session_state.get("llm_backend"):
    st.caption(f"LLM mode: {st.session_state['llm_backend']}")
else:
    st.caption("LLM mode: stub fallback")

# Sidebar: Tools info
with st.sidebar:
    st.header("🔧 Available Tools")
    if st.session_state.get("llm_backend"):
        st.success(f"LLM mode: {st.session_state['llm_backend']}")
    else:
        st.info("LLM mode: stub fallback")

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

    st.subheader("AOI (Optional)")
    aoi_col1, aoi_col2 = st.columns(2)
    with aoi_col1:
        aoi_city = st.text_input(
            "City/Place name",
            placeholder="E.g., Mandi, Himachal Pradesh",
        )
    with aoi_col2:
        aoi_bbox_text = st.text_input(
            "BBox (minlon,minlat,maxlon,maxlat)",
            placeholder="E.g., 73.80,18.45,73.95,18.60",
        )
    
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
        aoi_context = None
        parsed_bbox = _parse_bbox_text(aoi_bbox_text)

        if aoi_bbox_text.strip() and not parsed_bbox:
            st.error("Invalid BBox format. Use: minlon,minlat,maxlon,maxlat")
            st.stop()

        if parsed_bbox:
            minlon, minlat, maxlon, maxlat = parsed_bbox
            aoi_context = f"bbox:{minlon},{minlat},{maxlon},{maxlat}"
        elif aoi_city.strip():
            aoi_context = f"city:{aoi_city.strip()}"

        with st.spinner("Reasoning... 💭"):
            cot, workflow = st.session_state.planner.plan_workflow(user_query, context=aoi_context)
            st.session_state.workflow = workflow
            # Clear prior run results whenever a new workflow is generated.
            st.session_state.execution_result = None
            st.session_state.aoi_context = aoi_context
        
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
            # Rebuild executor per run to avoid stale registry or cached state.
            st.session_state.executor = WorkflowExecutor(ToolRegistry())
            with st.spinner("Executing workflow... ⏳"):
                result = st.session_state.executor.execute_workflow(
                    st.session_state.workflow,
                    output_dir="./outputs"
                )
                st.session_state.execution_result = result
                
                # Index the executed workflow for RAG learning
                try:
                    from rag.workflow_indexer import WorkflowIndexer
                    indexer = WorkflowIndexer(rag_retriever=st.session_state.planner.rag_retriever)
                    
                    # Get reasoning from planner history
                    reasoning = []
                    if st.session_state.planner.reasoning_history:
                        last_entry = st.session_state.planner.reasoning_history[-1]
                        reasoning = last_entry.get("reasoning", [])
                    
                    # Index the workflow
                    indexer.index_workflow(
                        workflow=st.session_state.workflow,
                        execution_result=result,
                        query=st.session_state.workflow.get("description", ""),
                        reasoning=reasoning,
                    )
                except Exception as e:
                    st.caption(f"ℹ️ Note: Could not index workflow: {e}")
            
            st.success("✓ Execution complete! Check the 'Results' tab.")
    else:
        st.warning("⚠️ No workflow to execute. Generate one first.")

# TAB 4: Results
with tab4:
    st.header("Step 4: View Results")
    
    if st.session_state.execution_result:
        result = st.session_state.execution_result

        # Show a compact failure summary first so execution issues are visible at a glance.
        failed_entries = [
            entry for entry in result.get("execution_log", [])
            if entry.get("result", {}).get("status") != "success"
        ]
        if failed_entries:
            st.error(f"{len(failed_entries)} step(s) failed. See quick summary below.")
            for entry in failed_entries:
                step_result = entry.get("result", {})
                st.write(
                    f"- `{entry.get('step_id', 'unknown')}`: "
                    f"`{entry.get('tool', 'unknown')}.{entry.get('operation', 'unknown')}`"
                )
                if step_result.get("error"):
                    st.caption(f"Error: {step_result['error']}")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Steps", result.get("total_steps", 0))
        col2.metric("✓ Successful", result.get("successful_steps", 0))
        col3.metric("✗ Failed", result.get("failed_steps", 0))
        col4.metric("Success Rate", 
                   f"{100 * result.get('successful_steps', 0) / max(1, result.get('total_steps', 1)):.0f}%")

        runtime_seconds = float(result.get("runtime_seconds", 0.0) or 0.0)
        step_count = int(result.get("total_steps", 0) or 0)
        avg_step_ms = (runtime_seconds * 1000.0 / max(1, step_count))
        generated_count = len(result.get("generated_output_files", []))

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Runtime (s)", f"{runtime_seconds:.2f}")
        kpi2.metric("Avg Step (ms)", f"{avg_step_ms:.1f}")
        kpi3.metric("Artifacts", generated_count)

        # Map visualization for vector outputs.
        st.subheader("Map Preview")
        view_lat, view_lon, view_zoom = _view_from_workflow(st.session_state.workflow)
        basemap_choice = st.selectbox("Basemap style", ["Road", "Satellite"], index=0)
        geojson_outputs = _extract_geojson_outputs(result)
        if geojson_outputs:
            selected_map_file = st.selectbox("Select output layer", geojson_outputs)
            _render_geojson_map(
                selected_map_file,
                center_override=(view_lat, view_lon),
                zoom_override=view_zoom,
                basemap=basemap_choice,
            )
        else:
            st.info("No GeoJSON outputs found for this run. Showing default map.")
            _render_default_map(view_lat, view_lon, view_zoom, basemap=basemap_choice)
        
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
