!pip install transformers torch -q
!pip install sentencepiece -q

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import re

print("AI 감정 분석 모델 로드 시도")

MODEL_NAME = "alsgyu/sentiment-analysis-fine-tuned-model"
emotion_classifier = None
label_map = {} 

try:
    print(f"{MODEL_NAME} 모델, 토크나이저 수동 로드")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    
    emotion_classifier = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        return_all_scores=True
    )

    label_map = {
        'LABEL_0': '슬픔/부정',
        'LABEL_1': '중립',
        'LABEL_2': '기쁨/긍정'
    }
    print(f"모델 로드 성공: {emotion_classifier.model.name_or_path}")

except Exception as e:
    print(f"모델 로드 실패: {e}")
    print("AI 모델 로드에 실패, 룰 기반 작동")


def analyze_emotion_final(text):
 
    #1-A순위: 룰(Rule) 기반 피로
    fatigue_keywords = ['피곤', '지친다', '지쳤어', '무기력', '힘들다']
    if any(re.search(keyword, text) for keyword in fatigue_keywords):
        return {"label": "피로", "source": "Rule-Based (Fatigue)"}

    #1-B순위: 룰(Rule) 기반 피로(패턴)
    if re.search(r'기운.*(없|안 나)', text):
        return {"label": "피로", "source": "Rule-Based (Fatigue Pattern)"}

    #2순위: 룰(Rule) 기반 불안
    anxiety_keywords = ['불안', '걱정', '초조', '떨린다']
    if any(re.search(keyword, text) for keyword in anxiety_keywords):
        return {"label": "불안", "source": "Rule-Based (Anxiety)"}

    #3순위: 룰(Rule) 기반 짜증/분노
    anger_keywords = ['짜증', '화가 나', '화나', '열 받네', '열받아']
    if any(re.search(keyword, text) for keyword in anger_keywords):
        return {"label": "짜증/분노", "source": "Rule-Based (Anger)"}

    #4순위: AI가 실수한 케이스 룰로 보완
    
    #슬퍼서를 중립으로 판단하는 AI 실수 방지
    sad_keywords = ['슬퍼서', '슬프다', '슬퍼']
    if any(re.search(keyword, text) for keyword in sad_keywords):
        return {"label": "슬픔/부정", "source": "Rule-Based (Sadness-Fix)"}
        
    # 아무렇지도 않아를 부정으로 판단하는 AI 실수 방지
    explicit_neutral_keywords = ['아무렇지도 않아']
    if any(re.search(keyword, text) for keyword in explicit_neutral_keywords):
        return {"label": "중립", "source": "Rule-Based (Neutral-Fix)"}

    #5순위: 룰에 안 걸린 것만 AI가 처리
    if emotion_classifier is not None:
        try:
            results = emotion_classifier(text)[0]
            top_result = sorted(results, key=lambda x: x['score'], reverse=True)[0]
            label_eng = top_result['label']
            label_kor = label_map.get(label_eng, '중립') 
            
            return {"label": label_kor, "source": f"AI-Model ({label_eng})"}
        except Exception as e:
            print(f"AI 분석 중 오류: {e}")
            return {"label": "중립", "source": "AI Runtime Error"}

    #6순위: AI 로드 실패 시, 모든 룰에 안 걸리면 중립처리
    return {"label": "중립", "source": "Rule-Based (Default)"}

# 테스트
texts = [
    "오늘 너무 피곤하고 지친다.",           # [룰 1-A] 피로
    "내일 발표 때문에 너무 불안해.",        # [룰 2] 불안
    "아무 이유 없이 그냥 화가 나.",         # [룰 3] 짜증/분노 
    "오늘 시험 완전 잘 봤어! 기분 최고야.", # [AI] 기쁨/긍정
    "그냥 그래.",                          # [AI] 중립
    "오늘따라 기운이 하나도 없네.",         # [룰 1-B] 피로
    "정말 짜증나 죽겠어.",                  # [룰 3] 짜증/분노 
    "너무 슬퍼서 눈물이 나.",               # [룰 4] 슬픔/부정
    "이건 정말 아무렇지도 않아.",           # [룰 4] 중립
    "와 정말 대단하다!",                    # [AI] 기쁨/긍정
]

print("\n최종 안정화 함수 테스트 시작")
for text in texts:
    emotion_result = analyze_emotion_final(text)
    print(f"\n입력 문장: \"{text}\"")
    print(f"==> 최종 감정: {emotion_result['label']} (출처: {emotion_result['source']})")

print("\n테스트 종료")