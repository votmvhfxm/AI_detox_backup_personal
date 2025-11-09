# wellness/views.py
# - 감정 메시지 입력 → 분류 → 저장 → 목표 조정 → 코칭 응답
# - 사용자 설정 조회/수정 API

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import EmotionLog, UserSettings
from .serializers import EmotionLogSerializer, UserSettingsSerializer
from .chatbot import classify_emotion, coaching_for
from .logic_goal import adjust_target_minutes

class EmotionMessageView(APIView):
    """
    POST /api/wellness/chatbot/message/
    Body: {"message": "오늘 너무 무기력하고 아무 것도 하기 싫어"}
    1) 규칙 기반으로 감정 분류(모호하면 TODO: 모델 분류)
    2) EmotionLog 저장
    3) UserSettings 읽어 목표치 조정 후 저장
    4) 감정/코칭문구/조정된 목표치를 응답
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get("message", "") or ""

        # 1) 규칙 기반 분류
        emotion = classify_emotion(text)

        # 2) 모호하면 추후 모델 분류(Fallback)로 확장 가능
        if emotion is None:
            # TODO: 모델(LLM/감정분류모델) 호출 후 emotion 결정
            emotion = "안정"  # 임시 기본값

        # 3) 감정 로그 저장
        EmotionLog.objects.create(
            user=request.user,
            emotion=emotion,
            text_original=text
        )

        # 4) 사용자 설정 가져오고 목표치 조정
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        new_target = adjust_target_minutes(
            settings_obj.target_daily_usage_min,
            emotion,
            settings_obj.stress_sensitivity
        )
        if new_target != settings_obj.target_daily_usage_min:
            settings_obj.target_daily_usage_min = new_target
            settings_obj.save(update_fields=["target_daily_usage_min"])

        # 5) 코칭 문구 생성
        msg = coaching_for(emotion)

        return Response({
            "emotion": emotion,
            "coachingMessage": msg,
            "newTargetDailyUsage": settings_obj.target_daily_usage_min,
        })

class UserSettingsView(APIView):
    """
    GET  /api/wellness/settings/   → 사용자 설정 조회
    PATCH /api/wellness/settings/  → 설정 일부 수정
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        return Response(UserSettingsSerializer(settings_obj).data)

    def patch(self, request):
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        ser = UserSettingsSerializer(settings_obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
