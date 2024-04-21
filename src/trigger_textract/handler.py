import json
import boto3
import logging
from trp import Document

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")


def extract_text_from_image(event):
    """
    Extracts text from an image using Amazon Textract.

    Args:
        event (dict): The event that triggered the function.

    Returns:
        dict: A dictionary containing the extracted text.
    """
    s3BucketName = event.get("_s3_bucket")
    fileName = event.get("_s3_key")

    textractmodule = boto3.client("textract", region_name="ap-southeast-2")

    try:
        response = textractmodule.detect_document_text(
            Document={"S3Object": {"Bucket": s3BucketName, "Name": fileName}}
        )
        text = ""
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                text += item["Text"] + "\n"

        LOGGER.info("Extracted Text: " + text)
        return {"text": text}
    except Exception as e:
        LOGGER.error("Error extracting text from image: " + str(e))
        return {"error": str(e)}


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
    extract_text_from_image(event)

    # response = textractmodule.detect_document_text(
    #     Document={"S3Object": {"Bucket": s3BucketName, "Name": fileName}}
    # )
    # print(
    #     "------------- Print plaintextimage detected text ------------------------------"
    # )
    # for item in response["Blocks"]:
    #     if item["BlockType"] == "LINE":
    #         print(item["Text"])

    # response_job = textractmodule.start_document_analysis(
    #     FeatureTypes=["TABLES", "FORMS"],
    #     DocumentLocation={"S3Object": {"Bucket": s3BucketName, "Name": fileName}},
    # )

    # print(response_job)
