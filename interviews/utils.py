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
        # question_types = [qt.value for qt in QuestionType if qt.value in type_names]
        question_type = type_names
        print(question_type)
        # Repository 테이블에서 interview_id에 해당하는 레코드를 가져옵니다.
        repository = Repository.objects.get(interview_id=interview.id)

        # Repository 객체에서 repo_name을 가져옵니다.
        repo_name = repository.repo_name
        position = interview.position
        repo_info = "This person has been involved in web development, primarily using Python and Django. They also have experience in designing REST APIs to handle communication between client and server. The code is cleanly written and has good test coverage, indicating high code quality. He is also an active contributor to the project with consistent commits and demonstrates effective project management skills through issue tracking."

        previous_question = Question.objects.filter(interview_id=interview.id).order_by('-id').first()
        previous_answer = Answer.objects.filter(question_id=previous_question.id).first()

        questions = []

        previous_question_type = previous_question.question_type
        # 현재 질문타입 꺼내기


        if(previous_question_type == question_type):
            print("same")
            # 전 질문타입과 같다면 꼬리질문 가능
            if question_type == "project":
                prompt = f"As a developer interviewer, you need to think from a project perspective and evaluate the candidate's knowledge, roles, experience, learning and problem-solving skills in projects. Your task is to create project-type one interview new question in Korean with 200 characters or less. The content of the question should be based on your analysis of the {repo_info} and {resume_contents} and should be relevant to the {position}. You can also create tail questions(Tail questions are additional questions that build on the answers to previous questions) that deepen and apply previous answer: {previous_answer.content}. When constructing the content of a question, add references from the previous answers, repository, and resume to make it look like it is a question naturally.You have to ask me questions like you're talking to an interviewer in real life. Don't explain what you think"

            elif question_type == "cs":
                prompt = f"You are participating as the company's CS expert and interviewer and should think from a ComputerScience perspective computer science, including topics such as data structures, algorithms, complexity analysis, computer architecture, software development methodologies, and more. Your task is to create one Korean question of computer science type with 200 characters or less.The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}.You can also create tail questions(Tail questions are additional questions that build on the answers to previous questions) that deepen and apply previous answer: {previous_answer.content}. When constructing the content of a question, add references from the previous answers, repository, and resume to make it look like it is a question naturally. You have to ask me questions like you're talking to an interviewer in real life.Don't explain what you think"

            elif question_type == "personality":
                prompt = f"You're participating as both the company's HR representative and the interviewer. So think of it from that perspective such as how the candidate would behave in certain situations and how they would adapt to the team and company culture. Your task is to create one Korean interview question of person's character, humanity type with 200 characters or less. The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}. You can also create tail questions(Tail questions are additional questions that build on the answers to previous questions) that deepen and apply previous answer: {previous_answer.content}. When constructing the content of a question, add references from the previous answers, repository, and resume to make it look like it is a question naturally.You have to ask me questions like you're talking to an interviewer in real life. Don't explain what you think"


        else:
            # 전 질문타임과 다르거나 두번째 질문이라면 꼬리질문 불가능
            print("different")
            if question_type == "project":
                prompt = f"As a developer interviewer, you need to think from a project perspective and evaluate the candidate's knowledge, roles, experience, learning and problem-solving skills in projects. Your main task is to talk to '지원자분' one interview question of project-type in Korean with 200 characters or less. The content of the question should be based on your analysis of the {repo_info} and {resume_contents} and should be relevant to the {position}. When constructing the content of a question, add references from the repository, and resume to make it look like it is a question naturally. You have to ask me questions like you're talking to an interviewer in real life. Don't explain the process of you creating a question"

            elif question_type == "cs":
                prompt = f"You are participating as the company's CS expert and interviewer and should think from a ComputerScience perspective computer science, including topics such as data structures, algorithms, complexity analysis, computer architecture, software development methodologies, and more. Your task is to create one Korean question of computer science type with 200 characters or less.The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}.When constructing the content of a question, add references from the repository, and resume to make it look like it is a question naturally.You have to ask me questions like you're talking to an interviewer in real life.Don't explain the process of you creating a question"

            elif question_type == "personality":
                prompt = f"You're participating as both the company's HR representative and the interviewer. So think of it from that perspective such as how the candidate would behave in certain situations and how they would adapt to the team and company culture. Your task is to create one interview question of person's character, humanity type in Korean with 200 characters or less. The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}.When constructing the content of a question, add references from the repository, and resume to make it look like it is a question naturally. You have to ask me questions like you're talking to an interviewer in real life. Don't explain the process of you creating a question"


        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.9,
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