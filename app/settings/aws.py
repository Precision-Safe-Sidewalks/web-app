import os

LAMBDA = {
    "geocoding": {
        "endpoint_url": os.environ.get("GEOCODING_LAMBDA_URL"),
        "function_name": os.environ.get("GEOCODING_LAMBDA_FUNCTION_NAME"),
        "enabled": os.environ.get("GEOCODING_ENABLED", "false").lower() == "true",
    },
    "pricing_sheet": {
        "endpoint_url": os.environ.get("PRICING_SHEET_LAMBDA_URL"),
        "function_name": os.environ.get("PRICING_SHEET_LAMBDA_FUNCTION_NAME"),
        "enabled": True,
    },
    "project_summary": {
        "endpoint_url": os.environ.get("PROJECT_SUMMARY_LAMBDA_URL"),
        "function_name": os.environ.get("PROJECT_SUMMARY_LAMBDA_FUNCTION_NAME"),
        "enabled": True,
    },
    "arcgis_sync": {
        "endpoint_url": os.environ.get("ARCGIS_SYNC_LAMBDA_URL"),
        "function_name": os.environ.get("ARCGIS_SYNC_LAMBDA_FUNCTION_NAME"),
        "enabled": True,
    },
}
