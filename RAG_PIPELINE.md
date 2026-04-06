# RAG Pipeline Documentation

## Overview

The RAG (Retrieval-Augmented Generation) pipeline enhances CortexGIS workflow planning by retrieving relevant workflows, tools, and templates from a semantic knowledge base before generating new workflows.

## Components

### 1. **GeoRAGRetriever** (`rag/rag_retriever.py`)
- Semantic search using sentence-transformers + FAISS
- Retrieves similar workflows, tool documentation, and templates
- Supports keyword-based fallback when embeddings unavailable
- Tag-based filtering for targeted queries

**Key Methods:**
- `retrieve(query, top_k=3)`: Semantic search for relevant documents
- `retrieve_by_tags(tags)`: Filter by workflow/tool tags
- `get_context_for_planning(query)`: Generate formatted context for planner prompts

### 2. **Tool Documentation** (`rag/tool_documentation.py`)
Comprehensive documentation for:
- **Sentinel Tools**: SAR and optical imaging
- **Raster Tools**: Filtering, thresholding, analysis
- **Vector Tools**: OSM, geometric operations
- **WhiteboxTools**: Slope, flow direction, etc.
- **Workflow Templates**: Common patterns (flood detection, suitability, change detection)

### 3. **WorkflowIndexer** (`rag/workflow_indexer.py`)
- Automatically indexes executed workflows to knowledge base
- Extracts metadata (success rate, runtime, artifacts)
- Updates RAG index for future retrievals
- Generates workflow summaries

**Key Methods:**
- `index_workflow()`: Save and index new workflow
- `export_workflow_summary()`: Generate knowledge base overview

### 4. **Integration Points**

#### Planner (`planner/geospatial_planner.py`)
- Automatically initializes RAG retriever if available
- Retrieves relevant examples before planning
- Injects retrieved context into LLM prompts
- Improves workflow quality with learned patterns

#### Streamlit UI (`ui/app.py`)
- Execute tab automatically indexes successful workflows
- Learn from user workflows over time
- Results improve as more workflows are indexed

## Usage

### Basic Retrieval
```python
from rag.rag_retriever import GeoRAGRetriever

retriever = GeoRAGRetriever()

# Semantic search
results = retriever.retrieve("Detect floods in mountainous terrain", top_k=3)
for doc in results:
    print(f"{doc['title']} (score: {doc['similarity_score']})")

# Get formatted context for prompts
context = retriever.get_context_for_planning("Detect flood risk")
print(context)
```

### Indexing Workflows
```python
from rag.workflow_indexer import WorkflowIndexer

indexer = WorkflowIndexer(rag_retriever=retriever)

# After workflow execution
indexer.index_workflow(
    workflow=workflow_json,
    execution_result=execution_result,
    query="Detect floods in Mandi",
    reasoning=cot_steps
)
```

## Test Results

✅ **12 documents indexed:**
- 6 tool operations
- 3 workflow templates  
- 3 example workflows

✅ **Query Performance:**
| Query | Top Result | Score |
|-------|-----------|-------|
| "Detect flood risk using SAR" | Flood Detection Template | 0.669 |
| "Find suitable sites for solar" | Solar Suitability Workflow | 0.672 |
| "Calculate slope from DEM" | Slope Tool | 0.553 |

✅ **Workflow Indexing:**
- New workflows immediately searchable
- Context generation for prompts works
- Tag-based retrieval effective

## Architecture

```
User Query
    ↓
[RAG Retriever] ← Semantic Search
    ↓
Retrieved Context (similar workflows, tools)
    ↓
[Planner LLM] + Retrieved Context
    ↓
Better Workflow Generation
    ↓
[Executor]
    ↓
[WorkflowIndexer] ← Add to knowledge base
    ↑
Next Query (improved by past workflows)
```

## Knowledge Base Structure

### Documents Indexed
1. **Tool Operations**: 6 tools with parameter guidance
2. **Workflow Templates**: General patterns for common tasks
3. **Historical Workflows**: Executed workflows with metrics
4. **Tags**: Categorical organization (flood, suitability, sar, etc.)

### Metadata Tracked
- Workflow ID and name
- Category (hazard, planning, etc.)
- Tags for filtering
- Steps count and execution summary
- Original query and reasoning

## Performance

- **Embedding Model**: `all-MiniLM-L6-v2` (384-dim, ~33MB)
- **Index Type**: FAISS (Flat L2 metric)
- **Retrieval Time**: < 100ms per query
- **Memory Footprint**: ~5MB for 12 documents

## Future Enhancements

1. **Dynamic Knowledge Growth**: Automatically index all executed workflows
2. **Workflow Suggestions**: Recommend templates based on queries
3. **Learning Analytics**: Track which workflows are most successful
4. **Multi-language Support**: Extend to regional languages
5. **Hybrid Retrieval**: Combine semantic + metadata search
6. **Workflow Ranking**: Score workflows by success metrics

## Integration with Planner

The RAG pipeline is **automatically initialized** when the planner starts:

```python
planner = GeospatialPlanner(llm_client=llm_client)
# RAG retriever is auto-initialized if dependencies available
```

Retrieved context flows into LLM prompts:
```
System: You are a geospatial workflow planner...
Query: "Detect flood risk in Mandi"
Retrieved Examples: [similar workflows, tool docs]
→ LLM generates better workflow
```

## Enabling in Production

RAG is enabled by default. To disable:
```python
planner = GeospatialPlanner(llm_client=llm_client, rag_retriever=None)
```

To use custom RAG setup:
```python
custom_retriever = GeoRAGRetriever(model_name="your-model")
planner = GeospatialPlanner(llm_client=llm_client, rag_retriever=custom_retriever)
```
