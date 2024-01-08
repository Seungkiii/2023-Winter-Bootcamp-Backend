from rest_framework import serializers
from .models import Interview_Type, Question

class InterviewTypeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Interview_Type
    fields = ['type_name']

class QuestionSerializer(serializers.ModelSerializer):
  class Meta:
    model = Question
    fields = ['content']