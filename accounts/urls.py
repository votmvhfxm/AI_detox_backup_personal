# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import SignUpView, EmailLoginView, MeView

urlpatterns = [
    # ✅ 회원가입
    path("signup/", SignUpView.as_view(), name="signup"),

    # ✅ 로그인(JWT 발급)
    path("login/", EmailLoginView.as_view(), name="login"),

    # ✅ access 재발급(refresh)
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),

    # ✅ 내 정보
    path("me/", MeView.as_view(), name="me"),
]