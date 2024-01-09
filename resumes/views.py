from django.core.files.storage import default_storage
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Resume
from .serializers import ResumeSerializer
from PyPDF2 import PdfReader
import logging

import io

#파일 업로드 처리 뷰
class ResumeCreate(generics.CreateAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

    def create(self, request, *args, **kwargs):
        # file = None
        # for key, value in request.FILES.items():
        #     if hasattr(value, 'read'):
        #         file = value
        #         break
        #
        # if not file:
        #     return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        pdf = PdfReader(file)
        text_contents = ""
        for page in pdf.pages:
            text_contents += page.extract_text()

        #파일을 S3에 업로드하고 URL을 가져옵니다.
        file_name = default_storage.save('pdfs/' + file.name, file)
        image_url = default_storage.url(file_name)

        data = {
            'text_contents': text_contents,
            'image_url': image_url,
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


#이력서 삭제하는 뷰
class ResumeDelete(generics.UpdateAPIView):  # DestroyAPIView 대신 UpdateAPIView를 사용합니다.
    queryset = Resume.objects.all()
    lookup_field = 'id'

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