from django.db import models
from common.models import BaseModel

class User(BaseModel):
  login_id = models.IntegerField(null=False)