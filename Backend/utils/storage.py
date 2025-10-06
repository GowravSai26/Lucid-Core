import boto3
from botocore.client import Config
from Backend.app.config import settings
import io

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

def upload_text(key: str, text: str):
    s3 = get_s3_client()
    bucket = settings.S3_BUCKET
    # ensure bucket exists (idempotent)
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        # create bucket
        try:
            s3.create_bucket(Bucket=bucket)
        except Exception:
            pass
    s3.put_object(Bucket=bucket, Key=key, Body=text.encode("utf-8"))
    return key

def download_text(key: str):
    s3 = get_s3_client()
    bucket = settings.S3_BUCKET
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj["Body"].read().decode("utf-8")
