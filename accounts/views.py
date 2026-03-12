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
    FirebaseLinkSerializer,
)

from firebase_admin import auth as firebase_auth
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

# ✅ Firebase sign_in_provider → 우리 DB provider 값으로 표준화하는 함수
def map_firebase_provider(sign_in_provider: str) -> str:
    """
    Firebase 토큰(decoded)에 들어있는 sign_in_provider 값을
    우리 서비스에서 쓰기 좋은 provider 문자열로 통일합니다.

    Firebase 예시값:
    - "password"   : Firebase Email/Password 로그인
    - "google.com" : Google 로그인
    - (카카오 OIDC 연동 시) "oidc.kakao" 같은 형태가 될 수 있음
    - 그 외 "custom", "anonymous" 등도 가능

    우리 DB에 저장할 표준값(추천):
    - local
    - google
    - kakao
    - firebase_password
    - firebase (기타)
    """
    if not sign_in_provider:
        return "firebase"

    p = sign_in_provider.lower()

    # 1) Firebase 이메일/비번 로그인
    if p == "password":
        return "firebase_password"

    # 2) 구글 로그인
    if p == "google.com":
        return "google"

    # 3) 카카오 로그인(연동 방식에 따라 문자열이 달라질 수 있어 넉넉히 처리)
    #    - 예: "oidc.kakao", "kakao", "kakao.com" 등
    if "kakao" in p:
        return "kakao"

    # 4) 그 외는 firebase로 묶기
    return "firebase"


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

User = get_user_model()

class FirebaseLoginView(APIView):
    """
    ✅ POST /api/accounts/firebase/login/
    body: { "id_token": "FIREBASE_ID_TOKEN" }

    - Flutter가 Firebase Auth 로그인 성공 후 받은 idToken을 보냄
    - 백엔드는 Firebase Admin으로 검증
    - provider/provider_uid로 User 생성/조회
    - 우리 서비스 JWT(SimpleJWT) 발급
    """
    permission_classes = [AllowAny]

    def post(self, request):
        id_token = request.data.get("id_token")
        if not id_token:
            return Response({"detail": "id_token이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded = firebase_auth.verify_id_token(id_token)
            firebase_uid = decoded.get("uid")
            email = decoded.get("email", "") or ""
            name = decoded.get("name", "") or ""
            picture = decoded.get("picture", "") or ""

            # 어떤 소셜로 로그인했는지 (google.com / password / custom / etc)
            sign_in_provider = (decoded.get("firebase") or {}).get("sign_in_provider", "firebase")

        except Exception as e:
            return Response({"detail": f"Firebase 토큰 검증 실패: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ (안전장치) uid가 없으면 사용자 식별이 불가능하므로 실패 처리
        if not firebase_uid:
            return Response({"detail": "Firebase 토큰에 uid가 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)

        # ✅ DB에 저장할 provider는 표준화해서 저장
        provider = map_firebase_provider(sign_in_provider)
        # ✅ provider_uid는 Firebase uid로 고정 (Firebase 기준 고유 식별자)
        provider_uid = firebase_uid

        # ✅ (안전장치) Firebase 계정은 이메일이 없을 수도 있음(특히 카카오/동의 설정)
        # User.email이 unique라면 빈 문자열로 저장하면 문제 생길 수 있어 임시 이메일을 만들어 둠
        if not email:
            email = f"{provider}_{provider_uid}@no-email.local"

        # 1) provider_uid로 먼저 찾기 (가장 정확)
        user = User.objects.filter(provider=provider, provider_uid=provider_uid).first()

        # 2) 없으면 email로 “계정 연결” 정책
        if user is None and email:
            existing = User.objects.filter(email=email).first()
            if existing:
                # 정책 A(추천): local 계정이 있으면 "연결할지" 따로 처리하거나 일단 막기
                # 여기서는 안전하게 "막기"로 해둘게 (혼선 방지)
                if getattr(existing, "provider", "") in ["", "local"]:
                    return Response(
                        {"detail": "동일 이메일의 local 계정이 이미 존재합니다. 계정 연결 정책이 필요합니다."},
                        status=status.HTTP_409_CONFLICT,
                    )
                # 이미 다른 provider 계정이면 그대로 사용
                user = existing

                # ✅ 기존 계정이라면 provider/provider_uid를 최신 로그인 정보로 정리
                user.provider = provider
                user.provider_uid = provider_uid

                # ✅ User 모델에 avatar_url 필드가 있을 때만 picture 저장 (이미 값이 없을 때만 채움)
                if hasattr(User, "avatar_url") and picture and not getattr(user, "avatar_url", ""):
                    user.avatar_url = picture

                user.save()

        # 3) 그래도 없으면 새로 생성
        if user is None:
            # username 자동 생성 (중복 피하기)
            base_username = (email.split("@")[0] if email else f"user_{provider_uid[:8]}")
            username = base_username
            i = 1
            while User.objects.filter(username=username).exists():
                i += 1
                username = f"{base_username}{i}"

            create_kwargs = {
                "email": email,
                "username": username,
                "provider": provider,
                "provider_uid": provider_uid,
                "is_active": True,
            }

            # ✅ User 모델에 avatar_url 필드가 있을 때만 picture 저장
            if hasattr(User, "avatar_url") and picture:
                create_kwargs["avatar_url"] = picture

            user = User.objects.create(**create_kwargs)

        # ✅ JWT 발급
        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": getattr(user, "username", ""),
                "provider": getattr(user, "provider", ""),
            }
        }
        return Response(data, status=status.HTTP_200_OK)


class FirebaseLinkView(APIView):
    """
    ✅ POST /api/accounts/firebase/link/
    - local로 로그인된 사용자가 자신의 계정을 Firebase 계정과 "연결"하는 API

    요청:
      header: Authorization: Bearer <local access>
      body: { "id_token": "<FIREBASE_ID_TOKEN>" }

    동작:
    1) Firebase id_token 검증
    2) provider/provider_uid 추출 + provider 표준화
    3) 이 provider/provider_uid가 다른 사용자에게 이미 연결되어 있으면 막기(409)
    4) 현재 로그인된 사용자(request.user)에 provider/provider_uid를 저장 (= 연결)
    5) (선택) 새 JWT 발급해서 반환 (권장: 바로 갱신해서 쓰기 편하게)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FirebaseLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token = serializer.validated_data["id_token"]

        # ✅ 1) Firebase 토큰 검증
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            firebase_uid = decoded.get("uid")
            email = decoded.get("email", "") or ""
            picture = decoded.get("picture", "") or ""

            sign_in_provider = (decoded.get("firebase") or {}).get("sign_in_provider", "firebase")

        except Exception as e:
            return Response(
                {"detail": f"Firebase 토큰 검증 실패: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not firebase_uid:
            return Response(
                {"detail": "Firebase 토큰에 uid가 없습니다."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ✅ 2) provider 표준화 + provider_uid 결정
        provider = map_firebase_provider(sign_in_provider)
        provider_uid = firebase_uid

        # ✅ 3) (중요) 이 Firebase 계정이 이미 다른 사용자에 연결되어 있으면 막기
        conflict_user = User.objects.filter(provider=provider, provider_uid=provider_uid).exclude(id=request.user.id).first()
        if conflict_user:
            return Response(
                {"detail": "이 Firebase 계정은 이미 다른 사용자에 연결되어 있습니다."},
                status=status.HTTP_409_CONFLICT
            )

        # ✅ 4) (선택) Firebase email과 local email이 다르면 막을지 여부
        # 초보자/안전 기준: 다르면 막는 게 안전
        if email and request.user.email and (email.lower() != request.user.email.lower()):
            return Response(
                {
                    "detail": "Firebase 이메일과 현재 로그인된 이메일이 다릅니다. "
                              "다른 계정에 연결할 수 없습니다."
                },
                status=status.HTTP_409_CONFLICT
            )

        # ✅ 5) 연결 수행: 현재 사용자에 provider/provider_uid 저장
        request.user.provider = provider
        request.user.provider_uid = provider_uid

        # ✅ avatar_url 필드가 있으면 저장(없으면 무시)
        if hasattr(User, "avatar_url") and picture:
            request.user.avatar_url = picture

        request.user.save()

        # ✅ 6) 연결 후 새 JWT 발급(권장)
        refresh = RefreshToken.for_user(request.user)
        return Response(
            {
                "success": True,
                "message": "Firebase 계정 연결 완료",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": request.user.id,
                    "email": request.user.email,
                    "username": getattr(request.user, "username", ""),
                    "provider": getattr(request.user, "provider", ""),
                    "provider_uid": getattr(request.user, "provider_uid", ""),
                },
            },
            status=status.HTTP_200_OK
        )





class MeView(APIView):
    """
    ✅ GET /api/accounts/me/
    header: Authorization: Bearer <access>
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)