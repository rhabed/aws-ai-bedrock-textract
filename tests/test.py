# @TODO Complete and fix all unit tests
# when running these unit test, you need to set the
# export STATEMACHINE_STATE_MACHINE_ARN="arn:aws:states:us-east-1:123456789012:stateMachine:my-state-machine" in your terminal

import sys

sys.path.append("./src/trigger_step_function")
import unittest
import unittest.mock

import handler


class TestHandler(unittest.TestCase):

    def setUp(self):
        self.event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "my-bucket"},
                        "object": {"key": "upload/my-file.pdf"},
                    }
                }
            ]
        }

    def test_get_s3_details_from_event(self):
        response = handler.get_s3_details_from_event(self.event)
        self.assertEqual(response["_s3_bucket"], "my-bucket")
        self.assertEqual(response["_s3_key"], "upload/my-file.pdf")
        self.assertEqual(response["_s3_object"], "my-bucket/upload/my-file.pdf")

    @unittest.mock.patch("handler.convert_from_path")
    def test_convert_pdf_to_images(self, mock_convert_from_path):
        mock_convert_from_path.return_value = [1, 2, 3]
        response = handler.convert_pdf_to_images(self.event)
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["_s3_bucket"], "my-bucket")
        self.assertEqual(response["_s3_path"], "202303081234")
        self.assertEqual(
            response["_s3_objects"],
            ["my-file-page-1.jpg", "my-file-page-2.jpg", "my-file-page-3.jpg"],
        )

    @unittest.mock.patch("handler.boto3")
    def test_handler(self, mock_boto3):
        mock_client = mock_boto3.client
        mock_client.return_value.start_execution.return_value = {}
        response = handler.handler(self.event, {})
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(response["message"], "OK")

    @unittest.mock.patch("handler.boto3")
    def test_handler_error(self, mock_boto3):
        mock_client = mock_boto3.client
        mock_client.return_value.start_execution.side_effect = Exception("Error")
        response = handler.handler(self.event, {})
        self.assertEqual(response["statusCode"], 500)
        self.assertEqual(response["message"], "Error starting step function execution")

    def test_handler_not_pdf(self):
        self.event["Records"][0]["s3"]["object"]["key"] = "my-file.jpg"
        response = handler.handler(self.event, {})
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(response["message"], "Wrong file type")
