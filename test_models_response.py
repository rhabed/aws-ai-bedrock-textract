import json
import logging
import os

import boto3
import click

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
LOGGER = logging.getLogger()
LOGGER.setLevel("INFO")

MODEL_ID = os.getenv("MODEL_ID")


def converse_with_model(model_id, text, type):
    try:
        client = boto3.client("bedrock-runtime")
        messages = [{"role": type, "content": [{"text": text}]}]
        breakpoint()
        response = client.converse(
            modelId=model_id,
            messages=messages,
        )

        LOGGER.info(response)

    except Exception as e:
        LOGGER.error("Error: " + str(e))
        return "Error: " + str(e)


def ask_model(text):

    try:
        bedrock = boto3.client("bedrock-runtime")

        # Invoke the agent with a prompt
        prompt = text
        #  f"Write a summary of the text provided: {text}"
        body = json.dumps(
            {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 4096,
                    "stopSequences": [],
                    "temperature": 0,
                    "topP": 1,
                },
            }
        )

        modelId = MODEL_ID  # "amazon.titan-text-express-v1"
        accept = "application/json"
        contentType = "application/json"

        response = bedrock.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())
        finish_reason = response_body.get("error")

        if finish_reason is not None:
            raise Exception(f"Text generation error. Error is {finish_reason}")

        LOGGER.info(
            "Successfully generated text with Amazon &titan-text-express; model %s",
            modelId,
        )

        for result in response_body["results"]:
            LOGGER.info(f"Token count: {result['tokenCount']}")
            LOGGER.info(f"Output text: {result['outputText']}")
            LOGGER.info(f"Completion reason: {result['completionReason']}")

    except Exception as e:
        LOGGER.error("Error summarizing text: " + str(e))
        return "Error summarizing text: " + str(e)


@click.command()
@click.option("--prompt", default="", help="Prompt for the model")
def handler(prompt):
    """
    Triggers a step function execution.

    Args:
        event (dict): The event that triggered the function.
        context (dict): The context of the function execution.

    Returns:
        dict: A dictionary containing the status code and message.
    """
    # Log the event argument for debugging and for use in local development.

    response = {"text": prompt}
    ask_model(response["text"])
    return {"statusCode": 200, "message": "Success"}


@click.command()
@click.option("--prompt", default="What is your name?", help="Prompt for the model")
@click.option("--type", default="user", help="user or assistant")
@click.option(
    "--model", default="amazon.titan-text-express-v1", help="AWS Bedrock Model ID"
)
def speak(model, prompt, type):
    converse_with_model(model_id=model, text=prompt, type=type)


if __name__ == "__main__":
    # handler()
    speak()
