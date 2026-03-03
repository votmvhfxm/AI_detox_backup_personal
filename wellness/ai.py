# wellness/ai.py
import re

# ✅ (중요) transformers가 없을 수도 있으니, import 자체를 try 안으로 넣는다.
emotion_classifier = None

LABEL_MAP = {
    "LABEL_0": "슬픔/부정",
    "LABEL_1": "중립",
    "LABEL_2": "기쁨/긍정",
}

MODEL_NAME = "alsgyu/sentiment-analysis-fine-tuned-model"


def _lazy_load_model():
    """
    ✅ 모델을 '필요할 때만' 로드 (서버 부팅/마이그레이션 단계에서 터지는 것 방지)
    """
    global emotion_classifier
    if emotion_classifier is not None:
        return

    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

        emotion_classifier = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            return_all_scores=True,
        )
        print(f">>> [System] 감정 모델 로드 성공: {MODEL_NAME}")

    except Exception as e:
        # transformers/torch 미설치 등 모든 실패 케이스에서 안전하게 None 유지
        emotion_classifier = None
        print(f">>> [System] 감정 모델 로드 실패 (룰 기반만 사용): {e}")


def analyze_emotion(text: str):
    """
    사용자의 텍스트를 받아 감정 라벨(문자열)과 분석 출처를 반환
    예: {"label": "피로", "source": "Rule-Based"}
    """

    # 1단계: 룰(Rule) 기반 - 피로
    fatigue_keywords = ["피곤", "지친다", "지쳤어", "무기력", "힘들다"]
    if any(re.search(keyword, text) for keyword in fatigue_keywords):
        return {"label": "피로", "source": "Rule-Based (Fatigue)"}

    # 1-B단계: 룰 기반 - 피로(패턴)
    if re.search(r"기운.*(없|안 나)", text):
        return {"label": "피로", "source": "Rule-Based (Fatigue Pattern)"}

    # 2단계: 룰 기반 - 불안
    anxiety_keywords = ["불안", "걱정", "초조", "떨린다"]
    if any(re.search(keyword, text) for keyword in anxiety_keywords):
        return {"label": "불안", "source": "Rule-Based (Anxiety)"}

    # 3단계: 룰 기반 - 짜증/분노
    anger_keywords = ["짜증", "화가 나", "화나", "열 받네", "열받아"]
    if any(re.search(keyword, text) for keyword in anger_keywords):
        return {"label": "짜증/분노", "source": "Rule-Based (Anger)"}

    # 4단계: AI 실수 방지용 룰 (슬픔/중립 보정)
    sad_keywords = ["슬퍼서", "슬프다", "슬퍼"]
    if any(re.search(keyword, text) for keyword in sad_keywords):
        return {"label": "슬픔/부정", "source": "Rule-Based (Sadness-Fix)"}

    explicit_neutral_keywords = ["아무렇지도 않아"]
    if any(re.search(keyword, text) for keyword in explicit_neutral_keywords):
        return {"label": "중립", "source": "Rule-Based (Neutral-Fix)"}

    # 5단계: AI 모델 (필요할 때만 로드)
    _lazy_load_model()

    if emotion_classifier is not None:
        try:
            results = emotion_classifier(text)[0]
            top_result = sorted(results, key=lambda x: x["score"], reverse=True)[0]

            label_eng = top_result["label"]
            label_kor = LABEL_MAP.get(label_eng, "중립")

            return {"label": label_kor, "source": f"AI-Model ({label_eng})"}

        except Exception as e:
            print(f"AI 분석 런타임 오류: {e}")
            return {"label": "중립", "source": "AI Runtime Error"}

    # 6단계: 기본값
    return {"label": "중립", "source": "Rule-Based (Default)"}
