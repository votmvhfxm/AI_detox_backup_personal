from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    사용자(User) 테이블
    - Django 기본 User 모델을 확장(Custom User Model)
    - email, username, provider 카카오/구글 소셜 로그인까지 고려
    """
    email = models.EmailField(unique=True)  # 사용자 이메일 (unique)
    auth_provider = models.CharField(
        max_length=50,
        default="local",
        help_text="로그인 제공자: local / kakao / google"
    )
    created_at = models.DateTimeField(auto_now_add=True)  # 가입일 자동 기록

    def __str__(self):
        return self.username # 사용자 이름 반환