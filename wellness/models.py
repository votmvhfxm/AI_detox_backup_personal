# wellness/models.py
# - 감정 기록(EmotionLog)과 사용자 설정(UserSettings) 테이블 정의

from django.db import models
from django.conf import settings

class UserSettings(models.Model):
    """
    사용자별 목표/설정 저장
    - target_daily_usage_min: 하루 목표 사용(제한) 시간(분)
    - stress_sensitivity: 감정에 따른 목표 조정 민감도 (가중치)
    - onboarding_completed: 온보딩 완료 여부
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    target_daily_usage_min = models.IntegerField(default=120)
    stress_sensitivity = models.FloatField(default=1.0)
    onboarding_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.user_id}] target={self.target_daily_usage_min}m"

class EmotionLog(models.Model):
    """
    사용자가 챗봇에 입력한 감정 문장을 분류해 저장
    - emotion: 분류된 감정 레이블(피로/무기력/우울/불안/안정/활력)
    - text_original: 원문 텍스트
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emotion = models.CharField(max_length=20)
    text_original = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.user_id}] {self.emotion}"
