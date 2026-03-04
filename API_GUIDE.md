# CortexGIS API Guide

Complete reference for integrating CortexGIS modules into your applications.

---

## Table of Contents

1. [Planner API](#planner-api)
2. [Tool Registry & Executor](#tool-registry--executor)
3. [RAG Index](#rag-index)
4. [Data Ingestion](#data-ingestion)
5. [Workflow Format](#workflow-format)
6. [Complete Examples](#complete-examples)

---

## Planner API

### Overview

The planner generates multi-step workflows from natural language queries using Chain-of-Thought reasoning.

**Module:** `planner/geospatial_planner.py`

### Basic Usage

```python
from planner.geospatial_planner import GeospatialPlanner

# Initialize planner
planner = GeospatialPlanner()

# Generate workflow from query
query = "Detect areas flooded using Sentinel-1 SAR data"
cot_reasoning, workflow_json = planner.plan_workflow(query)

# Print reasoning steps
print("=== Chain-of-Thought Reasoning ===")
print(cot_reasoning)

# Inspect generated workflow
print("\n=== Generated Workflow ===")
print(f"Workflow ID: {workflow_json['dataset_id']}")
print(f"Steps: {len(workflow_json['steps'])}")
for step in workflow_json['steps']:
    print(f"  Step {step['step_id']}: {step['tool']}.{step['operation']}")
```

**Output:**
```
=== Chain-of-Thought Reasoning ===
1. Task Decomposition: Flood detection → SAR analysis
2. Data Selection: Sentinel-1 VV-mode optimal...
3. Processing: SAR → filter → threshold → mask → vectorize
4. Confidence: 0.85

=== Generated Workflow ===
Workflow ID: flood_plan_001
Steps: 10
  Step 1: sentinel.fetch_s1
  Step 2: raster.speckle_filter
  ...
```

### Methods

#### `plan_workflow(query: str) -> Tuple[str, dict]`

Generate a workflow from natural language query.

**Parameters:**
- `query` (str): Natural language description of geospatial task

**Returns:**
- `cot_reasoning` (str): Chain-of-Thought reasoning steps
- `workflow_json` (dict): Structured workflow matching JSON schema

**Raises:**
- `ValueError`: If workflow fails validation

**Example:**
```python
# Flood mapping
cot, wf = planner.plan_workflow("Detect floods in Southeast Asia")

# Solar suitability
cot, wf = planner.plan_workflow(
    "Find optimal solar farm locations considering "
    "terrain, road access, and landcover"
)

# Land cover change
cot, wf = planner.plan_workflow(
    "Track forest loss over 5 years using Landsat"
)
```

#### `get_workflow_history() -> list`

Retrieve all previously generated workflows in this session.

**Returns:**
- `list` of workflow metadata dicts with keys: `workflow_id`, `query`, `timestamp`, `steps_count`, `confidence`

**Example:**
```python
history = planner.get_workflow_history()
for item in history:
    print(f"{item['workflow_id']}: {item['query']}")
```

### Integrating Real LLMs

To use actual LLMs instead of stubs, edit `_stub_reasoning()` in the planner:

#### OpenAI Example

```python
def _plan_with_openai(self, query: str):
    import openai
    
    # Set API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Get task type from query
    task_type = self._infer_task_type(query)
    
    # Load system prompt
    from prompts.system_prompts import GEOSPATIAL_SYSTEM_PROMPT, PROMPT_TEMPLATES
    system_msg = GEOSPATIAL_SYSTEM_PROMPT
    if task_type in PROMPT_TEMPLATES:
        system_msg += f"\n\n{PROMPT_TEMPLATES[task_type]}"
    
    # Call GPT-4
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": query}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    reasoning = response['choices'][0]['message']['content']
    workflow = self._extract_workflow_from_response(reasoning)
    return reasoning, workflow
```

#### Local LLM Example (using Ollama)

```python
def _plan_with_ollama(self, query: str):
    import requests
    import json
    
    # Connect to local Ollama instance
    ollama_url = "http://localhost:11434/api/generate"
    
    task_type = self._infer_task_type(query)
    from prompts.system_prompts import PROMPT_TEMPLATES
    
    prompt = f"""
{PROMPT_TEMPLATES.get(task_type, '')}

User Query: {query}

Generate a workflow JSON with steps and reasoning.
"""
    
    response = requests.post(
        ollama_url,
        json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        }
    )
    
    result = response.json()
    reasoning = result['response']
    workflow = self._extract_workflow_from_response(reasoning)
    return reasoning, workflow
```

---

## Tool Registry & Executor

### Overview

Tools are standardized geospatial operations registered with the executor. Workflows invoke tools by name and operation.

**Modules:** 
- `executor/tool_base.py` — Abstract base class
- `executor/tool_adapters.py` — Concrete implementations (Vector, Raster, Whitebox)
- `executor/executor.py` — Registry & executor logic

### Base Class

All tools inherit from `GeoTool`:

```python
from executor.tool_base import GeoTool, ToolResult, ToolStatus

class MyGeoTool(GeoTool):
    """Custom tool for geospatial processing."""
    
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="Description of what this tool does"
        )
    
    def execute(self, **params) -> ToolResult:
        """Execute the tool operation."""
        try:
            # Validate parameters
            required = ['input_path', 'output_path']
            for key in required:
                if key not in params:
                    return ToolResult(
                        status=ToolStatus.FAILED,
                        error=f"Missing required param: {key}"
                    )
            
            input_path = params['input_path']
            output_path = params['output_path']
            threshold = params.get('threshold', 0.5)  # Optional
            
            # Perform computation
            result_data = self._process(input_path, threshold)
            
            # Return structured result
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output={
                    'raster': result_data,
                    'statistics': {
                        'mean': result_data.mean(),
                        'std': result_data.std()
                    }
                },
                metrics={'execution_time_s': 42.5}
            )
        
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=str(e)
            )
    
    def _process(self, input_path: str, threshold: float):
        # Your implementation here
        import rasterio
        with rasterio.open(input_path) as src:
            data = src.read(1)
            return data > threshold
```

### Using Tool Registry

```python
from executor.executor import ToolRegistry, WorkflowExecutor
from executor.tool_adapters import VectorTool, RasterTool
from pathlib import Path

# Create registry
registry = ToolRegistry()

# Register built-in tools
registry.register("vector", VectorTool())
registry.register("raster", RasterTool())
registry.register("my_tool", MyGeoTool())

# Verify registration
print(registry.list_tools())
# Output:
# {
#     'vector': [...operations...],
#     'raster': [...operations...],
#     'my_tool': ['process_data', ...]
# }

# Execute a workflow
workflow_json = {
    "dataset_id": "test_001",
    "steps": [
        {
            "step_id": 1,
            "tool": "vector",
            "operation": "buffer",
            "parameters": {
                "input": "/path/to/shapes.geojson",
                "distance": 100
            },
            "depends_on": []
        },
        {
            "step_id": 2,
            "tool": "my_tool",
            "operation": "process_data",
            "parameters": {
                "input_path": "$step_1.outputs.raster",
                "threshold": 0.7
            },
            "depends_on": [1]
        }
    ]
}

executor = WorkflowExecutor(registry)
execution_log = executor.execute_workflow(workflow_json)

print(f"Execution Status: {execution_log['overall_status']}")
for step_log in execution_log['step_logs']:
    print(f"  Step {step_log['step_id']}: {step_log['status']}")
    if step_log['status'] == 'success':
        print(f"    Metrics: {step_log.get('metrics', {})}")
    else:
        print(f"    Error: {step_log.get('error')}")
```

### Extending with New Operations

Add operations to existing tools:

```python
from executor.tool_adapters import VectorTool

class ExtendedVectorTool(VectorTool):
    def __init__(self):
        super().__init__()
        self.operations.append('my_custom_operation')
    
    def execute(self, operation: str, **params):
        if operation == 'my_custom_operation':
            return self._my_operation(**params)
        else:
            return super().execute(operation=operation, **params)
    
    def _my_operation(self, input_geojson: str, param1: float):
        # Custom logic
        import json
        with open(input_geojson) as f:
            geojson = json.load(f)
        # Process...
        return ToolResult(status=ToolStatus.SUCCESS, output=geojson)
```

---

## RAG Index

### Overview

Retrieve relevant geospatial documentation to inform workflow planning.

**Module:** `rag/rag_index.py`

### Basic Usage

```python
from rag.rag_index import SimpleRAGIndex
from rag.sample_docs import SAMPLE_DOCUMENTS

# Initialize index
rag_index = SimpleRAGIndex(
    embedding_model="all-MiniLM-L6-v2",
    index_type="flat"  # or "ivf" for larger datasets
)

# Ingest documents
rag_index.ingest_documents(SAMPLE_DOCUMENTS)

# Retrieve relevant docs for a query
query = "How to detect floods using SAR?"
docs = rag_index.retrieve(query, top_k=3)

for i, doc in enumerate(docs):
    print(f"\n[{i+1}] Similarity: {doc['similarity']:.3f}")
    print(f"Title: {doc['title']}")
    print(f"Content: {doc['content'][:200]}...")
```

**Output:**
```
[1] Similarity: 0.875
Title: Sentinel-1 SAR for Flood Detection
Content: Sentinel-1 is a C-band SAR sensor with VV and VH polarizations...

[2] Similarity: 0.762
Title: Rasterio DEM Processing
Content: Digital Elevation Models (DEMs) are raster datasets encoding...

[3] Similarity: 0.521
Title: Cloud Detection in Optical Imagery
Content: Cloud cover frequently complicates optical remote sensing...
```

### Methods

#### `ingest_documents(documents: list) -> None`

Add documents to the RAG index.

**Parameters:**
- `documents` (list): List of dicts with keys: `id`, `title`, `content`, `metadata` (optional)

**Example:**
```python
custom_docs = [
    {
        "id": "custom_001",
        "title": "My Custom Processor",
        "content": "This tool does X with parameters Y and Z...",
        "metadata": {"category": "custom", "version": "1.0"}
    }
]
rag_index.ingest_documents(custom_docs)
```

#### `retrieve(query: str, top_k: int = 5) -> list`

Semantic search for relevant documents.

**Parameters:**
- `query` (str): Search query
- `top_k` (int): Number of results to return (default 5)

**Returns:**
- `list` of dicts with keys: `id`, `title`, `content`, `similarity` (0-1 score)

**Example:**
```python
# User query
user_query = "Solar panel placement on hillsides"

# Retrieve docs
docs = rag_index.retrieve(user_query, top_k=5)

# Use in planner context
context = "\n".join([
    f"- {doc['title']}: {doc['content'][:100]}"
    for doc in docs
])

# Pass to LLM planner
llm_prompt = f"""
Given these resources:
{context}

User asks: {user_query}

Generate a workflow...
"""
```

#### `save(filepath: str) -> None` and `load(filepath: str) -> None`

Persist and load the index.

```python
# Save
rag_index.save("rag_index.pkl")

# Load in new session
rag_index = SimpleRAGIndex.load("rag_index.pkl")
```

### Customizing Embeddings

```python
# Use different embeddings models
from sentence_transformers import SentenceTransformer

class CustomRAGIndex(SimpleRAGIndex):
    def __init__(self, custom_model: str = "paraphrase-MiniLM-L6-v2"):
        super().__init__(embedding_model=custom_model)

# Or use OpenAI embeddings
class OpenAIRAGIndex(SimpleRAGIndex):
    def _get_embedding_function(self):
        import openai
        def embed(text):
            response = openai.Embedding.create(
                model="text-embedding-3-small",
                input=text
            )
            return response['data'][0]['embedding']
        return embed
```

---

## Data Ingestion

### Overview

Fetch geospatial data from OSM, Sentinel, SRTM, Bhoonidhi, and custom sources.

**Module:** `data/ingestion.py`

### Basic Usage

```python
from data.ingestion import DatasetManager

# Initialize manager
data_mgr = DatasetManager()

# List available datasets
catalog = data_mgr.get_catalog()
for dataset in catalog:
    print(f"- {dataset['id']}: {dataset['source']}")

# Fetch data
aoi = {
    "type": "Polygon",
    "coordinates": [[
        [85.0, 27.0],  # SW corner
        [85.0, 28.0],  # NW corner
        [86.0, 28.0],  # NE corner
        [86.0, 27.0],  # SE corner
        [85.0, 27.0]   # Close ring
    ]]
}

# OSM roads
roads = data_mgr.fetch_osm_roads(aoi)
print(f"Found {len(roads)} road segments")

# Sentinel-1 SAR
s1_data = data_mgr.fetch_sentinel1(
    aoi=aoi,
    start_date="2023-01-01",
    end_date="2023-01-31",
    mode="VV"  # VV, VH, or both
)

# SRTM DEM
dem = data_mgr.fetch_srtm(aoi)

# Available data sources
available = data_mgr.get_available_sources()
print(available)
```

### Methods

#### `fetch_osm_roads(aoi: dict) -> GeoDataFrame`

Fetch OpenStreetMap road network.

**Parameters:**
- `aoi` (dict): GeoJSON Polygon defining area of interest

**Returns:**
- `GeoDataFrame` with columns: `geometry`, `type`, `name`, `highway`, `id`

**Real Implementation (commented in code):**

```python
def fetch_osm_roads(self, aoi):
    """
    Using Overpass API:
    
    import overpy
    import json
    
    bbox = aoi['coordinates'][0]  # Get bounding box
    query = f'''
    [bbox: {bbox[0][1]}, {bbox[0][0]}, {bbox[2][1]}, {bbox[2][0]}]
    (
        way["highway"~"motorway|primary|secondary"];
        relation["type"="multipolygon"]["highway"];
    );
    out geom;
    '''
    
    api = overpy.Overpass()
    result = api.query(query)
    # Parse to GeoDataFrame...
    """
```

#### `fetch_sentinel1(aoi: dict, start_date: str, end_date: str, mode: str) -> xr.Dataset`

Fetch Sentinel-1 SAR data.

**Parameters:**
- `aoi` (dict): GeoJSON Polygon
- `start_date` (str): Start date (YYYY-MM-DD)
- `end_date` (str): End date (YYYY-MM-DD)
- `mode` (str): Polarization mode ("VV", "VH", or "both")

**Returns:**
- `xr.Dataset` with dimensions: (time, lat, lon) and data variables for each polarization

**Real Implementation (commented in code):**

```python
def fetch_sentinel1(self, aoi, start_date, end_date, mode):
    """
    Using Copernicus Hub (SentinelHub Python):
    
    from sentinelhub import SentinelHubRequest, DataCollection, MimeType
    
    request = SentinelHubRequest(
        data_collection=DataCollection.SENTINEL1,
        time_interval=(start_date, end_date),
        layer="VV",  # or "VH"
        bbox=aoi_to_bbox(aoi),
        resolution=10,  # 10m resolution
        responses=[SentinelHubRequest.output_response('default', MimeType.TIFF)]
    )
    
    data = request.get_data()
    # Convert to xarray Dataset...
    """
```

#### `fetch_srtm(aoi: dict, resolution: int = 30) -> rioxarray.DataArray`

Fetch SRTM Digital Elevation Model.

**Parameters:**
- `aoi` (dict): GeoJSON Polygon
- `resolution` (int): Grid resolution in meters (30 or 90 available)

**Returns:**
- `rioxarray.DataArray` with elevation values and spatial metadata

#### `fetch_bhoonidhi_lulc(aoi: dict, year: float = 2020) -> rioxarray.DataArray`

Fetch Bhoonidhi land-use / land-cover data (India-specific).

---

## Workflow Format

### JSON Schema

Workflows are JSON documents matching this schema:

```json
{
  "dataset_id": "workflow_id_001",
  "query": "Natural language description of the analysis",
  "cot_reasoning": [
    "1. First reasoning step",
    "2. Second reasoning step",
    "..."
  ],
  "confidence": 0.85,
  "steps": [
    {
      "step_id": 1,
      "tool": "tool_name",
      "operation": "operation_name",
      "description": "What this step does",
      "parameters": {
        "param1": "value1",
        "param2": "$step_0.outputs.field_name"  # Parameter linking
      },
      "depends_on": []
    },
    {
      "step_id": 2,
      "tool": "other_tool",
      "operation": "other_op",
      "parameters": {
        "input": "$step_1.outputs.result"  # Reference previous step output
      },
      "depends_on": [1]
    }
  ],
  "expected_output": {
    "type": "feature_collection",
    "description": "Resulting geospatial data"
  },
  "caveats": ["Limitation 1", "Limitation 2"],
  "notes": "Implementation notes or operational guidance"
}
```

### Parameter Linking

Outputs from one step are referenced in downstream steps:

```javascript
// Step 1 output
{
  "step_id": 1,
  "output": {
    "raster": "path/to/result.tif",
    "statistics": { "mean": 0.5, "std": 0.1 }
  }
}

// Step 2 references Step 1
{
  "step_id": 2,
  "parameters": {
    "input_raster": "$step_1.outputs.raster",
    "mean_threshold": "$step_1.outputs.statistics.mean"
  }
}
```

### Tool Result Format

All tool outputs follow this structure:

```python
{
    "status": "success|failed|partial",
    "output": {
        # Tool-specific data: raster path, GeoDataFrame, etc.
    },
    "metrics": {
        "execution_time_s": 42.5,
        "memory_used_mb": 512,
        "output_size_mb": 128
    },
    "error": null  # or string with error details if failed
}
```

---

## Complete Examples

### Example 1: Flood Mapping Workflow

```python
from planner.geospatial_planner import GeospatialPlanner
from executor.executor import WorkflowExecutor, ToolRegistry
from executor.tool_adapters import VectorTool, RasterTool, WhiteboxTool
from rag.rag_index import SimpleRAGIndex
from rag.sample_docs import SAMPLE_DOCUMENTS

# Step 1: Initialize components
rag_index = SimpleRAGIndex()
rag_index.ingest_documents(SAMPLE_DOCUMENTS)

planner = GeospatialPlanner()

registry = ToolRegistry()
registry.register("vector", VectorTool())
registry.register("raster", RasterTool())
registry.register("whitebox", WhiteboxTool())

executor = WorkflowExecutor(registry)

# Step 2: Plan workflow from query
query = "Detect flooded areas in the Kathmandu valley using Sentinel-1 SAR data"
cot_reasoning, workflow = planner.plan_workflow(query)

print("=== CoT Reasoning ===")
print(cot_reasoning)

print("\n=== Workflow ===")
print(f"ID: {workflow['dataset_id']}")
print(f"Steps: {len(workflow['steps'])}")

# Step 3: Augment with RAG context
rag_docs = rag_index.retrieve(query, top_k=3)
print("\n=== Retrieved Documentation ===")
for doc in rag_docs:
    print(f"- {doc['title']} (similarity: {doc['similarity']:.2f})")

# Step 4: Execute workflow
print("\n=== Executing Workflow ===")
execution_log = executor.execute_workflow(workflow)

# Step 5: Process results
print(f"\nExecution Status: {execution_log['overall_status']}")
print(f"Total Time: {execution_log['total_time_s']:.1f}s")

for step_log in execution_log['step_logs']:
    status_icon = "✓" if step_log['status'] == 'success' else "✗"
    print(f"  {status_icon} Step {step_log['step_id']}: {step_log['status']}")
```

### Example 2: Solar Site Suitability with Custom Tool

```python
from executor.tool_base import GeoTool, ToolResult, ToolStatus
from executor.executor import ToolRegistry, WorkflowExecutor
import json

# Define custom tool for solar irradiance ranking
class SolarRankingTool(GeoTool):
    def __init__(self):
        super().__init__("solar", "Solar irradiance calculations")
        self.operations = ['fetch_irradiance', 'rank_sites']
    
    def execute(self, operation: str, **params):
        if operation == 'fetch_irradiance':
            return self._fetch_irradiance(**params)
        elif operation == 'rank_sites':
            return self._rank_sites(**params)
        else:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Unknown operation: {operation}"
            )
    
    def _fetch_irradiance(self, aoi: dict, year: int = 2023):
        # Stub: Return mock data
        import numpy as np
        irradiance = np.random.uniform(1200, 1800, (100, 100))
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output={"irradiance_map": irradiance.tolist()},
            metrics={"data_points": 10000}
        )
    
    def _rank_sites(self, candidates: dict, irradiance: list, slope: list):
        # Combined scoring: high irradiance + low slope
        scores = {}
        # Implementation...
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output={"ranked_sites": scores},
            metrics={"sites_evaluated": len(candidates)}
        )

# Register and use
registry = ToolRegistry()
registry.register("solar", SolarRankingTool())

# Workflow that uses solar tool
workflow = {
    "dataset_id": "suitability_001",
    "steps": [
        {
            "step_id": 1,
            "tool": "solar",
            "operation": "fetch_irradiance",
            "parameters": {"aoi": {...}, "year": 2023},
            "depends_on": []
        },
        {
            "step_id": 2,
            "tool": "solar",
            "operation": "rank_sites",
            "parameters": {
                "candidates": "$step_1.outputs.irradiance_map",
                "irradiance": "$step_1.outputs.irradiance_map",
                "slope": "$step_0.outputs.slope"  # From earlier step
            },
            "depends_on": [1]
        }
    ]
}

executor = WorkflowExecutor(registry)
log = executor.execute_workflow(workflow)
```

### Example 3: Multi-Stage Data Pipeline

```python
from data.ingestion import DatasetManager
from executor.executor import ToolRegistry, WorkflowExecutor
from executor.tool_adapters import VectorTool, RasterTool
import json

# Initialize data manager
data_mgr = DatasetManager()

# Define AOI (example: Kathmandu valley)
aoi = {
    "type": "Polygon",
    "coordinates": [[
        [85.1, 27.6],
        [85.1, 27.8],
        [85.3, 27.8],
        [85.3, 27.6],
        [85.1, 27.6]
    ]]
}

# Fetch data from multiple sources
print("Fetching data...")
roads = data_mgr.fetch_osm_roads(aoi)
dem = data_mgr.fetch_srtm(aoi)
s1 = data_mgr.fetch_sentinel1(
    aoi, 
    start_date="2024-01-01",
    end_date="2024-01-31",
    mode="VV"
)

print(f"Roads: {len(roads)} segments")
print(f"DEM: {dem.shape}")
print(f"Sentinel-1: {s1.dims}")

# Use with executor
registry = ToolRegistry()
registry.register("vector", VectorTool())
registry.register("raster", RasterTool())

workflow = {
    "dataset_id": "preprocessing_001",
    "steps": [
        {
            "step_id": 1,
            "tool": "vector",
            "operation": "buffer",
            "parameters": {
                "input": roads,  # Direct GeoDataFrame
                "distance": 100
            }
        },
        {
            "step_id": 2,
            "tool": "raster",
            "operation": "mask",
            "parameters": {
                "raster": dem,  # Direct DataArray
                "mask": "$step_1.outputs.geometry"
            }
        }
    ]
}

executor = WorkflowExecutor(registry)
result = executor.execute_workflow(workflow)
```

---

## Tips & Best Practices

1. **Always validate workflows** with JSON schema before execution
2. **Use parameter linking** (`$step_N.outputs`) for clean, traceable workflows
3. **Implement graceful fallbacks** in tools (return partial results if some operations fail)
4. **Log execution metrics** (time, memory) for performance monitoring
5. **Version your workflows** in Git for reproducibility and rollback
6. **Test with small AOI first** before scaling to larger regions
7. **Cache expensive operations** (DEM, landcover maps) when running multiple workflows
8. **Use appropriate CRS/projections** for your region (e.g., UTM zones)

---

**For more examples, see:** `scripts/demo_*.py` and `workflows/`

