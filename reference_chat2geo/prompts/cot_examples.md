# Chain-of-Thought Prompt Examples

## Example 1: Flood Risk Mapping

**User query:** "Map areas that are likely to flood along the River X using Sentinel-1 imagery and DEM."

**CoT reasoning:**
1. Identify the river boundary and buffer to capture adjacent land.
2. Retrieve Sentinel-1 SAR data for the AOI during last monsoon.
3. Apply speckle filtering, convert to backscatter (dB).
4. Threshold low backscatter values to identify water surfaces.
5. Use DEM to mask out elevated areas, keeping low-lying regions.
6. Vectorize result and compute inundation probability.

**Workflow JSON snippet:**
```json
{
  "steps": [
    {"id":"aoi","tool":"vector","op":"buffer","params":{"distance_m":200}},
    {"id":"fetch_s1","tool":"sentinel_fetch","params":{"polarization":"VV"}},
    {"id":"filter","tool":"rasterio","op":"speckle"},
    {"id":"threshold","tool":"python","op":"db_threshold","params":{"value":-17}},
    {"id":"mask","tool":"rasterio","op":"apply_dem_mask"}
  ]
}
```

## Example 2: Site Suitability

**User query:** "Find suitable locations for a solar farm avoiding wetlands, slopes >5°, and within 5km of roads."

**CoT reasoning:**
1. Load landcover to identify wetlands and mask them out.
2. Compute slope from DEM and threshold at 5°.
3. Load road network, compute 5km buffer.
4. Combine masks to produce candidate areas.
5. Rank by total solar irradiance if data available.

... (add more as needed)
