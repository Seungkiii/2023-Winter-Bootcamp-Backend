from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import Interview
from .serializers import QuestionListSerializer

class QuestionView(APIView):
  def get(self, request, id):
    try:
      interview = Interview.objects.get(id=id)
      serializer = QuestionListSerializer(interview)
      
      return Response(serializer.data)
    
    except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)