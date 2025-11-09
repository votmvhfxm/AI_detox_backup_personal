# wellness/logic_goal.py
# - 감정에 따라 목표 사용 시간을 상향/하향 조정하는 간단한 규칙

def adjust_target_minutes(baseline: int, emotion: str, sensitivity: float = 1.0) -> int:
    """
    baseline(현재 목표 시간, 분)을 감정별 가중치로 조정
    - sensitivity: 사용자 민감도(1.0이 기본)
    - 최종 값은 60 ~ 180분 사이로 클램프
    """
    delta = {
        "피로": -20, "무기력": -15, "우울": -25,
        "불안": -10, "안정": +5, "활력": +10,
    }.get(emotion, 0)

    new_value = baseline + int(delta * sensitivity)
    return max(60, min(180, new_value))  # 하한/상한 제한
