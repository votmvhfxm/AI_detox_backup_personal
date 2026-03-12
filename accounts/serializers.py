# accounts/serializers.py

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """
    ✅ 회원가입 Serializer
    POST /api/accounts/signup/
    body: { "email": "...", "username": "...", "password": "..." }
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "username", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")

        # ✅ provider 기본값(local) 넣기 (User 모델에 provider가 있을 때만)
        if hasattr(User, "provider"):
            validated_data["provider"] = "local"

        user = User(**validated_data)
        user.set_password(password)  # ✅ 비밀번호 해시 저장
        user.is_active = True
        user.save()
        return user


class MeSerializer(serializers.ModelSerializer):
    """
    ✅ 내 정보 조회 Serializer
    GET /api/accounts/me/
    """

    class Meta:
        model = User
        fields = ("id", "email", "username", "provider")


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    ✅ 로그인 입력으로 email 또는 username 둘 다 허용하는 JWT 발급 Serializer
    - email/password만 보내도 됨
    - username/password만 보내도 됨
    """

    email = serializers.EmailField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ TokenObtainPairSerializer가 기본으로 username_field를 필수로 잡는 경우가 있어서
        # 여기서 required=False로 강제로 풀어준다
        username_field = User.USERNAME_FIELD  # 보통 "username"
        if username_field in self.fields:
            self.fields[username_field].required = False
            self.fields[username_field].allow_blank = True

        if "password" in self.fields:
            self.fields["password"].required = True

    def validate(self, attrs):
        password = attrs.get("password")

        email = attrs.get("email")
        username = attrs.get("username") or attrs.get(User.USERNAME_FIELD)

        if not password:
            raise serializers.ValidationError("password는 필수입니다.")

        # ✅ email만 온 경우 → email로 유저 찾아서 username으로 인증
        if email and not username:
            try:
                user = User.objects.get(email=email)
                username = getattr(user, User.USERNAME_FIELD)
            except User.DoesNotExist:
                raise serializers.ValidationError("해당 이메일의 사용자가 없습니다.")

        if not username:
            raise serializers.ValidationError("email 또는 username 중 하나는 필수입니다.")

        user = authenticate(**{User.USERNAME_FIELD: username, "password": password})

        if user is None:
            raise serializers.ValidationError("이메일/아이디 또는 비밀번호가 올바르지 않습니다.")

        if not user.is_active:
            raise serializers.ValidationError("비활성화된 사용자입니다.")

        refresh = self.get_token(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": getattr(user, "username", ""),
                "provider": getattr(user, "provider", ""),
            },
        }
        return data

class FirebaseLinkSerializer(serializers.Serializer):
    """
    ✅ Firebase 계정 연결용 Serializer
    - local로 로그인한 사용자가 Firebase id_token을 제출하면 연결하는 데 사용
    """
    id_token = serializers.CharField()