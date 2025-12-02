import re
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification


# 1. AI 모델 전역 로드 
print(">>> [System] AI 감정 분석 모델 로딩 시작...")

MODEL_NAME = "alsgyu/sentiment-analysis-fine-tuned-model"
emotion_classifier = None
LABEL_MAP = {
    'LABEL_0': '슬픔/부정',
    'LABEL_1': '중립',
    'LABEL_2': '기쁨/긍정'
}

try:
    # 토크나이저와 모델 미리 로드
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    
    emotion_classifier = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        return_all_scores=True
    )
    print(f">>> [System] 모델 로드 성공: {MODEL_NAME}")

except Exception as e:
    print(f">>> [System] 모델 로드 실패 (룰 기반으로만 작동합니다): {e}")



# 2. 감정 분석 핵심 함수

def analyze_emotion(text):
    """
    사용자의 텍스트를 받아 감정 라벨(문자열)과 분석 출처를 반환합니다.
    예: {"label": "피로", "source": "Rule-Based"}
    """
    
    # 1단계: 룰(Rule) 기반 - 피로
    fatigue_keywords = ['피곤', '지친다', '지쳤어', '무기력', '힘들다']
    if any(re.search(keyword, text) for keyword in fatigue_keywords):
        return {"label": "피로", "source": "Rule-Based (Fatigue)"}

    # 1-B단계: 룰 기반 - 피로 (패턴)
    if re.search(r'기운.*(없|안 나)', text):
        return {"label": "피로", "source": "Rule-Based (Fatigue Pattern)"}

    # 2단계: 룰 기반 - 불안
    anxiety_keywords = ['불안', '걱정', '초조', '떨린다']
    if any(re.search(keyword, text) for keyword in anxiety_keywords):
        return {"label": "불안", "source": "Rule-Based (Anxiety)"}

    # 3단계: 룰 기반 - 짜증/분노
    anger_keywords = ['짜증', '화가 나', '화나', '열 받네', '열받아']
    if any(re.search(keyword, text) for keyword in anger_keywords):
        return {"label": "짜증/분노", "source": "Rule-Based (Anger)"}

    # 4단계: AI 실수 방지용 룰 (슬픔/중립 보정)
    sad_keywords = ['슬퍼서', '슬프다', '슬퍼']
    if any(re.search(keyword, text) for keyword in sad_keywords):
        return {"label": "슬픔/부정", "source": "Rule-Based (Sadness-Fix)"}
        
    explicit_neutral_keywords = ['아무렇지도 않아']
    if any(re.search(keyword, text) for keyword in explicit_neutral_keywords):
        return {"label": "중립", "source": "Rule-Based (Neutral-Fix)"}

    # 5단계: AI 모델 추론 (모든 룰에 안 걸렸을 때)
    if emotion_classifier is not None:
        try:
            # AI 예측 수행
            results = emotion_classifier(text)[0]
            # 점수가 가장 높은 감정 선택
            top_result = sorted(results, key=lambda x: x['score'], reverse=True)[0]
            
            label_eng = top_result['label']
            label_kor = LABEL_MAP.get(label_eng, '중립') 
            
            return {"label": label_kor, "source": f"AI-Model ({label_eng})"}
            
        except Exception as e:
            print(f"AI 분석 중 런타임 오류 발생: {e}")
            return {"label": "중립", "source": "AI Runtime Error"}

    # 6단계: 기본값 (AI도 없고 룰도 안 걸림)
    return {"label": "중립", "source": "Rule-Based (Default)"}


# 3. 테스트 코드 (이 파일을 직접 실행할 때만 작동)

if __name__ == "__main__":
    print("\n----- [테스트 모드] 감정 분석 시작 -----")
    test_sentences = [
        "오늘 너무 피곤하고 지친다.",
        "내일 발표가 있어서 너무 불안해.",
        "와! 기분 진짜 좋다!",
        "그냥 그래.",
        "진짜 짜증나게 하네."
    ]
    
    for sent in test_sentences:
        result = analyze_emotion(sent)
        print(f"입력: {sent}")
        print(f"결과: {result['label']} (출처: {result['source']})\n")