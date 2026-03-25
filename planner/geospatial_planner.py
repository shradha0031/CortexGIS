"""LLM-based planner that generates workflows from natural language queries."""
import json
import re
import hashlib
from typing import Dict, List, Optional, Tuple


class GeospatialPlanner:
    """
    Orchestrates reasoning and workflow generation.
    Uses an LLM (to be provided externally) to drive the planning loop.
    """

    def __init__(self, llm_client=None, rag_retriever=None):
        """
        Args:
            llm_client: An LLM client (e.g., OpenAI, local, etc.) with a generate() method.
            rag_retriever: A RAG retriever for context (optional).
        """
        self.llm_client = llm_client
        self.rag_retriever = rag_retriever
        self.reasoning_history: List[Dict] = []

    def plan_workflow(self, query: str, context: Optional[str] = None) -> Tuple[List[str], Dict]:
        """
        Generate a workflow plan from a natural language query.
        
        Args:
            query: Natural language description of the task.
            context: Optional additional context (e.g., AOI description).
        
        Returns:
            (cot_reasoning, workflow_json)
        """
        # Step 1: Retrieve relevant docs if RAG is available
        retrieved_docs = []
        if self.rag_retriever:
            retrieved_docs = self.rag_retriever.retrieve(query, top_k=3)
        
        # Step 2: Formulate the reasoning prompt
        from prompts.system_prompts import SYSTEM_PROMPT, WORKFLOW_GENERATION_PROMPT
        
        reasoning_prompt = f"""
{SYSTEM_PROMPT}

User Query: {query}

{'Context: ' + context if context else ''}

{'Retrieved Background:' + ''.join([doc[0][:500] for _, doc in enumerate(retrieved_docs)]) if retrieved_docs else ''}

Now, reason through this problem step-by-step:
"""
        
        # Step 3: Call LLM for reasoning (stubbed for now)
        if self.llm_client is None:
            cot_reasoning = self._stub_reasoning(query)
        else:
            # In production, call: cot_reasoning = self.llm_client.generate(reasoning_prompt)
            cot_reasoning = self._stub_reasoning(query)
        
        # Step 4: Generate workflow JSON
        workflow_gen_prompt = f"{reasoning_prompt}\n\n{WORKFLOW_GENERATION_PROMPT}"
        
        if self.llm_client is None:
            workflow_json = self._stub_workflow(query)
        else:
            # In production: raw_response = self.llm_client.generate(workflow_gen_prompt)
            # Extract JSON from response; for now use stub
            workflow_json = self._stub_workflow(query)
        
        # Step 5: Log this planning step
        self.reasoning_history.append({
            "query": query,
            "reasoning": cot_reasoning,
            "workflow": workflow_json,
        })
        
        return cot_reasoning, workflow_json

    def _stub_reasoning(self, query: str) -> List[str]:
        """Placeholder CoT reasoning for demonstration."""
        if "flood" in query.lower():
            return [
                "1. The user wants to detect flooded areas.",
                "2. Sentinel-1 SAR is ideal because it works through clouds.",
                "3. I should fetch VV polarization data for the AOI.",
                "4. Apply speckle filter then threshold for water detection.",
                "5. Use DEM to refine the result."
            ]
        elif "suitability" in query.lower() or "site" in query.lower():
            return [
                "1. The user is looking for suitable locations.",
                "2. I need to identify and apply spatial constraints.",
                "3. Load landcover to exclude unsuitable zones.",
                "4. Apply slope, distance, and other criteria.",
                "5. Rank remaining areas and identify clusters."
            ]
        else:
            return [
                "1. General geospatial analysis requested.",
                "2. Assessing available data and tools.",
                "3. Planning multi-step workflow."
            ]

    def _stub_workflow(self, query: str) -> Dict:
        """Placeholder workflow generation for demonstration."""
        center_lat, center_lon = self._infer_query_center(query)

        if "flood" in query.lower():
            return {
                "id": "flood_plan_001",
                "description": "Flood detection from Sentinel-1 SAR",
                "inputs": {"aoi": "polygon", "date_range": ["2024-01-01", "2024-12-31"]},
                "steps": [
                    {
                        "id": "fetch_s1",
                        "tool": "sentinel",
                        "op": "download_vv",
                        "params": {
                            "polarization": "VV",
                            "months": [8, 9],
                            "center_lat": center_lat,
                            "center_lon": center_lon,
                        }
                    },
                    {
                        "id": "speckle_filter",
                        "tool": "raster",
                        "op": "despeckle",
                        "params": {"kernel_size": 5}
                    },
                    {
                        "id": "threshold",
                        "tool": "raster",
                        "op": "threshold",
                        "params": {"value": -17}
                    },
                    {
                        "id": "vectorize",
                        "tool": "vector",
                        "op": "raster_to_poly",
                        "params": {
                            "center_lat": center_lat,
                            "center_lon": center_lon,
                            "size_deg": 0.03,
                        }
                    }
                ],
                "outputs": ["flood_mask.tif", "flood_boundary.geojson"],
                "cot": ["Fetch Sentinel-1", "Denoise", "Threshold", "Vectorize"]
            }
        else:
            return {
                "id": "generic_plan_001",
                "description": "Generic geospatial analysis",
                "inputs": {"aoi": "polygon"},
                "steps": [
                    {
                        "id": "step1",
                        "tool": "vector",
                        "op": "buffer",
                        "params": {
                            "input": "aoi.geojson",
                            "distance_m": 250,
                            "center_lat": center_lat,
                            "center_lon": center_lon,
                            "size_deg": 0.02,
                        }
                    }
                ],
                "outputs": ["buffered_250m.geojson"],
                "cot": ["Interpret query intent", "Create a map-ready vector result"]
            }

    def _infer_query_center(self, query: str) -> Tuple[float, float]:
        """Infer map center from known city mentions, else derive deterministic offset from query."""
        q = query.lower()
        known_centers = {
            "pune": (18.5204, 73.8567),
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.6139, 77.2090),
            "bangalore": (12.9716, 77.5946),
            "bengaluru": (12.9716, 77.5946),
            "hyderabad": (17.3850, 78.4867),
            "chennai": (13.0827, 80.2707),
            "kolkata": (22.5726, 88.3639),
            "india": (22.9734, 78.6569),
        }
        for place, coords in known_centers.items():
            if place in q:
                return coords

        # Deterministic offset so different queries render different map outputs.
        digest = hashlib.md5(query.encode("utf-8")).hexdigest()
        lat_n = int(digest[:8], 16) / 0xFFFFFFFF
        lon_n = int(digest[8:16], 16) / 0xFFFFFFFF
        base_lat, base_lon = 18.5204, 73.8567
        lat_offset = (lat_n - 0.5) * 0.8
        lon_offset = (lon_n - 0.5) * 0.8
        return base_lat + lat_offset, base_lon + lon_offset

    def validate_workflow(self, workflow: Dict) -> Tuple[bool, List[str]]:
        """Validate workflow against schema and tool registry."""
        errors = []
        
        # Check required fields
        if "id" not in workflow:
            errors.append("Missing 'id' field")
        if "steps" not in workflow or not isinstance(workflow["steps"], list):
            errors.append("Missing or invalid 'steps' field")
        
        # Check steps
        for step in workflow.get("steps", []):
            if "tool" not in step:
                errors.append(f"Step {step.get('id')} missing 'tool'")
        
        return len(errors) == 0, errors
