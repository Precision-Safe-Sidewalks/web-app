import os

# Lambda endpoint url
LAMBDA_ENDPOINT_URL = os.environ.get("LAMBDA_ENDPOINT_URL")

# Measurement geocoding queue
# FIXME: remove in favor of async invocation
MEASUREMENT_GEOCODING_QUEUE_URL = os.environ.get("MEASUREMENT_GEOCODING_QUEUE_URL")

# Pricing sheet Lambda function
PRICING_SHEET_LAMBDA_FUNCTION_NAME = os.environ.get(
    "PRICING_SHEET_LAMBDA_FUNCTION_NAME"
)
