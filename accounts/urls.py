# accounts/urls.py
# JWT 토큰 발급 + 갱신 + 내 정보 조회 API 라우팅

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import MeView

urlpatterns = [
    # JWT 로그인 (username + password 입력 → 토큰 발급)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),

    # JWT access token 재발급 (refresh token 필요)
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # 로그인된 사용자 정보 조회 (Authorization: Bearer <token> 필요)
    path("me/", MeView.as_view(), name="me"),
]
