import json
import boto3
import os

STATEMACHINEARN = os.environ["STATEMACHINE_STATE_MACHINE_ARN"]


def get_s3_details_from_event(event):

    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_key = event["Records"][0]["s3"]["object"]["key"]

    response = {
        "_s3_bucket": s3_bucket,
        "_s3_key": s3_key,
        "_s3_object": s3_bucket + "/" + s3_key,
    }

    return response


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))

    # Get the step function client.
    client = boto3.client("stepfunctions")

    # Get the input from the event.
    input = json.dumps(get_s3_details_from_event(event))
    print(f"This is the input to the step function execution: {input}")

    # Start the step function execution.
    client.start_execution(stateMachineArn=STATEMACHINEARN, input=input)
    # Return the response from the step function execution.
    return {"statusCode": 200, "message": "OK"}
