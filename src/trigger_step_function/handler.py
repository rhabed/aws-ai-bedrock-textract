import datetime
import io
import json
import logging
import os

import boto3
from pdf2image import convert_from_path

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


def convert_pdf_to_images(event):
    """
    Converts a PDF file to images and uploads them to an S3 bucket.

    Args:
        event (dict): The event that triggered the function.
        context (dict): The context of the function execution.

    Returns:
        dict: A dictionary containing the status code and message.
    """

    response = get_s3_details_from_event(event)
    # Get the details of the uploaded PDF file
    bucket = response["_s3_bucket"]

    # at this stage, the key contains upload - removing the prefix
    file = response["_s3_key"]
    key = response["_s3_key"].split("/")[1]

    # Create an S3 client
    s3 = boto3.client("s3")

    download_path = "/tmp/pdf_file.pdf"

    # Download the PDF file from S3
    s3.download_file(bucket, file, download_path)

    # Use pdf2image to convert PDF to images
    images = convert_from_path(download_path, fmt="jpeg")

    # Define S3 bucket for storing images (replace with your bucket name)
    now = datetime.datetime.now()
    images_path = now.strftime("%Y%m%d%H%M")

    # Loop through each image and upload to S3 with unique filename
    file_list = []
    for i, image in enumerate(images):
        filename = f"{key.split('.')[0]}-page-{i + 1}.jpg"
        in_mem_file = io.BytesIO()
        image.save(in_mem_file, format=image.format)
        in_mem_file.seek(0)
        s3.put_object(
            Body=in_mem_file,
            Bucket=bucket,
            Key="{}".format(images_path) + "/" + filename,
        )
        file_list.append(filename)

    # Delete the downloaded PDF file
    os.remove(download_path)

    return {
        "statusCode": 200,
        "body": json.dumps("PDF converted and images uploaded to S3"),
        "_s3_objects": file_list,
        "_s3_bucket": bucket,
        "_s3_path": "{}".format(images_path),
    }


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
    key = get_s3_details_from_event(event)["_s3_key"]
    LOGGER.info(f"This is the key: {key}")
    if key.endswith(".pdf"):
        LOGGER.info("This is a pdf file")
        input = json.dumps(convert_pdf_to_images(event))
        LOGGER.info(f"This is the input to the step function execution: {input}")

        try:
            # Start the step function execution.
            client.start_execution(stateMachineArn=STATEMACHINEARN, input=input)
            # Return the response from the step function execution.
            return {"statusCode": 200, "message": "OK"}
        except Exception as e:
            LOGGER.error("Error starting step function execution: " + str(e))
            return {
                "statusCode": 500,
                "message": "Error starting step function execution",
            }
    else:
        LOGGER.error("This is not a pdf file")
        return {"statusCode": 400, "message": "Wrong file type"}
