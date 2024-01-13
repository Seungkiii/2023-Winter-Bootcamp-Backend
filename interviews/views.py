# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.exceptions import ObjectDoesNotExist
# from .models import Interview
# #from .serializers import QuestionListSerializer
# from users.models import User
# from .serializers import InterviewSerializer,InterviewCreateSerializer
# from .serializers import InterviewCreateSerializer
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

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# from .serializers import CombinedSerializer

# # class InterviewCreateView(APIView):
# #     def post(self, request, *args, **kwargs):
# #         serializer = CombinedSerializer(data=request.data)
# #         if serializer.is_valid():
# #             interview_instance = serializer.save()
# #             return Response({"interview_id": interview_instance.id}, status=status.HTTP_201_CREATED)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class InterviewCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = CombinedSerializer(data=request.data)
#         if serializer.is_valid():
#             interview_instance = serializer.save()
#             # interview_id를 클라이언트로 반환하지 않음
#             return Response({"message": "Interview created successfully."}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



     
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# from .serializers import CombinedSerializer

# class InterviewCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = CombinedSerializer(data=request.data)
#         if serializer.is_valid():
#             interview_instances = serializer.save()

#             # 생성된 Interview 객체들의 정보를 응답에 포함
#             interview_data = []
#             for interview_instance in interview_instances:
#                 interview_data.append({
#                     'id': interview_instance.id,
#                     'resume': interview_instance.resume,
#                     'title': interview_instance.title,
#                     'style': interview_instance.style,
#                     'position': interview_instance.position,
#                     'interview_types': [
#                         {'type_name': type_choice.interview_type.type_name}
#                         for type_choice in interview_instance.type_choice_set.all()
#                     ],
#                     'repositories': [
#                         {'repo_name': repository.repo_name}
#                         for repository in interview_instance.repository_set.all()
#                     ],
#                     # 추가 필요한 정보들을 포함
#                 })

#             return Response({"message": "Interviews created successfully.", "interviews": interview_data}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import CombinedSerializer

class InterviewCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CombinedSerializer(data=request.data)
        if serializer.is_valid():
            interview_instances, repository_instances = serializer.save()

            # 생성된 Interview 및 Repository 객체들의 정보를 응답에 포함
            interview_data = []
            for interview_instance, repository_instance in zip(interview_instances, repository_instances):
                interview_data.append({
                    'id': interview_instance.id,
                    'resume': interview_instance.resume,
                    'title': interview_instance.title,
                    'style': interview_instance.style,
                    'position': interview_instance.position,
                    'interview_types': [
                        {'type_name': type_choice.interview_type.type_name}
                        for type_choice in interview_instance.type_choice_set.all()
                    ],
                    'repositories': [
                        {'repo_name': repository_instance.repo_name}
                        
                    ],
                    # 추가 필요한 정보들을 포함
                })

            return Response({"message": "Interviews created successfully.", "interviews": interview_data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        