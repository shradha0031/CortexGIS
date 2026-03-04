# CortexGIS Streamlit UI

A web-based interface for CortexGIS that enables interactive query → planning → execution → visualization of geospatial workflows.

## Features

- **Query Input**: Enter natural language descriptions of geospatial tasks.
- **Chain-of-Thought Display**: See the reasoning steps the LLM uses to plan workflows.
- **Workflow Inspection**: Review generated workflows in JSON format; edit if needed.
- **Execution**: Execute workflows step-by-step with live feedback.
- **Results Dashboard**: View metrics, logs, and output artifacts.
- **Tool Registry**: Browse all available geospatial tools and their operations.

## Installation & Setup

### 1. Install dependencies

```bash
pip install -r requirements_ui.txt
```

### 2. Run the Streamlit app

From the project root (or `ui/` directory):

```bash
streamlit run ui/app.py
```

The app will open at `http://localhost:8501` by default.

## Usage

1. **Query Tab**: Enter a natural language query (e.g., "Detect floods using SAR").
2. **Workflow Tab**: Review the generated workflow JSON; optionally edit it.
3. **Execute Tab**: Click "Execute" to run the workflow step-by-step.
4. **Results Tab**: View execution metrics, logs, and generated outputs.

## Optional: Full Setup with Dependencies

To enable actual geospatial processing:

```bash
pip install geopandas rasterio whitebox sentence-transformers faiss-cpu
python scripts/init_rag_index.py  # Initialize RAG system
```

Then queries will leverage the RAG retriever for context-aware planning.

## Architecture

- **Planner**: Generates workflows from queries using CoT reasoning.
- **Executor**: Runs workflows using tools from the registry.
- **Registry**: Manages available geospatial tools (Vector, Raster, Whitebox, etc.).

Each module is independent, so the UI can work in "stub mode" (immediate feedback) or "full mode" (with ML/GIS dependencies).
