from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import Interview
from .serializers import QuestionListSerializer, AnswerCreateSerializer, InterviewResultSerializer, \
    InterviewListSerializer, InterviewCreateSerializer


# 면접 질문 목록 조회 API
class QuestionView(APIView):
  def get(self, request, id):
    try:
      interview = Interview.objects.get(id=id)
      serializer = QuestionListSerializer(interview)
      
      return Response(serializer.data)
    
    except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)

# 면접 답변 등록 API
class AnswerCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AnswerCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)

# 면접 결과 조회 API
class InterviewResultView(APIView):
  def get(self, request, id):
    try:
      interview = Interview.objects.get(id=id)
      serializer = InterviewResultSerializer(interview)
        
      return Response(serializer.data)
    
    except ObjectDoesNotExist:
      return Response({'error': 'object not found'}, status=status.HTTP_404_NOT_FOUND)
    
# 면접 목록 조회 API
class InterviewListView(APIView):
  def get(self, request):
    interviews = Interview.objects.all()
    serializer = InterviewListSerializer(interviews, many=True)
      
    return Response(serializer.data)


class InterviewCreateView(APIView):
    def post(self, request):
        serializer = InterviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)