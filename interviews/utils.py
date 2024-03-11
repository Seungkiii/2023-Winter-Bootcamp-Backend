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

        # Repository 테이블에서 interview_id에 해당하는 레코드를 가져옵니다.
        repository = Repository.objects.filter(interview=interview.id)

        # Repository 객체에서 repo_name을 가져옵니다.
        repo_names=[]
        repo_infos=[]
        for repo in repository:
            repo_name = repo.repo_name
            repo_info = repo.repo_summary
            repo_names.append(repo_name)
            repo_infos.append(repo_info)

        previous_question = Question.objects.filter(interview=interview.id).order_by('-id').first()
        previous_answer = Answer.objects.filter(question=previous_question.id).first()

        position = interview.position

        questions = []

        previous_question_type = previous_question.question_type
        # 현재 질문타입 꺼내기


        if(previous_question_type == question_type):
            print("same")
            # 전 질문타입과 같다면 꼬리질문 가능
            if question_type == "project":
                #프로젝트 질문
                #prompt = f"As a developer interviewer, you need to think from a project perspective and evaluate the candidate's knowledge, roles, experience, learning and problem-solving skills in projects. Your task is to create project-type one interview new question in Korean with 200 characters or less. The content of the question should be based on your analysis of the {repo_info} and {resume_contents} and should be relevant to the {position}. You can also create tail questions(Tail questions are additional questions that build on the answers to previous questions) that deepen and apply previous answer: {previous_answer.content}. When constructing the content of a question, add references from the previous answers, repository, and resume to make it look like it is a question naturally.You have to ask me questions like you're talking to an interviewer in real life. Don't explain what you think"
                prompt = f"Your task is to role-play as a developer interviewer and ask a project-related interview question in Korean, within the limit of 200 characters that you haven't asked before. The question should be based on the {', '.join(repo_names)}:{', '.join(repo_infos)} and {resume_contents}, and should be relevant to the {position} to evaluate the candidate's technical skills, problem solving skills, learning skills, etc. You can create new contents of question or tail questions that deepen and apply previous answer: {previous_answer.content}. The tail questions should be unique and not repeat previous questions. They should explore different aspects of the candidate's experience, skills, and understanding of the project. Questions should be direct and natural. It should sound like a real person is asking the question but refrain from including greetings or personal sentiments, intention, emotion. do not say anything outside of the question and use the word '지원자분' instead of name. The output should not include any additional information or counters such as the character count of the question"
            elif question_type == "cs":
                #cs질문
                # prompt = f"You are role-playing as the company's CS expert and interviewer. Your task is to ask '지원자분' a natural and flowing question in Korean with 200 characters or less, based on the information from {repo_info}, {resume_contents}, and {position}. The question should be related to computer science topics. The question should be unique and not repeat previous questions. You can also create tail questions that deepen and apply previous answer: {previous_answer.content}. The question should propose a specific problem or situation that tests the candidate's problem-solving skills and understanding of the topic. The question should be direct and natural, referencing the candidate's repository and previous answer, resume. Your question should be direct and natural, seamlessly incorporating references to the candidate's repository and resume. It should sound like a real person is asking the question. Do not exceed 50 characters for the reference information. Avoid explicitly stating that you are creating a question. Avoid explicitly stating that you are creating a question. Also, don't include any additional suggestions or recommendations."
                prompt = f"Your task is to role-play as a company's CS expert and interviewer. Ask a natural and flowing question in Korean, within the limit of 200 characters that you haven't asked before. The question should be based on the {position}, and should be related to computer science topics such as Data Structures and Algorithms,Operating Systems,Networks,Databases,System Design,Software Engineering,Specific Technology Stacks. You can create new contents of question or tail questions that deepen and apply previous answer: {previous_answer.content}. The question should propose a specific problem or situation that tests the candidate's problem-solving skills and understanding of the topic. Questions should be direct and natural. It should sound like a real person is asking the question but refrain from including greetings or personal sentiments, intention, emotion. do not say anything outside of the question and use the word '지원자분' instead of name. The output should not include any additional information or counters such as the character count of the question"
            else:
                #인성질문
                #prompt = f"You're participating as both the company's HR representative and the interviewer. Your task to ask '지원자분' one interview question of person's character, humanity type in Korean with 200 characters or less. The content of your question should include your analysis of the {repo_info} and {resume_contents} and your consideration of the {position}. Your question should propose a specific and challenging situation that tests the candidate's problem-solving skills and character. You can also create tail questions(Tail questions are additional questions that build on the answers to previous questions) that deepen and apply previous answer: {previous_answer.content}. When constructing the content of a question, add references from the previous answers, repository, and resume to make it look like it is a question naturally. Don't explain the process of you creating a question."
                #prompt = f"You're participating as both the company's HR representative and the interviewer. Your task is to ask one interview question that proposes a specific and extreme situation in Korean within the limit of 200 characters. This situation should be something that could realistically occur within the {position} role, and it should test the candidate's teamwork skills, problem-solving abilities, and character under stress. The content of your question should be based on your analysis of the {', '.join(repo_names)}:{', '.join(repo_infos)} and {resume_contents}.You can create new contents of question or tail questions that deepen and apply previous answer: {previous_answer.content}. Questions should be direct and natural. It should sound like a real person is asking the question but refrain from including greetings or personal sentiments, intention, emotion. do not say anything outside of the question and use the word '지원자분' instead of name. The output should not include any additional information or counters such as the character count of the question"
                prompt = f"You're participating as both the company's HR representative and the interviewer. Your task is to ask one interview question that suggests a specific and extreme situation in Korean within 200 characters that you haven't asked before. This situation should be something that could realistically occur within the {position} role, and it should test the candidate's teamwork skills, problem-solving abilities, and character under stress. You can create new contents of question or tail questions that deepen and apply previous answer: {previous_answer.content}. The tail questions should be unique and not repeat previous questions. Questions should be direct and natural. It should sound like a real person is asking the question but refrain from including greetings or personal sentiments, intention, emotion. Do not say anything outside of the question and refer to the candidate as '지원자분' instead of using their name. The output should not include any additional information or counters or {previous_answer.content} such as the character count of the question."
        else:
            # 전 질문타임과 다르거나 두번째 질문이라면 꼬리질문 불가능
            print("different")
            if question_type == "project":
                # 프로젝트 질문
                #prompt = f"Your task is to role-play as a developer interviewer and ask a project-related interview question in Korean, with 200 characters or less. The question should be based on the {', '.join(repo_names)}:{', '.join(repo_infos)} and {resume_contents}, and should be relevant to the {position}. Your question should be direct and natural, seamlessly incorporating references to the candidate's repository and resume. It should sound like a real person is asking the question. Do not exceed 50 characters for the reference information. do not say anything outside of the question and use the word '지원자분' instead of name. Do not put formulas or descriptions such as 'Interviewer:' and 'Question:' before questions. Separate '지원자분이' from '지원자분은' and use it in context"
                #prompt = f"Your task is to role-play as a developer interviewer and ask a project-related interview question in Korean, within the limit of 200 characters. The question should be based on the {', '.join(repo_names)}:{', '.join(repo_infos)} and {resume_contents}, and should be relevant to the {position} to evaluate the candidate's technical skills, learning skills, etc..It should sound like a real person is asking the question but refrain from including greetings or personal sentiments, intention, emotion. do not say anything outside of the question and use the word '지원자분' instead of name. The output should not include any additional information or counters such as the character count of the question"
                #prompt = f"You, as the interviewee, are tasked to play the role of a developer interviewer. Formulate a project-related interview question in Korean, within the limit of 200 characters. Your question should be based on the project {', '.join(repo_names)} : {', '.join(repo_infos)} and relevant to the {position}. Make sure your questions are direct and natural, starting with references to the candidate's repository and resume. It should sound like a real person is asking, not exceeding 50 characters for the reference information. Use the term 'applicant' instead of a specific name. Do not include formulas or descriptions such as 'Interviewer:' and 'Question:' before the questions. Separate 'applicant has' from 'applicant is' and use it in context. Your question must not contain any content outside of these specifications."
                prompt = f"Your task is to role-play as a developer interviewer and analyze the applicant's submissions {', '.join(repo_names)}:{', '.join(repo_infos)}', and {resume_contents} to provide Korean interview questions in 200 characters or less for projects that fit the applicant's {position}. The questions should be questions that can evaluate the applicant's skills, learning abilities, etc... Also, do not say anything other than a question and use the word 'applicant' instead of your name. Do not include any character counts or additional information counters in the output."
            elif question_type == "cs":
                # cs질문
                #prompt = f"You are role-playing as the company's CS expert and interviewer. Your task is to ask '지원자분' a natural and flowing question in Korean with 200 characters or less, based on the information from {repo_info}, {resume_contents}, and {position}. The question should be related to computer science topics such as data structures, algorithms, complexity analysis, computer architecture, software development methodologies, and more. It should sound like a real person is asking the question. Don't explain the process of you creating a question and exceed 50 characters for the reference information. Avoid explicitly stating that you are creating a question. Avoid explicitly stating that you are creating a question. Also, don't include any additional suggestions or recommendations."
                #prompt = f"Your task is to role-play as a company's CS expert and interviewer. Ask a natural and flowing question in Korean, within the limit of 200 characters. The question should be based on the {', '.join(repo_names)}:{', '.join(repo_infos)}, {resume_contents}, and {position}, and should be related to computer science topics such as Data Structures and Algorithms,Operating Systems,Networks,Databases,System Design,Software Engineering,Specific Technology Stacks. Questions should be direct and natural. The question should sound like a real person is asking but refrain from including greetings or personal sentiments, intention, emotion. do not say anything outside of the question and use the word '지원자분' instead of name. The output should not include any additional information or counters such as the character count of the question"
                prompt = f"You are a developer with a lot of CS knowledge and are currently interviewing for developers to work with you. Please ask only one cs question in Korean related to {position}. Do not mention or refer to anything other than a question"
            
            else:
                # 인성질문
                #prompt = f"You're participating as both the company's HR representative and the interviewer. Your task is to ask one interview question of person's character type in Korean within the limit of 200 characters. The content of your question should include your analysis of the {', '.join(repo_names)}:{', '.join(repo_infos)} and {resume_contents} and your consideration of the {position}. Your question should propose a specific and extreme situation that tests the candidate's teamwork skills, values, and character, situational coping ability. Questions should be direct and natural. It should sound like a real person is asking the question but refrain from including greetings or personal sentiments, intention, emotion. do not say anything outside of the question and use the word '지원자분' instead of name. The output should not include any additional information or counters such as the character count of the question"
                #prompt = f"You're participating as both the company's HR representative and the interviewer. Your task is to ask one interview question that proposes a specific and extreme situation in Korean within the limit of 200 characters. This situation should be something that could realistically occur within the {position} role, and it should test the candidate's teamwork skills, problem-solving abilities, and character under stress. The content of your question should be based on your analysis of the {', '.join(repo_names)}:{', '.join(repo_infos)} and {resume_contents}. Questions should be direct and natural. It should sound like a real person is asking the question but refrain from including greetings or personal sentiments, intention, emotion. Do not say anything outside of the question and refer to the candidate as '지원자분' instead of using their name. The output should not include any additional information or counters such as the character count of the question."
                prompt = f"You're participating as both the company's HR representative and the interviewer. Your task is to ask one interview question that proposes a specific and extreme situation in Korean within the limit of 200 characters. This situation should be something that could realistically occur within the {position}. Questions should be direct and natural. It should sound like a real person is asking the question but refrain from including greetings or personal sentiments, intention, emotion. Do not say anything outside of the question and refer to the candidate as '지원자분' instead of using their name. The output should not include any additional information or counters such as the character count of the question."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            frequency_penalty=1,
            presence_penalty=-1,
            max_tokens=400,
            n=1,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"I want you to ask me a developer interview question. Instead, do not tell your thoughts, intentions, greetings, and conditions to me. Ask a different question from {previous_question}. do not tell me the number of characters"
                }

            ]
        )
        questions.append((response.choices[0].message.content.strip(), question_type))


    except Exception as e:
        return Response("Failed to create questions with GPT: " + str(e))
    return questions



def save_question(questions, interview):
    for question, question_type in questions:
        Question.objects.create(content=question, question_type=question_type, interview=interview)