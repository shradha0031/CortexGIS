"""Comprehensive tool documentation for RAG knowledge base."""

TOOL_DOCS = [
    {
        "id": "sentinel_download_sar",
        "title": "Sentinel Tool: Download SAR Imagery",
        "tool_name": "sentinel",
        "operation": "download_sar",
        "content": """
Sentinel-1 provides C-band Synthetic Aperture Radar (SAR) imagery in VV and VH polarizations.

**Use Cases:**
- Flood detection (water appears dark in VV polarization)
- Ship detection and tracking
- Sea ice monitoring
- Soil moisture estimation

**Parameters:**
- polarization: 'VV' or 'VH' (VV most sensitive to water)
- product_type: 'GRD' (Ground Range Detected) or 'SLC'
- months: list of months to search (e.g., [8, 9] for Aug-Sep)
- lookback_days: historical range (default 30 days)

**Output:**
- GeoTIFF raster file with intensity values
- Typical range: 0-65535 (16-bit)

**Best Practices:**
- Use VV for flood/water detection
- Use VH for texture/urban mapping
- Combine with multi-looking for noise reduction
- Convert to dB scale for interpretability
        """,
        "tags": ["sentinel-1", "sar", "water-detection", "flood"],
        "workflow_examples": ["flood_mapping_001"]
    },
    {
        "id": "sentinel_download_optical",
        "title": "Sentinel Tool: Download Optical Imagery",
        "tool_name": "sentinel",
        "operation": "download_optical",
        "content": """
Sentinel-2 provides multispectral optical imagery with 13 bands covering visible to SWIR wavelengths.

**Use Cases:**
- Land cover classification
- Vegetation analysis (NDVI)
- Water detection (NDWI)
- Urban mapping
- Crop monitoring

**Parameters:**
- bands: list of band numbers (e.g., [1,2,3,4,5,6,7,8,8A,11,12])
- cloud_cover_max: maximum cloud percentage (default 20%)
- resolution: output resolution in meters (default 20m)

**Spectral Bands:**
- B2 (Blue): 490nm, 10m resolution
- B3 (Green): 560nm, 10m resolution
- B4 (Red): 665nm, 10m resolution
- B8 (NIR): 842nm, 10m resolution
- B11 (SWIR1): 1610nm, 20m resolution
- B12 (SWIR2): 2190nm, 20m resolution

**Output:**
- Multi-band GeoTIFF
- Values: 0-10000 (reflectance * 10000)

**Common Indices:**
- NDVI = (B8 - B4) / (B8 + B4) for vegetation
- NDWI = (B8 - B11) / (B8 + B11) for water
        """,
        "tags": ["sentinel-2", "optical", "ndvi", "landcover"],
        "workflow_examples": ["site_suitability_solar_001"]
    },
    {
        "id": "raster_speckle_filter",
        "title": "Raster Tool: Speckle Filtering",
        "tool_name": "raster",
        "operation": "speckle_filter",
        "content": """
Reduce speckle noise in SAR imagery while preserving edges and features.

**Use Cases:**
- Pre-processing Sentinel-1 for flood detection
- Improving SAR image interpretability
- Preparing data for thresholding

**Parameters:**
- kernel_size: filter window size (3, 5, 7, etc.)
- filter_type: 'lee' (default), 'frost', 'median'
- iterations: number of passes (1-3)

**Filter Types:**
- Lee: reduces noise while preserving edges
- Frost: exponential filter for edge preservation
- Median: simple non-local filter

**Example Workflow:**
1. Download raw Sentinel-1 imagery
2. Apply speckle filter with kernel_size=5
3. Convert to dB scale
4. Threshold for water detection

**Output:**
- Filtered raster maintaining spatial resolution
        """,
        "tags": ["sar", "preprocessing", "noise-reduction"],
        "workflow_examples": ["flood_mapping_001"]
    },
    {
        "id": "raster_threshold",
        "title": "Raster Tool: Thresholding",
        "tool_name": "raster",
        "operation": "threshold",
        "content": """
Convert continuous raster values to binary classification based on threshold.

**Use Cases:**
- Water detection from SAR (values < -17 dB)
- Land cover masking
- Suitability classification

**Parameters:**
- value: threshold value
- comparison: 'less_than', 'less_than_equal', 'greater_than', 'greater_than_equal'
- output_values: [value_if_false, value_if_true] (default [0, 1])

**Common Thresholds:**
- Flood detection (SAR VV): -17 dB
- Water detection (NDWI): > 0.3
- Vegetation (NDVI): > 0.4
- Urban (NDBI): > 0.1

**Output:**
- Binary raster (0 or 1)
- Easily vectorizable to polygons

**Tips:**
- Multiple consecutive thresholds can create multi-class output
- Combine with morphological operations for cleanup
        """,
        "tags": ["classification", "binarization", "water-detection"],
        "workflow_examples": ["flood_mapping_001", "site_suitability_solar_001"]
    },
    {
        "id": "whitebox_slope",
        "title": "WhiteboxTools: Slope Calculation",
        "tool_name": "whitebox",
        "operation": "slope",
        "content": """
Calculate slope from a Digital Elevation Model (DEM).

**Use Cases:**
- Site suitability analysis (exclude steep terrain)
- Landslide susceptibility mapping
- Drainage pathway identification
- Solar farm site selection

**Parameters:**
- units: 'degrees' (default) or 'radians' or 'percent'
- algorithm: 'horn' (default) or 'simple'

**Output Values:**
- Degrees: 0-90° (flat to vertical)
- Percent: 0-infinite (0% = flat, 100% = 45°)

**Interpretation:**
- 0-3°: flat terrain (suitable for most uses)
- 3-15°: gentle slopes (buildable)
- 15-30°: steep (erosion concerns)
- >30°: very steep (avalanche/landslide risk)

**Typical Workflow Steps:**
1. Fetch DEM (SRTM 30m or Copernicus)
2. Calculate slope in degrees
3. Threshold to suitable range (e.g., < 5°)
4. Combine with other suitability layers

**Dependencies:**
- Input DEM must be in consistent units (meters recommended)
        """,
        "tags": ["dem", "terrain-analysis", "suitability"],
        "workflow_examples": ["flood_mapping_001", "site_suitability_solar_001"]
    },
    {
        "id": "vector_osm_roads",
        "title": "Vector Tool: OpenStreetMap Roads",
        "tool_name": "vector",
        "operation": "load_osm",
        "content": """
Download road network data from OpenStreetMap for accessibility analysis.

**Use Cases:**
- Site suitability: include areas near roads
- Route analysis and planning
- Accessibility assessment
- Infrastructure proximity

**Parameters:**
- highway_types: list of road classes
  - 'motorway': highways
  - 'trunk'/'primary'/'secondary'/'tertiary': main roads
  - 'residential': local roads
  - 'unclassified': local/minor roads

**Output:**
- LineString GeoJSON features
- Attributes: name, highway, surface, etc.

**Typical Workflow:**
1. Download roads for AOI
2. Compute distance raster to roads
3. Filter sites within acceptable distance (e.g., 1-5 km)

**Distance Interpretation:**
- <1 km: too close (pollution, noise)
- 1-5 km: optimal (accessible, not intrusive)
- >5 km: isolated (high access cost)

**Attributes Available:**
- name: road name
- highway: classification
- surface: paved/unpaved
- lanes: number of lanes
        """,
        "tags": ["osm", "roads", "accessibility", "vector"],
        "workflow_examples": ["site_suitability_solar_001"]
    },
]

WORKFLOW_TEMPLATES = [
    {
        "id": "flood_detection_template",
        "name": "Flood Detection from SAR",
        "description": "Quick template for detecting flooded areas using Sentinel-1 SAR imagery.",
        "steps": [
            "Download Sentinel-1 SAR (VV polarization)",
            "Apply speckle filter",
            "Convert to dB scale",
            "Threshold at -17 dB for water detection",
            "Apply morphological cleaning",
            "Vectorize flood extent"
        ],
        "typical_runtime": "3-5 minutes",
        "data_sources": ["sentinel-1"],
        "tags": ["flood", "sar", "emergency-response"]
    },
    {
        "id": "suitability_analysis_template",
        "name": "Multi-factor Site Suitability",
        "description": "General template for site suitability analysis (solar, agriculture, etc.).",
        "steps": [
            "Fetch DEM and calculate slope",
            "Fetch land cover and mask unsuitable classes",
            "Fetch auxiliary data (roads, utilities)",
            "Create distance rasters",
            "Combine all layers with weighted scoring",
            "Rank and identify top sites"
        ],
        "typical_runtime": "5-10 minutes",
        "data_sources": ["dem", "optical", "osm"],
        "tags": ["suitability", "planning", "multi-criteria"]
    },
    {
        "id": "change_detection_template",
        "name": "Change Detection (Before/After)",
        "description": "Detect changes between two time periods using optical imagery.",
        "steps": [
            "Download pre-event optical imagery",
            "Download post-event optical imagery",
            "Calculate vegetation index (NDVI) for both",
            "Compute difference map",
            "Threshold change magnitude",
            "Vectorize change polygons"
        ],
        "typical_runtime": "4-8 minutes",
        "data_sources": ["sentinel-2"],
        "tags": ["change-detection", "disaster-assessment"]
    },
]
