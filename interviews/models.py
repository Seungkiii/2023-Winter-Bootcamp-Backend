from django.db import models
from common.models import BaseModel
# Create your models here.

class Interview(BaseModel):
    
    id = models.AutoField(primary_key=True)
    #user_id = models.ForeignKey('YourUserModel', on_delete=models.CASCADE)
    resume_id=models.IntegerField(default=1)
    title = models.CharField(max_length=255)
    style=models.CharField(max_length=255)
    
    STYLE_CHOICES = [
         ('Video', 'Video Interview'),
        ('Voice', 'Voice Interview'),
       ('Text', 'Text Interview'),
    ]
    
    style = models.CharField(max_length=10, choices=STYLE_CHOICES)
    
    POSITION_CHOICES = [
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
         ('fullstack', 'FUllstack'),
    ]
    
    position = models.CharField(max_length=10, choices=POSITION_CHOICES)



# from django.db import models

# class Interview(models.Model):
#     # 1. pk로 면접ID가 int값으로 들어감
#     id = models.AutoField(primary_key=True)

#     # 2. 외래키로 사용자 ID가 int값으로 들어간다.
#     user_id = models.ForeignKey('YourUserModel', on_delete=models.CASCADE)

#     # 3. 외래키로 이력서ID가 int로 들어가고
#     resume_id = models.ForeignKey('YourResumeModel', on_delete=models.CASCADE) --->Int형 필드로 설정

#     # 4. 면접제목이 varchar(255)로 들어가고
#     title = models.CharField(max_length=255)

#     # 5. 면접방식이 ENUM으로 들어가고
#     INTERVIEW_METHOD_CHOICES = [
#         ('Video', 'Video Interview'),
#         ('Voice', 'Voice Interview'),
#         ('Text', 'Text Interview'),
#     ]
#     interview_method = models.CharField(max_length=10, choices=INTERVIEW_METHOD_CHOICES)

#     # 6. 포지션이 ENUM으로 들어가고
#     POSITION_CHOICES = [
#         ('frontend', 'Frontend'),
#         ('backend', 'Backend'),
#         ('fullstack', 'FUllstack'),
#     ]
#     position = models.CharField(max_length=10, choices=POSITION_CHOICES)

#     # 7. 생성일자가 DateTime으로 들어가고
#     created_at = models.DateTimeField(auto_now_add=True)

#     # 8. 수정일자가 DateTime으로 들어가고
#     updated_at = models.DateTimeField(auto_now=True)

#     # 9. 삭제여부가 Boolean으로 들어간다.
#     is_deleted = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.interview_id} - {self.interview_title}"
    
