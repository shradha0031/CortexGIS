"""Complete RAG retriever for CortexGIS workflows and tools."""
import json
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    faiss = None
    SentenceTransformer = None
    np = None


class GeoRAGRetriever:
    """
    Retrieves relevant workflows, tool documentation, and examples.
    Combines semantic search with metadata filtering.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize retriever with sentence transformer."""
        self.model_name = model_name
        self.encoder = None
        self.index = None
        self.documents = []
        self.embeddings = None
        
        if SentenceTransformer is not None:
            self.encoder = SentenceTransformer(model_name)
        
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load all available workflows and tool documentation."""
        docs_to_index = []
        
        # Load tool documentation
        try:
            from rag.tool_documentation import TOOL_DOCS, WORKFLOW_TEMPLATES
            
            for tool_doc in TOOL_DOCS:
                doc_id = tool_doc.get("id", "")
                title = tool_doc.get("title", "")
                content = tool_doc.get("content", "")
                tags = tool_doc.get("tags", [])
                
                docs_to_index.append({
                    "id": doc_id,
                    "type": "tool",
                    "title": title,
                    "content": content,
                    "tags": tags,
                    "tool_name": tool_doc.get("tool_name", ""),
                    "operation": tool_doc.get("operation", ""),
                    "relevance_keywords": " ".join(tags),
                })
            
            for template in WORKFLOW_TEMPLATES:
                docs_to_index.append({
                    "id": template.get("id", ""),
                    "type": "template",
                    "title": template.get("name", ""),
                    "content": template.get("description", ""),
                    "tags": template.get("tags", []),
                    "steps": template.get("steps", []),
                    "relevance_keywords": " ".join(template.get("tags", [])),
                })
        except ImportError:
            pass
        
        # Load existing workflows from workflow directory
        workflow_dir = Path(__file__).parent.parent / "workflows"
        if workflow_dir.exists():
            for workflow_file in workflow_dir.glob("*.json"):
                try:
                    with open(workflow_file, "r") as f:
                        workflow = json.load(f)
                        
                    docs_to_index.append({
                        "id": workflow.get("id", workflow_file.stem),
                        "type": "workflow",
                        "title": workflow.get("name", ""),
                        "content": workflow.get("description", ""),
                        "tags": workflow.get("tags", []),
                        "category": workflow.get("category", ""),
                        "steps_count": len(workflow.get("steps", [])),
                        "workflow_data": workflow,
                        "relevance_keywords": " ".join(workflow.get("tags", [])),
                    })
                except Exception as e:
                    print(f"Warning: Could not load workflow {workflow_file}: {e}")
        
        # Index all documents
        if docs_to_index:
            self._index_documents(docs_to_index)
    
    def _index_documents(self, docs: List[Dict]):
        """Build FAISS index from documents."""
        if self.encoder is None:
            self.documents = docs
            return
        
        self.documents = docs
        
        # Create searchable text for each document
        texts = []
        for doc in docs:
            title = doc.get("title", "")
            content = doc.get("content", "")
            tags = " ".join(doc.get("tags", []))
            keywords = doc.get("relevance_keywords", "")
            
            # Combine all text with weights
            searchable_text = f"{title} {content} {tags} {keywords}"
            texts.append(searchable_text)
        
        # Encode all documents
        if faiss is not None and SentenceTransformer is not None:
            embeddings = self.encoder.encode(texts, convert_to_numpy=True)
            self.embeddings = embeddings
            
            # Build FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype(np.float32))
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = 3,
        doc_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents by semantic similarity.
        
        Args:
            query: User query or workflow description
            top_k: Number of results to return
            doc_types: Filter by document type (tool, workflow, template)
        
        Returns:
            List of dicts with document info and relevance score
        """
        if self.encoder is None or self.index is None:
            return self._fallback_retrieve(query, top_k, doc_types)
        
        # Encode query
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)
        
        # Search index
        distances, indices = self.index.search(
            query_embedding.astype(np.float32), 
            min(top_k * 2, len(self.documents))  # Get extra to filter
        )
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= len(self.documents):
                continue
            
            doc = self.documents[idx]
            
            # Filter by type if specified
            if doc_types and doc.get("type") not in doc_types:
                continue
            
            # Convert distance to similarity score
            similarity = 1.0 / (1.0 + float(distance))
            
            result = {
                "id": doc.get("id"),
                "type": doc.get("type"),
                "title": doc.get("title"),
                "content": doc.get("content", ""),
                "tags": doc.get("tags", []),
                "similarity_score": round(similarity, 3),
            }
            
            # Include type-specific data
            if doc.get("type") == "workflow":
                result["workflow_id"] = doc.get("id")
                result["category"] = doc.get("category")
                result["steps_count"] = doc.get("steps_count")
            elif doc.get("type") == "template":
                result["steps"] = doc.get("steps", [])
            elif doc.get("type") == "tool":
                result["tool_name"] = doc.get("tool_name")
                result["operation"] = doc.get("operation")
            
            results.append(result)
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _fallback_retrieve(
        self,
        query: str,
        top_k: int,
        doc_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """Fallback keyword-based retrieval when embeddings unavailable."""
        query_lower = query.lower()
        query_tokens = set(query_lower.split())
        
        scored_docs = []
        for doc in self.documents:
            if doc_types and doc.get("type") not in doc_types:
                continue
            
            # Score based on keyword overlap
            doc_text = (
                doc.get("title", "") + " " +
                doc.get("content", "") + " " +
                " ".join(doc.get("tags", []))
            ).lower()
            
            doc_tokens = set(doc_text.split())
            overlap = len(query_tokens & doc_tokens)
            
            if overlap > 0:
                score = overlap / len(query_tokens)
                scored_docs.append((score, doc))
        
        # Sort by score and return top-k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scored_docs[:top_k]:
            result = {
                "id": doc.get("id"),
                "type": doc.get("type"),
                "title": doc.get("title"),
                "content": doc.get("content", ""),
                "tags": doc.get("tags", []),
                "similarity_score": round(score, 3),
            }
            results.append(result)
        
        return results
    
    def retrieve_by_tags(
        self,
        tags: List[str],
        top_k: int = 3,
    ) -> List[Dict]:
        """
        Retrieve documents matching specific tags.
        Useful for finding all flood-related or solar workflows.
        """
        tag_lower = [t.lower() for t in tags]
        results = []
        
        for doc in self.documents:
            doc_tags = [t.lower() for t in doc.get("tags", [])]
            match_count = sum(1 for tag in tag_lower if tag in doc_tags)
            
            if match_count > 0:
                results.append({
                    "id": doc.get("id"),
                    "type": doc.get("type"),
                    "title": doc.get("title"),
                    "tags": doc.get("tags", []),
                    "matched_tags": match_count,
                })
        
        # Sort by match count
        results.sort(key=lambda x: x["matched_tags"], reverse=True)
        return results[:top_k]
    
    def get_context_for_planning(self, query: str) -> str:
        """
        Build a context string for the planner from retrieved documents.
        Useful for prompt engineering.
        """
        results = self.retrieve(query, top_k=3)
        
        context_parts = []
        
        for result in results:
            doc_type = result.get("type", "")
            title = result.get("title", "")
            
            if doc_type == "workflow":
                context_parts.append(f"Similar workflow: {title}")
                context_parts.append(f"  Category: {result.get('category')}")
                context_parts.append(f"  Steps: {result.get('steps_count')}")
            elif doc_type == "tool":
                context_parts.append(f"Relevant tool operation: {result.get('tool_name')}.{result.get('operation')}")
                context_parts.append(f"  Description: {result.get('content', '')[:200]}...")
            elif doc_type == "template":
                context_parts.append(f"Workflow template: {title}")
                steps = result.get("steps", [])
                for i, step in enumerate(steps[:3], 1):
                    context_parts.append(f"  {i}. {step}")
        
        return "\n".join(context_parts) if context_parts else ""
