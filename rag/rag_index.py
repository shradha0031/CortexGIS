"""RAG index builder and retriever using FAISS and sentence-transformers."""
import json
import pickle
import os
from typing import List, Dict, Tuple
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class SimpleRAGIndex:
    """
    A minimal RAG system using FAISS for vector indexing.
    Encodes document chunks and enables similarity search.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Args:
            model_name: HuggingFace sentence transformer model.
        """
        self.model_name = model_name
        self.encoder = None
        self.index = None
        self.documents = []
        self.embeddings = None

        if SentenceTransformer is None:
            print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")
        else:
            self.encoder = SentenceTransformer(model_name)

        if faiss is None:
            print("Warning: faiss not installed. Install with: pip install faiss-cpu")

    def ingest_documents(self, docs: List[Dict[str, str]]):
        """
        Ingest documents into the index.
        Each doc should have 'id', 'title', 'content', 'tags' keys.
        """
        if self.encoder is None:
            print("Encoder not available; skipping ingestion.")
            return

        self.documents = docs
        texts = [f"{doc.get('title', '')} {doc.get('content', '')}" for doc in docs]

        # Encode all documents
        embeddings = self.encoder.encode(texts, convert_to_numpy=True)
        self.embeddings = embeddings

        # Build FAISS index
        if faiss is not None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype(np.float32))

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Retrieve top-k documents similar to the query.
        Returns list of (document_content, similarity_score) tuples.
        """
        if self.encoder is None or self.index is None:
            print("Index not initialized.")
            return []

        query_embedding = self.encoder.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding.astype(np.float32), top_k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            doc = self.documents[idx]
            score = 1.0 / (1.0 + distance)  # Convert L2 distance to similarity score
            content = f"{doc['title']}\n{doc['content']}"
            results.append((content, score))

        return results

    def save(self, path: str):
        """Save index to disk."""
        if self.index is None:
            print("No index to save.")
            return

        os.makedirs(os.path.dirname(path), exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))

        metadata = {
            "model_name": self.model_name,
            "documents": self.documents,
        }
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

    def load(self, path: str):
        """Load index from disk."""
        if faiss is None:
            print("FAISS not available.")
            return

        self.index = faiss.read_index(os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "metadata.json"), "r") as f:
            metadata = json.load(f)
            self.documents = metadata["documents"]
            self.model_name = metadata["model_name"]
