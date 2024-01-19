import boto3
from uuid import uuid4
from botocore.exceptions import NoCredentialsError
import openai
from rest_framework.response import Response
from openai import OpenAI
import os
import time
import interviews
from interviews.models import QuestionType, Question, Interview, Repository, Answer
from resumes.models import Resume
import requests

def get_github_file_content(username, repo_name):
    url = f"https://api.github.com/search/code?q=filename:package.json+OR+filename:build.gradle+repo:{username}/{repo_name}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get('items', [])
        if items:
            file_url = items[0].get('url')
            file_response = requests.get(file_url)
            if file_response.status_code == 200:
                download_url = file_response.json().get('download_url')
                download_response = requests.get(download_url)
                print(download_response)
                return download_response
    return None

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

def create_questions_withgpt(interview, type_names):
    try:
        # Resume 테이블에서 resume_id에 해당하는 레코드를 가져옵니다.
        resume = Resume.objects.get(id=interview.resume_id)
        # 이력서의 text_contents를 가져옵니다.
        resume_contents = resume.text_contents
        # GPT 함수에 resume_contents를 전달합니다.
        question_types = [qt.value for qt in QuestionType if qt.value in type_names]
        # Repository 테이블에서 interview_id에 해당하는 레코드를 가져옵니다.
        repository = Repository.objects.get(interview_id=interview.id)

        # Repository 객체에서 repo_name을 가져옵니다.
        repo_name = repository.repo_name
        position = interview.position
        repo_info = "AI Interview"

        previous_question = Question.objects.filter(interview_id=interview.id).order_by('-id').first()
        previous_answer = Answer.objects.filter(question_id=previous_question.id).first()
        all_questions = Question.objects.filter(interview_id=interview)
        questions = []

        previous_question_type = previous_question.question_type
        # 현재 질문타입 꺼내기
        question_type = question_types[0]
        # 전 질문타입과 같다면 꼬리질문 가능
        if (previous_question_type in question_types or previous_question_type=="common"):
            # 질문 타입에 맞게 프롬프트 생성
            if question_type == "project":
                prompt = \
                    f"""As a developer interviewer, you need to think from a project perspective and evaluate the candidate's knowledge, roles, experience, learning and problem-solving skills on projects they have worked on previously.Your task is to create a question of the type {question_type} in Korean within 200 characters.
                     The content of the question should be based on your analysis of the {repo_info} and {resume_contents} and should be relevant to the {position}.You can also create follow-up questions that deepen and apply the previous question: {previous_question.content} and its answer: {previous_answer.content}.
                     Specify which part of the previous answer or analysed repository you are referring to. The question you create should be specific and creative"""
            elif question_type == "cs":
                prompt = f"""You are participating as the company's CS expert and interviewer and should think from a ComputerScience perspective.Your task is to create one Korean question of {question_type} type with 200 characters or less.
                The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}. You can also create a tail question by referring to the previous question: {previous_question.content} and its answer: {previous_answer.content}.
                but make sure to specify which part of the previous answer you are referring to.The question you create should be specific and creative"""
            elif question_type == "personality":
                prompt = f"""You're participating as both the company's HR representative and the interviewer, so think of it from that perspective.Your task is to create one Korean question of {question_type} type with 200 characters or less.
                The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}. You can also create a tail question by referring to the previous question: {previous_question.content} and its answer: {previous_answer.content}.
                but make sure to specify which part of the previous answer you are referring to.The question you create should be specific and creative"""

        else:
            # 질문 타입에 맞게 프롬프트 생성
            # 전 질문타임과 다르다면 꼬리질문 불가능
            if question_type == "project":
                prompt = f"As a developer interviewer, you need to think from a project perspective. Your task is to create one question in Korean of {question_type} type within 200 characters. The content of the question should be based on your analysis of the {repo_info} and {resume_contents} and should be relevant to the {position}. Your question should be specific and creative.Don't explain what you are"
            elif question_type == "cs":
                prompt = f"You are participating as the company's CS expert and interviewer and should think from a ComputerScience perspective.Your task is to create one Korean question of {question_type} type with 200 characters or less. The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}.The question you create should be specific and creative. Don't explain what you are"
            elif question_type == "personality":
                prompt = f"You're participating as both the company's HR representative and the interviewer, so think of it from that perspective.Your task is to create one Korean question of {question_type} type with 200 characters or less. The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}.The question you create should be specific and creative. Don't explain what you are"


        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.8,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },

            ]
        )
        questions.append((response.choices[0].message.content.strip(), question_type))


    except Exception as e:
        return Response("Failed to create questions with GPT: " + str(e))
    return questions



def save_question(questions, interview):
    for question, question_type in questions:
        Question.objects.create(content=question, question_type=question_type, interview=interview)
