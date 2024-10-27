import boto3
from botocore.exceptions import NoCredentialsError
from app.config import Config

s3 = boto3.client(
    's3',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.S3_REGION
)

def upload_to_s3(file, s3_filename):

    try:
        s3.upload_file(file, Config.S3_BUCKET, s3_filename)
    except NoCredentialsError:
        return None

