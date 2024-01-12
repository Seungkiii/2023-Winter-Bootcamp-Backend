from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import Interview
#from .serializers import QuestionListSerializer
from users.models import User
from .serializers import InterviewSerializer
from .serializers import InterviewCreateSerializer
#from django.shortcuts import get_object_or_404

# class QuestionView(APIView):
#   def get(self, request, id):
#     try:
#       interview = Interview.objects.get(id=id)
#       serializer = QuestionListSerializer(interview)
      
#       return Response(serializer.data)
    
#     except ObjectDoesNotExist:
#             return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
    


# class InterviewList(APIView):
 
#     def get(self, request,user_id):
#         interviews = Interview.objects.filter(user_id=user_id)
#         serializer = InterviewSerializer(interviews, many=True)
#         return Response(serializer.data)

#     def post(self, request,user_id):
#         serializer = InterviewCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#---------------------------------------------
class InterviewList(APIView):
 
    def get(self, request):
        interviews = Interview.objects.all()
        serializer = InterviewSerializer(interviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InterviewCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    
     
