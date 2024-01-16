import boto3
from uuid import uuid4
from botocore.exceptions import NoCredentialsError
import openai
from openai import OpenAI
import os
import time
import interviews
from interviews.models import QuestionType, Question, Interview, Repository, Answer
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

def create_questions_withgpt(interview, type_names):

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

    previous_question = Question.objects.filter(interview_id=interview.id).order_by('-id').first()
    previous_answer = Answer.objects.filter(question_id=previous_question.id).first()

    questions = []


    #
    # for question_type in question_types:
    #     # prompt = f"You are an interviewer at a company and are interviewing a developer. {resume_contents} is the contents of the interviewer's resume. Your task is to create only one question in Korean, not exceeding 200 characters, and {question_type} related to {type_names}, {repo_name} and {position} based on the interviewer's resume. Any questions you make must be translated into Korean."
    #     prompt = f"Say hello "
    #     response = client.chat.completions.create(
    #         model="gpt-3.5-turbo",
    #         temperature=1,
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": prompt
    #             },
    #
    #         ]
    #     )
    #     print(response)
    #
    #     questions.append((response.choices[0].message.content.strip(), question_type))
    #
    # return questions

    prompt = f"You are an interviewer for a company and you are interviewing a developer. The {resume_contents} is the content of the interviewer's resume. Your task is to write 1 Korean question of 200 characters or less and {question_types} related to {', '.join(type_names)}, {repo_name}, {position} based on the interviewer's resume. You can also refer to the previous question:{previous_question.content} and previous answer:{previous_answer.content} to create a tail-to-tail question or a different question from the previous one. Questions must be translated into Korean."

    #프롬프트 생성
     #prompt = f"Do not explain yourself and do not take more than 100 characters to summarize.  Summarize {previous_question.content} and {previous_answer.content}"
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
    questions.append((response.choices[0].message.content.strip(), "project"))

    return questions

    # # 어시스턴트 생성
    # assistant = client.beta.assistants.create(
    #     name="면접관",
    #     instructions="면접관과 개발자의 면접을 진행할 때, 개발자의 이력서를 기반으로 면접 질문을 생성합니다. 질문은 한글로 작성되며, 200자 이내로 제한됩니다.",
    #     model="gpt-4-1106-preview",
    #     tools=[{"type": "retrieval"}]
    # )
    #
    # # 스레드 생성
    # interview_thread = client.beta.threads.create()
    #
    # # 스레드에 첫 번째 메시지 추가
    # message = client.beta.threads.messages.create(
    #     thread_id=interview_thread.id,
    #     role="user",
    #     content="면접을 시작합니다."
    # )
    #
    # # Run이 완료되었는지 확인하는 함수 생성
    # def poll_run(run, thread):
    #     while run.status != "completed":
    #         run = client.beta.threads.runs.retrieve(
    #             thread_id=thread.id,
    #             run_id=run.id,
    #         )
    #         time.sleep(0.5)
    #     return run
    #
    # # Run을 초기화합니다.
    # run = client.beta.threads.runs.create(
    #     thread_id=interview_thread.id,
    #     assistant_id=assistant.id,
    #     content="면접을 시작합니다."
    # )
    #
    # # 질문 유형 목록
    # question_types = ["기술", "경력", "성격"]
    #
    # # 질문 생성
    # for question_type in question_types:
    #     # prompt = f"You are an interviewer at a company and are interviewing a developer. {resume_contents} is the contents of the interviewer's resume. Your task is to create only one question in Korean, not exceeding 200 characters, and {question_type} related to {type_names}, {repo_name} and {position} based on the interviewer's resume. Any questions you make must be translated into Korean."
    #     prompt = f"면접관님, 개발자의 {question_type}에 대해 한 가지 질문을 드리겠습니다. {question_type}에 대한 질문은 다음과 같습니다."
    #     response = client.beta.threads.runs.create(
    #         thread_id=interview_thread.id,
    #         assistant_id=assistant.id,
    #         content=prompt,
    #     )
    #     run = poll_run(run, interview_thread)
    #
    #     questions.append((response.choices[0].message.content.strip(), question_type))
    #
    # # 질문 목록 반환
    # return questions


def save_question(questions, interview):
    for question, question_type in questions:
        Question.objects.create(content=question, question_type=question_type, interview=interview)
