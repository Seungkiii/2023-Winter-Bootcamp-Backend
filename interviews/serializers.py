# from rest_framework import serializers
# #from .models import Interview_Type, Question, Interview, Type_Choice
# from .models import Interview, Repository
# from users.models import User


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

# from rest_framework import serializers
# from .models import Interview, Type_Choice, Interview_Type, Repository

# class InterviewSerializer(serializers.ModelSerializer):
#     type_name = serializers.ListField(child=serializers.CharField(max_length=20))
#     repo_name = serializers.ListField(child=serializers.CharField(max_length=255))
#     class Meta:
#         model = Interview
#         fields = ['title', 'style', 'position', 'resume', 'type_name', 'repo_name']
#     def create(self, validated_data):
#         type_names = validated_data.pop('type_name')
#         repo_names = validated_data.pop('repo_name')
#         interview = Interview.objects.create(**validated_data)
#         for type_name in type_names:
#             type_obj, created = Interview_Type.objects.get_or_create(type_name=type_name)
#             Type_Choice.objects.create(interview=interview, interview_type=type_obj)
#         for repo_name in repo_names:
#             Repository.objects.create(interview=interview, repo_name=repo_name)
#         return interview


#---------------------------------------------------------------------------------------
from rest_framework import serializers
from .models import Interview_Type, Interview, Repository,Type_Choice

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['resume', 'title', 'style', 'position']

class InterviewTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview_Type
        fields = ['type_name']

class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = ['repo_name']

# class CombinedSerializer(serializers.Serializer):
#     interview = InterviewSerializer(many=True)
#     interview_types = InterviewTypeSerializer(many=True)
#     repositories = RepositorySerializer(many=True)

#     def create(self, validated_data):
#         interview_data = validated_data.pop('interview')
#         interview_types_data = validated_data.pop('interview_types')
#         repositories_data = validated_data.pop('repositories')

#         # Interview 인스턴스 생성
#         interview_instance = Interview.objects.create(**interview_data)

#         # Interview_Type 인스턴스들 생성
#         interview_type_instances = [Interview_Type.objects.create(**type_data) for type_data in interview_types_data]

#         # Repository 인스턴스들 생성
#         repository_instances = [Repository.objects.create(**repo_data) for repo_data in repositories_data]

#         # Interview_Type 인스턴스들을 Interview에 연결
#         for interview_type_instance in interview_type_instances:
#             Type_Choice.objects.create(interview=interview_instance, interview_type=interview_type_instance)

#         # Repository 인스턴스들을 Interview에 연결
#         for repository_instance in repository_instances:
#             Repository.objects.create(interview=interview_instance, **repository_instance)

#         return interview_instance
#---------------------------첫번쨰
# class CombinedSerializer(serializers.Serializer):
#     interview = InterviewSerializer(many=True)
#     interview_types = InterviewTypeSerializer(many=True)
#     repositories = RepositorySerializer(many=True)

#     def create(self, validated_data):
#         interview_data_list = validated_data.pop('interview')
#         interview_types_data = validated_data.pop('interview_types')
#         repositories_data = validated_data.pop('repositories')

#         # Interview 인스턴스들 생성
#         interview_instances = []
#         for interview_data in interview_data_list:
#             interview_instance = Interview.objects.create(**interview_data)
#             interview_instances.append(interview_instance)

#         # Interview_Type 인스턴스들 생성 및 Type_Choice 연결
#         for interview_instance in interview_instances:
#             for type_data in interview_types_data:
#                 interview_type_instance = Interview_Type.objects.create(**type_data)
#                 Type_Choice.objects.create(interview=interview_instance, interview_type=interview_type_instance)

#         # Repository 인스턴스들 생성
#         for interview_instance, repo_data in zip(interview_instances, repositories_data):
#             Repository.objects.create(interview=interview_instance, **repo_data)

#         return interview_instances



# class CombinedSerializer(serializers.Serializer):
#     interview = InterviewSerializer(many=True)
#     interview_types = InterviewTypeSerializer(many=True)
#     repositories = RepositorySerializer(many=True)

#     def create(self, validated_data):
#         interview_data_list = validated_data.pop('interview')
#         interview_types_data = validated_data.pop('interview_types')
#         repositories_data = validated_data.pop('repositories')

#         # Interview 인스턴스들 생성
#         interview_instances = []
#         for interview_data in interview_data_list:
#             interview_instance = Interview.objects.create(**interview_data)
#             interview_instances.append(interview_instance)

#         # Interview_Type 인스턴스들 생성 및 Type_Choice 연결
#         for interview_instance in interview_instances:
#             for type_data in interview_types_data:
#                 interview_type_instance = Interview_Type.objects.create(**type_data)
#                 Type_Choice.objects.create(interview=interview_instance, interview_type=interview_type_instance)

#         # Repository 인스턴스들 생성
#         repository_instances = []
#         for interview_instance, repo_data in zip(interview_instances, repositories_data):
#             repository_instance = Repository.objects.create(interview=interview_instance, **repo_data)
#             repository_instances.append(repository_instance)

#         return interview_instances, repository_instances




class CombinedSerializer(serializers.Serializer):
    interview = InterviewSerializer(many=True)
    interview_types = InterviewTypeSerializer(many=True)
    repositories = RepositorySerializer(many=True)

    def create(self, validated_data):
        print("Validated Data:", validated_data)#1

        interview_data_list = validated_data.pop('interview')
        interview_types_data = validated_data.pop('interview_types')
        repositories_data = validated_data.pop('repositories')

        # Interview 인스턴스들 생성
        interview_instances = []
        for interview_data in interview_data_list:
            interview_instance = Interview.objects.create(**interview_data)
            interview_instances.append(interview_instance)

        # Interview_Type 인스턴스들 생성 및 Type_Choice 연결
        for interview_instance in interview_instances:
            for type_data in interview_types_data:
                interview_type_instance = Interview_Type.objects.create(**type_data)
                Type_Choice.objects.create(interview=interview_instance, interview_type=interview_type_instance)

        # Repository 인스턴스들 생성
        repository_instances = []
        for repo_data in repositories_data:
            repository_instance, created = Repository.objects.get_or_create(interview=interview_instance, **repo_data)
            repository_instances.append(repository_instance)
        print("Interview Instance:", interview_instance)
        return interview_instances, repository_instances        
