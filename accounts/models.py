from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    ✅ 커스텀 유저 모델 (Phase 1: 이메일 + 소셜로그인 대비)
    - email: 이메일 로그인/가입용 (unique)
    - provider: 로그인 제공자 (local/google/kakao)
    - provider_uid: 소셜 제공자에서 주는 유저 고유 ID
    - avatar_url: 프로필 이미지 URL (선택)
    """

    # 이메일은 로그인/식별에 매우 중요하니 unique 권장
    email = models.EmailField(unique=True)

    # 로그인 제공자: local / google / kakao
    provider = models.CharField(
        max_length=20,
        default="local",
        help_text="로그인 제공자 (local/google/kakao)"
    )

    # 소셜 제공자에서 내려주는 유저 고유값 (sub, id 등)
    provider_uid = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="소셜 제공자 유저 고유 ID"
    )

    # 프로필 이미지 URL (선택)
    avatar_url = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username