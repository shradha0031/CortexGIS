# CortexGIS System Architecture

This document outlines the high-level architecture for the CortexGIS reasoning-enabled geospatial workflow system. It is based on the Chat2Geo reference project but tailored to the challenge requirements: chain-of-thought reasoning, geoprocessing orchestration, RAG integration, and transparent output.

## Core Components

1. **User Interface**
   - *Streamlit-based* web UI (or Next.js) for inputting natural language queries, displaying CoT logs, and previewing map layers.
   - Components:
     - Query box with optional ROI upload/drawing.
     - CoT reasoning panel.
     - Workflow editor/viewer (JSON/YAML).
     - Map canvas for layer visualization (using folium/leaflet or MapLibre).
     - Metrics dashboard.

2. **LLM Planner & Reasoning Engine**
   - Accepts user query + context + retrieved docs.
   - Maintains Chain-of-Thought logs and generates a structured workflow plan.
   - Implemented using LangChain-style `LLMChain` or custom prompt architecture.
   - CoT prompts stored in `prompts/` directory; examples for flood mapping, site suitability, etc.
   - Supports iterative reasoning: tool invocation results fed back into planner for adjustment.

3. **Retrieval-Augmented Generation (RAG)**
   - Maintains a vector store of geospatial documentation, function definitions, and example workflows.
   - Tools: FAISS local index (or Supabase/Weaviate for scale).
   - Retrieval component is called before planning to provide relevant context.
   - Scripts for ingesting docs from QGIS/GDAL manuals and sample workflows.

4. **Tool Abstraction & Executor Layer**
   - Standardized interface (`ToolResult`) for operations.
   - Tool adapters wrap geospatial libraries: GeoPandas, Rasterio, WhiteboxTools, GDAL CLI, PyQGIS headless.
   - Each tool returns output metadata (files, metrics, logs) and any errors.
   - Execution runs in Docker containers or local environment; queue-based asynchronous execution with retry logic.

5. **Data Management Layer**
   - Dataset ingestion scripts for OSM, Bhoonidhi, Sentinel/AWS, SRTM, etc.
   - Spatial database (PostGIS) or file-based caching for quick retrieval.
   - CRS management utilities for reprojection.

6. **Workflow Definition & Serialization**
   - JSON schema (`schemas/workflow_schema.json`) defines valid workflows with steps, tools, parameters, and CoT logs.
   - Workflows stored in version-controlled repo (or database) along with execution history.

7. **Evaluation & Benchmarking Module**
   - Automates execution of workflows on benchmark AOIs with ground truth.
   - Logs logical and syntactic validity, accuracy metrics (IoU, precision/recall), runtime/resource usage.
   - Generates comparison reports against manual baseline.

8. **Monitoring & Logging**
   - Centralized logging of reasoning steps, tool results, errors.
   - Metrics for execution time, resources, failure rates.
   - UI to inspect logs and debug workflows.

9. **Deployment**
   - Containerized services (FastAPI for LLM and contract endpoints, Streamlit or Next.js UI, vector DB, PostGIS).
   - GitHub Actions for CI (lint/test, Docker build, pipeline docs).

## Data Flow Sequence

1. User submits natural language query (optionally with ROI).
2. System runs RAG retrieval to gather context docs.
3. LLM planner generates explanation (CoT) and a workflow plan.
4. Workflow serialized to JSON/YAML, displayed to user for confirmation.
5. Execution layer runs each step sequentially, recording observations; errors trigger retries or human intervention.
6. Final outputs (rasters, vectors, reports) are stored and visualized.
7. Metrics recorded and optionally fed back into RAG for future planning.

## Notes

- **Iterative refinement:** planner can ask clarifying questions or adjust parameters after seeing interim results.
- **Extensibility:** new tools added by registering adapter + metadata in a central registry.
- **Security:** sandbox untrusted code; avoid executing arbitrary Python from unverified sources.

The architecture is intentionally modular to allow independent development of UI, planner, RAG, and execution components.
