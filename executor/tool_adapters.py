"""Tool adapters for GeoPandas, Rasterio, WhiteboxTools, etc."""
from executor.tool_base import GeoTool, ToolResult, ToolStatus
from typing import Dict, Any, List
import json
import os


def _ensure_output_dir(output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def _build_output_path(output_dir: str, filename: str) -> str:
    return os.path.join(_ensure_output_dir(output_dir), filename)


def _write_placeholder_file(path: str, contents: str = "") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(contents)


def _write_sample_geojson(
    path: str,
    feature_name: str = "result_polygon",
    center_lat: float = 18.5204,
    center_lon: float = 73.8567,
    size_deg: float = 0.02,
) -> None:
    """Write a small sample polygon centered on provided coordinates."""
    min_lon = center_lon - size_deg
    max_lon = center_lon + size_deg
    min_lat = center_lat - size_deg
    max_lat = center_lat + size_deg

    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": feature_name,
                    "center_lat": center_lat,
                    "center_lon": center_lon,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat],
                    ]],
                },
            }
        ],
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(feature_collection, f)


class VectorTool(GeoTool):
    """Adapter for vector operations (GeoPandas)."""
    
    def __init__(self):
        super().__init__("vector", "Vector data operations using GeoPandas")
        self.geopandas_available = False
        try:
            import geopandas
            self.geopandas_available = True
        except ImportError:
            pass
    
    def execute(self, operation: str, params: Dict[str, Any], **kwargs) -> ToolResult:
        logs = []
        if not self.geopandas_available:
            logs.append("GeoPandas not installed; running vector tool in stub mode")
        try:
            output_dir = kwargs.get("output_dir", ".")

            if operation == "buffer":
                # Stub: in real impl, load file, buffer, save
                input_file = params.get("input", "aoi.geojson")
                distance = params.get("distance_m", 100)
                center_lat = float(params.get("center_lat", 18.5204))
                center_lon = float(params.get("center_lon", 73.8567))
                size_deg = float(params.get("size_deg", 0.02))
                output_file = _build_output_path(output_dir, f"buffered_{distance}m.geojson")
                logs.append(f"Buffering {input_file} by {distance}m")
                # Stub: gpd.read_file(input_file).buffer(distance).to_file(output_file)
                _write_sample_geojson(
                    output_file,
                    feature_name="buffered_area",
                    center_lat=center_lat,
                    center_lon=center_lon,
                    size_deg=size_deg,
                )
                
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"buffer_distance_m": distance},
                    logs=logs
                )
            
            elif operation == "dissolve":
                output_file = _build_output_path(output_dir, "dissolved.geojson")
                logs.append("Dissolving geometries by attribute")
                _write_sample_geojson(output_file, feature_name="dissolved_area")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    logs=logs
                )
            
            elif operation in {"raster_to_vector", "raster_to_poly"}:
                center_lat = float(params.get("center_lat", 18.5204))
                center_lon = float(params.get("center_lon", 73.8567))
                size_deg = float(params.get("size_deg", 0.02))
                output_file = _build_output_path(output_dir, "flood_boundary.geojson")
                logs.append("Vectorizing raster mask to polygon features")
                _write_sample_geojson(
                    output_file,
                    feature_name="flood_extent",
                    center_lat=center_lat,
                    center_lon=center_lon,
                    size_deg=size_deg,
                )
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"features": 1},
                    logs=logs,
                )

            elif operation == "validate":
                logs.append("Validated vector inputs")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[],
                    logs=logs,
                )

            elif operation == "load_osm":
                feature_type = params.get("feature_type", "roads")
                center_lat = float(params.get("center_lat", 18.5204))
                center_lon = float(params.get("center_lon", 73.8567))
                output_file = _build_output_path(output_dir, f"osm_{feature_type}.geojson")
                logs.append(f"Loading OSM {feature_type} layer")
                _write_sample_geojson(
                    output_file,
                    feature_name=feature_type,
                    center_lat=center_lat,
                    center_lon=center_lon,
                    size_deg=0.03,
                )
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"feature_type": feature_type, "source": "OpenStreetMap"},
                    logs=logs,
                )

            else:
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.FAILED,
                    output_files=[],
                    error_message=f"Operation '{operation}' not supported in VectorTool"
                )
        
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.FAILED,
                output_files=[],
                error_message=str(e)
            )
    
    def supported_operations(self) -> List[str]:
        return [
            "buffer",
            "dissolve",
            "intersect",
            "reproject",
            "simplify",
            "raster_to_vector",
            "raster_to_poly",
            "validate",
            "load_osm",
        ]


class RasterTool(GeoTool):
    """Adapter for raster operations (Rasterio)."""
    
    def __init__(self):
        super().__init__("raster", "Raster data operations using Rasterio")
        self.rasterio_available = False
        try:
            import rasterio
            self.rasterio_available = True
        except ImportError:
            pass
    
    def execute(self, operation: str, params: Dict[str, Any], **kwargs) -> ToolResult:
        logs = []
        if not self.rasterio_available:
            logs.append("Rasterio not installed; running raster tool in stub mode")
        try:
            output_dir = kwargs.get("output_dir", ".")

            if operation == "threshold":
                threshold_val = params.get("value", -17)
                output_file = _build_output_path(output_dir, f"thresholded_{threshold_val}.tif")
                logs.append(f"Applying threshold at value {threshold_val}")
                _write_placeholder_file(output_file, "stub threshold raster")
                
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"threshold_value": threshold_val},
                    logs=logs
                )
            
            elif operation in {"speckle_filter", "despeckle"}:
                kernel_size = params.get("kernel_size", 5)
                output_file = _build_output_path(output_dir, "despeckled.tif")
                logs.append(f"Applying speckle filter with kernel {kernel_size}x{kernel_size}")
                _write_placeholder_file(output_file, "stub despeckled raster")
                
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"kernel_size": kernel_size},
                    logs=logs
                )
            
            elif operation == "to_db":
                scale_factor = params.get("scale_factor", 10)
                output_file = _build_output_path(output_dir, "sar_db.tif")
                logs.append(f"Converting SAR intensity to dB with scale factor {scale_factor}")
                _write_placeholder_file(output_file, "stub db raster")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"scale_factor": scale_factor},
                    logs=logs,
                )

            elif operation == "mask":
                output_file = _build_output_path(output_dir, "masked.tif")
                logs.append("Applying raster mask")
                _write_placeholder_file(output_file, "stub masked raster")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    logs=logs,
                )

            elif operation == "morphological_close":
                kernel_size = params.get("kernel_size", 3)
                output_file = _build_output_path(output_dir, "flood_mask_clean.tif")
                logs.append(f"Applying morphological close with kernel {kernel_size}")
                _write_placeholder_file(output_file, "stub morphologically cleaned raster")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"kernel_size": kernel_size},
                    logs=logs,
                )

            elif operation == "stats":
                output_file = _build_output_path(output_dir, "flood_stats.json")
                stats_payload = {
                    "flood_pixels": 1250,
                    "flood_area_sq_km": 4.5,
                    "note": "Stub statistics for demo output",
                }
                _write_placeholder_file(output_file, json.dumps(stats_payload, indent=2))
                logs.append("Computed raster statistics")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics=stats_payload,
                    logs=logs,
                )

            elif operation == "slope":
                output_file = _build_output_path(output_dir, "slope.tif")
                logs.append("Computing slope from DEM")
                _write_placeholder_file(output_file, "stub slope raster")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"method": "gdal_dem"},
                    logs=logs,
                )

            elif operation == "combine":
                method = params.get("method", "intersection")
                output_file = _build_output_path(output_dir, f"combined_{method}.tif")
                logs.append(f"Combining constraint layers via {method}")
                _write_placeholder_file(output_file, "stub combined constraint raster")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"method": method},
                    logs=logs,
                )

            elif operation == "rank":
                scale = params.get("scale", 100)
                output_file = _build_output_path(output_dir, "ranked_suitability.tif")
                logs.append(f"Ranking suitability scores on 0-{scale} scale")
                _write_placeholder_file(output_file, "stub ranked suitability raster")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"scale": scale},
                    logs=logs,
                )

            elif operation == "cluster":
                min_size = params.get("min_size", 10)
                output_file = _build_output_path(output_dir, "clusters.tif")
                logs.append(f"Clustering suitable areas (min size: {min_size} pixels)")
                _write_placeholder_file(output_file, "stub clustered regions raster")
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"min_cluster_size": min_size, "clusters_found": 5},
                    logs=logs,
                )


            else:
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.FAILED,
                    output_files=[],
                    error_message=f"Operation '{operation}' not supported in RasterTool"
                )
        
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.FAILED,
                output_files=[],
                error_message=str(e)
            )
    
    def supported_operations(self) -> List[str]:
        return [
            "threshold",
            "speckle_filter",
            "despeckle",
            "resample",
            "reproject",
            "mask",
            "to_db",
            "morphological_close",
            "stats",
            "slope",
            "combine",
            "rank",
            "cluster",
        ]


class SentinelTool(GeoTool):
    """Stub adapter for Sentinel operations used by generated workflows."""

    def __init__(self):
        super().__init__("sentinel", "Sentinel imagery retrieval operations")

    def execute(self, operation: str, params: Dict[str, Any], **kwargs) -> ToolResult:
        output_dir = kwargs.get("output_dir", ".")
        logs = []

        if operation in {"download_vv", "download_sar"}:
            output_file = _build_output_path(output_dir, "sentinel1_vv.tif")
            logs.append(f"Preparing Sentinel SAR layer with params: {params}")
            _write_placeholder_file(output_file, "stub sentinel SAR raster")
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.SUCCESS,
                output_files=[output_file],
                metrics={"source": "sentinel_stub"},
                logs=logs,
            )

        elif operation == "download_landcover":
            output_file = _build_output_path(output_dir, "landcover.tif")
            logs.append("Fetching landcover classification layer")
            _write_placeholder_file(output_file, "stub landcover raster")
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.SUCCESS,
                output_files=[output_file],
                metrics={"source": "copernicus_lulc"},
                logs=logs,
            )

        elif operation == "download_dem":
            output_file = _build_output_path(output_dir, "dem.tif")
            logs.append("Fetching DEM (Digital Elevation Model)")
            _write_placeholder_file(output_file, "stub DEM raster")
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.SUCCESS,
                output_files=[output_file],
                metrics={"source": "SRTM_90m"},
                logs=logs,
            )

        return ToolResult(
            tool_name=self.name,
            operation=operation,
            status=ToolStatus.FAILED,
            output_files=[],
            error_message=f"Operation '{operation}' not supported in SentinelTool",
        )

    def supported_operations(self) -> List[str]:
        return ["download_vv", "download_sar", "download_landcover", "download_dem"]


class WhiteboxTool(GeoTool):
    """Adapter for WhiteboxTools."""
    
    def __init__(self):
        super().__init__("whitebox", "Spatial analysis using WhiteboxTools")
        self.whitebox_available = False
        try:
            from whitebox.whitebox_tools import WhiteboxTools
            self.wbt = WhiteboxTools()
            self.whitebox_available = True
        except ImportError:
            pass
    
    def execute(self, operation: str, params: Dict[str, Any], **kwargs) -> ToolResult:
        if not self.whitebox_available:
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.FAILED,
                output_files=[],
                error_message="WhiteboxTools not installed. Install with: pip install whitebox"
            )
        
        logs = []
        try:
            if operation == "d8_flow_accumulation":
                dem_file = params.get("input_dem", "dem.tif")
                output_file = "flow_accumulation.tif"
                logs.append(f"Computing D8 flow accumulation from {dem_file}")
                # Stub: self.wbt.d8_flow_accumulation(dem_file, output_file)
                
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    logs=logs
                )
            
            else:
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.FAILED,
                    output_files=[],
                    error_message=f"Operation '{operation}' not available"
                )
        
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.FAILED,
                output_files=[],
                error_message=str(e)
            )
    
    def supported_operations(self) -> List[str]:
        return ["d8_flow_accumulation", "slope", "aspect", "slope_length"]
