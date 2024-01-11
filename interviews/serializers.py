from rest_framework import serializers
from .models import Interview_Type, Question, Interview, Type_Choice, Answer
from .utils import handle_uploaded_file_s3


# 질문 목록 조회 Serializer
# class QuestionListSerializer(serializers.ModelSerializer):
#   type_name = serializers.SerializerMethodField()
#   content = serializers.SerializerMethodField()

#   class Meta:
#     model = Interview
#     fields = ['type_name', 'content']
    
#   def get_type_name(self, obj):
#     type_name = Type_Choice.objects.get(interview=obj)
#     return type_name.interview_type.type_name if type_name else None

#   def get_content(self, obj):
#     question = Question.objects.get(interview=obj)
#     return question.content if question else None

# 질문 목록 조회 Serializer
class QuestionListSerializer(serializers.ModelSerializer):
  questions = serializers.SerializerMethodField()
  
  class Meta:
    model = Interview
    fields = ['questions']
    
  def get_questions(self, obj):
    questions = Question.objects.filter(interview=obj)
    return [{
      'type_name': self.get_type_name_for_question(question),
      'content': question.content
    } for question in questions]
  
  def get_type_name_for_question(self, question):
    return question.question_type


class AnswerCreateSerializer(serializers.ModelSerializer):
  record_url = serializers.FileField()  # FileField를 사용하여 파일 객체를 받습니다.

  class Meta:
    model = Answer
    fields = ['question', 'record_url']

  def create(self, validated_data):
    record_file = validated_data.pop('record_url')

    # AWS S3를 사용하는 경우
    record_url = handle_uploaded_file_s3(record_file)

    # record_url을 다시 설정
    validated_data['record_url'] = record_url

    return super().create(validated_data)
  #Response에 변환된 url 보여주기
  def to_representation(self, instance):
    ret = super().to_representation(instance)
    ret['record_url'] = instance.record_url  # 변환된 URL로 변경
    return ret