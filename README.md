# AWS AI Bedrock Textract (Work in Progress)
This repository contains code for deploying a serverless application that uses Amazon Textract to extract text from document uploaded to an S3 bucket and summarizes the text in the document.


# Prerequisites
- An AWS account
- The AWS CLI
- Docker (optional)
- SAM CLI

# Deployment
To deploy the application, run the following commands:

`sam build`

`sam deploy --stack-name <stack_name>  --force-upload  --no-confirm-changeset`

Replace <stack_name> with a unique name for your stack.

# Usage
Once the application is deployed, you can upload a document to the upload folder in the S3 bucket specified in the S3_BUCKET.

You can view the extracted text by accessing the output folder in the S3 bucket.

# Development
To make changes to the application, edit the code in the app directory. Then, run the following commands to build and deploy the application:

`sam build`

`sam deploy --stack-name <stack_name>  --force-upload  --no-confirm-changeset`

# License
This code is licensed under the Apache License 2.0.
