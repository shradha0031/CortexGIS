"""Sample GIS documentation for RAG index ingestion."""

SAMPLE_DOCS = [
    {
        "id": "sentinel1_guide",
        "title": "Sentinel-1 SAR Imagery Processing",
        "content": """
            Sentinel-1 provides C-band SAR (Synthetic Aperture Radar) imagery in VV and VH polarizations.
            Key steps for flood detection:
            1. Download data using Sentinel Hub or Google Earth Engine API.
            2. Apply multi-looking and speckle filtering to reduce noise.
            3. Convert to dB scale (10 * log10(intensity)).
            4. For flood mapping: use thresholds around -17 dB for VV polarization.
            5. Vectorize water extent using morphological operations.
            
            Typical parameters:
            - Polarization: VV or VH
            - Incidence angle: 20-45 degrees
            - Orbit: ascending or descending
        """,
        "tags": ["sentinel-1", "flood", "sar", "remote-sensing"]
    },
    {
        "id": "dem_analysis",
        "title": "Digital Elevation Model (DEM) Analysis",
        "content": """
            DEMs (e.g., SRTM, ALOS) are critical for terrain-based analysis.
            
            Common operations:
            - Slope calculation: identifies steep vs. gentle terrain.
            - Aspect: sun exposure and hydrological flow direction.
            - Hillshade: visual representation for validation.
            - Flow accumulation: identify water channels and basins.
            
            For site suitability:
            - Threshold slope > 5 degrees to exclude steep terrain.
            - Use flow direction to model runoff and erosion.
            
            Data sources: SRTM (30m), ALOS (12.5m), Copernicus DEM (30m)
        """,
        "tags": ["dem", "slope", "terrain", "suitability"]
    },
    {
        "id": "landcover_classification",
        "title": "Land Cover Classification and Change Detection",
        "content": """
            Land cover is derived from optical satellite data (Landsat, Sentinel-2).
            
            Common classifications:
            - Urban / Built-up
            - Agriculture
            - Forest
            - Water
            - Barren / Desert
            
            For change detection:
            1. Classify two time periods independently or use spectral indices (NDVI, NDBI).
            2. Compare classifications to identify gains/losses.
            3. Report area statistics and transition matrices.
            
            Tools: QGIS, GDAL, GeoPandas, Rasterio
        """,
        "tags": ["landcover", "classification", "ndvi", "change-detection"]
    },
    {
        "id": "vector_operations",
        "title": "Vector Data Operations with GeoPandas",
        "content": """
            GeoPandas extends pandas for spatial operations.
            
            Key operations:
            - Buffer: create a polygon around features at a given distance.
            - Dissolve: merge adjacent polygons by attribute.
            - Intersection: overlay and compute overlaps.
            - Simplify: reduce vertex count while maintaining geometry.
            - Reproject: convert between coordinate reference systems (CRS).
            
            Example:
                import geopandas as gpd
                gdf = gpd.read_file('aoi.geojson')
                buffered = gdf.buffer(distance=100)  # 100m buffer
                
            Always check/reproject to consistent CRS before combining datasets.
        """,
        "tags": ["geopandas", "vector", "buffer", "overlay"]
    },
    {
        "id": "raster_operations",
        "title": "Raster Data Processing with Rasterio",
        "content": """
            Rasterio is a Python library for reading and writing raster data (GeoTIFF, etc.).
            
            Key operations:
            - Read/write GeoTIFF with georeferencing metadata.
            - Resample to different resolutions.
            - Reproject to different CRS.
            - Apply masks and filters.
            - Vectorize raster boundaries.
            
            Example:
                import rasterio
                from rasterio.mask import mask
                
                with rasterio.open('image.tif') as src:
                    masked, transform = mask(src, [aoi_geom], crop=True)
                    
            Always preserve CRS and geotransform metadata.
        """,
        "tags": ["rasterio", "geotiff", "raster", "mask"]
    },
    {
        "id": "whitebox_tools",
        "title": "WhiteboxTools for Spatial Analysis",
        "content": """
            WhiteboxTools provides 500+ geospatial analysis tools.
            
            Common tools:
            - D8_flow_accumulation: compute drainage networks.
            - slope: compute slope from DEM.
            - feature_preserving_smoothing: denoise raster.
            - connected_components: identify clusters.
            
            Usage:
                from whitebox.whitebox_tools import WhiteboxTools
                wbt = WhiteboxTools()
                wbt.d8_flow_accumulation(dem_file, output_file)
                
            Tools run independently; output is written to file.
        """,
        "tags": ["whitebox", "flow-accumulation", "slope", "tools"]
    },
    {
        "id": "flood_mapping_workflow",
        "title": "Flood Mapping Workflow Example",
        "content": """
            Complete flood mapping workflow using Sentinel-1 + DEM:
            
            1. Input: AOI (polygon), date range.
            2. Fetch Sentinel-1 VV polarization for date range.
            3. Preprocess: speckle filter, convert to dB.
            4. Threshold: identify water (VV < -17 dB).
            5. Mask: exclude areas with slope > 2 degrees.
            6. Morphology: close small gaps, remove noise.
            7. Vectorize: convert raster mask to GeoJSON.
            8. Output: inundation map, area statistics, GeoJSON boundaries.
            
            Validation:
            - Compare against optical imagery (if available).
            - Check for false positives (urban areas, calm water bodies).
            
            Metrics: True Positive Rate, False Positive Rate, IoU with reference.
        """,
        "tags": ["flood", "workflow", "sentinel-1", "example"]
    },
    {
        "id": "site_suitability_workflow",
        "title": "Site Suitability Analysis Workflow",
        "content": """
            Suitability analysis for solar farms, agriculture, etc.
            
            Steps:
            1. Input: AOI, criteria (avoid wetlands, slope limits, distance rules).
            2. Load baseline: landcover, DEM, distance layers.
            3. Mask out unsuitable zones:
               - Landcover: exclude forest, water, urban.
               - Slope: exclude > 5 degrees.
               - Distance: exclude < 5 km from roads (accessibility).
            4. Rank remaining cells by suitability (e.g., solar irradiance).
            5. Identify candidate sites as contiguous clusters above threshold.
            6. Output: suitability map, candidate coordinates, area stats.
            
            Tools: GeoPandas, Rasterio, WhiteboxTools, GDAL
        """,
        "tags": ["suitability", "site-selection", "workflow", "criteria"]
    }
]
