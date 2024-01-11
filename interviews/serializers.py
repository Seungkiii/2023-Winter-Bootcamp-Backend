from rest_framework import serializers
#from .models import Interview_Type, Question, Interview, Type_Choice
from .models import Interview
from users.models import User
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


#----------------------------------------------------------
#질문 목록 조회 Serializer
# class QuestionListSerializer(serializers.ModelSerializer):
#   questions = serializers.SerializerMethodField()
  
#   class Meta:
#     model = Interview
#     fields = ['questions']
    
#   def get_questions(self, obj):
#     questions = Question.objects.filter(interview=obj)
#     return [{
#       'type_name': self.get_type_name_for_question(question),
#       'content': question.content
#     } for question in questions]
  
#   def get_type_name_for_question(self, question):
#     return question.question_type

#------------------------------------------------------------------


class InterviewCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model=Interview
    fields=['title', 'style', 'position', 'resume', 'repo_name']

class InterviewSerializer(serializers.ModelSerializer):
 
  class Meta:
    model=Interview
    fields=["id","title","created_at"]
    

