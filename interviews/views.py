from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, views
from django.core.exceptions import ObjectDoesNotExist
from .models import Interview
from .serializers import QuestionListSerializer
from .serializers import AnswerCreateSerializer
from .models import Question

class QuestionView(APIView):
  def get(self, request, id):
    try:
      interview = Interview.objects.get(id=id)
      serializer = QuestionListSerializer(interview)
      
      return Response(serializer.data)
    
    except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)



class AnswerCreateView(views.APIView):
    def post(self, request, *args, **kwargs):
        serializer = AnswerCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)

