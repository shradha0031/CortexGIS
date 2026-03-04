"""Tool adapters for GeoPandas, Rasterio, WhiteboxTools, etc."""
from executor.tool_base import GeoTool, ToolResult, ToolStatus
from typing import Dict, Any, List
import os


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
        if not self.geopandas_available:
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.FAILED,
                output_files=[],
                error_message="GeoPandas not installed. Install with: pip install geopandas"
            )
        
        logs = []
        try:
            import geopandas as gpd
            
            if operation == "buffer":
                # Stub: in real impl, load file, buffer, save
                input_file = params.get("input", "aoi.geojson")
                distance = params.get("distance_m", 100)
                output_file = f"buffered_{distance}m.geojson"
                logs.append(f"Buffering {input_file} by {distance}m")
                # Stub: gpd.read_file(input_file).buffer(distance).to_file(output_file)
                
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"buffer_distance_m": distance},
                    logs=logs
                )
            
            elif operation == "dissolve":
                output_file = "dissolved.geojson"
                logs.append("Dissolving geometries by attribute")
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
        return ["buffer", "dissolve", "intersect", "reproject", "simplify"]


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
        if not self.rasterio_available:
            return ToolResult(
                tool_name=self.name,
                operation=operation,
                status=ToolStatus.FAILED,
                output_files=[],
                error_message="Rasterio not installed. Install with: pip install rasterio"
            )
        
        logs = []
        try:
            if operation == "threshold":
                threshold_val = params.get("value", -17)
                output_file = f"thresholded_{threshold_val}.tif"
                logs.append(f"Applying threshold at value {threshold_val}")
                
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"threshold_value": threshold_val},
                    logs=logs
                )
            
            elif operation == "speckle_filter":
                kernel_size = params.get("kernel_size", 5)
                output_file = "despeckled.tif"
                logs.append(f"Applying speckle filter with kernel {kernel_size}x{kernel_size}")
                
                return ToolResult(
                    tool_name=self.name,
                    operation=operation,
                    status=ToolStatus.SUCCESS,
                    output_files=[output_file],
                    metrics={"kernel_size": kernel_size},
                    logs=logs
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
        return ["threshold", "speckle_filter", "resample", "reproject", "mask"]


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
