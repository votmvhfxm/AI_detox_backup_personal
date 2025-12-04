# usage/models.py
from django.db import models
from accounts.models import User


class AppCategory(models.Model):
    """
    앱 카테고리 테이블
    ex) Social, Game, Productivity...
    """
    category_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category_name


class AppUsage(models.Model):
    """
    앱 사용 기록 테이블
    - 사용자가 어떤 앱을 언제 얼마나 사용했는지 기록
    - start_time ~ end_time 을 기반으로 사용시간 계산 가능
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app_name = models.CharField(max_length=255)
    category = models.ForeignKey(AppCategory, on_delete=models.SET_NULL, null=True)
    usage_type = models.CharField(
        max_length=50,
        default="foreground",
        help_text="앱 사용 방식 (foreground / background)"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    @property
    def usage_minutes(self):
        """start_time ~ end_time 차이를 분 단위로 계산한 필드"""
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def __str__(self):
        return f"{self.user.username} - {self.app_name}"
