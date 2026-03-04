# Data Ingestion Module

This module provides utilities to ingest geospatial datasets from various open sources for use in CortexGIS workflows.

## Supported Data Sources

| Source | Type | Format | URL |
|--------|------|--------|-----|
| **OpenStreetMap** | Vector | GeoJSON | https://overpass-api.de/ |
| **Sentinel-1** | Raster (SAR) | GeoTIFF | https://scihub.copernicus.eu/ |
| **Sentinel-2** | Raster (Optical) | GeoTIFF | https://scihub.copernicus.eu/ |
| **SRTM** | DEM | GeoTIFF | https://earthexplorer.usgs.gov/ |
| **Bhoonidhi** | Vector/Raster | GeoJSON/GeoTIFF | https://www.isro.gov.in/ |

## Quick Start

### 1. List Available Datasets

```python
from data.ingestion import DATASET_CATALOG

for ds_id, metadata in DATASET_CATALOG.items():
    print(f"{ds_id}: {metadata.name} ({metadata.source})")
```

### 2. Ingest Data

```python
from data.ingestion import DatasetManager

manager = DatasetManager(cache_dir="./data")

# Fetch OpenStreetMap data
bbox = (73.7, 18.4, 73.9, 18.6)  # Example: Pune, India
roads = manager.ingest_osm(
    bbox=bbox,
    tags={"highway": "primary|secondary"},
    output_file="roads.geojson"
)

# Fetch Sentinel-1 SAR data
s1 = manager.ingest_sentinel(
    bbox=bbox,
    date_range=("2024-08-01", "2024-08-31"),
    product="S1",
    output_file="sentinel1.tif"
)

# Fetch SRTM DEM
dem = manager.ingest_srtm(
    bbox=bbox,
    output_file="dem.tif"
)
```

## Implementation Notes

Current implementation provides **stubs** that log operations. To enable actual data downloads:

### OpenStreetMap
Install `osmnx` or `overpy`:
```bash
pip install osmnx
```

Example implementation using osmnx:
```python
import osmnx as ox

gdf = ox.features_from_bbox(18.4, 18.6, 73.7, 73.9, 
                            tags={"highway": "primary|secondary"})
gdf.to_file("roads.geojson", driver="GeoJSON")
```

### Sentinel Data
Install `sentinelhub` or use Google Earth Engine:
```bash
pip install sentinelhub
# or
pip install earthengine-api
```

### SRTM DEM
Download from USGS Earth Explorer or use:
```bash
pip install rasterio
# Fetch from AWS Terrain Tiles or other source
```

### Bhoonidhi Data
Access via official portal or state-level FTP servers.

## Dataset Catalog Extension

To add new data sources, extend `DatasetManager`:

```python
def ingest_custom(self, params, output_file):
    """Custom data source."""
    # Implement actual download
    return output_file

manager = DatasetManager()
custom_file = manager.ingest_custom(params={...}, output_file="custom.tif")
```

## CRS & Validation

All data is normalized to a common coordinate reference system (CRS) before use:
- **Default**: EPSG:4326 (WGS84)
- **Projection**: Reproject as needed for specific analyses

Always validate:
- Extent (fits within AOI)
- No-data values
- Geospatial metadata (CRS, resolution)

## Data Caching

Datasets are cached in `./data/` after first download. Delete cached files to force re-download:

```bash
rm -rf data/osm data/sentinel data/dem
```

## Example Workflow

```bash
python scripts/demo_data_ingestion.py
```

This will show how to ingest from each source.
