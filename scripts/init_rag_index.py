"""Initialize and test the RAG index with sample documents."""
import os
import sys

# Add rag module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.rag_index import SimpleRAGIndex
from rag.sample_docs import SAMPLE_DOCS


def main():
    print("Initializing RAG index...")
    
    # Check dependencies
    try:
        import faiss
        print("✓ FAISS available")
    except ImportError:
        print("⚠ FAISS not installed. Install with: pip install faiss-cpu")
        print("  Continuing without vector search...")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers available")
    except ImportError:
        print("⚠ sentence-transformers not installed. Install with: pip install sentence-transformers")
        print("  Continuing with placeholder...")
    
    # Create and ingest index
    rag = SimpleRAGIndex(model_name="all-MiniLM-L6-v2")
    print(f"\nIngesting {len(SAMPLE_DOCS)} sample documents...")
    rag.ingest_documents(SAMPLE_DOCS)
    print("✓ Documents ingested")
    
    # Demo retrieval
    test_queries = [
        "How do I detect floods using SAR imagery?",
        "What are the steps for site suitability analysis?",
        "How do I process DEM data?",
    ]
    
    print("\n--- Retrieval Demo ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = rag.retrieve(query, top_k=2)
        if results:
            for i, (content, score) in enumerate(results, 1):
                title = content.split("\n")[0]
                print(f"  {i}. {title} (score: {score:.3f})")
        else:
            print("  (No results - dependencies may not be installed)")
    
    # Save index
    index_path = os.path.join(os.path.dirname(__file__), "..", "rag", "index_data")
    print(f"\nSaving index to {index_path}...")
    rag.save(index_path)
    print("✓ Index saved")


if __name__ == "__main__":
    main()
