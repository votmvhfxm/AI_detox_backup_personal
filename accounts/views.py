# accounts/views.py
# - /api/accounts/me/ 엔드포인트를 위한 뷰

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import MeSerializer

class MeView(APIView):
    """로그인(인증)된 사용자의 기본 정보를 반환하는 뷰"""
    permission_classes = [IsAuthenticated]  # JWT 토큰이 있어야 접근 가능

    def get(self, request):
        # request.user 에는 JWT 토큰으로 인증된 User 객체가 들어있음
        return Response(MeSerializer(request.user).data)
