# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    SignUpSerializer,
    EmailOrUsernameTokenObtainPairSerializer,  # ✅ 여기로 변경
    MeSerializer,
)


class SignUpView(APIView):
    """
    ✅ POST /api/accounts/signup/
    body: { "email": "...", "username": "...", "password": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "success": True,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "provider": user.provider,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmailLoginView(TokenObtainPairView):
    """
    ✅ POST /api/accounts/login/
    body: { "email": "...", "password": "..." }  또는 { "username": "...", "password": "..." }
    응답: { "access": "...", "refresh": "...", "user": {...} }
    """
    permission_classes = [AllowAny]
    serializer_class = EmailOrUsernameTokenObtainPairSerializer  # ✅ 여기로 변경


class MeView(APIView):
    """
    ✅ GET /api/accounts/me/
    header: Authorization: Bearer <access>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)