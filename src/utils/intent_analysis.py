def classify_intent(text: str) -> str:
    """간단한 의도 분류"""
    text = text.lower().strip()
    
    # 긍정적 응답
    if any(word in text for word in ["네", "그래", "예", "yes", "y", "계속", "더","알았어", "알았", "알겠"]):
        return "POSITIVE"
    # 부정적 응답  
    elif any(word in text for word in ["아니", "no", "n", "그만", "종료", "나가"]):
        return "NEGATIVE"
    else:
        return "UNCLEAR"
