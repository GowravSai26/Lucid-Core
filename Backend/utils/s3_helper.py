import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from Backend.app.config import settings

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    )

def upload_file_to_s3(local_path: str, s3_key: str) -> str:
    """Uploads a file to MinIO and returns the public URL."""
    s3 = get_s3_client()
    try:
        s3.upload_file(local_path, settings.S3_BUCKET, s3_key)
        return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{s3_key}"
    except (NoCredentialsError, ClientError) as e:
        return f"[S3 Upload Error] {e}"
