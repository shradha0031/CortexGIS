"""Example scripts to ingest geospatial data from various sources."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data.ingestion import DatasetManager, DATASET_CATALOG


def demo_osm_ingestion():
    """Example: fetch roads from OpenStreetMap."""
    print("\n" + "="*60)
    print("Example 1: OpenStreetMap Data")
    print("="*60)
    
    manager = DatasetManager(cache_dir="./data/osm")
    
    # Define bounding box (Example AOI: Pune, India)
    bbox = (73.7, 18.4, 73.9, 18.6)  # minlon, minlat, maxlon, maxlat
    
    # Fetch roads
    roads_file = manager.ingest_osm(
        bbox=bbox,
        tags={"highway": "primary|secondary|residential"},
        output_file="roads.geojson"
    )
    print(f"Saved to: {roads_file}")
    
    # Fetch water bodies
    water_file = manager.ingest_osm(
        bbox=bbox,
        tags={"natural": "water"},
        output_file="water.geojson"
    )
    print(f"Saved to: {water_file}")


def demo_sentinel_ingestion():
    """Example: fetch Sentinel-1 SAR data for flood detection."""
    print("\n" + "="*60)
    print("Example 2: Sentinel-1 SAR Data")
    print("="*60)
    
    manager = DatasetManager(cache_dir="./data/sentinel")
    
    bbox = (73.7, 18.4, 73.9, 18.6)
    date_range = ("2024-08-01", "2024-08-31")
    
    s1_file = manager.ingest_sentinel(
        bbox=bbox,
        date_range=date_range,
        product="S1",
        output_file="sentinel1_vv.tif"
    )
    print(f"Saved to: {s1_file}")
    
    # Note: In practice, would use:
    # - Sentinel Hub API (sentinelhub library)
    # - Google Earth Engine (ee library)
    # - AWS Public Datasets (boto3)
    # - USGS Earth Explorer (API call)


def demo_srtm_ingestion():
    """Example: fetch SRTM DEM."""
    print("\n" + "="*60)
    print("Example 3: SRTM DEM Data")
    print("="*60)
    
    manager = DatasetManager(cache_dir="./data/dem")
    
    bbox = (73.7, 18.4, 73.9, 18.6)
    
    dem_file = manager.ingest_srtm(
        bbox=bbox,
        output_file="srtm_dem.tif"
    )
    print(f"Saved to: {dem_file}")
    
    # Note: In practice:
    # - Download from USGS Earth Explorer
    # - Or use GEBCO for global bathymetry/topography
    # - Or use AWS Terrain Tiles


def demo_bhoonidhi_ingestion():
    """Example: fetch Bhoonidhi data for India."""
    print("\n" + "="*60)
    print("Example 4: Bhoonidhi Data (India)")
    print("="*60)
    
    manager = DatasetManager(cache_dir="./data/bhoonidhi")
    
    # Maharashtra (MH) LULC
    lulc_file = manager.ingest_bhoonidhi(
        state_code="MH",
        dataset="lulc",
        output_file="bhoonidhi_lulc_mh.tif"
    )
    print(f"Saved to: {lulc_file}")
    
    # Maharashtra DEM
    dem_file = manager.ingest_bhoonidhi(
        state_code="MH",
        dataset="dem",
        output_file="bhoonidhi_dem_mh.tif"
    )
    print(f"Saved to: {dem_file}")
    
    # Note: Access via Bhoonidhi portal:
    # https://www.isro.gov.in/


def demo_dataset_catalog():
    """Display available datasets in catalog."""
    print("\n" + "="*60)
    print("Available Datasets in Catalog")
    print("="*60)
    
    for dataset_id, metadata in DATASET_CATALOG.items():
        print(f"\n**{metadata.name}**")
        print(f"  ID: {dataset_id}")
        print(f"  Source: {metadata.source}")
        print(f"  Format: {metadata.format}")
        print(f"  CRS: {metadata.crs}")
        print(f"  Description: {metadata.description}")
        if metadata.url:
            print(f"  URL: {metadata.url}")


def main():
    print("CortexGIS Data Ingestion Examples")
    print("="*60)
    
    demo_dataset_catalog()
    demo_osm_ingestion()
    demo_sentinel_ingestion()
    demo_srtm_ingestion()
    demo_bhoonidhi_ingestion()
    
    print("\n" + "="*60)
    print("Notes:")
    print("- Replace stub calls with actual API calls to data providers.")
    print("- Consider caching downloaded data to avoid re-downloading.")
    print("- Validate CRS and extent of ingested data.")
    print("="*60)


if __name__ == "__main__":
    main()
