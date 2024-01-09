from rest_framework import serializers
from .models import Interview

class InterviewSerializer(serializers.ModelSerializer):

    model=Interview
    fields =['id','user_id','title','style','position']
