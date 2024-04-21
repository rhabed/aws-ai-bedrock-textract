import json
import boto3
import os
import logging

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")

STATEMACHINEARN = os.environ["STATEMACHINE_STATE_MACHINE_ARN"]


def get_s3_details_from_event(event):
    """
    Extracts the S3 bucket and key from the event.

    Args:
        event (dict): The event that triggered the function.

    Returns:
        dict: A dictionary containing the S3 bucket and key.
    """
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_key = event["Records"][0]["s3"]["object"]["key"]

    response = {
        "_s3_bucket": s3_bucket,
        "_s3_key": s3_key,
        "_s3_object": s3_bucket + "/" + s3_key,
    }

    return response


def handler(event, context):
    """
    Triggers a step function execution.

    Args:
        event (dict): The event that triggered the function.
        context (dict): The context of the function execution.

    Returns:
        dict: A dictionary containing the status code and message.
    """

    # Log the event argument for debugging and for use in local development.
    LOGGER.info(json.dumps(event))

    # Get the step function client.
    client = boto3.client("stepfunctions")

    # Get the input from the event.
    input = json.dumps(get_s3_details_from_event(event))
    LOGGER.info(f"This is the input to the step function execution: {input}")

    try:
        # Start the step function execution.
        client.start_execution(stateMachineArn=STATEMACHINEARN, input=input)
        # Return the response from the step function execution.
        return {"statusCode": 200, "message": "OK"}
    except Exception as e:
        LOGGER.error("Error starting step function execution: " + str(e))
        return {"statusCode": 500, "message": "Error starting step function execution"}
