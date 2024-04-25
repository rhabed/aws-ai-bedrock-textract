import json
import boto3
import os
import logging

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")

def handler(event, context):
    """
    This function is triggered by a Step Function state machine.
    It processes the text extracted from a PDF document by Amazon Textract.

    Args:
        event (dict): The event data passed to the function by Step Functions.
        context (dict): The context data passed to the function by Step Functions.

    Returns:
        dict: The response data to be passed to the next Step Function state.
    """
    
    LOGGER.info(json.dumps(event))
    return {"statusCode": 200, "message": "Success"}