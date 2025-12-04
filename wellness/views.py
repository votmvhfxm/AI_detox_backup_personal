import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .chatbot import AICoach 

# [로깅 설정] 서버 콘솔에 에러를 빨간색으로 기록
logger = logging.getLogger(__name__)

class ChatbotAPIView(APIView):
    """
    [POST] /api/wellness/chat/
    - 기능: 앱(피그마)에서 보낸 메시지를 받아 AI '디토'의 답변을 반환합니다.
    - 입력 예시: { "message": "피곤해", "usage_data": {"most_used_app": "YouTube"} }
    """
    # 로그인 안 된 상태에서도 테스트 가능하게 허용 (나중에 IsAuthenticated로 변경 가능)
    permission_classes = [AllowAny] 

    def post(self, request):
        try:
            # 1. 데이터 수신 (안전하게 가져오기)
            # request.data가 비어있을 경우를 대비해 {} 처리
            data = request.data if request.data else {}
            
            user_text = data.get('message', '')
            usage_data = data.get('usage_data', None)

            # 로그 찍기 (누가 요청을 보냈는지 확인용)
            logger.info(f"📩 [요청 수신] 메시지: {user_text} / 데이터: {usage_data}")

            # 2. 유효성 검사 (빈 말은 거절)
            if not user_text or str(user_text).strip() == "":
                return Response(
                    {
                        "success": False,
                        "error": "내용을 입력해주세요.",
                        "code": "EMPTY_MESSAGE"
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3. AI '디토' 소환 및 답변 생성
            coach = AICoach()
            
        
            reply = coach.generate_response(user_text, usage_data)

           
            # 4. 성공 응답 반환
            
            logger.info(f"📤 [응답 발송] 디토: {reply[:20]}...") 
            
            return Response({
                "success": True,
                "response": reply,
                "persona": "Ditto (Forest Guardian)",
                "emotion_analysis": "Complete" 
            }, status=status.HTTP_200_OK)

        except Exception as e:
            
            # 5. 비상 사태 처리 
            # 에러 내용 콘솔 출력 

            logger.error(f"🚨 [서버 에러 발생]: {str(e)}")
            
            # 앱에는 잠시 후 다시 시도해달라는 메시지 전달
            return Response(
                {
                    "success": False,
                    "error": "서버 내부에서 오류가 발생했습니다.",
                    "detail": str(e) 
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )