from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from .models import Resume

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'image_url', 'created_at']

    def create(self, validated_data):
        # image_url이 validated_data에 포함되어 있음을 가정
        return Resume.objects.create(**validated_data)
