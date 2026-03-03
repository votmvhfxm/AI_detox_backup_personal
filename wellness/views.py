# wellness/views.py

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

class ChatbotAPIView(APIView):
    """
    [POST] /api/wellness/chat/
    - 앱에서 보낸 메시지를 받아 AI '디토'의 답변을 반환
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data if request.data else {}

            user_text = data.get("message", "")
            usage_data = data.get("usage_data", None)

            logger.info(f"📩 [요청 수신] 메시지: {user_text} / 데이터: {usage_data}")

            if not user_text or str(user_text).strip() == "":
                return Response(
                    {"success": False, "error": "내용을 입력해주세요.", "code": "EMPTY_MESSAGE"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # ✅ 여기서 import (서버 부팅 시점에 import하다가 터지는 문제 방지)
            from .chatbot import AICoach

            coach = AICoach()
            reply = coach.generate_response(user_text, usage_data)

            logger.info(f"📤 [응답 발송] 디토: {reply[:20]}...")

            return Response(
                {
                    "success": True,
                    "response": reply,
                    "persona": "Ditto (Forest Guardian)",
                    "emotion_analysis": "Complete",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"🚨 [서버 에러 발생]: {str(e)}")
            return Response(
                {"success": False, "error": "서버 내부에서 오류가 발생했습니다.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
