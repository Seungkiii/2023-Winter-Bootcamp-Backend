import boto3
from uuid import uuid4
from botocore.exceptions import NoCredentialsError
import openai
from openai import OpenAI
import os
from interviews.models import QuestionType, Question
from resumes.models import Resume


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


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def create_questions_withgpt(repo_name, type_name, position, resume_id):
    # Resume 테이블에서 resume_id에 해당하는 레코드를 가져옵니다.
    resume = Resume.objects.get(id=resume_id)
    # 이력서의 text_contents를 가져옵니다.
    resume_contents = resume.text_contents
    # GPT 함수에 resume_contents를 전달합니다.
    question_types = [qt.value for qt in QuestionType if qt.value in type_name]
    questions = []



    for question_type in question_types:
        prompt = f"You are an interviewer at a company and are interviewing a developer. {resume_contents} is the contents of the interviewer's resume. Your task is to create only one question in Korean, not exceeding 200 characters, and {question_type} related to {type_name} and {position} based on the interviewer's resume. Any questions you make must be translated into Korean."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=1,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },

            ]
        )


        questions.append((response.choices[0].message.content.strip(), question_type))

    return questions




def save_question(questions, interview):
    for question, question_type in questions:
        Question.objects.create(content=question, question_type=question_type, interview=interview)
