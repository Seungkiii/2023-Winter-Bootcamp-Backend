
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Interview
from .serializers import InterviewSerializer


#from drf_yasg.utils import swagger_auto_schema


class InterviewList(APIView):
    
    def get(self,request):
        interviews = Interview.objects.all()
        serializer = InterviewSerializer(interviews, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_created)
        return Response(serializer.errors,tatus=status.HTTP_400_BAD_REQUEST)
        

