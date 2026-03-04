# Example Workflows

This directory contains pre-defined, validated geospatial workflows that serve as templates for common spatial analysis tasks.

## Available Workflows

### 1. Flood Mapping (`flood_mapping.json`)

**Objective**: Detect inundated areas using Sentinel-1 SAR imagery and Digital Elevation Model.

**Input**:
- AOI polygon (GeoJSON)
- Date range (e.g., August 2024 for monsoon)
- Slope threshold (default: 2°)

**Output**:
- `flood_mask_clean.tif` — Raster binary mask (1 = flooded, 0 = not flooded)
- `flood_extent.geojson` — Vector polygons of flood boundaries
- `flood_stats.json` — Inundated area statistics

**Key Steps**:
1. Fetch Sentinel-1 VV-polarized SAR data
2. Speckle filtering (Lee filter, kernel 5×5)
3. Convert to dB scale
4. Threshold at -17 dB (water detection; low backscatter)
5. Mask out steep terrain (slope >2°)
6. Morphological cleaning (close gaps, remove noise)
7. Vectorize result
8. Compute statistics

**Confidence**: 85% (typical SAR-based flood detection)

**Caveats**:
- Threshold (-17 dB) may vary by incidence angle; requires local calibration
- Needs optical imagery for validation (clouds can be problematic)
- Misclassification risk: calm water bodies, urban areas with low backscatter

**Time**: ~20 minutes execution

**Use Case**: Emergency response, flood risk assessment, climate adaptation planning

---

### 2. Solar Site Suitability (`site_suitability.json`)

**Objective**: Identify optimal locations for utility-scale solar farms by evaluating environmental, accessibility, and resource criteria.

**Input**:
- AOI polygon
- Constraints:
  - Max slope: 5°
  - Min distance to roads: 1 km
  - Max distance to roads: 5 km
  - Exclude land cover: water, forest, urban, wetland

**Output**:
- `suitability_ranked.tif` — Raster map ranked by solar potential
- `site_clusters.tif` — Raster of identified site clusters
- `candidate_sites.geojson` — Vector polygons of candidate sites (>10 ha each)
- `site_summary.csv` — Table with site attributes (area, elevation, solar irradiance, distance-to-roads)

**Key Steps**:
1. Fetch land cover classification (Sentinel-2 LULC)
2. Fetch DEM and compute slope
3. Download road network (OSM)
4. Mask unsuitable land covers
5. Mask steep terrain (>5°)
6. Compute distance-to-roads raster
7. Mask areas outside road distance range
8. Combine all masks (AND operation) → candidate areas
9. Fetch solar irradiance data (MERRA-2)
10. Rank by solar potential
11. Identify clusters (min 10 ha)
12. Vectorize and compute site attributes

**Confidence**: 80% (subject to local constraints and permitting requirements)

**Caveats**:
- Does not account for land ownership, environmental permits, or soil quality
- Solar data is modeled; actual production depends on weather and system design
- Thresholds (1-5 km roads, 5° slope, 10 ha minimum) are configurable
- Further ESIA and feasibility studies required before development

**Time**: ~25 minutes execution

**Use Case**: Renewable energy planning, utility-scale solar development, land-use optimization

---

## Workflow Format

All workflows conform to `../schemas/workflow_schema.json` with additional metadata:

```json
{
  "id": "unique_workflow_id",
  "name": "Human-readable name",
  "description": "Detailed description",
  "category": "category",
  "tags": ["tag1", "tag2"],
  "inputs": {...},
  "steps": [
    {"id": "step1", "tool": "...", "op": "...", "params": {...}}
  ],
  "outputs": {...},
  "cot_reasoning": ["step 1", "step 2", ...],
  "confidence": 0.85,
  "caveats": ["caveat 1", "caveat 2"],
  "references": [...]
}
```

## Load and Execute

### Python

```python
import json
from workflows import load_workflow
from executor.executor import WorkflowExecutor, ToolRegistry

# Load workflow
with open("workflows/flood_mapping.json") as f:
    workflow = json.load(f)

# Execute
executor = WorkflowExecutor(ToolRegistry())
result = executor.execute_workflow(workflow, output_dir="./outputs")

print(f"Execution complete: {result['successful_steps']}/{result['total_steps']} steps")
```

### CLI

```bash
# List available workflows
ls -la workflows/*.json

# Validate workflow
python scripts/validate_workflow.py workflows/flood_mapping.json

# Execute workflow
python scripts/execute_workflow.py workflows/flood_mapping.json --aoi aoi.geojson --output-dir ./results
```

### Web UI (Streamlit)

1. Run: `streamlit run ui/app.py`
2. Upload workflow JSON in "Workflow" tab
3. Click "Execute"

---

## Extending Workflows

### Add New Workflow

1. Create JSON file in `workflows/`
2. Populate fields: `id`, `name`, `description`, `inputs`, `steps`, `outputs`, `cot_reasoning`, `caveats`
3. Validate against schema: `python scripts/validate_workflow.py workflows/my_workflow.json`
4. Update this README with summary

### Modify Existing Workflow

Edit JSON in-place; update version number and "modified" timestamp.

### Test Before Deployment

```python
from planner.geospatial_planner import GeospatialPlanner

planner = GeospatialPlanner()
valid, errors = planner.validate_workflow(workflow_dict)
if not valid:
    print("Validation errors:", errors)
```

---

## Future Workflows

Planned workflows:
- **Land Cover Change Detection**: Multi-temporal classification (2020 vs. 2024)
- **Urban Growth Analysis**: Sprawl detection and rate quantification
- **Water Resource Assessment**: River basin characterization for hydropower planning
- **Agricultural Suitability**: Crop yield prediction based on climate and soil
- **Disaster Risk Mapping**: Multi-hazard (flood, landslide, cyclone)

---

## References

- COPERNICUS Emergency Response (EMS): https://emergency.copernicus.eu/
- IRENA Renewable Energy Resource Mapping
- USGS Water Resources Monitoring
- ESA Sentinel Mission Handbook
