import json
import boto3
from trp import Document


def handler(event, context):
    # Log the event argument for debugging and for use in local development.

    print(json.dumps(event))
    s3BucketName = event.get("_s3_bucket")
    plaintextimage = event.get("_s3_key")
    formimage = "image.jpg"
    tableimage = "table_image.jpg"

    textractmodule = boto3.client("textract")
    response = textractmodule.detect_document_text(
        Document={"S3Object": {"Bucket": s3BucketName, "Name": plaintextimage}}
    )
    print(
        "------------- Print plaintextimage detected text ------------------------------"
    )
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            print(item["Text"])

    return {}
