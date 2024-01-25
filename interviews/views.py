import json
import tempfile
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from django.core.exceptions import ObjectDoesNotExist
from .models import Answer, Interview, Question
from .serializers import QuestionListSerializer, AnswerCreateSerializer, InterviewResultSerializer, \
    InterviewListSerializer, InterviewCreateSerializer, QuestionCreateSerializer
from openai import OpenAI
from .utils import handle_uploaded_file_s3
import boto3
from botocore.exceptions import NoCredentialsError
from celery_worker.tasks import process_interview
from celery.result import AsyncResult

from dotenv import load_dotenv
import os

load_dotenv()

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
  
# 프롬프팅
system_prompt = "Your task is to correct any spelling discrepancies in the transcribed Korean text. It's about an interview with a development company."

# GPT를 이용해 텍스트를 후처리해주는 함수
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

# 면접 질문 목록 조회 API
class QuestionView(APIView):
  def get(self, request, id):
    try:
      interview = Interview.objects.get(id=id)
      serializer = QuestionListSerializer(interview)
      
      return Response(serializer.data)
    
    except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)

# 면접 답변 등록 API
class AnswerCreateView(APIView):
    def post(self, request, *args, **kwargs):
        # serializer = AnswerCreateSerializer(data=request.data)
        # if serializer.is_valid():
        #   # 파일 객체 가져오기
        #   record_file = request.FILES.get('record_url')
          
        #   # 음성 파일 url 변환
        #   record_url, file_key = handle_uploaded_file_s3(record_file)
        #   record_binary = binary(file_key)
          
        #   temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        #   temp_file_path = temp_file.name
          
        #   # 임시 음성 파일 생성
        #   with open(temp_file_path, "wb") as file:
        #     file.write(record_binary)
                
        #   with open(temp_file_path, "rb") as temp_file:
        #     # Whisper API로 텍스트 변환
        #     if temp_file:
        #       # 음성 파일을 text로 변환
        #       transcript = generate_corrected_transcript(0, system_prompt, temp_file)
        #       content = transcript
        #       print(content)
            
        #       serializer.save(content=content, record_url=record_url)
        #       answer = serializer.save(content=content, record_url=record_url)
        #       return Response(status=status.HTTP_200_OK)
        #     else:
        #       return Response({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        #   return Response(serializer.errors, status=400)
        
        serializer = AnswerCreateSerializer(data=request.data)
        if serializer.is_valid():
            record_file = request.FILES.get('record_url')

            if record_file is None:
                return Response({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

            with open(temp_file_path, "wb") as file:
                for chunk in record_file.chunks():
                    file.write(chunk)

            request.data['record_url'] = None

            task = process_interview.delay(request.data, temp_file_path, True)

            return Response({"task_id": task.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterviewProcessView(APIView):
    def post(self, request, interview_id, question_id, *args, **kwargs):
        request.data['question'] = question_id
        request.data['interview'] = interview_id
        serializer = AnswerCreateSerializer(data=request.data)
        if serializer.is_valid():
            is_last = request.data.get('is_last', False)

            record_file = request.FILES.get('record_url')

            if record_file is None:
                return Response({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

            with open(temp_file_path, "wb") as file:
                for chunk in record_file.chunks():
                    file.write(chunk)

            request.data['record_url'] = None

            task = process_interview.delay(request.data, temp_file_path, is_last)

            return Response({"task_id": task.id, "wait_time": 4}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskResultView(APIView):
    def get(self, request, task_id):
        user_id = request.user.id
        print("user_id", user_id)

        task = AsyncResult(task_id)

        total_delay = 4
        num_checks = 2  # check 2 per 1s
        delay = total_delay / num_checks

        for _ in range(num_checks):
            task_done = task.ready()
            if task_done:
                result = task.get()

                if result is not None:
                    # keyword = result["keyword"]
                    pass
                else:
                    return Response(
                        "bing_api error", status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                response_data = task.get()

                return Response(response_data, status=status.HTTP_200_OK)

            # await asyncio.sleep(delay)

        return Response(
            status=status.HTTP_202_ACCEPTED,
        )  # status code 수정

#질문 생성 API
class QuestionCreateView(APIView):
  def post(self, request, id, *args, **kwargs):
    data = request.data
    data['interview'] = id  # interview_id를 request.data에 추가
    serializer = QuestionCreateSerializer(data=data)
    if serializer.is_valid():
      created_questions = serializer.save()
      for question in created_questions:
        serializer = QuestionCreateSerializer(question)  # 개별 객체를 직렬화
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 면접 결과 조회 API
class InterviewResultView(APIView):
  def get(self, request, id):
    try:
      interview = Interview.objects.get(id=id)
      serializer = InterviewResultSerializer(interview)
        
      return Response(serializer.data)
    
    except ObjectDoesNotExist:
      return Response({'error': 'object not found'}, status=status.HTTP_404_NOT_FOUND)
    
# 면접 목록 조회 API
class InterviewListView(APIView):
  def get(self, request):
    user_id = request.user.id
    
    # user의 모든 interview를 조회
    interviews = Interview.objects.filter(user=user_id)
    
    # question이 있고 question과 answer의 개수가 일치하는 interview만 filter
    valid_interviews = []
    for interview in interviews:
        questions = Question.objects.filter(interview=interview)
        if not questions.exists():
            interview.is_deleted = True  # 질문이 없으면 is_deleted를 true로 설정
            interview.save()
            continue
        
        # 모든 question에 대한 answer이 있는지 확인
        all_answered = all(Answer.objects.filter(question=question).exists() for question in questions)
        if all_answered:    # 모든 question에 대한 answer이 있는 경우
            valid_interviews.append(interview)
        else:
            interview.is_deleted = True  # 모든 질문에 대한 답변이 없으면 is_deleted를 true로 설정
            interview.save()
    
    serializer = InterviewListSerializer(valid_interviews, many=True)
      
    return Response(serializer.data)

# 면접 생성 API
class InterviewCreateView(APIView):
    def post(self, request):
        serializer = InterviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
