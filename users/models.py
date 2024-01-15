from django.db import models
from common.models import BaseModel

class User(BaseModel):
  login_id = models.IntegerField(null=False)
  username = models.CharField(max_length=50)
  last_login = models.DateTimeField(null=True, blank=True)
  