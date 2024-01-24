import os
import uuid
import redis
import boto3
import asyncio
import logging

from .celery import app

from uuid import uuid4
from openai import OpenAI
from django.core.files import File
from botocore.exceptions import NoCredentialsError
from interviews.utils import handle_uploaded_file_s3
from interviews.serializers import AnswerCreateSerializer, QuestionCreateSerializer

# from common.aws import AWSManager
# from api.api import upload_img_to_s3
# from api.imageGenAPI import ImageGenAPI

MAX_CONCURRENT_REQUESTS = 3

redis_client = redis.StrictRedis(host="redis", port=6379, db=2)

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

# # ## 아직 작업 중 시작
# def get_ImageCreator_Cookie():
#     try:
#         cookie = []
#         for i in range(2):
#             cookie_key = "cookie" + str(i + 1)
#             cookie.append(AWSManager.get_secret("BingImageCreator")[cookie_key])
#         return cookie
#     except Exception as e:
#         raise Exception("BingImageCreator API 키를 가져오는 데 실패했습니다.") from e


# auth_cookies = get_ImageCreator_Cookie()
# print("auth_cookies", *auth_cookies)
# # ## 아직 작업 중 끝

# app.conf.update({"worker_concurrency": MAX_CONCURRENT_REQUESTS * len(auth_cookies)})


# def get_round_robin_key():
#     cookie_index = redis_client.incr("cookie_index")
#     cookie_index %= len(auth_cookies)
#     return cookie_index, auth_cookies[cookie_index]


# async def create_image(key, auth_cookie, prompt):
#     while True:
#         current_requests = redis_client.incr(key)
#         if current_requests <= MAX_CONCURRENT_REQUESTS:
#             redis_client.delete(key + ":lock")  # 락 해제
#             print("get request approval " + str(current_requests))
#             print("delete lock " + key + ":lock")
#             break
#         else:
#             redis_client.decr(key)
#             await asyncio.sleep(1)

#     try:
#         image_generator = ImageGenAPI(auth_cookie)
#         result = await image_generator.get_images(prompt)
#         return result
#     except Exception as e:
#         raise e
#     finally:
#         redis_client.decr(key)

system_prompt = "Your task is to correct any spelling discrepancies in the transcribed Korean text. It's about an interview with a development company."

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def binary(key):
    s3_client = boto3.client('s3')
    bucket_name = 'resume7946'  # 여기에 실제 버킷 이름을 넣어주세요.

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        audio_file = response['Body'].read()

        return audio_file
    except NoCredentialsError:
        return {"error": "S3 credential is missing"}
     
# Whisper API로 오디오를 텍스트로 변환하는 메소드
def transcribe(audio_file):
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

    return transcript

def generate_corrected_transcript(temperature, system_prompt, audio_file):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": transcribe(audio_file)
            }
        ]
    )
    return response.choices[0].message.content

@app.task(bind=True)
def process_interview(self, data, temp_file_path, is_last):
    try:
        # logger.info(keywords)

        # loop = asyncio.get_event_loop()
        # result_url, _ = loop.run_until_complete(create_image(key, auth_cookie, prompt))

        # R-Rate Limit

        with open(temp_file_path, "rb") as temp_file:
            record_file = File(temp_file)
            data['record_url'] = record_file

            serializer = AnswerCreateSerializer(data=data)
            if serializer.is_valid():
                if temp_file:
                    # 음성 파일을 text로 변환
                    content = generate_corrected_transcript(0, system_prompt, temp_file)[:500]
                    record_file.seek(0)
                    record_url, _ = handle_uploaded_file_s3(record_file)

                    print(type(content), len(content))

                    answer = serializer.save(content=content, record_url=record_url)
                
                print("IS LAST", is_last)

                if is_last:
                    return {}
                
                question_serializer = QuestionCreateSerializer(data=data)
                if question_serializer.is_valid():
                    created_questions = question_serializer.save()
                    question_serializer = QuestionCreateSerializer(created_questions, many=True)
                    answer_serializer = AnswerCreateSerializer(answer)                        
                    return {
                        "answer": answer_serializer.data,
                        "question": question_serializer.data
                    }
                else:
                    raise ValueError(question_serializer.errors)
            else:
                raise ValueError(serializer.errors)
    except Exception as e:
        self.update_state(state="FAILURE")
        raise ValueError("Some condition is not met. " + str(e))
    finally:
        # if redis_client.get(key + ":lock") == lock_owner:
        #     redis_client.delete(key + ":lock")  # 락 해제
        #     print("delete lock " + key + ":lock " + lock_owner)
        
        os.remove(temp_file_path)

@app.task(bind=True)
def create_character(self, submit_id, keywords, duplicate=False):
    cookie_index, auth_cookie = get_round_robin_key()

    key = "concurrent_requests_" + str(cookie_index)

    lock_acquired = False

    try:
        lock_owner = str(uuid.uuid4())

        while not lock_acquired:
            lock_acquired = redis_client.setnx(key + ":lock", lock_owner)  # 락 설정
            if lock_acquired:
                redis_client.expire(key + ":lock", 16)  # 락의 자동 만료 설정
                print("get lock " + key + ":lock " + lock_owner)
                logger.info("get lock " + key + ":lock " + lock_owner)

        loop = asyncio.get_event_loop()
        result_url, _ = loop.run_until_complete(create_image(key, auth_cookie, prompt))

        if duplicate:
            result_url = upload_img_to_s3(result_url[0])

            submit = Submit.objects.get(id=submit_id)
            submit.result_url = result_url
            submit.save()

        return {"result_url": result_url, "submit_id": submit_id, "keyword": keywords}
    except Exception as e:
        self.update_state(state="FAILURE")

        raise ValueError("Some condition is not met. " + str(e))
    finally:
        if redis_client.get(key + ":lock") == lock_owner:
            redis_client.delete(key + ":lock")  # 락 해제
            print("delete lock " + key + ":lock " + lock_owner)
