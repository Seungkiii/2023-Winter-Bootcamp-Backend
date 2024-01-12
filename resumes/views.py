from django.core.files.storage import default_storage
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, serializers
from rest_framework.response import Response
from .models import Resume
from .serializers import ResumeSerializer
from PyPDF2 import PdfReader
import logging

import io


class ResumeCreate(generics.CreateAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    http_method_names = ['post']

    @swagger_auto_schema(operation_description="이력서를 생성하고 PDF 파일을 업로드합니다.",
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             properties={
                                 'file': openapi.Schema(type=openapi.TYPE_FILE, description='PDF file'),
                                 'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='User ID'),
                             }
                         ),
                         responses={201: openapi.Response('Created', ResumeSerializer)})
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        img_file = request.FILES.get('img_file')
        pdf_file = request.FILES.get('pdf_file')

        if not img_file or not user_id or not pdf_file or not title:
            return Response({'error': 'img file or user ID or pdf file or title not provided'}, status=status.HTTP_400_BAD_REQUEST)

        pdf = PdfReader(pdf_file)
        text_contents = ""
        for page in pdf.pages:
            text_contents += page.extract_text()

        # 파일을 S3에 업로드하고 URL을 가져옵니다.
        file_name = default_storage.save('imgs/' + img_file.name, img_file)
        image_url = default_storage.url(file_name)

        data = {
            'text_contents': text_contents,
            'pre_image_url': image_url,
            'user_id': user_id,
            'title':title
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


#이력서 리스트 보여주는 뷰
class ResumeList(generics.ListAPIView):
    queryset = Resume.objects.filter(is_deleted=False)  # is_deleted가 False인 객체만 가져옵니다.
    serializer_class = ResumeSerializer
    http_method_names = ['get']

    @swagger_auto_schema(operation_description="이력서 리스트를 반환합니다.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class EmptySerializer(serializers.Serializer):
    pass
#이력서 삭제 뷰
class ResumeDelete(generics.UpdateAPIView):
    queryset = Resume.objects.all()
    lookup_field = 'id'
    serializer_class = EmptySerializer
    http_method_names = ['delete']

    @swagger_auto_schema(operation_description="특정 이력서를 삭제합니다.")
    def delete(self, request, *args, **kwargs):
        resume = self.get_object()
        resume.is_deleted = True
        resume.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



# class ResumeCreate(generics.CreateAPIView):
#     queryset = Resume.objects.all()
#     serializer_class = ResumeSerializer

# class ResumeList(generics.ListAPIView):
#     queryset = Resume.objects.all()
#     serializer_class = ResumeSerializer

# class ResumeDelete(generics.DestroyAPIView):
#     queryset = Resume.objects.all()
#     lookup_field = 'id'  # URL에서 삭제할 Resume의 id를 가져옵니다.