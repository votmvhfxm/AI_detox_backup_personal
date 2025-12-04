import os
import google.generativeai as genai
from wellness.ai import analyze_emotion
from dotenv import load_dotenv

# 1. 환경 설정 및 보안 (Security)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 키가 제대로 로드되었는지 확인 (서버 실행 시 로그로 알려줌)
if not GEMINI_API_KEY:
    print("🚨 [에러].env 파일에서 GEMINI_API_KEY를 찾을 수 없어, AI 기능 작동 불가")
else:
    # 구글 API 연결 설정
    genai.configure(api_key=GEMINI_API_KEY)


# 2. AI 코치 클래스 (핵심 로직)

class AICoach:
    def __init__(self):
        # 만약 키가 없으면, 모델 생성하지 않고 종료 
        if not GEMINI_API_KEY:
            self.model = None
            return

        # 모델 설정 (Gemini 1.5 Flash 사용)
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=300,  # 답변 길이 제한 
            )
        )
        
        # AI 페르소나 정의
        self.persona = (
            "역할: 당신은 '디토'이라는 이름의 다정한 디지털 디톡스 AI 코치입니다.\n"
            "목표: 사용자의 감정을 위로하고, 스마트폰 사용을 줄여 현실의 즐거움을 찾도록 돕는 것입니다.\n"
            "말투: 존댓말을 사용하며 🌿, 📱, ✨, 🍵 같은 이모지를 적절히 섞어 따뜻하게 대화하세요.\n"
            "제약: 답변은 3~4문장 이내로 간결하게 작성하고, 구체적인 행동 하나를 추천해주세요."
        )

    def generate_response(self, user_text, usage_data=None):
        """
        [기능] 사용자 멘트와 앱 사용 기록을 종합하여 AI 조언을 생성합니다.
        """
        #  모델이 준비되지 않았을 때
        if not self.model:
            return "현재 AI 시스템 점검 중입니다. (관리자에게 문의하세요: API Key Missing) 🔧"

        # 1. 하이브리드 감정 분석 모델
        try:
            emotion_result = analyze_emotion(user_text)
            current_emotion = emotion_result.get('label', '알 수 없음')
        except Exception as e:
            print(f"⚠️ 감정 분석 중 에러 발생: {e}")
            current_emotion = "중립"

        # 2. 앱 사용 데이터 비어있을 경우 기본값 처리
        if not usage_data:
            usage_data = {"most_used_app": "스마트폰", "total_time": 0}
            
        most_used_app = usage_data.get('most_used_app', '스마트폰')
        
        # 3. 프롬프트 작성
        prompt = f"""
{self.persona}

[사용자 현재 상태]
- 사용자가 한 말: "{user_text}"
- 분석된 감정: {current_emotion}
- 오늘 가장 많이 쓴 앱: {most_used_app}

위 정보를 바탕으로 사용자에게 공감해주고, 따뜻한 디지털 디톡스 조언을 해주세요.
특히 '{current_emotion}' 상태일 때 도움이 되는 작은 행동(산책, 물 마시기 등)을 추천해주세요.
        """

        # 4. Gemini에게 답변 요청 
        try:
            response = self.model.generate_content(prompt)
            # 앞뒤 불필요한 공백 제거 후 텍스트 반환
            return response.text.strip()
        except Exception as e:
            print(f"⚠️[에러] Gemini API 호출 실패: {e}")
            # 인터넷이 끊기거나 구글 서버 문제 시 나가는 비상용 멘트
            return "숲의 신호가 잠시 약해졌어요. 잠시 후 다시 말씀해 주시겠어요? 🌿"

# 3. 테스트 실행 (이 파일만 단독 실행 시 작동)

if __name__ == "__main__":
    print("\n>>> [테스트 모드] AI 코치 대화 시뮬레이션 시작")
    
    # 테스트용 가짜 데이터
    coach = AICoach()
    test_input = "오늘 게임을 너무 많이 해서 눈이 아프고 피곤해."
    test_data = {"most_used_app": "리그 오브 레전드", "total_time": 240}
    
    print(f"사용자 입력: {test_input}")
    print(f"앱 사용 기록: {test_data}")
    print("-" * 50)
    
    # 결과 출력
    reply = coach.generate_response(test_input, test_data)
    print(f"🤖 AI 코치 답변:\n{reply}")
    print("-" * 50)