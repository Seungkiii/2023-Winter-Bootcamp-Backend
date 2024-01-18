from rest_framework import serializers
from .models import Interview_Type, Question, Interview, Type_Choice, Answer, Repository
from .utils import create_questions_withgpt, save_question


# 면접 결과 조회 Serializer
class InterviewResultSerializer(serializers.ModelSerializer):
  repo_names = serializers.SerializerMethodField()
  interview_type_names = serializers.SerializerMethodField()
  questions = serializers.SerializerMethodField()
  answers = serializers.SerializerMethodField()
  
  class Meta:
    model = Interview
    fields = ['title','interview_type_names', 'position', 'style', 'resume', 'repo_names', 'questions', 'answers']
  
  def get_repo_names(self, obj):
    repositories = Repository.objects.filter(interview=obj)
    return [repo.repo_name for repo in repositories]
  
  def get_interview_type_names(self, obj):
    type_choices = Type_Choice.objects.filter(interview=obj)
    if type_choices.exists():
      return [tc.interview_type.type_name for tc in type_choices]
    return []
  
  def get_questions(self, obj):
    questions_list_serializer = QuestionListSerializer(instance=obj)
    return questions_list_serializer.get_questions(obj)
  
  def get_answers(self, obj):
    questions = Question.objects.filter(interview=obj)
    answers = Answer.objects.filter(question__in=questions)
    return [{
      'content': answer.content,
      'record_url': answer.record_url
    } for answer in answers]
    
# 질문 목록 조회 Serializer
class QuestionListSerializer(serializers.ModelSerializer):
  questions = serializers.SerializerMethodField()
  
  class Meta:
    model = Interview
    fields = ['questions']
    
  def get_questions(self, obj):
    questions = Question.objects.filter(interview=obj)
    return [{
      'id': question.id,
      'type_name': self.get_type_name_for_question(question),
      'content': question.content
    } for question in questions]
  
  def get_type_name_for_question(self, question):
    return question.question_type

# 면접 답변 등록 Serializer
class AnswerCreateSerializer(serializers.ModelSerializer):
  record_url = serializers.FileField()  # FileField를 사용하여 파일 객체를 받습니다.

  class Meta:
    model = Answer
    fields = ['question', 'record_url']

  # def create(self, validated_data):
  #   record_file = validated_data.pop('record_url')

  #   # AWS S3를 사용하는 경우
  #   # record_url = handle_uploaded_file_s3(record_file)

  #   # record_url을 다시 설정
  #   validated_data['record_url'] = record_url

  #   return super().create(validated_data)
  # #Response에 변환된 url 보여주기
  # def to_representation(self, instance):
  #   ret = super().to_representation(instance)
  #   ret['record_url'] = instance.record_url  # 변환된 URL로 변경
  #   return ret
  
# 면접 목록 조회 Serializer
class InterviewListSerializer(serializers.ModelSerializer):
  
  
  class Meta:
    model = Interview
    fields = ['id', 'title']

# 면접 생성 Serializer
class InterviewCreateSerializer(serializers.ModelSerializer):
  repo_names = serializers.ListField(child=serializers.CharField(max_length=200), write_only=True)
  type_names = serializers.ListField(child=serializers.CharField(max_length=200), write_only=True)

  repo_names_display = serializers.SerializerMethodField()
  type_names_display = serializers.SerializerMethodField()
  
  resume = serializers.IntegerField(write_only=True)

  class Meta:
    model = Interview
    fields = ['id', 'user', 'title', 'position', 'style', 'resume', 'repo_names', 'type_names', 'repo_names_display',
              'type_names_display']

  def create(self, validated_data):
    repo_names = validated_data.pop('repo_names', None)
    type_names = validated_data.pop('type_names', None)
    resume_id = validated_data.pop('resume', None)

    interview = Interview.objects.create(resume_id=resume_id, **validated_data)

    if repo_names:
      for name in repo_names:
        Repository.objects.create(interview=interview, repo_name=name)

    if type_names:
      for name in type_names:
        type_obj, created = Interview_Type.objects.get_or_create(type_name=name)
        Type_Choice.objects.create(interview=interview, interview_type=type_obj)

    # repo_name, type_name, position 중 하나라도 없으면 질문을 생성하지 않습니다.
    # if repo_names and type_names and 'position' in validated_data and resume_id:
    #   for repo_name in repo_names:
    #     for type_name in type_names:
    #       questions = create_questions_withgpt(repo_name, type_name, validated_data['position'], resume_id)
    #       save_question(questions, interview)

    question="간단한 자기소개 부탁드립니다."
    Question.question_type="common"
    Question.objects.create(content=question, question_type=Question.question_type, interview=interview)

    return interview

  def create_interviews(self, validated_data):
    interview = Interview.objects.create(**validated_data)
    return interview

  def create_repo(self, repo_names, interview):
    for repo_name in repo_names:
      Repository.objects.create(repo_name=repo_name, interview=interview)

  def create_type_name(self, type_names, interview):
    for type_name in type_names:
        interview_type, created = Interview_Type.objects.get_or_create(type_name=type_name)
        type_choice, created = Type_Choice.objects.get_or_create(interview=interview, interview_type=interview_type)
        if not created:
            type_choice.interview = interview
            type_choice.save()


  def get_repo_names_display(self, obj):
    return [repo.repo_name for repo in obj.repository_set.all()]

  def get_type_names_display(self, obj):
    return [type_choice.interview_type.type_name for type_choice in obj.type_choice_set.all()]






#질문 생성
class QuestionCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # id 필드를 읽기 전용으로 설정
    interview = serializers.PrimaryKeyRelatedField(queryset=Interview.objects.all())

    class Meta():
        model = Question
        fields = ['id', 'interview']

    def create(self, validated_data):
        interview = validated_data['interview']

        # Interview 객체에서 type_names 가져오기
        type_names = [choice.interview_type.type_name for choice in Type_Choice.objects.filter(interview=interview)]
        print(type_names)
        questions = create_questions_withgpt(interview, type_names)

        # 생성된 Question 객체를 저장할 리스트
        created_questions = []

        for question, question_type in questions:
            question_obj = Question.objects.create(content=question, question_type=question_type, interview=interview)
            created_questions.append(question_obj)

        # 생성된 Question 객체들을 반환
        return created_questions