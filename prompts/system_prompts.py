"""System prompts and Chain-of-Thought templates for the LLM planner."""

SYSTEM_PROMPT = """You are a reasoning-enabled LLM specialized in geospatial analysis and workflows.

Your role:
1. Understand the user's natural language query about spatial analysis.
2. Use Chain-of-Thought (CoT) reasoning to break down the problem into steps.
3. Plan a structured workflow using geospatial tools and datasets.
4. Output BOTH your reasoning (CoT) and a structured workflow JSON.

When reasoning:
- Explicitly list assumptions and constraints.
- Reference available tools and data sources (from retrieved documents).
- Provide confidence scores for your plan.
- Suggest alternative approaches if uncertain.

Output format:
- **Reasoning**: numbered steps of your thought process
- **Workflow JSON**: a valid workflow conforming to schemas/workflow_schema.json
- **Confidence**: a score 0-1 indicating plan robustness
- **Caveats**: any limitations or data gaps
"""

COT_FLOOD_TEMPLATE = """
Task: Flood Risk Mapping from SAR imagery

Reasoning steps:
1. Understand input: user provides AOI (polygon) and date range.
2. Data selection: Sentinel-1 VV polarization is appropriate for flood detection (good for open water).
3. Preprocessing: SAR imagery requires speckle filtering and dB conversion.
4. Analysis: Threshold low backscatter (<-17 dB for VV) to identify water surfaces.
5. Refinement: Use DEM to mask out areas unlikely to hold water (high elevation, steep slope).
6. Validation: Compare result extent with optical imagery if available.

Key parameters:
- SAR polarization: VV
- dB threshold: -17 (can vary by sensor angle)
- Slope threshold: ~2 degrees (exclude steep terrain)

Confidence: HIGH (established method)
Caveats: Requires cloud-free optical data for validation; sensitive to threshold choice.
"""

COT_SUITABILITY_TEMPLATE = """
Task: Site Suitability Analysis

Reasoning steps:
1. Define criteria: list constraints (wetlands, slope, distance-to-roads, etc.).
2. Data gathering: collect landcover, DEM, road network for AOI.
3. Masking: apply constraints sequentially to eliminate unsuitable zones.
4. Ranking: for remaining cells, assign suitability score based on accessibility, climate, etc.
5. Clustering: identify contiguous suitable regions as candidate sites.
6. Output: deliver suitability map, candidate locations, summary statistics.

Key parameters:
- Slope limit: >5 degrees (exclude)
- Landcover: exclude forest, water, urban
- Distance buffer: 5 km from roads (or user-specified)

Confidence: MEDIUM-HIGH (depends on data quality)
Caveats: Results sensitive to criteria thresholds; local knowledge of ground conditions important.
"""

WORKFLOW_GENERATION_PROMPT = """
Based on the above reasoning and user request, generate a structured GIS workflow.

The workflow must:
1. Include all necessary steps to solve the problem.
2. Reference only available tools (sentinel, vector, raster, whitebox, etc.).
3. Include realistic parameters for each operation.
4. Have a clear input/output specification.
5. Include a CoT reasoning log as a list of short strings.

Example workflow structure (JSON):
{{
  "id": "unique_id",
  "description": "brief description",
  "inputs": {{"aoi": "polygon", "date": "date range"}},
  "steps": [
    {{"id": "step1", "tool": "...", "op": "...", "params": {{}}}},
    ...
  ],
  "outputs": ["file1", "file2"],
  "cot": ["step 1 reasoning", "step 2 reasoning", ...]
}}

Now, generate the workflow:
"""

ITERATIVE_REFINEMENT_PROMPT = """
The workflow execution encountered an error or the results need refinement.

Error / Issue:
{error_message}

Current workflow:
{current_workflow_json}

Please:
1. Analyze what went wrong.
2. Suggest specific parameter adjustments or additional preprocessing steps.
3. Provide a revised workflow JSON (or just the modified steps).
4. Explain your changes in CoT reasoning.

Confidence in fix: [HIGH/MEDIUM/LOW]
Fallback suggestions: [alternative approaches if this fix fails]
"""

PROMPT_TEMPLATES = {
    "system": SYSTEM_PROMPT,
    "flood_cot": COT_FLOOD_TEMPLATE,
    "suitability_cot": COT_SUITABILITY_TEMPLATE,
    "workflow_gen": WORKFLOW_GENERATION_PROMPT,
    "refinement": ITERATIVE_REFINEMENT_PROMPT,
}
