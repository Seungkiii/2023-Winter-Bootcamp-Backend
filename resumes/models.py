from django.db import models
from common.models import BaseModel

class Resume(BaseModel):
    #id = models.AutoField(primary_key=True)  # 이력서 ID
    user_id = models.CharField(max_length=500)  # 사용자 ID
    image_url = models.URLField()  # 미리보기 이미지 URL
    text_contents = models.TextField()  # 텍스트 추출내용

    class Meta:
        db_table = 'resumes'
