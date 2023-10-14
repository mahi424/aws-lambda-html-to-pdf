import subprocess
import os
import boto3
import json
import logging

# Read the desired logging level from an environment variable
# Default to DEBUG if LOG_LEVEL is not set
log_level = os.environ.get('LOG_LEVEL', 'DEBUG')

# Configure the logging settings based on the environment variable
numeric_log_level = getattr(logging, log_level.upper(), None)
if not isinstance(numeric_log_level, int):
    raise ValueError(f'Invalid log level: {log_level}')
level = numeric_log_level
logging.basicConfig(level=numeric_log_level)

bucket = os.environ['BUCKET_NAME']
region_name = os.environ['REGION']

s3 = boto3.client('s3')


def getEventBody(event):
    try:
        body = json.loads(event['body'])
        return body
    except json.JSONDecodeError as e:
        logging.error('Bad Request: Invalid JSON %s', e)
        raise e


def getKeyFromEvent(event, key='html'):
    body = getEventBody(event)
    try:
        val = body.get(key)
        return val
    except Exception as e:
        logging.info(e)
        raise e


def uploadToS3(pdf_file_path, pdf_key, bucket):
    try:
        s3.upload_file(pdf_file_path, bucket, pdf_key, ExtraArgs={
                       'ContentType': 'application/pdf'})
        logging.info(f"PDF uploaded to: s3://{bucket}/{pdf_key}")
        # Constructing the S3 URL
        s3_url = f"https://{bucket}.s3.{region_name}.amazonaws.com/{pdf_key}"

        logging.info(f"Object URL: {s3_url}")
        return s3_url
    except Exception as e:
        logging.info("Error uploading PDF to S3:", str(e))
        raise e


def lambda_handler(event, context):
    html_data = getKeyFromEvent(event, "html")
    pdf_filename = getKeyFromEvent(event, "filename")
    path = getKeyFromEvent(event, "path")
    bucket = getKeyFromEvent(event, "bucket")

    logging.info(
        f" pdf_filename: {pdf_filename} path: {path} bucket: {bucket}")

    html_file_path = "/tmp/input.html"
    pdf_file_path = "/tmp/output.pdf"

    try:
        with open(html_file_path, "w") as f:
            f.write(html_data)
        logging.info('file written')
    except Exception as e:
        logging.error(str(e))
        raise e

    # Convert HTML to PDF using wkhtmltopdf
    logging.info(level, 'writing pdf')
    try:
        process = subprocess.Popen(
            ["wkhtmltopdf", html_file_path, pdf_file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logging.info(
                f"Failed to convert HTML to PDF. Stdout: {stdout.decode()}, Stderr: {stderr.decode()}")
        else:
            logging.info('pdf written')
    except Exception as e:
        logging.error(e)
        logging.error(f"Failed to convert HTML to PDF: {str(e)}")

    file_key = f'{path}/{pdf_filename}'
    try:
        s3_url = uploadToS3(pdf_file_path, file_key, bucket)
        logging.info(f's3_url:{s3_url}')
    except Exception as e:
        logging.error(f"Failed to upload PDF to S3: {str(e)}")
        return {
            'statusCode': 500,
            'body': 'Failed to upload PDF to S3'
        }

    try:
        os.remove(html_file_path)
        os.remove(pdf_file_path)
    except Exception as e:
        logging.error(e)
    return {
        'statusCode': 200,
        'body': json.dumps({'s3_url': s3_url})
    }
