"""Indexing pipeline for new workflows after execution."""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class WorkflowIndexer:
    """
    Indexes executed workflows to the RAG knowledge base.
    Extracts metadata and makes workflows searchable for future planning.
    """
    
    def __init__(self, workflow_dir: Path = None, rag_retriever=None):
        """
        Args:
            workflow_dir: Directory where workflows are stored (default: ./workflows)
            rag_retriever: RAG retriever to update with new workflows
        """
        self.workflow_dir = workflow_dir or Path(__file__).parent.parent / "workflows"
        self.rag_retriever = rag_retriever
        self.workflow_dir.mkdir(exist_ok=True)
    
    def index_workflow(
        self,
        workflow: Dict[str, Any],
        execution_result: Dict[str, Any],
        query: str = "",
        reasoning: List[str] = None,
    ) -> str:
        """
        Save workflow and execution metadata for future retrieval.
        
        Args:
            workflow: The generated workflow JSON
            execution_result: Execution results from executor
            query: Original user query
            reasoning: CoT reasoning steps
        
        Returns:
            Workflow file path
        """
        workflow_id = workflow.get("id", f"workflow_{datetime.now().isoformat()}")
        workflow_file = self.workflow_dir / f"{workflow_id}.json"
        
        # Enhance workflow with execution metadata
        enriched_workflow = workflow.copy()
        enriched_workflow["indexed_at"] = datetime.now().isoformat()
        enriched_workflow["original_query"] = query
        enriched_workflow["reasoning"] = reasoning or []
        
        # Add execution summary
        if execution_result:
            enriched_workflow["execution_summary"] = {
                "success_rate": execution_result.get("successful_steps", 0) / max(1, execution_result.get("total_steps", 1)),
                "total_steps": execution_result.get("total_steps", 0),
                "successful_steps": execution_result.get("successful_steps", 0),
                "failed_steps": execution_result.get("failed_steps", 0),
                "runtime_seconds": execution_result.get("runtime_seconds", 0),
                "artifacts_generated": len(execution_result.get("generated_output_files", [])),
            }
        
        # Save workflow
        with open(workflow_file, "w") as f:
            json.dump(enriched_workflow, f, indent=2)
        
        # Update RAG index if available
        if self.rag_retriever:
            try:
                self._update_rag_index(enriched_workflow)
            except Exception as e:
                print(f"Warning: Could not update RAG index: {e}")
        
        return str(workflow_file)
    
    def _update_rag_index(self, workflow: Dict[str, Any]):
        """Add workflow to RAG index for semantic search."""
        if not self.rag_retriever or not hasattr(self.rag_retriever, 'documents'):
            return
        
        doc = {
            "id": workflow.get("id", "unknown"),
            "type": "workflow",
            "title": workflow.get("name", "Untitled Workflow"),
            "content": workflow.get("description", ""),
            "tags": workflow.get("tags", []),
            "category": workflow.get("category", ""),
            "steps_count": len(workflow.get("steps", [])),
            "workflow_data": workflow,
            "relevance_keywords": " ".join(workflow.get("tags", [])),
        }
        
        # Add to documents list
        self.rag_retriever.documents.append(doc)
        
        # Rebuild index
        if self.rag_retriever.encoder is None:
            return
        
        # Re-index all documents
        texts = []
        for d in self.rag_retriever.documents:
            title = d.get("title", "")
            content = d.get("content", "")
            tags = " ".join(d.get("tags", []))
            keywords = d.get("relevance_keywords", "")
            searchable_text = f"{title} {content} {tags} {keywords}"
            texts.append(searchable_text)
        
        # Re-encode and re-index
        embeddings = self.rag_retriever.encoder.encode(texts, convert_to_numpy=True)
        self.rag_retriever.embeddings = embeddings
        
        if self.rag_retriever.index is not None:
            # FAISS index rebuild
            import numpy as np
            try:
                import faiss
                dimension = embeddings.shape[1]
                self.rag_retriever.index = faiss.IndexFlatL2(dimension)
                self.rag_retriever.index.add(embeddings.astype(np.float32))
            except ImportError:
                pass
    
    def export_workflow_summary(self, output_file: Path = None) -> str:
        """
        Generate a summary of all indexed workflows.
        Useful for understanding the knowledge base.
        """
        output_file = output_file or self.workflow_dir.parent / "workflow_summary.json"
        
        workflows = []
        for wf_file in self.workflow_dir.glob("*.json"):
            try:
                with open(wf_file) as f:
                    wf = json.load(f)
                
                workflows.append({
                    "id": wf.get("id"),
                    "name": wf.get("name"),
                    "category": wf.get("category"),
                    "tags": wf.get("tags", []),
                    "steps_count": len(wf.get("steps", [])),
                    "description": wf.get("description", "")[:200] + "...",
                    "created": wf.get("created"),
                    "indexed_at": wf.get("indexed_at"),
                })
            except Exception as e:
                print(f"Warning: Could not read workflow {wf_file}: {e}")
        
        summary = {
            "total_workflows": len(workflows),
            "categories": {},
            "workflows": workflows,
        }
        
        # Aggregate by category
        for wf in workflows:
            cat = wf.get("category", "other")
            summary["categories"].setdefault(cat, 0)
            summary["categories"][cat] += 1
        
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)
        
        return str(output_file)


def setup_indexing_in_executor(executor, rag_retriever=None):
    """
    Attach workflow indexing to the executor.
    Automatically indexes workflows after successful execution.
    """
    indexer = WorkflowIndexer(rag_retriever=rag_retriever)
    return indexer
