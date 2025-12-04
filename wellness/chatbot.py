import os
import google.generativeai as genai
from wellness.ai import analyze_emotion
from dotenv import load_dotenv

# 1. 환경 설정 및 보안 (Security)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 키가 제대로 로드되었는지 확인
if not GEMINI_API_KEY:
    print("🚨 [에러] .env 파일에서 GEMINI_API_KEY를 찾을 수 없음")
else:
    genai.configure(api_key=GEMINI_API_KEY)


# 2. AI 코치 

class AICoach:
    def __init__(self):
        if not GEMINI_API_KEY:
            self.model = None
            return

        # 테스트에서 검증된 모델 gemini-2.5-flash 사용
        try:
            self.model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=300, 
                )
            )
        except:
            # 혹시 2.5가 안 되면 1.5로 자동 전환 
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # AI 페르소나 정의
        self.persona = (
            "역할: 당신은 '디토(Ditto)'입니다. 데이터 기반의 디지털 디톡스 코치입니다.\n"
            "목표: 사용자의 '앱 사용 패턴'이 '현재 감정'에 미친 영향을 분석하고 행동을 교정하세요.\n"
            "말투: 다정하지만 논리적으로 팩트를 짚어주는 말투 (존댓말, 🌿 이모지 사용).\n"
        )

    def generate_response(self, user_text, usage_data=None):
        """
        [기능] 사용자 멘트와 앱 사용 기록을 종합하여 AI 조언을 생성합니다.
        """
        if not self.model:
            return "현재 AI 시스템 점검 중입니다. (API Key Missing) 🔧"

        # 1. 감정 분석
        try:
            emotion_result = analyze_emotion(user_text)
            current_emotion = emotion_result.get('label', '알 수 없음')
        except Exception as e:
            print(f"⚠️ 감정 분석 중 에러 발생: {e}")
            current_emotion = "중립"

        # 2. 앱 사용 데이터 처리
        if not usage_data:
            usage_data = {"most_used_app": "스마트폰", "total_time": 0}
            
        most_used_app = usage_data.get('most_used_app', '스마트폰')
        
        # 3. 프롬프트 
        prompt = f"""
{self.persona}

[데이터 분석 요청]
- 사용자 멘트: "{user_text}"
- 현재 감정: {current_emotion}
- 원인 의심 앱: {most_used_app} (과다 사용 감지됨)

[지시사항]
위 데이터를 바탕으로 다음 논리 구조로 답변하세요:
1. 원인 분석: "데이터를 보니 오늘 '{most_used_app}' 사용량이 많았던 게 {current_emotion}의 원인인 것 같아요."
2. 해결책: 스마트폰을 끄고 할 수 있는 행동 1가지 추천.
3. 독려: 짧은 응원.
        """

        # 4. Gemini에게 답변 요청
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"⚠️[에러] Gemini API 호출 실패: {e}")
            return "신호가 잠시 약해졌어요. 잠시 후 다시 말씀해 주시겠어요? 🌿"

# 3. 테스트 실행 (단독 실행 시)

if __name__ == "__main__":
    print("\n[테스트 모드]")
    coach = AICoach()
    
    test_input = "유튜브 보느라 밤새서 너무 피곤해..."
    test_data = {"most_used_app": "YouTube"}
    
    if coach.model:
        reply = coach.generate_response(test_input, test_data)
        print(f"🤖 디토의 답변:\n{reply}")
    else:
        print("API 키를 확인해주세요.")