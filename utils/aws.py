import json
import logging

import boto3
from django.conf import settings

LOGGER = logging.getLogger(__name__)


def invoke_lambda_function(function, payload=None):
    """Return an invocation function for the AWS Lambda function"""
    params = settings.LAMBDA.get(function)

    if not params:
        raise ValueError(f"Invalid function {function}")

    if not params["enabled"]:
        LOGGER.info(f"Lambda function {function} disabled")
        return

    client = boto3.client("lambda", endpoint_url=params["endpoint_url"])
    client.invoke(
        FunctionName=params["function_name"],
        InvocationType="Event",
        Payload=json.dumps(payload, default=str),
    )
