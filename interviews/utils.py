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
        repositories = Repository.objects.filter(interview_id=interview.id)
        
        # Interview에서 username을 가져옴
        user = interview.user
        username = user.username

        # 각 Repository에서 파일 내용을 가져옴
        repo_content = []
        for repo in repositories:
          repo_name = repo.repo_name
          repo_content = get_github_file_content(username, repo_name)

        position = interview.position

        previous_question = Question.objects.filter(interview_id=interview.id).order_by('-id').first()
        previous_answer = Answer.objects.filter(question_id=previous_question.id).first()

        questions = []

        # prompt = f"""
        #         You are an interviewer for a company and you are interviewing a developer.
        #         The {resume_contents} are the contents of the interviewee's resume.
        #         Your task is to write 1 Korean {question_type} type question of 200 characters or less related to {repo_name}, {repo_content}, {position} based on the interviewer's resume or referred to the previous question:{previous_question.content} and its answer:{previous_answer.content} to create a question with a tail between its legs
        #         Keep your questions directed at the candidate, and avoid describing yourself, such as what you think or how you feel.
        #         Also, if you create a tail question, make it clear what part of the previous answer you're referring to.
        #         Your questions should be written in the same tone and natural sentence structure as the interviewer would use in real life. Be creative and varied when writing your questions.
        #         """

        # 프롬프트 생성
        for question_type in question_types:

           if question_type == "project":
               prompt = f"As a developer interviewer, you need to think from a project perspective. Your task is to create one question in Korean of {question_type} type within 200 characters. The content of the question should be based on your analysis of the {repo_content} and {resume_contents} and should be relevant to the {position}. You can also create a follow-up question referring to the previous question: {previous_question.content} and its answer: {previous_answer.content}, but make sure to specify which part of the previous answer you are referring to. Your question should be specific and creative.Don't explain what you are"
           elif question_type == "cs":
               prompt = f"You are participating as the company's CS expert and interviewer and should think from a ComputerScience perspective.Your task is to create one Korean question of {question_type} type with 200 characters or less. The content of your question should include your analysis of the {repo_content} and {resume_contents} and your consideration of the {position}. You can also create a tail question by referring to the previous question: {previous_question.content} and its answer: {previous_answer.content}, but make sure to specify which part of the previous answer you are referring to.The question you create should be specific and creative"
           elif question_type == "personality":
               prompt = f"You're participating as both the company's HR representative and the interviewer, so think of it from that perspective.Your task is to create one Korean question of {question_type} type with 200 characters or less. The content of your question should include your analysis of the {repo_content} and {resume_contents} and your consideration of the {position}. You can also create a tail question by referring to the previous question: {previous_question.content} and its answer: {previous_answer.content}, but make sure to specify which part of the previous answer you are referring to.The question you create should be specific and creative"

           response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=0,
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
