# wellness/serializers.py
# - 위 모델들을 API 응답/요청에 사용하기 위한 직렬화기

from rest_framework import serializers
from .models import EmotionLog, UserSettings

class EmotionLogSerializer(serializers.ModelSerializer):
    """감정 로그를 조회할 때 사용할 Serializer"""
    class Meta:
        model = EmotionLog
        fields = ("id", "emotion", "text_original", "created_at")

class UserSettingsSerializer(serializers.ModelSerializer):
    """사용자 설정 조회/수정용 Serializer"""
    class Meta:
        model = UserSettings
        fields = ("target_daily_usage_min", "stress_sensitivity", "onboarding_completed")
