from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Question, Type_Choice
from .serializers import InterviewTypeSerializer, QuestionSerializer

class QuestionView(APIView):
  def get(self, request, id):
    try:
      question = Question.objects.get(id=id)
      interview = question.interview
      type_choice = Type_Choice.objects.get(interview=interview)
      interview_type = type_choice.interview_type
      
      question_serializer = QuestionSerializer(question)
      interview_type_serializer = InterviewTypeSerializer(interview_type)
      
      return Response({
        'type_name': interview_type_serializer.data['type_name'],
        'content': question_serializer.data['content']
      })
    except Question.DoesNotExist:
      return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
    except Type_Choice.DoesNotExist:
      return Response({'error': 'Interview Type not found'}, status=status.HTTP_404_NOT_FOUND)