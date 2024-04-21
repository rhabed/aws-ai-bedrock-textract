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



def summarize_text(text):
    """
    Summarizes the given text.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summarized text.
    """
    try:
        bedrock = boto3.client('bedrock-runtime')


        # Invoke the agent with a prompt
        prompt = f"Write a summary of the text provided: {text}"
        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0,
                "topP": 1
            }
        })

        modelId = 'amazon.titan-text-express-v1'
        accept = 'application/json'
        contentType = 'application/json'

        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        finish_reason = response_body.get("error")

        if finish_reason is not None:
            raise Exception(f"Text generation error. Error is {finish_reason}")

        LOGGER.info(
            "Successfully generated text with Amazon &titan-text-express; model %s", modelId)
        
        
        for result in response_body['results']:
            LOGGER.info(f"Token count: {result['tokenCount']}")
            LOGGER.info(f"Output text: {result['outputText']}")
            LOGGER.info(f"Completion reason: {result['completionReason']}")

    except Exception as e:
        LOGGER.error("Error summarizing text: " + str(e))
        return "Error summarizing text: " + str(e)


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
    response = extract_text_from_image(event)
    summarize_text(response["text"])
    return {"statusCode": 200, "message": "Success"}
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
