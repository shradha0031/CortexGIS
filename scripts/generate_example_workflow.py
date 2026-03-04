"""Generate and validate example workflows using JSON schemas."""
import json
import jsonschema
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SCHEMA_DIR = os.path.join(BASE_DIR, "reference_chat2geo", "schemas")

WORKFLOW_SCHEMA_PATH = os.path.join(SCHEMA_DIR, "workflow_schema.json")


def load_schema(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    schema = load_schema(WORKFLOW_SCHEMA_PATH)
    validator = jsonschema.Draft7Validator(schema)

    example = {
        "id": "flood_example",
        "description": "Simple workflow demonstrating flood detection steps",
        "inputs": {"aoi": "polygon.geojson"},
        "steps": [
            {"id": "buffer_aoi", "tool": "vector", "op": "buffer", "params": {"distance_m": 200}},
            {"id": "fetch_s1", "tool": "sentinel", "op": "download", "params": {"polarization": "VV"}},
            {"id": "speckle", "tool": "raster", "op": "speckle_filter", "params": {}},
            {"id": "threshold", "tool": "raster", "op": "threshold", "params": {"value": -17}},
        ],
        "outputs": ["flood_mask.tif"],
        "cot": [
            "1. Buffer the AOI to include nearby land.",
            "2. Download Sentinel-1 image for AOI.",
            "3. Apply speckle filter.",
            "4. Threshold to identify water."
        ]
    }

    errors = list(validator.iter_errors(example))
    if errors:
        print("Validation errors:")
        for err in errors:
            print(err.message)
    else:
        print("Example workflow is valid:")
        print(json.dumps(example, indent=2))

if __name__ == "__main__":
    main()
