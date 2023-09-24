import json

import boto3
from django.conf import settings


def invoke_lambda_function(function, payload=None):
    """Return an invocation function for the AWS Lambda function"""
    params = settings.LAMBDA.get(function)

    if not params:
        raise ValueError(f"Invalid function {function}")

    client = boto3.client("lambda", endpoint_url=params["endpoint_url"])
    client.invoke(
        FunctionName=params["function_name"],
        InvocationType="Event",
        Payload=json.dumps(payload, default=str),
    )
