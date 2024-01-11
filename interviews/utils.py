import boto3
from uuid import uuid4
from botocore.exceptions import NoCredentialsError

def handle_uploaded_file_s3(file):

    s3_client = boto3.client('s3')
    bucket_name = 'resume7946'  # 여기에 실제 버킷 이름을 넣어주세요.
    file_key = 'answer_audio/' + str(uuid4()) + '.m4a'  # UUID를 사용하여 파일 키를 생성합니다.

    try:
        s3_client.upload_fileobj(file, bucket_name, file_key)
        file_url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{file_key}"

        return file_url
    except NoCredentialsError:
        return {"error": "S3 credential is missing"}