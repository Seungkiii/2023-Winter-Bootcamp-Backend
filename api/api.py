import uuid
import requests

from datetime import timedelta, datetime
from common.aws import AWSManager

from botocore.exceptions import ClientError

s3_client = AWSManager.get_s3_client()
bucket_name = s3_client.list_buckets()["Buckets"][0]["Name"]
expires_in = int(timedelta(days=7).total_seconds())  # URL의 만료 시간 (초 단위)


def upload_img_to_s3(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download the JPEG file from URL: {url}")

        file_key = str(uuid.uuid4()) + ".jpeg"
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=response.content)

        url, expiration_time = generate_presigned_url(file_key)
        return url

    except ClientError as e:
        raise Exception(f"Error generating the presigned URL: {str(e)}")
    except Exception as e:
        raise Exception(
            f"Error processing image and generating presigned URL: {str(e)}"
        )


def generate_presigned_url(object_name):
    try:
        expiration_time = datetime.utcnow() + timedelta(seconds=expires_in)

        # Pre-signed URL 생성
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_name,
                # "ResponseContentType": "image/jpeg",
            },
            ExpiresIn=expires_in,
        )

        return response, expiration_time
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None, None
