from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import Interview
#from .serializers import QuestionListSerializer

from .serializers import InterviewSerializer


# class QuestionView(APIView):
#   def get(self, request, id):
#     try:
#       interview = Interview.objects.get(id=id)
#       serializer = QuestionListSerializer(interview)
      
#       return Response(serializer.data)
    
#     except ObjectDoesNotExist:
#             return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
    


class InterviewList(APIView):
    def get(self, request):
        interviews = Interview.objects.all()
        serializer = InterviewSerializer(interviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InterviewDetail(APIView):
    def get(self, request, id):
        try:
            interviews = Interview.objects.get(id=id)
            serializer = InterviewSerializer(interviews)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'error': 'Interview not found'}, status=status.HTTP_404_NOT_FOUND)
    
     
