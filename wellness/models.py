# wellness/models.py
from django.db import models
from accounts.models import User
from usage.models import AppCategory


class EmotionLog(models.Model):
    """
    감정 기록 테이블
    - 사용자 감정 분석 결과(라벨) 저장
    - source: 감정 분류 방식 (Rule-Based / LLM 등)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emotion_label = models.CharField(max_length=50)
    source = models.CharField(max_length=100, null=True, blank=True)
    log_text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.emotion_label}"


class DailySummary(models.Model):
    """
    하루 요약 데이터
    - AI 분석 용 핵심 데이터
    - unlock 횟수, 총 사용시간, 가장 많이 사용한 카테고리
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summary_date = models.DateField()
    total_usage_minutes = models.IntegerField()
    total_unlocks = models.IntegerField()
    most_used_category = models.ForeignKey(
        AppCategory, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        unique_together = ("user", "summary_date")  # 하루에 한 개만 생성

    def __str__(self):
        return f"{self.user.username} {self.summary_date} 요약"


class Challenge(models.Model):
    """
    챌린지(목표) 테이블
    - AI 또는 사용자가 설정한 행동 목표
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="ongoing")
    challenge_type = models.CharField(max_length=50)
    target_category = models.ForeignKey(AppCategory, null=True, on_delete=models.SET_NULL)
    target_app_name = models.CharField(max_length=255, null=True, blank=True)
    target_minutes = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AiCoachingLog(models.Model):
    """
    AI 코칭 내역 테이블
    - AI가 어떤 분석(insight)을 했고 어떤 조언을 했는지 저장
    - 사용자 반응(user_response)도 저장하여 나중에 개선 가능
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    insight_text = models.TextField(null=True, blank=True)
    suggestion_text = models.TextField()
    user_response = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Coaching for {self.user.username}"


class UserPreferences(models.Model):
    """
    사용자 개인 설정
    - 집중모드에서 차단할 앱 목록
    - AI 조언 스타일 (neutral / friendly / strict 등)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    focus_blocked_apps = models.TextField(null=True, blank=True)
    ai_coaching_style = models.CharField(max_length=50, default="neutral")

    def __str__(self):
        return f"{self.user.username} Preferences"
