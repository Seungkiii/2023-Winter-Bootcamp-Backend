import boto3
from uuid import uuid4
from botocore.exceptions import NoCredentialsError
import openai

from interviews.models import QuestionType, Question


def handle_uploaded_file_s3(file):

    s3_client = boto3.client('s3')
    bucket_name = 'resume7946'  # 여기에 실제 버킷 이름을 넣어주세요.
    file_key = 'answer_audio/' + str(uuid4()) + '.mp3'  # mp3로 저장되면 mp3로 바꾸기

    try:
        s3_client.upload_fileobj(file, bucket_name, file_key)
        file_url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{file_key}"

        return file_url, file_key
    except NoCredentialsError:
        return {"error": "S3 credential is missing"}




openai.api_key = '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'


def create_questions_withgpt(repo_name, type_name, position):
    question_types = [QuestionType.PROJECT.value, QuestionType.CS.value, QuestionType.PERSONALITY.value]
    questions = []

    for question_type in question_types:
        prompt = f"{repo_name}에 대한 {type_name}, {position} 관련 {question_type} 질문은 무엇인가요?"

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            temperature=0.5,
            max_tokens=60
        )

        questions.append((response.choices[0].text.strip(), question_type))

    return questions


def save_question(questions, interview):
    for question, question_type in questions:
        Question.objects.create(content=question, question_type=question_type, interview=interview)
