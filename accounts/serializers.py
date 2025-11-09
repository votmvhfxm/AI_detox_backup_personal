from rest_framework import serializers
from .models import User

class MeSerializer(serializers.ModelSerializer):
    """현재 로그인한 사용자 정보를 내려주는 Serializer"""
    class Meta:
        model = User
        fields = ("id", "username", "email", "provider", "provider_uid", "avatar_url")
