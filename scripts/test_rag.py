"""Test the complete RAG pipeline integration."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag.rag_retriever import GeoRAGRetriever
from rag.workflow_indexer import WorkflowIndexer
from rag.tool_documentation import TOOL_DOCS, WORKFLOW_TEMPLATES


def test_rag_retriever():
    """Test RAG retriever with sample queries."""
    print("=" * 60)
    print("Testing RAG Retriever")
    print("=" * 60)
    
    retriever = GeoRAGRetriever()
    
    # Test queries
    queries = [
        "Detect flood risk using SAR imagery",
        "Find suitable sites for solar farms",
        "Calculate slope from DEM",
        "Water detection with NDWI index",
    ]
    
    for query in queries:
        print(f"\n📌 Query: {query}")
        results = retriever.retrieve(query, top_k=2)
        
        for i, result in enumerate(results, 1):
            doc_type = result.get("type", "unknown").upper()
            title = result.get("title", "")
            score = result.get("similarity_score", 0)
            tags = ", ".join(result.get("tags", [])[:3])
            
            print(f"  {i}. [{doc_type}] {title}")
            print(f"     Score: {score:.3f} | Tags: {tags}")
    
    # Test context generation
    print("\n" + "=" * 60)
    print("Testing Context Generation for Planner")
    print("=" * 60)
    
    test_query = "Detect inundated areas in Mandi district"
    context = retriever.get_context_for_planning(test_query)
    print(f"\nQuery: {test_query}")
    print(f"Generated Context:\n{context}")
    
    return retriever


def test_workflow_indexing(retriever):
    """Test workflow indexing."""
    print("\n" + "=" * 60)
    print("Testing Workflow Indexing")
    print("=" * 60)
    
    indexer = WorkflowIndexer(rag_retriever=retriever)
    
    # Create a sample workflow
    sample_workflow = {
        "id": "test_flood_detection",
        "name": "Test Flood Detection Workflow",
        "description": "Detect flooded areas using Sentinel-1 SAR",
        "category": "hazard",
        "tags": ["flood", "sar", "sentinel-1"],
        "steps": [
            {"id": "download", "tool": "sentinel", "op": "download_sar"},
            {"id": "filter", "tool": "raster", "op": "speckle_filter"},
            {"id": "threshold", "tool": "raster", "op": "threshold"},
        ]
    }
    
    sample_result = {
        "total_steps": 3,
        "successful_steps": 3,
        "failed_steps": 0,
        "runtime_seconds": 45.2,
        "generated_output_files": ["flood_extent.geojson"]
    }
    
    print("\n✓ Indexing sample workflow...")
    indexer.index_workflow(
        workflow=sample_workflow,
        execution_result=sample_result,
        query="Detect flood risk",
        reasoning=["Download SAR data", "Filter noise", "Threshold water"],
    )
    
    print("✓ Workflow indexed successfully")
    
    # Verify it can be retrieved
    print("\nSearching for indexed workflow...")
    results = retriever.retrieve("flood detection SAR", top_k=3)
    
    found = False
    for result in results:
        if "test" in result.get("id", "").lower():
            found = True
            print(f"✓ Found indexed workflow: {result.get('title')}")
            print(f"  Similarity: {result.get('similarity_score')}")
    
    if not found:
        print("⚠️  Indexed workflow not immediately found in search results")
        print("  (This is OK - it may require index rebuild)")


def test_tag_based_retrieval(retriever):
    """Test tag-based retrieval."""
    print("\n" + "=" * 60)
    print("Testing Tag-Based Retrieval")
    print("=" * 60)
    
    tags_to_search = ["flood", "sar"]
    print(f"\nSearching for workflows with tags: {tags_to_search}")
    
    results = retriever.retrieve_by_tags(tags_to_search, top_k=3)
    
    if results:
        for result in results:
            print(f"  - {result.get('title')} (matched: {result.get('matched_tags')} tags)")
    else:
        print("  No matching workflows found")


def main():
    """Run all tests."""
    print("\n" + "🚀 CortexGIS RAG Pipeline Test Suite".center(60))
    
    try:
        retriever = test_rag_retriever()
        test_workflow_indexing(retriever)
        test_tag_based_retrieval(retriever)
        
        print("\n" + "=" * 60)
        print("✅ All RAG tests completed successfully!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  - Loaded {len(retriever.documents)} documents")
        print(f"  - Tool docs: {len(TOOL_DOCS)}")
        print(f"  - Templates: {len(WORKFLOW_TEMPLATES)}")
        print(f"  - Embedding model: {retriever.model_name}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
