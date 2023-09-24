import os

LAMBDA = {
    "geocoding": {
        "endpoint_url": os.environ.get("GEOCODING_LAMBDA_URL"),
        "function_name": os.environ.get("GEOCODING_LAMBDA_FUNCTION_NAME"),
    },
    "pricing_sheet": {
        "endpoint_url": os.environ.get("PRICING_SHEET_LAMBDA_URL"),
        "function_name": os.environ.get("PRICING_SHEET_LAMBDA_FUNCTION_NAME"),
    },
}
